from agent_sdk import FileParam, UploadFileParams




# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    """
    One-time file upload.


    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """
    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection


    filename = "changeme.csv"
    body = "Hello, World!"


    new_file_param = FileParam(
        filename=filename,
        body=body,
    )


    return UploadFileParams(files=[new_file_param])



# E2E Test Code - 1776300863049