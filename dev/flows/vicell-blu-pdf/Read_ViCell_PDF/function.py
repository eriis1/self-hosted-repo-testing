import pandas as pd
from io import BytesIO
from typing import Dict
# from ganymede_sdk.api.benchling import Benchling
from ganymede_sdk.io import NodeReturn
from ganymede_sdk.file_tag import add_file_tag


def add_tags(file_data, ganymede_context):

    for filename in file_data.keys():
        add_file_tag(
            input_file_path=filename,
            tag_type_id="data_source_type",
            display_value="Internal Instrument",
            bucket="input",
        )
        add_file_tag(
            filename,
            "data_lifecycle_stage",
            display_value="Instrument Report",
            bucket="input",
        )
        add_file_tag(
            filename, "instrument_type", display_value="Viable Cell Counter", bucket="input"
        )


def execute(
    pdf_file: Dict[str, BytesIO],
    ganymede_context=None,
) -> NodeReturn:
    """
    Processes pdf file(s) (passed to function as BytesIO file-like objects) into blobs and
    data tables stored in the data lake

    Parameters
    ----------
    pdf_file : Dict[str, BytesIO]
        pdf files, indexed by file name
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage
    """
    # b = Benchling(ganymede_context)

    add_tags(pdf_file, ganymede_context)

    return NodeReturn()
