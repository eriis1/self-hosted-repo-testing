from agent_sdk import FileParam, UploadFileParams


# Required Function
def execute(**kwargs) -> UploadFileParams:
    filename = "changeme.csv"
    body = "Hello, World!"

    new_file_param = FileParam(
        filename=filename,
        body=body,
    )

    return UploadFileParams(files=[new_file_param])
