from ganymede_sdk import GanymedeContext, NodeReturn
import pandas as pd
import io


def get_file_contents_from_botos(s3_obj) -> pd.DataFrame:
    """Get file contents of s3 boto object"""
    return s3_obj.get()["Body"].read().decode("utf-8")


def write_boto_to_bytes_io(s3_obj):
    """Download file from S3 from boto object into BytesIO for saving to GCS"""
    s3_obj_io = io.BytesIO()
    s3_obj.download_fileobj(s3_obj_io)
    s3_obj_io.seek(0)
    return s3_obj_io.read()


def execute(
    df_s3_objects: pd.DataFrame, ganymede_context: GanymedeContext = None, **kwargs
) -> pd.DataFrame:
    """
    Parameters
    ----------
    df_s3_objects: pd.DataFrame
        Dataframe containing s3_object key metadata like Key, ETag, LastModified, Size, StorageClass,
        and additional columns such as UploadToGCS (determined by parameters of S3_Read node),
        BotoObjects, and KeyFileContents

    Returns
    -------
    NodeReturn:
        Upload files or tables of the S3 files to GCS. If files_to_upload is empty, resort to
        uploading only the files in df_s3_objects that has UploadToGCS set to true. If
        files_to_upload is not empty, ignore the auto transfer of files and manually upload only
        files in files_to_upload.

    Examples
    --------

    # inspect file contents
    df_s3_objects["FileContents"] = df_s3_objects["BotoObjects"].apply(get_file_contents_from_botos)

    # open files in bytes object to save to Ganymede
    df_s3_objects["FileObjs"] = df_s3_objects["BotoObjects"].apply(write_boto_to_bytes_io)
    files = df_s3_objects.set_index("Key").query("UploadToGCS").to_dict()["FileObjs"]

    return NodeReturn(files_to_upload=files, tags=my_file_tags)
    """

    print(df_s3_objects.to_string())

    # By default, return empty files_to_upload to sync all files
    return NodeReturn()