import glob
import json
import os
import re
from pathlib import Path
from typing import Callable, Dict, List, Union
from urllib import parse

from ganymede_sdk.agent import FileWatcherResult, add_file_tag_to_fileparam
from ganymede_sdk.agent.models import (
    FileParam,
    FileWatcherResult,
    MultiFileParam,
    TriggerFlowParams,
)
from ganymede_sdk.file_tag import get_file_tags

SESSION_JSON_PATH = Path("C:/Program Files/Ganymede/session.json")
BENCHLING_ENTRY_TAG_TYPE_ID = "benchling_entry_id"
ASSAY_RUN_TAG_TYPE_ID = "assay_run_entity"


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
    return {
        "FlowJo_Virtualization_Outputs.file_pattern": fp(watch_dir, parent_dir, f"**/*"),
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

    with open(SESSION_JSON_PATH, "r") as f:
        session_json = f.read()

    session_dict = json.loads(session_json)
    input_files = session_dict["input_files"]

    # Try to tag output files based on the tags of the input files
    # If there are FCS files, use one as the source of tags.
    # Otherwise, don't tag the output files.
    entry_tags = []
    run_tags = []
    fcs_files = [input_file for input_file in input_files if input_file.endswith(".fcs")]
    tag_file = fcs_files[0] if len(fcs_files) else None
    if tag_file:
        tags = get_file_tags(tag_file)
        if tags is not None:
            for tag in tags:
                if tag.tag_type_id == BENCHLING_ENTRY_TAG_TYPE_ID:
                    entry_tags.append(tag)
                if tag.tag_type_id == ASSAY_RUN_TAG_TYPE_ID:
                    run_tags.append(tag)

    logger = kwargs.get("logger", print)
    logger(f"Entry tags: {entry_tags}")
    if len(entry_tags):
        entry_tag = entry_tags[0]
        for param, files in flow_params_fw.files.items():
            if isinstance(files, FileParam):
                add_file_tag_to_fileparam(
                    file_param=files,
                    tag_type_id=BENCHLING_ENTRY_TAG_TYPE_ID,
                    display_value=entry_tag.display_value,
                    url=entry_tag.url,
                )
                single_file_params[param] = files
            else:
                multi_file_params[param] = MultiFileParam.from_file_param(files)
    if len(run_tags):
        run_tag = run_tags[0]
        for param, files in flow_params_fw.files.items():
            if isinstance(files, FileParam):
                logger(f"Adding run tag {run_tag.tag_id} to file param: {files}")
                add_file_tag_to_fileparam(
                    file_param=files,
                    tag_type_id=ASSAY_RUN_TAG_TYPE_ID,
                    display_value=run_tag.display_value,
                    tag_id=run_tag.tag_id,
                    url=run_tag.url,
                )
                single_file_params[param] = files
            else:
                multi_file_params[param] = MultiFileParam.from_file_param(files)

    return TriggerFlowParams(
        single_file_params=flow_params_fw.files,
        multi_file_params=None,
        benchling_tag=None,
        additional_params={},
    )
