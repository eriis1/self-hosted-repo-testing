from typing import List, Optional
import time
import zipfile
from dataclasses import dataclass
from ganymede_sdk.agent.models import TriggerFlowParams, FileParam

# TODO: tag files
# from ganymede_sdk.agent.models import Tag
from google.cloud import storage
import os
import fnmatch
from datetime import datetime, timedelta
from pathlib import Path

WATCH_DIRECTORY = Path("D:/Data/Ganymede")
BUCKET_NAME = "ganymede-umoja-test-lab-ingest"
# PREFIX = "LCMS-Instrument-Output/Input_File"
# PARAM = "Input_File.file_pattern"
FILEPATH_SEP = "---"

PATTERNS_TO_ZIP = ["*.d", "inst_method*", "LC_*"]

# BUCKET_NAME = "ganymede-ganymede-dev-lab-ingest"
PREFIX = "luke-multi-----/Input_File"
PARAM = "Input_File---------lksdjflskj.file_pattern"


@dataclass
class FileUpload:
    local_relative_pathname: str
    cloud_filename: str

def matches_zip_pattern(filename: str) -> bool:
    """
    Check if a file matches any of the patterns in `PATTERNS_TO_ZIP`.
    """
    for pattern in PATTERNS_TO_ZIP:
        if fnmatch.fnmatch(filename, pattern):
            print(f"File {filename} matches pattern {pattern}")
            return True
    print(f"File {filename} NOT matches any pattern")
    return False

def was_zipped_before_upload(filename: str) -> bool:
    """
    Check if a file was zipped before upload by checking if the file matches any of the patterns
    in `PATTERNS_TO_ZIP` and ends in `.zip`.
    """
    if filename.endswith(".zip"):
        filename_sans_zip = filename[:-4]
        return matches_zip_pattern(filename_sans_zip)
    return False

def execute(**kwargs) -> Optional[TriggerFlowParams]:  # type: ignore
    print("Executing at", datetime.now())
    finished_filenames = scan_for_finished_files(WATCH_DIRECTORY)
    print("Locally complete files:", finished_filenames)
    finished_files: List[FileUpload] = convert_to_upload_names(finished_filenames)
    already_uploaded = check_if_already_uploaded(finished_files)
    print(f"Already uploaded files in {BUCKET_NAME}/{PREFIX}:", already_uploaded)
    for file in already_uploaded:
        # If a file/dir was zipped and then uploaded, delete the local .zip file 
        if was_zipped_before_upload(file.cloud_filename):
            # check if the file exists before deleting it
            local_copy = WATCH_DIRECTORY / file.cloud_filename
            if os.path.exists(local_copy):
                print(
                    f"Removing {file.cloud_filename} since the temporary .zip file was already uploaded",
                )
                os.remove(local_copy)
    not_uploaded = [file for file in finished_files if file not in already_uploaded]
    print("Files to upload:", not_uploaded)
    if len(not_uploaded):
        current_file_to_process = not_uploaded[0]
        if  matches_zip_pattern(current_file_to_process.local_relative_pathname):
            # TODO: look into using zip to store full relative path
            print("Zipping", current_file_to_process.local_relative_pathname)
            zip_directory(
                WATCH_DIRECTORY / current_file_to_process.local_relative_pathname,
                WATCH_DIRECTORY / current_file_to_process.cloud_filename,
            )
            return get_flow_trigger(current_file_to_process)
        else:
            return get_flow_trigger(current_file_to_process)
    else:
        return None


def get_flow_trigger(file: FileUpload) -> TriggerFlowParams:
    upload_time = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    if file.cloud_filename.endswith(".zip"):
        content_type = "application/zip"
        body = open(WATCH_DIRECTORY / file.cloud_filename, "rb").read()
    else:
        content_type = "application/octet-stream"
        body = open(WATCH_DIRECTORY / file.local_relative_pathname, "rb").read()

    new_file_param = FileParam(
        file.cloud_filename,
        content_type,
        body,
        PARAM,
        "",
        upload_time,
    )

    # TODO add tags
    # tag = Tag(
    #     file.cloud_filename.split(FILEPATH_SEP)[0],
    #     file.cloud_filename.split(FILEPATH_SEP)[0],
    #     upload_time,
    # )
    return TriggerFlowParams(
        single_file_params={new_file_param.param: new_file_param},
        multi_file_params=None,
        # benchling_tag=tag,
        benchling_tag=None,
        additional_params=None,
    )


def convert_to_upload_names(finished_files: List[str]) -> List[FileUpload]:
    """
    Convert file paths to upload names where `path/to/file` becomes `path---to---file`
    if FILEPATH_SEP is `---`.

    certain files/dirs are zipped together before upload, so the upload name will be the 
    zip file name
    """
    result = []
    for file in finished_files:
        if matches_zip_pattern(file):
            result.append(FileUpload(file, file.replace(os.sep, FILEPATH_SEP) + ".zip"))
        else:
            result.append(FileUpload(file, file.replace(os.sep, FILEPATH_SEP)))
    return result


def get_sa_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "sa.json"))


def check_if_already_uploaded(finished_files: List[FileUpload]) -> List[FileUpload]:
    """
    Check if a file exists in the cloud bucket already according its "cloud filename",
    which is the filepath with the path separator replaced with FILEPATH_SEP.
    """
    storage_client = storage.Client.from_service_account_json(get_sa_path())
    blobs = storage_client.list_blobs(BUCKET_NAME, prefix=PREFIX)
    already_uploaded_filenames = [str(b.name.split(PREFIX + "/")[1]) for b in blobs]

    return [file for file in finished_files if file.cloud_filename in already_uploaded_filenames]


@dataclass
class ScanResult:
    relative_path: str
    modified_time: datetime


def get_most_recent_access_result(directory: Path) -> Optional[ScanResult]:
    """
    Return the access time of the most recently accessed file in a directory.
    Access time is updated when a file is read or written to.

    :param directory: Directory to scan
    :return: datetime of the most recently accessed file
    """
    max_atime = 0
    max_atime_file = None
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            atime = os.path.getatime(filepath)
            max_atime = max(max_atime, atime)  # type: ignore
            max_atime_file = filepath

    return ScanResult(max_atime_file, datetime.fromtimestamp(max_atime)) if max_atime_file else None


def filter_by_age(scan_results: List[ScanResult], min_age_in_min: int) -> List[str]:
    """
    Filter a list of ScanResult objects to only include those with a mod_time
    that's at least `age` minutes old.

    :param scan_results: List of ScanResult objects
    :param age: Age threshold in minutes
    :return: List of ScanResult objects older than `age` minutes
    """
    min_cutoff_time = datetime.now() - timedelta(minutes=min_age_in_min)

    for result in scan_results:
        print(result.relative_path, result.modified_time, result.modified_time < min_cutoff_time)

    return [
        result.relative_path for result in scan_results if result.modified_time < min_cutoff_time
    ]


def is_file_ready(filename, interval_in_seconds=0.1):
    """
    Checks whether a file is ready to be read from.
    - Tries to obtain an exclusive lock.
    - Checks if the last modification time changes over an interval.
    - Checks if the file size changes over an interval.
    If conditions are met (seems like file is not being changed), file is assumed to be ready.
    """
    try:
        # Attempt to open and lock the file
        # This will throw an exception if it cannot obtain an exclusive lock
        with open(filename, "rb+", buffering=0) as _:
            pass

        # Check file modification time
        mtime1 = os.path.getmtime(filename)

        # Check file size
        size1 = os.path.getsize(filename)

        # Wait for specified interval
        time.sleep(interval_in_seconds)

        mtime2 = os.path.getmtime(filename)
        size2 = os.path.getsize(filename)

        # If the modification time or file size changes, return False
        if mtime1 != mtime2 or size1 != size2:
            return False
        else:
            return True

    except Exception:
        return False


def list_files_recursive(path):
    all_files = []
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            all_files.append(os.path.join(dirpath, filename))
    return all_files


def scan_for_finished_files(base_dir: Path, age_in_minutes: int = 1) -> List[str]:
    """
    Scan a directory and return paths with their datetime of last modification
    that are at least `age_in_minutes` old.

    :param base_dir: Base directory to start the scan
    :param directory_pattern: Glob pattern that, if a directory matches, the directory will be
        checked instead of the files within it.
    :return: List of ScanResult objects
    """
    result = []

    for root, dirs, files in os.walk(base_dir):
        # Some directories are zipped together and uploaded, so all files within them need to be ready before
        # the directory is ready
        for directory_pattern in PATTERNS_TO_ZIP:
            for d in dirs[:]:  # Iterate over a slice copy so we can modify `dirs` in-place
                if fnmatch.fnmatch(d, directory_pattern):
                    dirpath = os.path.join(root, d)
                    rel_dirpath = os.path.relpath(dirpath, base_dir)
                    access_result = get_most_recent_access_result(Path(dirpath))
                    if access_result is not None:
                        files_before = list_files_recursive(access_result.relative_path)
                        if is_file_ready(access_result.relative_path):
                            # The above `if`` statement waits to check if the most recent file is
                            # still being written to over an time interval. We also double check
                            # that other files have not been together and uploaded during this same interval.
                            files_after = list_files_recursive(access_result.relative_path)
                            if set(files_before) == set(files_after):
                                result.append(ScanResult(rel_dirpath, access_result.modified_time))
                    dirs.remove(d)

        for filename in files:
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, base_dir)
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if is_file_ready(filepath):
                result.append(ScanResult(rel_path, mod_time))

    return filter_by_age(result, age_in_minutes)


def zip_directory(directory, output_filename):
    """
    Zip an entire directory and save it to an output file.

    :param directory: The directory to be zipped.
    :param output_filename: The file where the archive should be saved.
    """
    # Get the base name of the directory to ensure the top-level folder is preserved
    base_dir = os.path.basename(directory)

    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(directory):
            for file in files:
                # Adjust the path to include the base directory
                full_path_name = os.path.join(
                    base_dir, os.path.relpath(os.path.join(root, file), directory)
                )
                zip_file.write(os.path.join(root, file), full_path_name)
