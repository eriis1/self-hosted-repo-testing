import pandas as pd
from io import BytesIO
from typing import Union, Dict
from ganymede_sdk.file_tag import add_file_tag


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

    # file_path = ganymede_context.inputs["csv"]
    # print("1")
    # add_file_tag(file_path, "multi", "From Operator", "cqeqou", None)
    # print("2")
    # add_file_tag(file_path, "multi", "From Operator 2", "ajfkd", None)
    # print("3")
    # add_file_tag(file_path, "multi", "Operator 3", "asldjf", None)
    # print("4")
    # add_file_tag(file_path, "multi", "From Operator 4", "jkasdf", None)
    # print("5")
    # add_file_tag(file_path, "plain", "From Op 5", None, None)
    # print("6")
    # add_file_tag(file_path, "has_url", "Op 6", "sdav", "https://ganymede.bio")
    # print("7")
    # add_file_tag(file_path, "test_name_with_spaces", "Op 7", None, "https://dev.ganymede.bio")
    # print("8")
    # add_file_tag(file_path, "test_name_with_spaces", "From Op 8", None, "https://google.com")

    results_dict = dict()

    if len(csv_file) > 1:
        for filename, file_contents in csv_file.items():
            results_dict[filename] = pd.read_csv(file_contents)
    else:
        return pd.read_csv(list(csv_file.values()).pop())

    return results_dict
