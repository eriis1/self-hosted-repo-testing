import copy
from io import BytesIO

import random
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from ganymede_sdk import GanymedeContext
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
    Documentation on these functions can be found at https://docs.ganymede.bio/api/GanymedeClass
    """

    # Generate a list of 10 timestamps starting from now, each 1 day apart
    timestamps = [datetime.now() for i in range(10)]

    # Convert timestamps to strings and extract month and day
    months = [timestamp.strftime("%B") for timestamp in timestamps]
    days = [timestamp.day for timestamp in timestamps]

    # Generate 7 columns of random values between 0 and 1
    random_values = np.random.rand(10, 10)

    # Create a DataFrame with the generated data
    data = {"Timestamp": timestamps, "Month": months, "Day": days}

    # Add the random value columns to the data dictionary
    for i in range(1, 10):
        data[f"RandomValue{i}"] = random_values[:, i - 1]

    # Create the DataFrame
    output = pd.DataFrame(data)

    dict_df_out = {"test_prod_mode_generated_data": output}

    print(dict_df_out)

    return NodeReturn(
        files_to_upload=None,
        tables_to_upload=dict_df_out,
    )