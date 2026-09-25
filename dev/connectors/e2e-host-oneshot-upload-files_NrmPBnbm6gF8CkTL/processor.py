# E2E Test Code - 1790311233208
from agent_sdk import FileParam, UploadFileParams
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Required Function
def execute(**kwargs) -> UploadFileParams:
    filename = f"e2e_host_oneshot_upload_{get_timestamp()}.txt"
    body = "Hello, World!"

    new_file_param = FileParam(
        filename=filename,
        body=body,
    )

    return UploadFileParams(files=[new_file_param])
