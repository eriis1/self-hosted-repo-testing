import copy
from io import BytesIO

import numpy as np
import pandas as pd
from ganymede_sdk import GanymedeContext
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
    dataframe = pd.DataFrame(
        {
            "The X Column": range(10),
            "The Y Column": [0.2 for _ in range(10)],
            "The Z Column (repeated)": ["a" for _ in range(10)],
            "Bool Column": [True for _ in range(10)],
            "NaN Column": [np.nan for _ in range(10)],
            "None Column": [None for _ in range(10)],
        }
    )
    dict_df_out = {f"e2e_create_table_{ganymede_context.flow_run_id}": dataframe}

    return NodeReturn(
        files_to_upload=None,
        tables_to_upload=dict_df_out,
    )