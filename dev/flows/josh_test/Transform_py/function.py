import pandas as pd
from typing import Union, Dict, List
import zipfile
import io
from ganymede_sdk import NodeReturn
import ganymede_sdk
from importlib.metadata import version

def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Process tabular data from user-defined SQL query, writing results back to data lake

    Parameters
    ----------
    df_sql_result : Union[pd.DataFrame, List[pd.DataFrame]]
        Table(s) or list of tables retrieved from user-defined SQL query
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

    # if isinstance(df_sql_result, pd.DataFrame):
    #     df_out = df_sql_result.copy()
    # else:
    #     df_out = {str(k): df for k, df in enumerate(df_sql_result)}

    filename = "something"
    # # Create a BytesIO object to hold the zip file data
    # zip_buffer = io.BytesIO()
    # # Create a ZipFile object and write the file_bytes to it
    # with zipfile.ZipFile(zip_buffer, "w") as zip_file:
    #     zip_file.writestr(filename + ".xml", "test string")
    # # Move the buffer's position to the beginning
    # zip_buffer.seek(0)

    # Create an in-memory bytes buffer
    zip_buffer = io.BytesIO()

    # Create a new zip file using the in-memory bytes buffer
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add files to the zip archive, using file name and file content as strings
        zip_file.writestr("file1.txt", "This is the content of file 1")
        zip_file.writestr("file2.txt", "This is the content of file 2")

    # Get the in-memory zip file data
    zip_data = zip_buffer.getvalue()
    print("version: ", version('ganymede_sdk'))

    test_broken_zip_url = "gs://ganymede-ganymede-dev-multi-lab-ingest/_agents/atl_basic_file_outputs/fe6ff254-7f72-4d08-9cc3-87ddf0d6b032/direct from gm Takedown Symphony 2_EXP24002198_IVFCPMG025.zip"
    zip_raw = ganymede_sdk.storage.get_data(test_broken_zip_url)
    print("Type of results: ", type(zip_raw))
    if test_broken_zip_url.startswith("gs://"):
        # get bucket name from uri
        bucket_name = test_broken_zip_url.split("/")[2]
        # get filename from uri
        filename = test_broken_zip_url.split(f"{bucket_name}/")[1]
        print("bucket_name: ", bucket_name)
        print("filename: ", filename)
    zip_raw = ganymede_sdk.storage.get_data(filename)

    return NodeReturn(
        files_to_upload={
            filename + ".zip": zip_data,
            "Symphony_2_EXP24002198_IVFCPMG025.zip": zip_raw,
        }
    )