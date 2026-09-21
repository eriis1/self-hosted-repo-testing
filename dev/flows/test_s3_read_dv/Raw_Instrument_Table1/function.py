import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import GanymedeContext, Ganymede
from ganymede_sdk.io import NodeReturn

S3_METADATA_TABLE = "test_table_s3_dv"
S3_FOLDER = "raw_instrument_tables"
TABLE_NAME = "test_table_1_dv"
MAX_RUN_IDS_TO_UPLOAD = None

MAX_BYTES = 1e6


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    """
    Process tabular data from user-defined SQL query, writing results back to data lake.  Data
    is written to the output bucket.

    Parameters
    ----------
    df_sql_result : pd.DataFrame | list[pd.DataFrame]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.  NodeReturn object takes
        2 parameters:
        - tables_to_upload: dict[str, pd.DataFrame]
            keys are table names, values are pandas DataFrames to upload
        - files_to_upload: dict[str, bytes]
            keys are file names, values are file data to upload

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/api/GanymedeClass
    """
    df_sql_result = None
    g = Ganymede(ganymede_context)

    df_s3 = g.retrieve_tables(S3_METADATA_TABLE)[S3_METADATA_TABLE].query(
        f"Key.str.startswith('{S3_FOLDER}/')"
    )

    print("S3 Keys = ", df_s3["Key"].tolist())

    df_s3["run_id"] = df_s3["Key"].str.extract(
        f"raw_instrument_tables/{TABLE_NAME}/(.*)/.*.parquet"
    )

    raw_table_run_ids = (
        g.retrieve_sql(f"SELECT DISTINCT __run_id FROM {TABLE_NAME}")["__run_id"]
        .astype(str)
        .tolist()
    )
    print(raw_table_run_ids)

    run_ids_not_uploaded = set(raw_table_run_ids).difference(df_s3["run_id"])
    run_ids_not_uploaded = list(run_ids_not_uploaded)[:MAX_RUN_IDS_TO_UPLOAD]

    # run_ids_not_uploaded = df_s3["run_id"].tolist()
    print("run IDs to pull: ", run_ids_not_uploaded)

    files_out = {}

    num_runs_all = len(run_ids_not_uploaded)
    num_runs_pulled = 0
    bytes_pulled = 0

    for run_id in run_ids_not_uploaded:
        bytes_io_df = BytesIO()
        df = g.retrieve_sql(
            f"SELECT * FROM {TABLE_NAME} where CAST(__run_id AS STRING) = '{run_id}'"
        )
        bytes_pulled += df.memory_usage(deep=True).sum()
        df.to_parquet(bytes_io_df)
        bytes_io_df.seek(0)

        files_out.update({f"{TABLE_NAME}/{run_id}/{TABLE_NAME}.parquet": bytes_io_df.read()})

        print(f"\n{run_id}")
        print(
            f"-> Percentage of max bytes pulled {bytes_pulled}/{MAX_BYTES} = {100 * bytes_pulled / MAX_BYTES}%"
        )

        num_runs_pulled += 1
        num_runs_in_queue = num_runs_all - num_runs_pulled
        msg = f"-> Number of runs saved to files out of total: {num_runs_all - num_runs_in_queue} / {num_runs_all} = {100 * (num_runs_all - num_runs_in_queue) / num_runs_all}%"
        print(msg)

        if bytes_pulled > MAX_BYTES:
            print("\n\nReached bytes limit. Exiting loop...")
            break

    return NodeReturn(
        files_to_upload=files_out,
        tables_to_upload={},
    )