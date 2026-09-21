from io import BytesIO
from zipfile import ZipFile

from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn


def execute(input_zip_file: bytes, ganymede_context: GanymedeContext) -> NodeReturn:
    """
    Reads Zip file and stores extracted files in the data lake.

    Parameters
    ----------
    input_zip_file : bytes
        Zip file as a bytes object
    ganymede_context : Optional[GanymedeContext]
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.
    """
    zip_file = ZipFile(BytesIO(input_zip_file))

    file_dict = {}
    for filename in zip_file.namelist():
        if filename.startswith("__MACOSX") or filename == ".DS_Store" or filename.endswith("/"):
            print(f"{filename} excluded from upload")
            continue

        filename_for_ganymede = filename.split("/")[-1] if "/" in filename else filename
        file_dict[filename_for_ganymede] = zip_file.read(filename)

    return NodeReturn(files_to_upload=file_dict)
