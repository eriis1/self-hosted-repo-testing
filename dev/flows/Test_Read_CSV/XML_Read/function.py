import pandas as pd
from lxml import etree
from io import BytesIO
from ganymede_sdk.io import NodeReturn


def execute(xml_file: BytesIO, ganymede_context=None) -> pd.DataFrame:
    """
    Parse XML file into table for storage in data lake

    Parameters
    ----------
    xml_file : BytesIO
        Contents of input XML file
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.
    """
    tree = etree.parse(xml_file)
    root = tree.getroot()

    df_out = pd.DataFrame()

    return NodeReturn(tables_to_upload={"results": df_out})