from ganymede_sdk import GanymedeContext
import pandas as pd


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
    dict[str, str]
        Dictionary specifying files to upload to GCS.  The keys are the file names to use in
        Ganymede and the values are the S3 keys.

    Examples
    --------
    Retrieve body of S3 object of first record in df_s3_objects (assuming boto3 client is passed in as client)

    >>> obj = df_s3_objects.iloc[0].to_dict()
    >>> file_contents = client.get_object(Key=obj["Key"], Bucket=obj["Bucket"])['Body'].read()
    """

    s3_keys_to_upload = df_s3_objects["Key"].tolist()
    files_to_upload = {k: k.split("/")[-1] for k in s3_keys_to_upload}

    return files_to_upload