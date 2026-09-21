from typing import List, Optional
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

# TODO: update these
# cron is happening way to quickly, and not waiting long enough
WATCH_DIRECTORY = Path("./data_files/Ganymede")
BUCKET_NAME = "ganymede-ganymede-dev-lab-ingest"
PREFIX = "LC-test-luke/Input_File"
PARAM = "Input_File.file_pattern"
FILEPATH_SEP = "---"


@dataclass
class FileUpload:
    local_relative_pathname: str
    cloud_filename: str


def execute(**kwargs) -> Optional[TriggerFlowParams]:  # type: ignore
    print("Executing at", datetime.now())
    finished_filenames = scan_for_finished_files(
        WATCH_DIRECTORY, ignore_pattern="*.d", age_in_minutes=2
    )
    print("Locally complete files:", finished_filenames)
    finished_files: List[FileUpload] = convert_to_upload_names(finished_filenames)
    already_uploaded = check_if_already_uploaded(finished_files)
    print(f"Already uploaded files in {BUCKET_NAME}/{PREFIX}:", already_uploaded)
    for file in already_uploaded:
        # If a *.d.zip file has been uploaded, delete the local copy
        if file.cloud_filename.endswith(".d.zip"):
            # check if the file exists before deleting it
            # For *.d.zip files, we'd have mae a local copy that has the same name as the cloud file
            local_copy = WATCH_DIRECTORY / file.cloud_filename
            if os.path.exists(local_copy):
                print(
                    "Removing",
                    file.cloud_filename,
                    "since the temporary .d.zip file was already uploaded",
                )
                os.remove(local_copy)
    not_uploaded = [file for file in finished_files if file not in already_uploaded]
    print("Files to upload:", not_uploaded)
    if len(not_uploaded):
        current_file_to_process = not_uploaded[0]
        if current_file_to_process.local_relative_pathname.endswith(".d"):
            # TODO: look into using zip to store full relative path
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
    if file.cloud_filename.endswith(".d.zip"):
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

    `*.d` "files" (actually directories) are converted to `*.d.zip` files as well.
    """
    result = []
    for file in finished_files:
        if file.endswith(".d"):
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
    Access time is update when a file is read or written to.

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


def filter_by_age(
    scan_results: List[ScanResult], min_age_in_min: int, max_age_in_hours: int = 94
) -> List[str]:
    """
    Filter a list of ScanResult objects to only include those with a mod_time
    that's at least `age` minutes old.

    :param scan_results: List of ScanResult objects
    :param age: Age threshold in minutes
    :return: List of ScanResult objects older than `age` minutes
    """
    min_cutoff_time = datetime.now() - timedelta(minutes=min_age_in_min)
    max_cutoff_time = datetime.now() - timedelta(minutes=max_age_in_hours * 60)

    for result in scan_results:
        print(result.relative_path, result.modified_time)

    return [
        result.relative_path
        for result in scan_results
        if result.modified_time < min_cutoff_time and result.modified_time > max_cutoff_time
    ]


def is_file_ready(filename):
    """
    Try to open a file in read/write mode to see if it's ready to be read from.
    """
    try:
        with open(filename, "rb+", buffering=0) as _:
            pass
        return True
    except IOError:
        return False


def scan_for_finished_files(
    base_dir: Path, ignore_pattern: Optional[str] = None, age_in_minutes: int = 1
) -> List[str]:
    """
    Scan a directory and return paths with their datetime of last modification
    that are at least `age_in_minutes` old

    :param base_dir: Base directory to start the scan
    :param ignore_pattern: Glob pattern to match directories
    :return: List of ScanResult objects
    """
    result = []

    for root, dirs, files in os.walk(base_dir):
        if ignore_pattern:
            # Check directories based on the ignore pattern
            for d in dirs[:]:  # Iterate over a slice copy so we can modify `dirs` in-place
                if fnmatch.fnmatch(d, ignore_pattern):
                    dirpath = os.path.join(root, d)
                    rel_dirpath = os.path.relpath(dirpath, base_dir)
                    access_result = get_most_recent_access_result(Path(dirpath))
                    if access_result is not None and is_file_ready(access_result.relative_path):
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
