import pandas as pd
from typing import Union, List
import io


from ganymede_sdk.io import NodeReturn
from ganymede_sdk import Ganymede

from subprocess import check_output
import re


def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None
) -> NodeReturn:
    """
    Populate package version numbers

    Parameters
    ----------
    df_sql_result : Union[pd.DataFrame, List[pd.DataFrame]]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Table(s) and File(s) to store in Ganymede.  To write to the table referenced on the node,
        return a DataFrame in the "results" key of the tables_to_upload dictionary.  For more info,
        type '?NodeReturn' into a cell in the editor notebook.

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/ModuleIO
    """

    g = Ganymede(ganymede_context)

    python_packages = check_output(["pip", "freeze"])

    df = pd.DataFrame({"package_full": python_packages.decode("utf-8").split("\n")})

    df_packages = df["package_full"].str.split(re.compile("==|@"), expand=True)
    df_packages.columns = ["package_name", "version_number"]
    df_packages = df_packages[
        (df_packages["package_name"].str.strip() != "")
        & (df_packages["version_number"])
    ].copy()

    return NodeReturn(tables_to_upload={"results": df_packages})
