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

    for filename, file_contents in csv_file.items():
        trimmed_filename = filename.split("/")[-1].split(".")[-2]
        if trimmed_filename == "Instrument_State_Timings_OEE":
            df = pd.read_csv(file_contents)
            df["Start_Time"] = pd.to_datetime(df["Start_Time"])
            df["End_Time"] = pd.to_datetime(df["End_Time"])
            results_dict[trimmed_filename] = df
        else:
            results_dict[trimmed_filename] = pd.read_csv(file_contents)

    return NodeReturn(tables_to_upload=results_dict)