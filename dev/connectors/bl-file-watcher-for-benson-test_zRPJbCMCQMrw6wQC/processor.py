from typing import Callable

import glob
import os
import re
from urllib import parse

from agent_sdk import FileParam, FileWatcherResult, TriggerFlowParams


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
) -> dict[str, Callable[[str], bool] | list[Callable[[str], bool]]]:
    """
    This function is called when a file is added or modified in the watch directory.
    Modify this function to capture the files you want to trigger the flow;
    the function should return a dictionary where the keys are <node name>.<param name>
    and values are functions for performing pattern matching against the target file.

    For nodes that accept multiple inputs, specify a list of functions to match against;
    each specified function should uniquely match 1 file.
    """
    # if a certain pattern should be used to group files for a flow
    id_group = re.search(r"^(\w+)", file_name)
    if id_group is None:
        return {}

    # The id found from the regex defined above
    id = id_group.group()  # noqa: F841
    return {
        "Ingest_Data.csv": fp(watch_dir, parent_dir, f"*.csv"),
    }


def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TriggerFlowParams | None:
    """
    Called when all glob patterns specified by get_param_mapping have been matched.
    Returning None will result in no Flow run triggered, but would still capture files matched by get_param_mapping.

    Parameters
    ----------
    flow_params_fw : FileWatcherResult
        Dict of FileParam objects indexed by <node name>.<param name>
    """

    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection

    single_file_param_key = "CSV_Read.csv"
    multi_file_param_key = "XML_Read.xml"

    params = TriggerFlowParams()

    for param in flow_params_fw.files.values():
        if isinstance(param, FileParam):
            params.add_file_param(param_node_key=single_file_param_key, file=param)
        elif isinstance(param, list):
            params.add_file_param(param_node_key=multi_file_param_key, files=param)

    params.set_text_param("custom param", "new val")

    return params