from typing import Dict


def execute(blob_data: Dict[str, bytes], ganymede_context=None) -> bytes:
    """
    Processes blob data for saving in cloud storage

    Parameters
    ----------
    blob_data : Dict[str, bytes]
        Bytes object to process, indexed by filename
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    bytes
        Bytes object to save in cloud storage
    """

    return {"output_file_name": blob_data}
