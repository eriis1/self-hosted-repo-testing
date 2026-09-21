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
        "Excel_Read.excel": fp(watch_dir, parent_dir, f""),
        "CSV_Read_Multi.csv": fp(watch_dir, parent_dir, f""),
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

    for param, files in flow_params_fw.files.items():
        if isinstance(files, FileParam):
            single_file_params[param] = files
        else:
            multi_file_params[param] = MultiFileParam.from_file_param(files)

    return TriggerFlowParams(
        single_file_params=flow_params_fw.files,
        multi_file_params=None,
        benchling_tag=None,
        additional_params={},
    )
