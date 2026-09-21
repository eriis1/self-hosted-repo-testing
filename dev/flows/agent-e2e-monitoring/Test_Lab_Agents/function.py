import copy
from io import BytesIO

import api_server
import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext, lib
from ganymede_sdk.io import NodeReturn

CONNECTION_IDS: list[str] = [
    "064be127-65b0-4c38-88db-262c200c0f49",
    "e7e3df4f-aa37-4116-80aa-73805449827f",
]

HAS_FILES: list[bool] = [
    False,
    True,
]

HAS_FLOWS: list[bool] = [
    False,
    True,
]


def get_current_connections() -> pd.DataFrame:
    api_requests = api_server.ApiServerRequests(lib.config())
    connections = api_requests.get_all_agent_connections()
    return pd.DataFrame(
        [
            {
                "agent_id": conn.agent_id,
                "connection_id": conn.id,
                "status": conn.status.value,
                "latest_ping_timestamp": conn.latest_ping_timestamp,
                "connection_name": conn.name,
                "core_version": conn.core_version,
            }
            for conn in connections
        ]
    )


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
    monitored_conns = pd.DataFrame(
        {
            "connection_id": CONNECTION_IDS,
            "has_files": HAS_FILES,
            "has_flows": HAS_FLOWS,
        }
    )
    all_conns = get_current_connections()
    result_df = pd.merge(monitored_conns, all_conns, on="connection_id", how="left")
    dict_df_out = None
    if isinstance(result_df, pd.DataFrame):
        dict_df_out = {"agent_e2e_monitoring_Test_Lab_Connections": result_df.copy()}

    return NodeReturn(
        files_to_upload=None,
        tables_to_upload=dict_df_out,
    )