import glob
import os
import re
from typing import Callable, Dict

from ganymede_sdk.agent.models import FileWatcherResult, NoOpFileTagParams


def fp(watch_dir: str, parent_dir: str, pattern: str) -> Callable[[str], bool]:
    def fp_res(x: str):
        return x in glob.glob(os.path.join(watch_dir, pattern), recursive=True)

    return fp_res


# Required Function
# Must return a dictionary where key is the parameter
# and value is the lambda for files that match that parameter
def get_param_mapping(
    watch_dir: str,
    parent_dir: str = "",
    file_name: str = "",
) -> Dict[str, Callable[[str], bool]]:
    id_group = re.search(r"^(\w+)", file_name)

    if id_group is None:
        return {}
    id = id_group.group()  # noqa: F841

    return {
        "param_1.placeholder": fp(watch_dir, parent_dir, "*"),
    }


# Required Function
def execute(flow_params_fw: FileWatcherResult, **kwargs) -> NoOpFileTagParams:
    file_params = list(flow_params_fw.files.values())
    return NoOpFileTagParams(files=file_params)
