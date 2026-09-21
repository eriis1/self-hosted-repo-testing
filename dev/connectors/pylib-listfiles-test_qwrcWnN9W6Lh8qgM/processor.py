from ganymede_sdk.agent.models import UploadFileParams, FileParam
from datetime import datetime

# from ganymede_sdk.io.input import list_files_all
from google.cloud import storage


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
    check_if_already_exists()
    new_file_param = FileParam(
        filename,
        content_type,
        body,
        "",
        "",
        upload_time,
    )

    return UploadFileParams(files=[new_file_param])


# for files that are older than 1 day don't check if they exist
# need to ensure incomplete files don't get reuploaded all the time
def check_if_already_exists(
    # param: models.FileParam,
    # parent_dir: str,
) -> str:
    BUCKET_NAME = f"ganymede-ganymede-dev-lab-ingest"
    # BUCKET_NAME = f"ganymede-umoja-dev-lab-ingest/luke-test"
    PREFIX = "LC-test-luke/Blob_Read"
    # thing = list_files_all(context=None, flow_name='LC-test-luke')  # type: ignore
    # print('after')
    # print(thing)

    # upload_location = posixpath.join(parent_dir, param.filename)
    # TODO: make prefix specific to flow/input node
    storage_client = storage.Client()  # .from_service_account_json(get_sa_path())
    blobs = storage_client.list_blobs(BUCKET_NAME, prefix=PREFIX)
    already_uploaded_filenames = [str(b.name.split(PREFIX)[1]) for b in blobs]
    print(already_uploaded_filenames)

    # TODO: batch for all files
    # Check for duplicate file in bucket
    # if any(blob.name == upload_location for blob in blobs):
    # default behavior is use existing file, otherwise append timestamp to filename
    # print(
    # f"Returning upload location because it already exists: {upload_location}",
    # )
    # just return the location of the already existing file
    # return upload_location