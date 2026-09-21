from typing import Callable

import glob
import os
import re
from urllib import parse

from agent_sdk import FileParam, MultiFileParam, FileWatcherResult, TriggerFlowParams, debug


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
    csv_tags = ["WellTable", "PeakTable", "SizeTable"]

    gxd_file_pattern = "Input_File_Multi_GXD.file_pattern"
    csv_file_pattern = "Input_File_Multi_CSV.file_pattern"

    # if a certain pattern should be used to group files for a flow
    id_group = re.search(
        r"^(\w+)", re.sub("|".join([f"_{tag}" for tag in csv_tags]), "", file_name)
    )
    if id_group is None:
        return {}

    # The id found from the regex defined above
    id = id_group.group()  # noqa: F841

    res = {
        gxd_file_pattern: fp(watch_dir, parent_dir, f"{id}.gxd"),
        **{
            f"{csv_file_pattern}_{i}": fp(watch_dir, parent_dir, f"{id}_{tag}.csv")
            for i, tag in enumerate(csv_tags)
        },
    }
    debug(id, f"{id}_WellTable.csv", str(res.keys()))

    return res


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

    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection

    single_file_params = {}
    multi_file_params = {}

    for file_name, file_param in flow_params_fw.files.items():
        param_name = file_param.param
        node_search = re.search("(.*)(_\d$)", param_name)
        if node_search:
            new_param_name = node_search.group(1)
            if new_param_name not in multi_file_params:
                multi_file_params[new_param_name] = MultiFileParam(files={}, param=new_param_name)
            file_param.param = new_param_name
            print(f"{param_name} -> {new_param_name}")
            multi_file_params[new_param_name].files.append(file_param)
        else:
            print(f"{param_name}")
            single_file_params[param_name] = file_param

    return TriggerFlowParams(singleFileParams=single_file_params, multiFileParams=multi_file_params)