import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext

# from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn
from datetime import datetime


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

    dataframe = pd.DataFrame(
        {
            "Task": [ganymede_context.task.task_id],
            "Execution": [datetime.now().isoformat()],
        }
    )

    dict_df_out = {f"e2e_task_order_{ganymede_context.task.task_id}": dataframe}


    return NodeReturn(
        files_to_upload=None,
        tables_to_upload=dict_df_out,
    )
