import pandas as pd
from io import BytesIO
from typing import Union, Dict
import logging
from ganymede_sdk.io import NodeReturn


def execute(
    csv_file: Dict[str, BytesIO], ganymede_context=None
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    This function takes in a dictionary of csv files as input, where keys are filenames and values are contents of CSV files.

    It returns either a dataframe or a dictionary of dataframes, where the keys are the output table names.

    If a dictionary is returned, the value where the key is 'results' is shown with table head.
    """
    logging.info(f"Ganymede context run id: {ganymede_context.run_id}")

    df = pd.read_csv(list(csv_file.values()).pop())
    df["__run_id"] = ganymede_context.flow_run_id
    df["__input_file_name"] = ganymede_context.get_param("Ingest_Data", "csv")
    df["test"] = 5
    # x = 8

    # return NodeReturn(tables_to_upload={"results": df}, wait_for_job=True)
    return NodeReturn(tables_to_upload={"results": df})