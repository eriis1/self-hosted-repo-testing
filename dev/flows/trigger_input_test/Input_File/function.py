from typing import Dict
import pandas as pd
from ganymede_sdk.io import NodeReturn
import io  # Importing the necessary module


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
        Object containing data to store in data lake and/or file storage

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/ModuleIO
    """

    csv_file = list(file_data.values()).pop()

    # Using io.BytesIO to create a file-like object from bytes
    csv_file_io = io.BytesIO(csv_file)

    df_excel_file = pd.read_csv(csv_file_io)  # Read from the file-like object

    return NodeReturn(
        tables_to_upload={"trigger_input_test": df_excel_file},
    )
