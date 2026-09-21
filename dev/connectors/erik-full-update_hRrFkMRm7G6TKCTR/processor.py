from agent_sdk import FileParam, UploadFileParams, activity


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    filename = "test_cutoff.txt"
    body = bytes("Hello, World!", "utf-8")
    activity("TESTING FULL UPDATE")

    new_file_param = FileParam(filename=filename, body=body)
    return UploadFileParams(files=[])













