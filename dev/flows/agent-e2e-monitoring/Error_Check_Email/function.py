import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn
from ganymede_sdk.util.email import GanymedeEmailAlert


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
    errors, notifications = df_sql_result
    if errors is None:
        errors = pd.DataFrame({"flow_run_id": [], "connection_id": [], "step": []})
    if notifications is None:
        notifications = pd.DataFrame({"connection_id": [], "step": []})

    # Check if there are any errors listed for the current run
    errors_this_run = errors[errors["flow_run_id"] == ganymede_context.flow_run_id]
    if len(errors_this_run) > 0:
        # Perform an anti-join to filter rows in `errors` not in `notifications`
        filtered_errors = (
            errors_this_run.merge(
                notifications, on=["connection_id", "step"], how="left", indicator=True
            )
            .query('_merge == "left_only"')
            .drop(columns=["_merge"])
        )

        if len(filtered_errors):
            email_alert = GanymedeEmailAlert(ganymede_context)
            email_alert.send_email(
                "agent-test-lab-users@ganymede.bio",
                "Errors found in Agent monitoring flow",
                f"The following errors were found in the agent test lab monitoring flow {filtered_errors.to_html()}",
            )

    return NodeReturn(
        files_to_upload=None,
        tables_to_upload={
            "Agent_e2e_error_notifications": errors_this_run[
                ["flow_run_id", "step", "connection_id"]
            ]
        },
    )