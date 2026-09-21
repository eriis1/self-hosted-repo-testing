import glob
import os
from typing import Callable, Dict

from ganymede_sdk.agent.models import (
    FileWatcherResult,
    MultiFileParam,
    TriggerFlowParams,
)


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
    modified_time: str = "",
    body: bytes = bytes(),
) -> Dict[str, Callable[[str], bool]]:
    return {
        "CSV_Read.csv": fp(watch_dir, parent_dir, f"*1.csv"),
        "CSV_Read1.csv": fp(watch_dir, parent_dir, f"*2.csv"),
    }


# Required Function
def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TriggerFlowParams:
    m = (
        MultiFileParam.from_file_param(list(flow_params_fw.files.values()))
        if flow_params_fw.files
        else None
    )

    m.param = "CSV_Read_Multi.csv"

    return TriggerFlowParams(
        single_file_params=None,
        multi_file_params={"CSV_Read_Multi.csv": m},
        benchling_tag=None,
        additional_params={},
    )