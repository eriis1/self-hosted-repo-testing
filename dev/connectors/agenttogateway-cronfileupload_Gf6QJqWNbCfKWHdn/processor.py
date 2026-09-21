from agent_sdk import FileParam, UploadFileParams
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    filename = f"cron_upload_{get_timestamp()}.txt"
    body = "Hello, World!"  # Any binary data read or generated

    new_file_param = FileParam(filename=filename, body=body)

    return UploadFileParams(files=[new_file_param])


