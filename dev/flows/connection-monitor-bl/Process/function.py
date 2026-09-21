import api_server_shared
import firebase_admin
import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext, lib
from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn
from ganymede_sdk.util.email import GanymedeEmailAlert
from ganymede_sdk.lib import _is_editor_notebook, _is_airflow
from IPython.display import display, HTML

EMAIL_RECIPIENTS = [
    "benson@ganymede.bio",
]

# list of connection UUIDs of specified as a list
CONNECTION_IDS: bool | list[str] = True
CONNECTION_IDS_TO_EXCLUDE: list[str] = []

try:
    app = firebase_admin.initialize_app()
except ValueError as e:
    print(e)
    pass


def get_last_known_connections(g: Ganymede) -> pd.DataFrame:
    print(f"Retrieving last known connection statuses from the agent_connections table")

    query_connections_sql = """
        WITH most_rec_connection AS (
            SELECT connection_id, MAX(flow_run_id) as flow_run_id
            FROM _agent_conn
            GROUP BY connection_id
        )
        SELECT DISTINCT
            _agent_conn.connection_id, 
            _agent_conn.status, 
            _agent_conn.agent_id, 
            _agent_conn.name,
            _agent_conn.latest_ping_timestamp
        FROM _agent_conn
        INNER JOIN most_rec_connection
        ON _agent_conn.connection_id = most_rec_connection.connection_id 
        AND _agent_conn.flow_run_id = most_rec_connection.flow_run_id
        """

    return g.retrieve_sql(query_connections_sql)


def get_current_connections() -> pd.DataFrame:
    api_requests = api_server_shared.ApiServerSharedRequests(lib.config())
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


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    if not _is_editor_notebook() and not _is_airflow():
        raise GanymedeException(
            "Connections monitoring is only designed to be run in editor notebooks and pipelines"
        )

    g = Ganymede(ganymede_context)

    df_last_known_conn = get_last_known_connections(g)
    df_current_conn = get_current_connections()
    df_current_conn["flow_run_id"] = g["flow_run_id"]

    if df_last_known_conn is None or df_last_known_conn.empty:
        df_status_cmp = df_current_conn.copy()
        df_status_cmp["status_prev"] = "None"

        return NodeReturn(
            tables_to_upload={"_agent_conn": df_current_conn, "_agent_conn_change": df_status_cmp},
        )

    df_status_cmp = df_current_conn.merge(
        df_last_known_conn[["connection_id", "status", "latest_ping_timestamp"]].rename(
            columns={"status": "status_prev", "latest_ping_timestamp": "latest_ping_timestamp_prev"}
        ),
        on="connection_id",
        how="left",
    )
    df_status_cmp["status_prev"] = df_status_cmp["status_prev"].fillna("None")

    df_status_change = df_status_cmp[
        (df_status_cmp["status_prev"].notnull())
        & (df_status_cmp["status_prev"] != df_status_cmp["status"])
    ].copy()

    if isinstance(CONNECTION_IDS, list):
        df_reporting = df_status_change[df_status_change["connection_id"].isin(CONNECTION_IDS)]
    else:
        df_reporting = df_status_change.copy()

    df_reporting = df_reporting[~df_reporting["connection_id"].isin(CONNECTION_IDS_TO_EXCLUDE)]

    if not df_reporting.empty:
        if _is_editor_notebook():
            msg = df_reporting.to_html(index=False, notebook=True)
            display(HTML(msg))
        else:
            msg = df_reporting.to_html(index=False)
            GanymedeEmailAlert(g.ganymede_context).send_email(
                EMAIL_RECIPIENTS,
                f"Ganymede Connection Status Changes for environment {lib.config().env}",
                msg,
            )

    return NodeReturn(
        tables_to_upload={"_agent_conn": df_current_conn, "_agent_conn_change": df_status_change},
        if_exists="append",
    )