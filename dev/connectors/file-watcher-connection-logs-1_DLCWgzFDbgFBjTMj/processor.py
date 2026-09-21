from typing import Callable, Dict

import glob
import os
import re
from urllib import parse

from agent_sdk import (
    FileWatcherResult,
    TagFilesOnlyParams,
    debug,
    info,
    error,
)
from gateway.processor_sdk import get_sdk


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
) -> Dict[str, Callable[[str], bool]]:
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
        "*": fp(watch_dir, parent_dir, f"*"),
    }


# Required Function
def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TagFilesOnlyParams | None:
    """
    Called when all glob patterns specified by get_param_mapping have been matched.

    Parameters
    ----------
    flow_params_fw : FileWatcherResult
        The result of the file watcher, containing the matched files.

    Returns
    -------
    TagFilesOnlyParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """
    # Path 1: module-level imports (legacy style) — should be connection-scoped via
    # ambient contextvars set in event_listener._trigger_pipeline; if logs appear
    # under host instead, a threading context propagation issue may be the cause
    debug("MODULE-LEVEL DEBUG")
    info("MODULE-LEVEL INFO")
    error("MODULE-LEVEL ERROR")

    # Path 2: explicit sdk — always connection-scoped regardless of thread context
    sdk = get_sdk(kwargs)
    sdk.debug("SDK DEBUG")
    sdk.info("SDK INFO")
    sdk.error("SDK ERROR")
    sdk.activity("SDK ACTIVITY")
    sdk.notify("SDK NOTIFY")

    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection

    file_params = list(flow_params_fw.files.values())
    return TagFilesOnlyParams(files=file_params)
