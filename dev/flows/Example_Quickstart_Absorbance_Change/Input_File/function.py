from typing import Dict
from ganymede_sdk.io import NodeReturn
import pandas as pd
from io import BytesIO

from pandera import Column, DataFrameSchema, Check
import re

def execute(file_data: Dict[str, bytes], ganymede_context=None) -> NodeReturn:
    """
    Processes file data for saving in cloud storage

    Parameters
    ----------
    file_data : Dict[str, bytes]
        Bytes object to process, indexed by filename
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Table(s) and File(s) to store in Ganymede.  To write to the table referenced on the node,
        return a DataFrame in the "results" key of the tables_to_upload dictionary.  For more info,
        type '?NodeReturn' into a cell in the editor notebook.
    """

    raise ValueError('abc')
    # Get the first file_data value as an input_df
    input_df = pd.read_excel(list(file_data.values()).pop())

    return NodeReturn(
        tables_to_upload={"plate_reader_results": input_df},
    )






