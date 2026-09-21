import pandas as pd
from typing import Union, List
from ganymede_sdk.io import NodeReturn
from io import BytesIO
import requests

# Uncomment to use Pandera validation
#
# from pandera import Column, DataFrameSchema, Check
# import re
#
# schema = DataFrameSchema(
#     {
#         "well_position": Column(str,
#                         Check.str_matches(r'\w\d\d?'),
#                         required=True,
#                         nullable=False
#                        ),
#         "run1": Column(float, required=True, nullable=False),
#         "run2": Column(float, required=True, nullable=False)
#     }
# )
#
# To validate a dataframe called df_to_validate, run:
#
# schema.validate(df_to_validate)


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
        Table(s) and File(s) to store in Ganymede.  To write to the table referenced on the node,
        return a DataFrame in the "results" key of the tables_to_upload dictionary.  For more info,
        type '?NodeReturn' into a cell in the editor notebook.
    """

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
    ip_addr = 'http://10.32.0.6:80'
    print(f'Attempting connection to {ip_addr}')
    resp = requests.get(ip_addr)
    print(resp)
    print(resp.text)

    return NodeReturn(
        files_to_upload={},
        tables_to_upload={},
    )


