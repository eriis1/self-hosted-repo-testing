import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext

# from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn


def execute(file_data: dict[str, bytes], ganymede_context: GanymedeContext) -> NodeReturn:
    """
    Processes file data for saving in cloud storage

    Parameters
    ----------
    file_data : dict[str, bytes]
        Bytes object to process, indexed by filename
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/GanymedeClass
    """

    return NodeReturn()