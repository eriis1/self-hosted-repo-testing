import pandas as pd
from typing import Union, Dict, List, Optional


def execute(
    data: Dict[str, bytes],
    df_sql_result: Optional[Union[pd.DataFrame, List[pd.DataFrame]]],
    ganymede_context=None,
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Processes bytes data file(s) into output data table for storage in data lake

    Parameters
    ----------
    data : Dict[str, bytes]
        Bytes data to process, indexed by object name
    df_sql_result : Optional[Union[pd.DataFrame, List[pd.DataFrame]]]
        Tabular result(s) of user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    Union[pd.DataFrame, Dict[str, pd.DataFrame]]
        Table(s) to store in data lake.

    Notes
    -----
    If a DataFrame is returned, the table name corresponds to the **results** parameter of the node.

    If a dict is returned, the keys of the dict are used as table names for the corresponding
    DataFrames to store.  The table with **results** as its key is displayed on the Flow Editor.
    """

    if isinstance(df_sql_result, pd.DataFrame):
        df_out = df_sql_result
    elif isinstance(df_sql_result, list):
        [df_out] = df_sql_result
    else:
        df_out = pd.DataFrame()

    return df_out
