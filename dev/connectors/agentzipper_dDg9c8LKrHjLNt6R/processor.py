import glob
import os
import re
from typing import Callable, Dict, List, Union
from urllib import parse

from ganymede_sdk.agent.models import (
    FileParam,
    FileWatcherResult,
    MultiFileParam,
    TriggerFlowParams,
)
import zipfile
from google.cloud import storage
from ganymede_sdk.storage import get_bucket_name

from ganymede_sdk import lib
from ganymede_sdk import file_tag


FLOW_NAME = "DV_Zip_Read"
INGEST_NODE = "Zip_Read"
INGEST_EXT = ".zip"

UPLOAD_PREFIX = f"{FLOW_NAME}/{INGEST_NODE}/"
INGEST_NODE_PARAM = INGEST_NODE + INGEST_EXT

NUM_FILES_TO_ZIP = 2

EQUIPMENT_NUMBER = "EQ-1234"

TAG_TYPE = "instrument_id"


def check_file_exists(bucket_source: str, blob_name: str) -> bool:
    """
    Check whether a file already exists in gcs

    Parameters
    ----------
    bucket_source: str
        'input' or 'output' bucket
    blob_name: str
        File name to generate signed URL for

    Returns
    -------
    bool
    """
    if lib._is_agent():
        set_sa_path()

    client = storage.Client()
    bucket_name = get_bucket_name(bucket_source)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()


def set_sa_path():
    sa_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "sa.json"))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path


def fp(watch_dir: str, parent_dir: str, *patterns) -> Callable[[str], bool]:
    """
    This function returns a function that performs pattern matching against a file path.
    Use this function as a template for creating your own pattern matching functions, which
    you can then use in the values of the return object in the get_param_mapping function.

    Returns
    -------
    Callable[[str], bool]
        Function that takes a file as input and returns True if the file matches the pattern.
    """

    def fp_res(x: str):
        x = parse.unquote(x)
        matched_globs = [
            glob.glob(os.path.join(watch_dir, pattern), recursive=True) for pattern in patterns
        ]
        return any([x in matched_files for matched_files in matched_globs])

    return fp_res


# Required Function
def get_param_mapping(
    watch_dir: str,
    parent_dir: str = "",
    file_name: str = "",
    modified_time: str = "",
    body: bytes = bytes(),
) -> Dict[str, Union[Callable[[str], bool], List[Callable[[str], bool]]]]:
    """
    This function is called when a file is added or modified in the watch directory.
    Modify this function to capture the files you want to trigger the flow;
    the function should return a dictionary where the keys are <node name>.<param name>
    and values are functions for performing pattern matching against the target file.

    For nodes that accept multiple inputs, specify a list of functions to match against;
    each specified function should uniquely match 1 file.
    """
    id_group = re.search(r"^(\w+)", file_name)
    if id_group is None:
        print(f"{file_name} exists in storage")
        return {}

    print(f"{file_name} does not exist in storage")

    id = id_group.group()

    print(f"Watch dir = {watch_dir}, Parent dir = {parent_dir}")

    result_dict = {
        INGEST_NODE_PARAM: fp(
            watch_dir, parent_dir, f"*.sda", f"*.txt", f"*/*.txt", f"*/*.sda", f"*/*.zip"
        )
    }

    # if file_exists_in_storage(file_name) and not file_name.endswith(".zip"):
    if check_file_exists(
        "input", UPLOAD_PREFIX.strip("/") + "/" + file_name
    ) and not file_name.endswith(".zip"):
        print(f"File {file_name} exists in storage")
        result_dict = {}

    if parent_dir != watch_dir:

        dir = os.path.join(watch_dir, parent_dir)
        parent_dir_files = [file for file in os.listdir(dir)]
        print("Found files:", parent_dir_files)
        print(f"{dir} num files = {len(parent_dir_files)}")

        if len(parent_dir_files) == NUM_FILES_TO_ZIP:
            if any([re.search("zip", file) for file in parent_dir_files]):
                return result_dict
            zip_name = os.path.join(dir, f"{parent_dir}.zip")
            print("Zipping to ", zip_name)
            with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for file in parent_dir_files:
                    zf.write(os.path.join(dir, file), os.path.basename(file))

    return result_dict


def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TriggerFlowParams:
    """
    Called when all glob patterns specified by get_param_mapping have been matched.

    Parameters
    ----------
    flow_params_fw : FileWatcherResult
        Dict of FileParam objects indexed by <node name>.<param name>
    """

    logger = kwargs["logger"]

    parent_dir = flow_params_fw.files[INGEST_NODE_PARAM].parent_dir
    watch_dir = kwargs.get("vars").get("input_path")

    filename = flow_params_fw.files[INGEST_NODE_PARAM].filename
    is_zip_file = ".zip" in filename

    logger(str((parent_dir, watch_dir, filename)))
    logger(f"Is zip file {is_zip_file}")

    if not is_zip_file:
        return None

    single_file_params = {}
    multi_file_params = {}

    for param, files in flow_params_fw.files.items():
        if isinstance(files, FileParam):
            single_file_params[param] = files
        else:
            multi_file_params[param] = MultiFileParam.from_file_param(files)

    file_tag.add_file_tag(
        flow_params_fw.files[INGEST_NODE_PARAM].upload_path,
        TAG_TYPE,
        EQUIPMENT_NUMBER,
        tag_id=EQUIPMENT_NUMBER,
    )

    return TriggerFlowParams(
        single_file_params=flow_params_fw.files,
        multi_file_params=None,
        benchling_tag=None,
        additional_params={"Input_Param": parent_dir},
    )