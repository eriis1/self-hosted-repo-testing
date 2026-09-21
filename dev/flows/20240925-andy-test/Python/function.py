from io import BytesIO

import pandas as pd
import ganymede_api
import requests
from ganymede_sdk.editor import get_secret

from ganymede_sdk import Ganymede, GanymedeContext, lib
from ganymede_sdk.io import NodeReturn


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
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/GanymedeClass
    """
    g = Ganymede(ganymede_context)
    # Attach all the files to the unitoperationrun
    public_api_config = ganymede_api.Configuration(
        host="dev.ganymede.bio",
        api_key={"api-key": get_secret("ganymede_api_key_e2e_flows")},
    )

    # public api information
    lib_config = lib.config()
    public_api_client = ganymede_api.ApiClient(configuration=public_api_config)
    unit_operation_runs_api = ganymede_api.UnitOperationRunsApi(api_client=public_api_client)

    # create unit operation run
    flow_run_id = g.flow_run_id
    unit_operation_run_body = ganymede_api.CreateUnitOperationRunBody(
        unit_operation_id=2, external_id=flow_run_id
    )
    unit_operation_run_body.flow_runs = [
        {
            "runId": flow_run_id,
            "flowId": g.flow_id,
        }
    ]

    unit_operation_run_body.file_uris = [
        "gs://ganymede-ganymede-dev-multi-lab-ingest/CSV_Read_Multi_Test/CSV_Read_Multi/data_2023-06-15_11-13-215.csv",
        "gs://ganymede-ganymede-dev-multi-lab-ingest/CSV_Read_Multi_Test/CSV_Read_Multi/data_2023-06-15_11-13-216.csv",
        "gs://ganymede-ganymede-dev-multi-lab-ingest/CSV_Read_Multi_Test/CSV_Read_Multi/data_2023-06-15_11-13-217.csv",
        "gs://ganymede-ganymede-dev-multi-lab-ingest/CSV_Read_Multi_Test/CSV_Read_Multi/data_2024-02-24_18-34-000.csv",
        "gs://ganymede-ganymede-dev-multi-lab-ingest/CSV_Read_Multi_Test/CSV_Read_Multi/data_2024-02-24_18-34-001.csv",
        "gs://ganymede-ganymede-dev-multi-lab-ingest/CSV_Read_Multi_Test/CSV_Read_Multi/data_2024-02-24_18-35-000.csv",
        "gs://ganymede-ganymede-dev-multi-lab-ingest/CSV_Read_Multi_Test/CSV_Read_Multi/data_2024-02-24_18-36-000.csv",
    ]
    unit_operation_run_body.state = "Completed"
    try:
        unit_operation_runs_api.create_unit_operation_run(
            environment=lib_config.env, create_unit_operation_run_body=unit_operation_run_body
        )

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

    return NodeReturn()