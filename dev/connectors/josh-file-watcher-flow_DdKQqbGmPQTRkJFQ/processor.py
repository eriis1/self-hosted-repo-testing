import glob
import os
import re
from typing import Callable, Dict, List, Union
from urllib import parse

from agent_sdk import (
    FileParam,
    FileWatcherResult,
    MultiFileParam,
    TriggerFlowParams,
    debug
)
# from ganymede_sdk import lib
# from ganymede_sdk.editor.secrets import access_secret_version
from datetime import datetime


def fp(watch_dir: str, parent_dir: str, pattern: str) -> Callable[[str], bool]:
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
        return x in glob.glob(os.path.join(watch_dir, pattern), recursive=True)

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
        return {}
    id = id_group.group()
    return {
        # "CSV_Read3750.csv": fp(watch_dir, parent_dir, f"param2*.csv"),
        "CSV_Read_1157.csv": fp(watch_dir, parent_dir, f"param1*.csv"),
        # "XML_FEB1.xml": fp(watch_dir, parent_dir, f"*.xml"),
    }


def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TriggerFlowParams:
    """
    Called when all glob patterns specified by get_param_mapping have been matched.

    Parameters
    ----------
    flow_params_fw : FileWatcherResult
        Dict of FileParam objects indexed by <node name>.<param name>
    """
    single_file_params = {}
    multi_file_params = {}
    # from google.cloud import storage
    logger = kwargs["logger"]

    # print("IS AGENT: ", lib._is_agent())
    # # Necessary to authZ with the correct credentials in agent config
    # sa_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "sa.json"))
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path

    # try:
        # storage_client = storage.Client()
        # project_id = storage_client.project
        # logger("accessing secret")
    
        # env_name = "ganymede-dev"
    
        # secret = access_secret_version(project_id, f"{env_name}-var-example_secret", "latest")
    
        # secret = get_secret("example_secret")
    #     logger(f"got secret: {secret}")
    # except Exception as e:
    #     logger("!!!!!! Exception: ", e)
    #     raise e

    for param, files in flow_params_fw.files.items():
        if isinstance(files, FileParam):
            single_file_params[param] = files
        else:
            multi_file_params[param] = MultiFileParam.from_file_param(files)
    test_var = kwargs.get("vars", {}).get("test", "")
    curr_ts = datetime.now().strftime("%H:%M:%S")
    debug(f">>> Result: {test_var=} at {curr_ts}")

    return TriggerFlowParams(
        single_file_params=flow_params_fw.files,
        multi_file_params=None,
        benchling_tag=None,
        additional_params={},
    )






