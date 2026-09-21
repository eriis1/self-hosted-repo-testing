import copy
from datetime import datetime, timezone, timedelta
from io import BytesIO

import pandas as pd
import requests
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn
from ganymede_sdk import editor
from ganymede_sdk.util.email import GanymedeEmailAlert


def get_latest_release():
    """
    Lists all releases in the remote-agent GitHub repository.

    Returns:
        dict: The most recent release from the repo
    """
    token = editor.get_secret("github_token")
    url = "https://api.github.com/repos/Ganymede-Bio/remote-agent/releases"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        releases = response.json()
        return releases[0]
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


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
            keys are file names, values are file data to uplo`ad

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/GanymedeClass
    """
    df_sql_result = copy.deepcopy(df_sql_result)
    latest_release = get_latest_release()
    print(f'Retrieved {latest_release["name"]} as the latest release')
    dict_df_out = None

    current_time = datetime.now(timezone.utc)
    release_time = datetime.fromisoformat(latest_release["published_at"].replace("Z", "+00:00"))
    time_difference = current_time - release_time
    error_rows = None
    for index, row in df_sql_result.iterrows():
        if (
            row["core_version"] != latest_release["name"]
            and time_difference > timedelta(hours=1)
            and row["status"] == "Live"
        ):
            if not error_rows:
                error_rows = {
                    "flow_run_id": [],
                    "connection_id": [],
                    "connection_name": [],
                    "step": [],
                    "message": [],
                }
            error_rows["flow_run_id"].append(ganymede_context.flow_run_id)
            error_rows["connection_id"].append(row["connection_id"])
            error_rows["connection_name"].append(row["connection_name"])
            error_rows["step"].append(ganymede_context.task.task_id)
            error_rows["message"].append(
                f"{row['connection_name']} is at {row['core_version']} not the latest release version {latest_release['name']}"
            )

    if error_rows:
        error_result = pd.DataFrame(error_rows)
        dict_df_out = {"Agent_e2e_errors": error_result.copy()}

    return NodeReturn(
        files_to_upload=None,
        tables_to_upload=dict_df_out,
        if_exists="append",
    )