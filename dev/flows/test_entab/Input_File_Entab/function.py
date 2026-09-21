import entab
import pandas as pd
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn

valid_parsers = [
    "chemstation_dad",
    "chemstation_fid",
    "chemstation_ms",
    "chemstation_mwd",
    "chemstation_uv",
    "masshunter_dad",
]


def execute(lc_file_path: str, ganymede_context: GanymedeContext) -> NodeReturn:
    """
    Function to convert a datafile object into a dictionary of pandas DataFrame, one for the data
    and another for the metadata.

    Parameters
    ----------
    lc_file_path : str
        Path to LC file to be read
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage
    """

    parser_selected = "chemstation_fid"
    assert parser_selected in valid_parsers, f"Parser {parser_selected} not supported"

    datafile = entab.Reader(filename=lc_file_path, parser=parser_selected)

    # print LC file metadata; parser attribute contains data
    datafile_attr = [attr for attr in dir(datafile) if not attr.startswith("_")]
    for attr in datafile_attr:
        if attr == "parser":
            continue
        print("Attribute: ", attr)
        print(getattr(datafile, attr))

    # print records
    for idx, record in enumerate(datafile):
        print(idx, record)
        if idx == 5:
            break

    return NodeReturn(
        tables_to_upload={"lc_headers_example": pd.DataFrame({"headers": datafile.headers})}
    )