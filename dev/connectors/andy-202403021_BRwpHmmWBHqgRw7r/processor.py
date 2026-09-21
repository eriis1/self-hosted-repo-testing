from agent_sdk import FileParam, UploadFileParams


# Required Function
def execute(**kwargs) -> UploadFileParams:
    filename = "changeme.csv"
    body = bytes("Hello, World!", "utf-8")

    new_file_param = FileParam(
        filename=filename,
        body=body,
    )

    return UploadFileParams(files=[new_file_param])

