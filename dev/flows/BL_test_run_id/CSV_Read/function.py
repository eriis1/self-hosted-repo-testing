from io import BytesIO

import pandas as pd
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn

from ganymede_sdk.lib import config


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

    df = pd.read_csv(list(csv_file.values()).pop())
    df["__run_id"] = ganymede_context.flow_run_id
    df["__run_id_old"] = ganymede_context.run_id
    x = 9

    return NodeReturn(tables_to_upload={"results": df}, if_exists="append")