from ganymede_sdk.agent.models import TriggerFlowParams, FileParam
import traceback
from datetime import datetime
import os
from pathlib import Path
from typing import Optional

WATCH_DIRECTORY = Path("./input")
UPLOADED_FILES = "./uploaded_files.txt"


def execute(**kwargs) -> Optional[TriggerFlowParams]:
    try: 
        content_type = "plain/txt"
        param = "Input_FCS.file_pattern"  # Match to flow
        upload_time = datetime.utcnow().isoformat(timespec="seconds") + "Z"

        if not os.path.exists(WATCH_DIRECTORY):
            os.makedirs(WATCH_DIRECTORY)

        files = os.listdir(WATCH_DIRECTORY)
        bodies = [open(os.path.join(WATCH_DIRECTORY, f), "rb").read() for f in files]

        if not os.path.exists(UPLOADED_FILES):
            open(UPLOADED_FILES, "w").close()
        already_uploaded_files = open(UPLOADED_FILES, "r").read().splitlines()

        if len(files) > 0:
            file = files[0]
            if file not in already_uploaded_files:
                open(UPLOADED_FILES, "a").write(file + "\n")
                new_file_param = FileParam(
                    filename=files[0],
                    content_type=content_type,
                    body=bodies[0],
                    param=param,
                    parent_dir="",
                    upload_ts=upload_time,
                )

                return TriggerFlowParams(
                    single_file_params={new_file_param.param: new_file_param},
                    multi_file_params=None,
                    benchling_tag=None,
                    additional_params=None,
                )
        return None
    except Exception as e:
        vars = []
        for frame in traceback.extract_tb(e.__traceback__):
            a = frame.locals
            vars.append(a)
        raise type(e)(f"An error occurred: {e}. \n {vars}").with_traceback(e.__traceback__)


