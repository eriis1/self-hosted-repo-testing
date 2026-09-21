import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import lib, Ganymede, GanymedeContext
from ganymede_sdk.util.email import GanymedeEmailAlert
from ganymede_sdk.io import NodeReturn
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter, Or
import pandas as pd
from openapi_client.models.connection_v4 import ConnectionState

app = firebase_admin.initialize_app()

###############
# CONFIG      #
###############
EMAIL_RECIPIENTS = ["eric.song@ganymede.bio"]

MONITOR_ALL_CONNECTIONS = True
CONNECTION_IDS = [
    "e5b15ae4-c01f-4ef9-8d4e-7e2d0572ca32"
]  # If MONITOR_ALL_CONNECTIONS is False, only monitor these connections
###########################################

DATA_LAKE_TABLE_NAME = "agent_connections"
DATA_LAKE_DROPPED_CONNECTIONS_TABLE_NAME = "dropped_agent_connections"


def get_last_known_connections(g: Ganymede) -> pd.DataFrame:
    print(
        f"Retrieving last known connection statuses from Ganymede Data Lake Table: {DATA_LAKE_TABLE_NAME}"
    )
    query_connections_sql = (
        f"SELECT connection_id, status, agent_id, name FROM {DATA_LAKE_TABLE_NAME}"
    )
    return g.retrieve_sql(query_connections_sql)



def get_current_connections() -> pd.DataFrame:
    try:
        import api_server_shared

        api_requests = api_server_shared.ApiServerSharedRequests(lib.config())
        connections = api_requests.get_all_agent_connections()
    except AttributeError:
        import api_server

        api_requests = api_server.ApiServerRequests(lib.config())
        connections = api_requests.get_all_agent_connections()

    return pd.DataFrame(
        [
            {
                "agent_id": conn.agent_id,
                "connection_id": conn.id,
                "status": conn.status.value,
                "latest_ping_timestamp": conn.latest_ping_timestamp,
                "name": conn.name,
            }
            for conn in connections
        ]
    )


def get_dropped_connections(prev_df: pd.DataFrame, new_df: pd.DataFrame):
    merged_df = pd.merge(
        prev_df[["status", "connection_id"]],
        new_df[["status", "connection_id"]],
        on="connection_id",
        how="outer",
        suffixes=("_status", "_new_status"),
    )
    print(merged_df.columns) 
    print("merged_df.columns")
    merged_df.rename(
        columns={"status_status": "status", "status_new_status": "new_status"}, inplace=True
    )

    # Fill missing values
    merged_df["status"] = merged_df["status"].fillna("Unknown")
    merged_df["new_status"] = merged_df["new_status"].fillna("Unknown")

    # Get all rows where the status changed from Live -> anything else
    return merged_df[
        (merged_df["status"] == "Live") & (merged_df["status"] != merged_df["new_status"])
    ]


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    tables_to_upload = {}
    g = Ganymede()

    last_known_connections_df = get_last_known_connections(g)
    current_connections_df = get_current_connections()
    tables_to_upload[DATA_LAKE_TABLE_NAME] = current_connections_df

    # If there's no existing connection data, we don't report on anything so we can
    # exit early
    if last_known_connections_df is None or last_known_connections_df.empty:
        print(tables_to_upload[DATA_LAKE_TABLE_NAME].columns)
        return NodeReturn(
            tables_to_upload=tables_to_upload,
        )
    print(last_known_connections_df.columns)
    print(current_connections_df.columns)
    filtered_df = get_dropped_connections(last_known_connections_df, current_connections_df)
    print(filtered_df.columns)
    print(f"Found {len(filtered_df)} dropped connections that have changed from Live status.")

    if not MONITOR_ALL_CONNECTIONS:
        filtered_df = filtered_df[filtered_df["connection_id"].isin(CONNECTION_IDS)]
        print(
            f"Found {len(filtered_df)} dropped donnections that are being monitored for notifications."
        )

    if not filtered_df.empty:
        # Merge dropped connections with metadata from last_known_connections_df
        with_metadata_df = pd.merge(
            filtered_df,
            last_known_connections_df.drop(columns=["status"]),
            on="connection_id",
            how="left",
        )
        tables_to_upload[DATA_LAKE_DROPPED_CONNECTIONS_TABLE_NAME] = with_metadata_df
        print(with_metadata_df)

        msg = f"Env [{lib.config().env}]<br><br>"
        for i, row in with_metadata_df.iterrows():
            msg += f'Connection {row["agent_id"]}:{row["name"]} changed from {row["status"]} to {row["new_status"]}<br>'

        print(f"Sending email with message: {msg}")
        GanymedeEmailAlert(g.ganymede_context).send_email(
            EMAIL_RECIPIENTS,
            f"Ganymede Agent Connection{'s' if len(filtered_df) > 1 else ''} Lost",
            msg,
        )
    else:
        tables_to_upload[DATA_LAKE_DROPPED_CONNECTIONS_TABLE_NAME] = filtered_df
        
    print(tables_to_upload[DATA_LAKE_DROPPED_CONNECTIONS_TABLE_NAME].columns)
    return NodeReturn(
        tables_to_upload=tables_to_upload,
    )

