import copy
from io import BytesIO
from datetime import datetime, timezone

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext, lib
import ganymede_api


# from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn
import requests
from ganymede_sdk.editor import get_secret


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
    df_sql_result = copy.deepcopy(df_sql_result)

    g = Ganymede(ganymede_context)
    # df = g.retrieve_sql("SELECT * FROM list_python_packages_Python_results")
    # file_data = g.retrieve_files_current_run()

    # Get file uri, bq table name, and flow run id for instrument run
    file_data = g.retrieve_files_current_run()
    file_name, file_content = next(iter(file_data.items()), (None, None))
    uri = g.get_gcs_uri("input", file_name)
    flow_run_id = g.flow_run_id

    public_api_config = ganymede_api.Configuration(
        host="dev.ganymede.bio",
        api_key={"api-key": get_secret("ganymede_api_key_e2e_flows")},
    )

    # public api information
    lib_config = lib.config()
    public_api_client = ganymede_api.ApiClient(configuration=public_api_config)
    instrument_runs_api = ganymede_api.InstrumentRunsApi(api_client=public_api_client)

    # create instrument run
    instrument_run_body = ganymede_api.CreateInstrumentRunBody(
        instrument_id=1, external_id=flow_run_id
    )
    instrument_run_body.flow_runs = [
        {
            "runId": flow_run_id,
            "flowId": g.flow_id,
            "unitOperationRunIds": [1],
        }
    ]
    instrument_run_body.file_uris = [uri]
    instrument_run_body.url = "http://example.com/instrument-run"
    instrument_run_body.bq_table_names = ["instrument_run_table"]
    instrument_run_body.start_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    instrument_run_body.initiator = {
        "flowRun": {
            "runId": flow_run_id,
            "flowId": g.flow_id,
        }
    }
    instrument_run_body.state = "Running"
    try:
        response = instrument_runs_api.create_instrument_run(
            environment=lib_config.env, create_instrument_run_body=instrument_run_body
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

    if isinstance(df_sql_result, pd.DataFrame):
        dict_df_out = {"results": df_sql_result.copy()}
        table_out = df_sql_result
    else:
        dict_df_out = {str(k): df for k, df in enumerate(df_sql_result)}
        table_out = df_sql_result[0]

    # Add the current flow run ID to the dataframe to later identify which flow run created
    # these rows
    table_out["flow_run_id"] = g.flow_run_id

    bio = BytesIO()
    table_out.to_csv(bio)
    bio.seek(0)
    files_out = {"demo_file": bio.read()}

    return NodeReturn(
        files_to_upload=files_out,
        tables_to_upload=dict_df_out,
    )


