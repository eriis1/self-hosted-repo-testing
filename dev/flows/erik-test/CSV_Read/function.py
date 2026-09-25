from io import BytesIO

import pandas as pd
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn


def execute(csv_file: dict[str, BytesIO], ganymede_context: GanymedeContext) -> NodeReturn:
    """
    Processes CSV file(s) (passed to function as BytesIO file-like objects) into data tables
    stored in data lake

    Parameters
    ----------
    csv_file : dict[str, BytesIO]
        CSV files, indexed by file name
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.
    """

    results_dict = dict()

    if len(csv_file) > 1:
        for filename, file_contents in csv_file.items():
            results_dict[filename] = pd.read_csv(file_contents)
    else:
        return NodeReturn(tables_to_upload={"results": pd.read_csv(list(csv_file.values()).pop())})

    return NodeReturn(tables_to_upload=results_dict)


