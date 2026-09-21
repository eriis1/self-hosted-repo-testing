import pandas as pd
from typing import Union, Dict, List
from io import BytesIO, StringIO


def execute(
    csv_file: Dict[str, BytesIO], ganymede_context=None
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
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
    from ganymede_sdk.io import list_files_all, list_files_current_run, list_files_current_flow, list_files

    from ganymede_sdk.io import retrieve_sql, retrieve_files

    g = ganymede_context

    # logging.info("LIST TABLES")

    # tbl_all = list_tables_all(g)
    # tbl_current_flow = list_tables_current_flow(g)
    # tbl_current_run = list_tables_current_run(g)

    # logging.info(tbl_all)
    # logging.info(tbl_current_flow)
    # logging.info(tbl_current_run)

    logging.info("LIST_FILES")
    # files_all = list_files_all(g)
    files_current_run = list_files_current_run(g)
    files_current_flow = list_files_current_flow(g)

    # logging.info(files_all)
    logging.info(files_current_flow)
    logging.info(files_current_run)

    # if len(files_all) < 13000:
    #     raise ValueError("files_all is not expected length")

    if len(files_current_run) != 1 or len(files_current_flow) != 3:
        raise ValueError("files_current_run or files_current_flow is not expected length")
    if (
        files_current_run["flow_name"][0] != "e2e-csv-read-and-transform"
        or files_current_flow["flow_name"][0] != "e2e-csv-read-and-transform"
    ):
        raise ValueError("files_current_run or files_current_flow is not expected flow name")

    if not files_current_run["uri"][0].startswith(
        "gs://ganymede-ganymede-dev-multi-lab-ingest"
    ) or not files_current_flow["uri"][0].startswith("gs://ganymede-ganymede-dev-multi-lab-ingest"):
        raise ValueError(
            "files_current_run or files_current_flow does not have expected uri startswith value"
        )

    if files_current_run["file_path"][0] != files_current_flow["file_path"][0]:
        raise ValueError(
            "files_current_run and files_current_flow do not have the same expected file_path"
        )


    # ASSERT get files from another flow is using v2 files query
    FLOW_NAME_MAX_FILES = "e2e-agent-cron-flow"
    maxed_file_list = list_files(g, flow_input_or_output="input",
        flow_name=FLOW_NAME_MAX_FILES,
        current_flow_flag=False)

    logging.info(f"length of optimized endpoint is {maxed_file_list}")
    if len(maxed_file_list) > 5000:
        raise ValueError(
            "Too many files returned by default by list_files of a different flow"
        )

    logging.info("RETRIEVE_FILES")
    full_file_path = files_current_run.loc[
        files_current_run["param_name"] == "CSV_Read", "file_path"
    ].values[0]
    logging.info(full_file_path)
    file_path = full_file_path.split("/")[-1]
    logging.info(file_path)
    fle = retrieve_files(g, file_path, input_or_output_bucket="input")
    logging.info(fle)
    logging.info(fle[full_file_path])
    # Convert bytes to a string
    csv_string = fle[full_file_path].decode("utf-8")

    # Create a file-like object from the string
    csv_file = StringIO(csv_string)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(csv_file)
   

    return df



