import pandas as pd
from ganymede_sdk.io import NodeReturn
from typing import Union, Dict, List

def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
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
        Table(s) and File(s) to store in Ganymede.  To write to the table referenced on the node,
        return a DataFrame in the "results" key of the tables_to_upload dictionary.  For more info,
        type '?NodeReturn' into a cell in the editor notebook.
    """

    # remove fields that do not contain well measurements
    df_out = df_sql_result[~df_sql_result['field'].isin(['Cycle Nr.', 'Time [s]', 'Temp. [°C]'])].copy()    
    
    # calculate absorbance difference
    df_out['run_diff'] = df_out['run2'] - df_out['run1']

    return NodeReturn(
        tables_to_upload={'Quickstart_Absorbance_Change_data': df_out},
    )
