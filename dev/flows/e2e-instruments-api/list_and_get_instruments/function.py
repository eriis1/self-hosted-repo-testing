import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext, lib, get_secret
import ganymede_api

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
    lib_config = lib.config()
    public_api_config = ganymede_api.Configuration(
        host="dev.ganymede.bio",
        api_key={"api-key": get_secret("ganymede_api_key_e2e_flows")},
    )
    public_api_client = ganymede_api.ApiClient(configuration=public_api_config)
    instruments_api = ganymede_api.InstrumentsApi(public_api_client)
    instruments = instruments_api.get_instruments(environment=lib_config.env)
    assert len(instruments) > 0, "No instruments were returned"

    instrument = instruments_api.get_instrument(environment=lib_config.env, id=instruments[0].id)
    assert instrument.id == instruments[0].id

    return NodeReturn()