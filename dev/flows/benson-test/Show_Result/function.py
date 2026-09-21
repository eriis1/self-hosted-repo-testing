import pandas as pd
from typing import Dict, Union
from io import BytesIO
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn


def execute(csv_file: Dict[str, BytesIO], ganymede_context: GanymedeContext) -> NodeReturn:
    """
    Processes CSV file(s) (passed to function as BytesIO file-like objects) into data tables
    stored in data lake

    Parameters
    ----------
    csv_file : Dict[str, BytesIO]
        CSV files, indexed by file name
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    Union[pd.DataFrame, Dict[str, pd.DataFrame]]
        Table(s) to store in data lake

    Notes
    -----
    If a DataFrame is returned, the table name corresponds to the **results** parameter of the node.

    If a dict is returned, the keys of the dict are used as table names for the corresponding
    DataFrames to store.  The table with **results** as its key is displayed on the Flow Editor.
    """

    import logging
    from ganymede_sdk.io import list_tables_all, list_tables_current_flow, list_tables_current_run
    from ganymede_sdk.io import list_files_all, list_files_current_run, list_files_current_flow

    from ganymede_sdk.io import retrieve_sql, retrieve_files

    g = ganymede_context

    logging.info("ganymede context")
    logging.info(ganymede_context.inputs)

    logging.info("LIST TABLES")

    tbl_all = list_tables_all(g)
    tbl_current_flow = list_tables_current_flow(g)
    tbl_current_run = list_tables_current_run(g)

    logging.info(tbl_all)
    logging.info(tbl_current_flow)
    logging.info(tbl_current_run)

    logging.info("LIST_FILES")
    files_all = list_files_all(g)

    logging.info("LIST_FILES_CURRENT_RUN")
    files_current_run = list_files_current_run(g)

    logging.info("LIST_FILES_CURRENT_FLOW")
    files_current_flow = list_files_current_flow(g)

    logging.info(files_all)
    logging.info(files_current_flow)
    logging.info(files_current_run)

    df = retrieve_sql("select * from example_results limit 5", context=g)
    logging.info(df)
    fle = retrieve_files(g, "sample_test3.csv", input_or_output_bucket="input")
    logging.info(fle)

    return df

