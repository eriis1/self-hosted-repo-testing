from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn
from pandas import json_normalize

def execute(
    event_data_json: dict, ganymede_context: GanymedeContext
) -> NodeReturn:
    """
    Get raw event from webhook and store in table or file for further processing

    Parameters
    ----------
    event_data_json : dict
        raw event payload from webhook

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.
    """
    df = json_normalize(event_data_json)
    print("test")

    return NodeReturn(tables_to_upload={"events":df})

