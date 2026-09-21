from agent_sdk import FileParam, UploadFileParams, info


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    info("testing processor commit build")
    info("testing processor runtime update HEREEEEEE")

    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection

    filename = "legacy_agent_testing_1.txt"
    body = "Hello, World!"  # Any binary data read or generated

    new_file_param = FileParam(filename=filename, body=body)

    return UploadFileParams(files=[new_file_param])


