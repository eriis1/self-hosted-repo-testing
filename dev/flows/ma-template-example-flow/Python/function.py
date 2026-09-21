import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext

# from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn


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
    df_sql_result = copy.deepcopy(df_sql_result)

    # Example of how to use the Ganymede object to retrieve files and tables
    g = Ganymede(ganymede_context)
    # df = g.retrieve_sql("SELECT * FROM list_python_packages_Python_results")
    # file_data = g.retrieve_files_current_run()

    # Example validation check for file name
    # Replace 'file_name' with your actual file name variable in your implementation.
    # This will raise a validation exception instead of a normal flow error, clearly indicating
    # that the user input is the problem, not the code.
    # if not file_name.endswith(".csv"):
    #     raise GanymedeException(
    #         exception_type="Validation", message="File must be a CSV file."
    #     )

    if isinstance(df_sql_result, pd.DataFrame):
        dict_df_out = {"results": df_sql_result.copy()}
        table_out = df_sql_result
    else:
        dict_df_out = {str(k): df for k, df in enumerate(df_sql_result)}
        table_out = df_sql_result[0]

    # Add the current flow run ID to the dataframe to later identify which flow run created
    # these rows
    table_out["flow_run_id"] = g.flow_run_id

    bio = BytesIO()
    table_out.to_csv(bio)
    bio.seek(0)
    files_out = {"demo_file": bio.read()}

    return NodeReturn(
        files_to_upload=files_out,
        tables_to_upload=dict_df_out,
    )
