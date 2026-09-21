import pandas as pd
from typing import Union, List
from ganymede_sdk.io import NodeReturn
import copy


def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None
) -> NodeReturn:
    """
    Process tabular data from user-defined SQL query, writing results back to data lake

    Parameters
    ----------
    df_sql_result : Union[pd.DataFrame, List[pd.DataFrame]]
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
