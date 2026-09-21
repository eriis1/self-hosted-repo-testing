import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext
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

    print(
        """
        List files with
        flow_input_or_output="input",
        flow_name=None,
        current_flow_flag=True,
        current_run_id=None,
    """
    )
    df_files = g.list_files(
        flow_input_or_output="input",
        flow_name=None,
        current_flow_flag=True,
        current_run_id=None,
    )
    files = df_files["file_name"].tolist()
    print(files)
    print(g.retrieve_files(files, flow_input_or_output="input"))

    print(
        """
        List files with
        flow_input_or_output="output",
        input_or_output_bucket=None,
        flow_name=None,
        current_flow_flag=True,
        current_run_id=None,
    """
    )
    df_files = g.list_files(
        flow_input_or_output="output",
        flow_name=None,
        current_flow_flag=True,
        current_run_id=None,
    )
    files = df_files["file_name"].tolist()
    print(files)
    print(g.retrieve_files(files, flow_input_or_output="output"))
    print(g.retrieve_files(files, flow_input_or_output="output", run_id=g.flow_run_id))

    print(
        """
        List files with
        flow_input_or_output="input",
        input_or_output_bucket=None,
        flow_name=None,
        current_flow_flag=True,
        current_run_id=g.flow_run_id,
    """
    )
    df_files = g.list_files(
        flow_input_or_output="input",
        flow_name=None,
        current_flow_flag=True,
        current_run_id=g.flow_run_id,
    )
    files = df_files["file_name"].tolist()
    print(files)
    print(g.retrieve_files(files, flow_input_or_output="input"))

    return NodeReturn()