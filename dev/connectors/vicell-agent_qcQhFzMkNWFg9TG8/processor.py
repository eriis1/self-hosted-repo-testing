import glob
import os
import re
from typing import Callable, Dict
from urllib import parse

from agent_sdk import FileWatcherResult, TriggerFlowParams, activity, debug, error, info


def fp(watch_dir: str, parent_dir: str, pattern: str) -> Callable[[str], bool]:
    def fp_res(x: str):
        info("x before unquote:")
        info(x)
        x = parse.unquote(x)
        info("x after unquote:")
        info(x)
        info("pattern to be matched:")
        info(pattern)
        # info(x in glob.glob(os.path.join(watch_dir, pattern), recursive=True))
        return x in glob.glob(os.path.join(watch_dir, pattern), recursive=True)

    return fp_res


def get_param_mapping(
    watch_dir: str,
    parent_dir: str = "",
    file_name: str = "",
    modified_time: str = "",
    body: bytes = bytes(),
) -> Dict[str, Callable[[str], bool]]:
    id_group = re.search(r"^(\w+)", parent_dir)
    if id_group == None:
        return {}

    id = id_group.group()
    info(watch_dir)
    info(parent_dir)
    info(id)
    info(file_name)

    sample_name = file_name.rsplit("_", 1)[0]

    return {
        "Read_Single_Measurement_File.csv": fp(
            watch_dir, parent_dir, f"{parent_dir}/{sample_name}*.csv*"
        ),
        #: fp_parent_dir(parent_dir),
        "Read_ViCell_PDF.pdf": fp(watch_dir, parent_dir, f"{parent_dir}/{sample_name}*.pdf*"),
    }


def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TriggerFlowParams:
    info(flow_params_fw)
    file = flow_params_fw.files
    info("Files: ", file)
    parent_dir = file["Read_Single_Measurement_File.csv"].parent_dir
    info(parent_dir)
    return TriggerFlowParams(
        single_file_params=flow_params_fw.files,
        multi_file_params=None,
        benchling_tag=None,
        additional_params={"Input_ViCell_Instrument": parent_dir},
    )

