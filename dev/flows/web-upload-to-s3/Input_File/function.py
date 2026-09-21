from ganymede_sdk import GanymedeContext, Ganymede
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

    first_filename_full, first_file = list(file_data.items())[0]
    first_filename = first_filename_full.split("/")[-1]

    g = Ganymede(ganymede_context)

    files = g.list_files_current_run()
    print(files)
    print(files["uri"])
    print(first_file)

    if not files["uri"][0].startswith("s3://"):
        raise ValueError(f"Incorrect s3 uri: {first_filename_full}")

    if not first_file:
        raise ValueError("File is empty")

    return NodeReturn(
        files_to_upload={first_filename: first_file},
    )