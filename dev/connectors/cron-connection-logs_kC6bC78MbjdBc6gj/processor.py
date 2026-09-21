from agent_sdk import FileParam, UploadFileParams, debug, info, error
from gateway.processor_sdk import get_sdk


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """
    # Path 1: module-level imports — connection-scoped via ambient context
    debug("MODULE-LEVEL DEBUG")
    info("MODULE-LEVEL INFO")
    error("MODULE-LEVEL ERROR")

    # Path 2: explicit sdk — always connection-scoped
    sdk = get_sdk(kwargs)
    sdk.debug("SDK DEBUG")
    sdk.info("SDK INFO")
    sdk.error("SDK ERROR")
    sdk.activity("SDK ACTIVITY")
    sdk.notify("SDK NOTIFY")

    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection

    filename = "changeme.txt"
    body = "Hello, World!"  # Any binary data read or generated

    new_file_param = FileParam(filename=filename, body=body)

    return UploadFileParams(files=[new_file_param])
