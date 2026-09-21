from io import BytesIO
from typing import List, Union

import numpy as np
import pandas as pd


def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]],
    output_spreadsheet_name: str,
    ganymede_context=None,
) -> BytesIO:
    """
    Graphs table(s) from SQL query and stores graphs in cloud storage.

    Parameters
    ----------
    df_sql_result : Union[pd.DataFrame, List[pd.DataFrame]], optional
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    Dict[str, bytes]
        Plot images to store in cloud storage, indexed by image name
    """
    bio = BytesIO()

    writer = pd.ExcelWriter(bio, engine="xlsxwriter")

    if isinstance(df_sql_result, pd.DataFrame):
        df_sql_result.to_excel(writer, output_spreadsheet_name, index=False)
    else:
        for idx, df in enumerate(df_sql_result):
            df.to_excel(writer, sheet_name=str(idx), index=False)

    writer.close()
    bio.seek(0)

    return bio.read()

