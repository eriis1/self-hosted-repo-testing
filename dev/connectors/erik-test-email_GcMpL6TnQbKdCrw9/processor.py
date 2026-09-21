from agent_sdk import FileParam, UploadFileParams, notify


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    # filename = "changeme.txt"
    # body = "Hello, World!"  # Any binary data read or generated

    # new_file_param = FileParam(filename=filename, body=body)

    # notify("test sending email from connection")
    return UploadFileParams(files=[])
