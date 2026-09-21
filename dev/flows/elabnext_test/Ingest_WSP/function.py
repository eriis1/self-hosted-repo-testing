def execute(blob_data: bytes, ganymede_context=None) -> bytes:
    """
    Processes blob data for saving in cloud storage

    Parameters
    ----------
    blob_data : bytes
        Bytes object to process
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    bytes
        Bytes object to save in cloud storage
    """

    blob_data_out = blob_data.copy()

    return blob_data_out
