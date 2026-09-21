import copy

import pandas as pd
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    """
    Process tabular data from user-defined SQL query, writing results back to data lake

    Parameters
    ----------
    df_sql_result : pd.DataFrame | list[pd.DataFrame]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage
    """
    df_sql_result = copy.deepcopy(df_sql_result)

    if isinstance(df_sql_result, pd.DataFrame):
        df_out = df_sql_result.copy()
    else:
        df_out = df_sql_result.pop()

    return NodeReturn(tables_to_upload={"analysis": df_out})
