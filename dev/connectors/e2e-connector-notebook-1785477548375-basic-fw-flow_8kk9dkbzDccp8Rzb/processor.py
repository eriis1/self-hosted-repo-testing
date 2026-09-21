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
    # id = id_group.group()  # noqa: F841# E2E Test Code - 1785477548375