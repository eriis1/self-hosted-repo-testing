import pandas as pd
from typing import Union, List


def execute(df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None) -> bytes:
    """
    Process table(s) resulting from user-defined SQL query into CSV file

    Parameters
    ----------
    df_sql_result : Union[pd.DataFrame, List[pd.DataFrame]]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    bytes
        CSV file to store
    """

    if isinstance(df_sql_result, pd.DataFrame):
        bytes_output = bytes(df_sql_result.to_csv(index=False), encoding="utf-8")
    else:
        df_first = df_sql_result[0]
        bytes_output = bytes(df_first.to_csv(index=False), encoding="utf-8")

    return bytes_output

