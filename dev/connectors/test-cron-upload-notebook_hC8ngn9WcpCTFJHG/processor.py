from ganymede_sdk.agent.models import UploadFileParams, FileParam
from datetime import datetime

# helper function to build FileParams to upload files from a directory
def build_file_param(path_to_file: str, parent_path: str, filename: str):
    import os
    import mimetypes
    import utils
    from urllib import parse
    
    (content_type, _) = mimetypes.guess_type(filename)
    if content_type is None:
        content_type = ""

    full_path = os.path.join(path_to_file, filename)
    body = bytes("", "utf-8")
    with open(full_path, "rb") as f:
        body = f.read()

    return FileParam(
        parse.quote(filename),
        content_type,
        body,
        "",
        parent_path,
        utils.get_current_time(),
    )

# Required Function
def execute(**kwargs) -> UploadFileParams:
    filename = "changeme.txt"
    content_type = "plain/txt"
    body = bytes("Hello, World!", "utf-8")
    upload_time = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    new_file_param = FileParam(
        filename,
        content_type,
        body,
        "",
        "",
        upload_time,
    )
    
    return UploadFileParams(
        files=[new_file_param]
    )
