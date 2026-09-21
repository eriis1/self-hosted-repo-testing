import numpy as np
import pandas as pd
from typing import Union, List
from ganymede_sdk.io import NodeReturn
from io import BytesIO
import copy


def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None
) -> NodeReturn:
    """
    Process tabular data from user-defined SQL query, writing results back to data lake.  Data
    is written to the output bucket.

    Parameters
    ----------
    df_sql_result : Union[pd.DataFrame, List[pd.DataFrame]]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.  NodeReturn object takes
        2 parameters:
        - tables_to_upload: Dict[str, pd.DataFrame]
            keys are table names, values are pandas DataFrames to upload
        - files_to_upload: Dict[str, bytes]
            keys are file names, values are file data to upload

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/ModuleIO
    """
    df_sql_result = copy.deepcopy(df_sql_result)

    if isinstance(df_sql_result, pd.DataFrame):
        dict_df_out = {"results": df_sql_result.copy()}
        table_out = df_sql_result
    else:
        dict_df_out = {str(k): df for k, df in enumerate(df_sql_result)}
        table_out = df_sql_result[0]

    bio = BytesIO()
    table_out.to_csv(bio)
    bio.seek(0)
    files_out = {"demo_file": bio.read()}

    return NodeReturn(
        files_to_upload=files_out,
        tables_to_upload=dict_df_out,
    )

