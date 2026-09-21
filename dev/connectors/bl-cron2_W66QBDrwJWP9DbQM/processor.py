from agent_sdk import UploadFileParams, notify
from datetime import datetime


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    current_time = datetime.today().strftime("%Y-%m-%d %H:%m:%S")
    abc = "abc"
    notify(f"test sending f-string: {abc}")
    notify(f"test sending email from connection: {current_time}")
    return UploadFileParams(files=[])