from ganymede_sdk import GanymedeContext
import pandas as pd
from ganymede_sdk.flow_runtime import GanymedeException

def execute(
    df_s3_objects: pd.DataFrame,
    client=None,
    ganymede_context: GanymedeContext = None,
) -> dict[str, str]:
    """
    Specify list of S3 keys to upload to GCS

    Parameters
    ----------
    df_s3_objects: pd.DataFrame
        Dataframe containing s3_object key metadata like Key, ETag, LastModified, Size, StorageClass,
        and Bucket
    client: botocore.client.S3
        Boto3 client to interact with S3.  This can be used to retrieve the body of objects from S3.
    ganymede_context: GanymedeContext
        Ganymede context object

    Returns
    -------
    dict[str, str] | NodeReturn
        If dict, files to upload to GCS.  The keys are the keys in S3 and the values
        are the file names to use in Ganymede.

        If NodeReturn, object containing data to store in data lake and/or file storage.
        NodeReturn object takes 2 parameters:

        - tables_to_upload: dict[str, pd.DataFrame]
            keys are table names, values are pandas DataFrames to upload
        - files_to_upload: dict[str, bytes]
            keys are file names, values are file data to upload

    Examples
    --------
    Retrieve body of S3 object of first record in df_s3_objects (assuming boto3 client is passed in as client)

    >>> obj = df_s3_objects.iloc[0].to_dict()
    >>> file_contents = client.get_object(Key=obj["Key"], Bucket=obj["Bucket"])['Body'].read()
    """

    if df_s3_objects.empty or "Key" not in df_s3_objects.columns:
        raise GanymedeException("No S3 Files Found")
        return {}

    return

