import copy
from io import BytesIO
from datetime import datetime, timezone

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext
import json

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

    # Example of how to use the Ganymede object to retrieve files and tables
    g = Ganymede(ganymede_context)

    # public api information
    api_key = get_secret("ganymede_api_key_e2e_flows")
    host = "dev.ganymede.bio"
    environment = "ganymede-dev-multi"  # todo get this from variables?
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    # get instrument run 
    get_process_run_url = f"https://{host}/v1/environment/{environment}/process-runs/external/{g.flow_run_id}"
    response = requests.get(get_process_run_url, headers=headers)
    data = json.loads(response.text)
    process_run_id = data[0]['id']  
    
    # update instrument run
    process_runs_url = f"https://{host}/v1/environment/{environment}/process-runs/{process_run_id}"
    body = {
        "endTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "state": "Completed",
        "externalId": g.flow_run_id,
    }
    try:
        response = requests.patch(process_runs_url, headers=headers, data=json.dumps(body))
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")

        response.raise_for_status()
        print("Request successful!")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
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
