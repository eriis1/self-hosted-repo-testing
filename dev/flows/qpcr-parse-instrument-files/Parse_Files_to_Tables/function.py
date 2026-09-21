from io import BytesIO

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext
from ganymede_sdk.io import NodeReturn

SPLIT_INDEX = (
    "Well"  # Anchor text used to locate the start of the data in the instrument reading file
)


def extract_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    data_start = df[df[df.columns[0]] == SPLIT_INDEX].index[0]

    df = df.iloc[data_start:, :].reset_index(drop=True)
    df.columns = df.iloc[0, :]
    df = df[1:]
    df = df[df["Well"].astype(str).str.match(r"^\d+$")].reset_index(drop=True)

    df = _process_raw_data(df)

    return df


def extract_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract metadata from the top of the file
    """
    data_end = df[df[df.columns[0]] == SPLIT_INDEX].index[0]

    df = df.iloc[:data_end, :].reset_index(drop=True).dropna(axis=0, how="all").T
    df.columns = df.iloc[0, :]
    df = df[1:].dropna(axis=0, how="all").reset_index()
    df.rename(columns={"index": df.columns.name}, inplace=True)
    for col in df.columns:
        # Ignore calibration columns and empty columns
        if pd.isnull(col) or col.startswith("Calibration "):
            df.drop(columns=[col], inplace=True)
    return df


def _process_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    df["CT"] = pd.to_numeric(df["CT"], errors="coerce").round(3)
    df["Well Column"] = df["Well Position"].str.extract(r"(\d+)").astype(int)
    df["Well Row"] = df["Well Position"].str.extract(r"(\w)")
    return df


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    """
    Process tabular data from user-defined SQL query, writing results back to data lake.  Data
    is written to the output bucket.

    Parameters
    ----------
    df_sql_result : pd.DataFrame | list[pd.DataFrame]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.  NodeReturn object takes
        2 parameters:
        - tables_to_upload: dict[str, pd.DataFrame]
            keys are table names, values are pandas DataFrames to upload
        - files_to_upload: dict[str, bytes]
            keys are file names, values are file data to upload

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/GanymedeClass
    """

    g = Ganymede(ganymede_context)

    files = g.retrieve_files_current_run()

    reading_file_name, reading_file_bytes = list(files.items())[0]

    # ========== Process Raw Data File ==========
    dfs_raw_data = pd.read_excel(BytesIO(reading_file_bytes), sheet_name=None)  # type: ignore

    df_raw_data_results = extract_raw_data(dfs_raw_data["Results"])

    df_raw_metadata = extract_metadata(dfs_raw_data["Results"])

    df_raw_metadata["filename"] = reading_file_name
    df_raw_data_results["filename"] = reading_file_name

    dfs_out = {
        "qpcr_raw_readings": df_raw_data_results,
        "qpcr_run_metadata": df_raw_metadata,
    }
    for df in dfs_out.values():
        df["__run_id"] = ganymede_context.flow_run_id

    return NodeReturn(
        # todo add protocol stuff
        tables_to_upload=dfs_out,
        if_exists="append",
    )
