import glob
import os
import re
from typing import Callable
from urllib import parse
from win11toast import toast

from agent_sdk import (
    FileParam,
    FileWatcherResult,
    MultiFileParam,
    TriggerFlowParams,
    activity,
    add_file_param_to_trigger_flow,
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
    # two commits from now, use the following regex pattern
    message = "hello"
    value = toast('New File Found', message, buttons=['Approve', 'Dismiss', 'Other'], app_id="Ganymede Agent")

    id_group = re.search(r"^(\w+)", file_name)
    activity("should show up two commits from now")
    if id_group is None:
        return {}
    activity("one commit late")

    # The id found from the regex defined above
    id = id_group.group()  # noqa: F841
    return {}


def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TriggerFlowParams | None:
    """
    Called when all glob patterns specified by get_param_mapping have been matched.
    Returning None will not result in no Flow run triggered, but would still capture files matched by get_param_mapping.

    Parameters
    ----------
    flow_params_fw : FileWatcherResult
        Dict of FileParam objects indexed by <node name>.<param name>
    """
    single_file_params: dict[str, FileParam] = {}
    multi_file_params: dict[str, MultiFileParam] = {}
 

    flow_params = TriggerFlowParams(
        single_file_params=single_file_params,
        multi_file_params=multi_file_params,
        benchling_tag=None,
        additional_params={},
    )
    for param, files in flow_params_fw.files.items():
        add_file_param_to_trigger_flow(flow_params, param, files)

    return flow_params

