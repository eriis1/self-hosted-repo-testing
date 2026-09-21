import re
from pathlib import Path
import os
import time
from typing import Tuple, Union, Callable

# from agent_sdk import info, error
from ganymede_sdk.agent.models import (
    FileParam,
    FileWatcherResult,
    MultiFileParam,
    NoOpFileTagParams,
    ObservedFile,
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
) -> dict[str, Callable[[str], bool] | list[Callable[[str], bool]]]:
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
        "Input_File.file_pattern": fp(watch_dir, parent_dir, f"*.trc"),
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
        # additional_params={},
    )


# user-defined function to map files to flow parameters
# def get_param_mapping(
#     file_current: ObservedFile,
#     files_captured: Union[dict[str, ObservedFile], None] = None,
#     watch_dir: str = "",
#     logger=None,
#     **kwargs,
# ) -> Tuple[str | None, ObservedFile, bool]:
#     """
#     This function is called when a file is added or modified in the watch directory.  By default, it maps the
#     current file to a pattern if it matches any pattern not yet matched in patterns_expected.  This function
#     is called by the agent event loop.

#     A flow is triggered when all of the following are true:
#      1. all patterns specified in patterns_expected are matched
#      2. all matched ObservedFile objects have their ready flag set to True
#      3. _required_seconds_since_mod_ seconds has elapsed since last file modification for all matched ObservedFile objects

#     Parameters
#     ----------
#     file_current : ObservedFile
#         path to newly observed file to compare against patterns
#     files_captured : dict[str, ObservedFile]
#         files previously associated with patterns, keyed by node parameter to associate with
#     watch_dir: str
#         directory being watched by the agent
#     logger: logging.Logger
#         logger object for logging messages when the agent is running

#     Returns
#     -------
#     Tuple[str, ObservedFile, bool]
#         Returns a tuple with 3 elements:
#         - a string with the node parameter that was matched
#         - the ObservedFile object that was matched
#         - a boolean flag indicating whether all patterns have been matched and are ready for flow processing

#     Example Modifications
#     ---------------------
#     - Modify logic to determine how to handle multiple files that should match the same pattern
#     - Modify patterns_expected based on the content of a specific file (e.g. based on the contents of a plate map file)
#     - Set the ready flag to False for the current_file if the file is not ready for processing
#     - Set the required_seconds_since_mod to a non-zero value to require a file to be aged before processing

#     Notes
#     -----
#     ObservedFile has the following attributes that can be modified to specify whether a file is ready for flow processing:
#     - required_seconds_since_mod: float
#         number of seconds that must elapse without file modification before the file is considered ready for flow processing, by default 0.0
#     - ready: bool
#         flag if the file is ready for flow processing, by default True
#     """

#     # keys are the <node name>.<param name> to match against
#     # values are the regex patterns to match against
#     patterns_expected = {"Input_File.file_pattern": "*.trc"}

#     if not files_captured:
#         files_captured = {}

#     # file_current.required_seconds_since_mod = 60
#     assert all(
#         [k.count(".") == 1 for k in patterns_expected.keys()]
#     ), "Each key in patterns_expected should be of the form <node name>.<param name>"

#     # obtain set of unmatched patterns
#     unmatched_patterns = {
#         flow_param: filename_regex
#         for flow_param, filename_regex in patterns_expected.items()
#         if flow_param not in files_captured.keys()
#     }

#     # match observed file against unmatched patterns
#     matched_flow_param = None
#     for flow_param, pattern in unmatched_patterns.items():
#         if re.match(pattern, file_current.file_name):
#             matched_flow_param = flow_param
#             if logger:
#                 logger(f"Matched {file_current.file_name} to {flow_param}...")
#             break

#     # update unmatched_patterns dictionary
#     if matched_flow_param:
#         matched_file = file_current
#         files_captured.update({matched_flow_param: matched_file})
#         del unmatched_patterns[matched_flow_param]
#     else:
#         matched_file = None
#         if logger:
#             logger(
#                 f"Did not find a param with a matching filter for path {file_current.file_path}",
#             )

#     ready_for_execution = (
#         all([file.is_ready for file in files_captured.values()]) and not unmatched_patterns
#     )

#     return matched_flow_param, matched_file, ready_for_execution


# # user-defined function to associate files with parameters and trigger flow
# def execute(
#     flow_params_fw: FileWatcherResult, logger=None, **kwargs
# ) -> NoOpFileTagParams | TriggerFlowParams:
#     """
#     This function is called when all regex patterns specified by get_param_mapping have been matched.  It
#     allows for any adjustments to logic mapping captured files to node parameters on a triggered flow.

#     Parameters
#     ----------
#     flow_params_fw : FileWatcherResult
#         Dict of FileParam objects indexed by <node name>.<param name>
#     logger: logging.Logger
#         logger object for logging messages when the agent is running

#     Returns
#     -------
#     NoOpFileTagParams | TriggerFlowParams
#         Object containing the mapping to trigger flow.

#     Example Modifications
#     ---------------------
#     - The upload_only flag can be set to True to only upload files when the user wants to keep files
#       that do not conform with what is expected by the downstream flow.
#     - Tag files being uploaded using [add_file_tag_to_fileparam](https://docs.ganymede.bio/connectivity/Tags#tagging-files-in-agents)

#     Notes
#     -----
#     The TriggerFlowParams object has the following parameters for accepting inputs from the agent:
#     - single_file_params: dict[str, FileParam] are files uploaded to nodes that accept a single file
#     - multi_file_params: dict[str, MultiFileParam] are files uploaded to nodes that accept multiple files
#     - benchling_tag: dict[str, str] are used to specify parameters, used with the Benchling_Tag node type
#     - additional_params: dict[str, str] is a dictionary of input parameters, used with the Input_Param node type
#     """

#     # agent_variables = kwargs.get("agent_variables", {})
#     # watch_dir = agent_variables.get("input_path", None)
#     # print(f"watch_dir = {watch_dir}")
#     # recency_min = float(agent_variables.get("recency_min", 0))
#     # print(f"recency_min = {recency_min}")
#     # recency_max = float(agent_variables.get("recency_max", 3600))
#     # print(f"recency_max = {recency_max}")

#     # filepath = list(flow_params_fw.files.values())[0]
#     # print(f"file's path = {filepath}")

#     # elapsed_time = time.time() - os.stat(file_path).st_mtime
#     # if elapsed_time >= recency_min and elapsed_time < recency_max:
#     #     if not os.access(full_file_path, os.R_OK):
#     #         raise OSError(f"Do not have read permissions for file {full_file_path}")
#     #         return None
#     #     # new_file_param = FileParam(filename=str(full_file_path), body=body)
#     #     return TriggerFlowParams(
#     #         single_file_params=flow_params_fw.files,
#     #         multi_file_params=None,
#     #         benchling_tag=None,
#     #         additional_params={},
#     #     )
#     # else:
#     #     print(
#     #         f"File exists, but was last modified {elapsed_time} seconds ago.  Only files modified between {recency_min} and {recency_max} seconds are uploaded."
#     #     )
#     #     return None

#     single_file_params = {}
#     upload_only = False

#     for param, files in flow_params_fw.files.items():
#         single_file_params[param] = files

#     # can implement user-defined logic to determine if flow should be triggered
#     if upload_only:
#         return NoOpFileTagParams(files=list(flow_params_fw.files.values()))

#     return TriggerFlowParams(
#         single_file_params=flow_params_fw.files,
#         multi_file_params=None,
#         benchling_tag=None,
#         additional_params={},
#     )