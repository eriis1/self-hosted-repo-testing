from agent_sdk import FileParam, UploadFileParams, add_file_tag_to_fileparam, info, debug
from dateutil.relativedelta import relativedelta
from pathlib import Path
from datetime import datetime, date
import shutil
import hashlib
import time
import os
import re
import pandas as pd

FILE_VALIDATION_TIMEOUT = 3000
FILE_COPY_TIMEOUT = 3000
FILE_WALK_TIMEOUT = 3000
FILE_UPLOAD_LIMIT = 100
FILE_COPY_LIMIT = 500
VALIDATION_MAX_FILE_SIZE_MB = 10


def delete_file(filepath):
    """
    Deletes file at provided file path.

    Catches FileNotFoundError and PermissionError and logs error message to the associated Agent.

    Parameters:
    ----------
    filepath : string
        The full path of the file to be deleted

    Returns:
    -------
    None

    """
    try:
        os.remove(filepath)
        info(f"File '{filepath}' has been deleted successfully.")
    except FileNotFoundError:
        debug(f"Warning: File '{filepath}' not found when trying to delete.")
    except PermissionError:
        debug(f"Warning: Permission denied when trying to delete '{filepath}'.")

    return None


def find_file_instances_w_tracking(
    directory, file_extensions_to_skip, timeout_seconds=FILE_WALK_TIMEOUT
):
    """
    Find file instances in a provided directory and provide either filenames or relative path.

    Finds file instances by recursively walking the specified directory. Implements a basic timeout
    to exit scenarious where an infinite loop is encountered. Tries to preempt recursion errors
    by maintaining a list of visited directories and skipping them if encountered again.

    Parameters:
    ----------
    directory_to_check : string
        The full path of the directory to check in a filesystem

    file_extensions_to_skip: list
        File extensions to ignore during directory walk

    timeout_seconds: int
        Maximum search time before raising timeout exception

    Returns:
    -------
    list
        List of all files found that match the provided extensions.

    """
    file_list = []
    visited = set()  # To keep track of visited directories
    start_time = time.perf_counter()

    info(f"in dir walk for directory:{directory}")
    loop_counter = 0
    for root, dirs, files in os.walk(directory, topdown=True):
        loop_counter += 1

        try:

            stat_info = os.stat(root)
            # On Unix, use (device ID, inode number), on Windows use (st_dev, st_ino)
            directory_id = (stat_info.st_dev, stat_info.st_ino)

            if directory_id in visited:
                continue

            visited.add(directory_id)

            for file in files:

                full_path = os.path.relpath(os.path.join(root, file), directory)

                if file_extensions_to_skip:
                    if not any(full_path.lower().endswith(ext) for ext in file_extensions_to_skip):
                        file_list.append(full_path)
                else:
                    file_list.append(full_path)

                if time.perf_counter() - start_time > timeout_seconds:
                    debug(
                        f"We reached timeout during directory walk at: {time.perf_counter() - start_time}"
                    )
                    info(f"len of file list at timeout is: {len(file_list)}")
                    info(f"len of loop counter at timeout is: {loop_counter}")
                    return file_list

        except PermissionError as e:
            continue  # Skip this directory if permission is denied


    info(f"len of loop counter at non timeout is: {loop_counter}")
    info(f"len of files list at non timeout is: {len(file_list)}")
    info(f"time passed for non timeout is: {time.perf_counter() - start_time}")
    return file_list


def copy_file(source_filepath, target_filepath):
    """
    Copies file from source_filepath to target_filepath.

    Catches FileNotFoundError and PermissionError and logs error message to the associated Agent.
    File contents are copied though file metadata is not.

    Parameters:
    ----------
    source_filepath : string
        The full path of the file to be copied

    source_filepath : string
        The full path of location where the file is to be copied.

    Returns:
    -------
    None

    """

    try:
        # copy2 can be used to preserve metadata
        shutil.copy(source_filepath, target_filepath)
    except FileNotFoundError:
        debug(f"Warning: File '{source_filepath}' not found. Cannot produce copy.")
    except PermissionError:
        debug(
            f"Warning: Permission denied when trying to copy '{target_filepath}' to network drive."
        )

    return None


def copy_files_w_timeout(file_list, source_root, target_root, timeout_seconds=FILE_COPY_TIMEOUT):
    """
    Copies list of files to provided target directory.

    Copies each provide file from the source_root to the target root. After each file is copied,
    validates file contents via md5 checksum. If the checksum does not match, the file is removed
    from the target directory. Employs a basic timeout to ensure operations are not stuck in
    a failed state. If function exits due to timeout, a partial list of succesfully copied files
    is returned.

    Parameters:
    ----------
    file_list: list
        List of files to be copied.

    source_root: string
        The root directory for files to be copied from.

    target_root: string
        The root directory for file copy locations.

    timeout_seconds: int
        Maximum time, in seconds, before raising timeout exception


    Returns:
    -------
    list
        List of all files copied prior to reaching timeout.

    """

    start_time = time.perf_counter()
    completed_files = []

    info(f"number of files to copy is: {len(file_list)} ")

    for file in file_list:
        source_path = os.path.join(source_root, file)
        target_path = os.path.join(target_root, file)

        target_dir = os.path.dirname(target_path)
        os.makedirs(target_dir, exist_ok=True)

        copy_file(source_path, target_path)

        if not checksum_validation(source_path, target_path):
            debug(
                "Warning: Validation failed for the following file: "
                + str(target_path)
                + ". Removing file to try again next cycle."
            )
            delete_file(target_path)
        else:
            completed_files.append(file)

        if time.perf_counter() - start_time > timeout_seconds:
            info(f"Warning: Timeout during copy files at: {time.perf_counter() - start_time}")
            return completed_files

    info(f"time elapsed during copy files was: {time.perf_counter() - start_time}")
    return completed_files


def checksum_validation(filepath1, filepath2):
    """
    Performs md5 checksum validation on provided filepaths.

    Opens and reads specified files in 8192 byte chunks. Catches FileNotFoundError and PermissionError and
    logs error message to the associated Agent.

    Parameters:
    ----------
    filepath1 : string
        The full path of the first file to compare.

    filepath2 : string
        The full path of the second file to compare.

    Returns:
    -------
    Bool
        Returns True if the two files contain the same contents. Otherwise returns False.

    """
    # Create a hash object
    hash_object1 = hashlib.md5()
    hash_object2 = hashlib.md5()

    try:

        # Open the file in binary mode and hash it chunk by chunk
        with open(filepath1, "rb") as f:
            while chunk := f.read(8192):
                hash_object1.update(chunk)
    except FileNotFoundError:
        debug(f"File {filepath1} not found. Cannot validate contents.")
        return False

    except PermissionError:
        debug(
            f"Permission denied when accessing {filepath1}. Unable to perform checksum validation."
        )
        return False

    try:
        with open(filepath2, "rb") as f:
            while chunk := f.read(8192):
                hash_object2.update(chunk)

    except FileNotFoundError:
        debug(f"File {filepath2} not found. Cannot validate contents.")
        return False

    except PermissionError:
        debug(
            f"Permission denied when accessing {filepath2}. Unable to perform checksum validation."
        )
        return False

    return hash_object1.hexdigest() == hash_object2.hexdigest()


def validate_files_w_timeout(
    file_list,
    source_root,
    target_root,
    timeout_seconds=FILE_VALIDATION_TIMEOUT,
    max_file_size=VALIDATION_MAX_FILE_SIZE_MB,
):
    """
    Validates contents of provided files in two locations.

    Assumes each file present in file_list is present in both source and target direcotries. Each file
    is compared in both locations via md5 checksum. If the checksum does not match, the file is removed
    from the target directory. Employs a basic timeout to ensure operations are not stuck in
    a failed state. If function exits due to timeout, a partial list of succesfully validated files is returned.

    Parameters:
    ----------
    file_list: list
        List of files to be copied.

    source_root: string
        The root directory for files to be copied from.

    target_root: string
        The root directory for file copy locations.

    timeout_seconds: int
        Maximum time, in seconds, before raising timeout exception

    max_file_size: int
        Maximum file size, in MB, for a file to be validated.


    Returns:
    -------
    list
        List of all files validated prior to reaching timeout.

    """
    start_time = time.perf_counter()
    validated_files = []

    info(f"number of files to copy is: {len(file_list)} ")

    for file in file_list:
        source_filepath = os.path.join(source_root, file)
        target_filepath = os.path.join(target_root, file)

        file_size = os.path.getsize(source_filepath) / 1048576

        if file_size > max_file_size:
            checksum_result = True
        else:
            checksum_result = checksum_validation(source_filepath, target_filepath)

        if not checksum_result:
            delete_file(target_filepath)
        else:
            validated_files.append(file)

        if time.perf_counter() - start_time > timeout_seconds:
            info(f"We reached timeout during validate files at: {time.perf_counter() - start_time}")
            return validated_files

    info(f"time elapsed during validate files was: {time.perf_counter() - start_time}")
    return validated_files


def parse_experiment_from_filename(filename):
    """
    Parsed provided string for experiment id prepended by 'EXP'.

    Parameters:
    ----------
    filename: str
        List of files to be copied.

    Returns:
    -------
    str
        Returns first instance that matches the search pattern. If no match is found
        returns 'invalid_exp_id'.

    """
    experiment_pattern = r"EXP\d+"

    matches = re.findall(experiment_pattern, filename)
    try:
        parsed_tag = matches[0]
    except:
        parsed_tag = "invalid_exp_id"

    return parsed_tag


def parse_plate_from_filename(filename):
    """
    Parsed provided string for a plate id by searching for 'PLT' prepended and appended with digits.

    Parameters:
    ----------
    filename: str
        List of files to be copied.

    Returns:
    -------
    str
        Returns first instance that matches the search pattern. If no match is found
        returns 'invalid_plate_id'.

    """
    plate_pattern = r"\d+PLT\d+"

    matches = re.findall(plate_pattern, filename)

    try:
        parsed_tag = matches[0]
    except:
        parsed_tag = "invalid_plate_id"

    return parsed_tag


def sanitize_extension_list_from_user_input(kwargs, variable_name):
    """
    Reads and sanitizes connection level variable associated with the provided variable name.

    All bracketing characers are removed from the user specified string and separated by comma.
    Separated strings without a '.' automatically have a '." added to them.

    Parameters:
    ----------
    variable_name: str
        Agent level variable name.

    Returns:
    -------
    list
        Returns list of file extensions extracted from user input.

    """
    

    sanitized_input = re.sub(
        r"[(){}\[\]<> \s]",
        "",
        kwargs.get("vars", {}).get(variable_name),
    )

    
    parsed_extensions = sanitized_input.split(",")
    file_extension_list = [
        ext.lower() if ext.startswith(".") else f".{ext}".lower() for ext in parsed_extensions
    ]

    return file_extension_list


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    info(f"execution time was: {datetime.now()} ")

    time.sleep(185)


    
    return None



