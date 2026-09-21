from ganymede_sdk.agent.models import TriggerFlowParams, FileWatcherResult
import re
from typing import Dict, Callable
import glob
import os


def fp(watch_dir: str, parent_dir: str, pattern: str) -> Callable[[str], bool]:
    def fp_res(x: str):
        return x in glob.glob(os.path.join(watch_dir, pattern), recursive=True)

    return fp_res


# Must return a dictionary where key is the parameter
# and value is the lambda for files that match that parameter
def get_param_mapping(
    watch_dir: str,
    parent_dir: str = "",
    file_name: str = "",
    modified_time: str = "",
    body: bytes = bytes(),
) -> Dict[str, Callable[[str], bool]]:
    id_group = re.search(r"^(\w+)", file_name)
    if id_group == None:
        return {}
    id = id_group.group()
    return {
    }


def execute(flow_params_fw: FileWatcherResult, **kwargs) ->TriggerFlowParams:
    return TriggerFlowParams(single_file_params=flow_params_fw.files,
        multi_file_params=None, benchling_tag=None, additional_params={})
