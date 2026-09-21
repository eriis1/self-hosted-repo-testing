from ganymede_sdk import GanymedeContext, Ganymede
from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn
import pandas as pd
import io

S3_METADATA_TABLE = "test_table_s3_dv"
S3_FOLDER = "raw_instrument_tables"


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
        Dictionary specifying files to upload to GCS.  The keys are the keys in S3 and the values
        are the file names to use in Ganymede

    Examples
    --------
    Retrieve body of S3 object of first record in df_s3_objects (assuming boto3 client is passed in as client)

    >>> obj = df_s3_objects.iloc[0].to_dict()
    >>> file_contents = client.get_object(Key=obj["Key"], Bucket=obj["Bucket"])['Body'].read()
    """

    g = Ganymede(ganymede_context)

    s3_file_paths = (
        df_s3_objects.query(f"Key.str.startswith('{S3_FOLDER}/')")["Key"]
        .apply(lambda path: "/".join(path.split("/")[1:]))
        .tolist()
    )

    print("\nS3 file paths", *s3_file_paths[:10], sep="\n")

    df_files = g.list_files(flow_input_or_output="output")
    ganymede_file_paths = (
        df_files["file_path"].apply(lambda path: "/".join(path.split("/")[2:])).tolist()
    )

    print("\nGanymede file paths", *ganymede_file_paths[:10], sep="\n")

    changed_file_paths = set(s3_file_paths).difference(ganymede_file_paths)
    changed_file_paths = "\n".join(list(changed_file_paths))

    if changed_file_paths:
        raise GanymedeException(
            message=f"The following file names in S3 do not match to existing files in Ganymede storage. Please delete them to reset:\n{changed_file_paths}",
            exception_type="Validation",
        )

    df_s3_ganymede = g.retrieve_tables(S3_METADATA_TABLE)[S3_METADATA_TABLE]

    if not df_s3_ganymede.empty:
        df_s3_merged = pd.merge(
            df_s3_objects.query(f"Key.str.contains('^{S3_FOLDER}/.*/.*', regex=True)"),
            df_s3_ganymede,
            how="inner",
            on="Key",
            suffixes=["_in_s3", "_in_ganymede"],
        )
        print(df_s3_merged.filter(regex="LastModified|ETag").to_string())

        keys_changed = df_s3_merged.query("ETag_in_s3 != ETag_in_ganymede")["Key"]
        keys_changed = "\n".join(keys_changed.tolist())

        if keys_changed:
            raise GanymedeException(
                message=f"The following files were changed in S3 since last time the flow ran. Please delete them to reset:\n{keys_changed}",
                exception_type="Validation",
            )

    bytes_io_df = io.BytesIO()
    df_s3_objects.query(f"Key.str.startswith('{S3_FOLDER}/')").to_csv(bytes_io_df)
    bytes_io_df.seek(0)

    return NodeReturn(
        tables_to_upload={S3_METADATA_TABLE: df_s3_objects},
        files_to_upload={"s3_metadata.csv": bytes_io_df.read()},
        wait_for_job=True,
    )