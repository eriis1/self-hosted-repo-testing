from typing import Callable

import glob
import os

from agent_sdk import (
    FileParam,
    FileWatcherResult,
    MultiFileParam,
    TriggerFlowParams,
    add_file_tag_to_fileparam,
    debug,
    error,
    info,
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
        # To only get files directly in watch_dir, use the following line instead of the glob with parent_dir:
        # return x in glob.glob(os.path.join(watch_dir, pattern), recursive=True)
        return x in glob.glob(os.path.join(watch_dir, parent_dir, pattern), recursive=True)

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
    # id_group = re.search(r"^(\w+)", file_name)
    # if id_group is None:
    #     return {}

    # The id found from the regex defined above
    # id = id_group.group()  # noqa: F841
    return {
        "CSV_Read.csv": fp(watch_dir, parent_dir, f"*.csv"),
    }


def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TriggerFlowParams | None:
    """
    Called when all glob patterns specified by get_param_mapping have been matched.
    Returning None will result in no Flow run triggered, but would still capture files matched by get_param_mapping.

    Parameters
    ----------
    flow_params_fw : FileWatcherResult
        Dict of FileParam objects indexed by <node name>.<param name>

    Returns
    -------
    TriggerFlowParams | None
        Files and parameters to execute Flow with; if set to None, then Flow will not be triggered.
        If set to TriggerFlowParams, then the Flow will be triggered with the specified parameters.
    """

    # # The path that the agent is watching
    # input_path = kwargs.get("vars", {}).get("input_path", "")

    # # parent_dir is the subdirectory relative to watch_dir where the file was found. Or watch dir itself if the file was found directly in watch_dir.
    # file_param = list(flow_params_fw.files.values())[0]
    # parent_dir = file_param.parent_dir if file_param.parent_dir else ""
    # if input_path and parent_dir.startswith(input_path):
    #     parent_dir = parent_dir[len(input_path):].lstrip(os.sep)

    # # Types of logging
    # info(f"Parent directory: {parent_dir}")
    # debug(f"Parent directory: {parent_dir}")
    # error(f"Parent directory: {parent_dir}")

    # # Tag files with values derived from the directory structure.
    # # add_file_tag_to_fileparam accepts both FileParam and MultiFileParam.
    # # tag_type_id must match a tag type configured in your Ganymede tenant.
    # for param in flow_params_fw.files.values():
    #     add_file_tag_to_fileparam(param, "tag_id_change_me", parent_dir)

    # Route each param to singleFileParams or multiFileParams based on type.
    single_file_params = {}
    multi_file_params = {}
    for key, param in flow_params_fw.files.items():
        if isinstance(param, MultiFileParam):
            multi_file_params[key] = param
        else:
            single_file_params[key] = param

    return TriggerFlowParams(
        singleFileParams=single_file_params or None,
        multiFileParams=multi_file_params or None,
    )
