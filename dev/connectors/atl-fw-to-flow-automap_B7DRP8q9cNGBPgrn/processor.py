from typing import Callable

import glob
import os
import re
from urllib import parse

import agent_sdk
from agent_sdk import (
    FileParam,
    FileWatcherResult,
    MultiFileParam,
    TriggerFlowParams,
    add_file_param_to_trigger_flow,
    add_file_tag_to_fileparam,
    info,
)

INSTRUMENT_PATH_TAG_TYPE_ID = "instrument"
print("237")

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
        agent_sdk.debug(f"** X: {x}")
        x = parse.unquote(x)
        agent_sdk.debug(f"** watch_dir: {watch_dir}")
        agent_sdk.debug(
            f"** os.path.join(watch_dir, **, pattern),: {os.path.join(watch_dir, '**', pattern)}"
        )
        agent_sdk.debug(
            f"** globs: {glob.glob(os.path.join(watch_dir, '**', pattern), recursive=True)}"
        )
        return x in glob.glob(os.path.join(watch_dir, "**", pattern), recursive=True)

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
        "CSV_Read.csv": fp(watch_dir, parent_dir, f"sample_*.csv"),
        # "Input_File.file_pattern": fp(watch_dir, parent_dir, f"*.txt"),
    }


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
    # print("TEST UPDATE 1115 1336")
    info(f"&&&&& TEST UPDATE 09192025 0946")

    # flow_params = TriggerFlowParams(
    #     single_file_params=single_file_params,
    #     multi_file_params=multi_file_params,
    #     benchling_tag=None,
    #     additional_params={},
    # )
    # for param, files in flow_params_fw.files.items():
    #     add_file_param_to_trigger_flow(flow_params, param, files)

    # return flow_params
    agent_variables = kwargs.get("vars", {})
    watch_dir = agent_variables.get("input_path", None)
    info(f"&&&&& watch_dir: {watch_dir}")

    for param, file_param in flow_params_fw.files.items():

        relative_path = file_param.parent_dir  # type: ignore
        info(f"&&&&& relative_path: {relative_path}")

        info(
            f"Adding tag '{INSTRUMENT_PATH_TAG_TYPE_ID}:{relative_path}' to file param: {file_param}"
        )
        add_file_tag_to_fileparam(
            file_param=file_param,  # type: ignore
            tag_type_id=INSTRUMENT_PATH_TAG_TYPE_ID,
            display_value=os.path.join(watch_dir, relative_path),
        )
        single_file_params[param] = file_param  # type: ignore

    flow_params = TriggerFlowParams(
        single_file_params=single_file_params,  # type: ignore
        multi_file_params=multi_file_params,  # type: ignore
        benchling_tag=None,  # type: ignore
        additional_params={},  # type: ignore
    )
    for param, file_param in flow_params_fw.files.items():
        add_file_param_to_trigger_flow(flow_params, param, file_param)

    info(f"&&&&& flow_params: {flow_params}")
    return flow_params


