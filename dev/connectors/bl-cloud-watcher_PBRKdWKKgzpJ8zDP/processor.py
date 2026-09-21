from ganymede_sdk.agent.models import FileParam
from pathlib import Path


def write_file(new_file: FileParam, kwargs) -> None:
    """
    If you pass in an output_path variable, it will save the file to that path.
    e.g. on agent installation if you provide `-v "output_path=/path/"` the file will be saved there.
    Otherwise, it will save the file to the current working directory.
    """
    filename = new_file.filename.split("/")[-1]
    DEFAULT_PATH = "./"
    path = Path(kwargs.get("vars", []).get("output_path", DEFAULT_PATH))
    full_path = path / filename
    fp = open(full_path, "wb")
    fp.write(new_file.body)
    return


def execute(new_file: FileParam, **kwargs) -> None:
    if "new_files" in kwargs:
        for new_file in kwargs["new_files"]:
            write_file(new_file, kwargs)
    else:
        write_file(new_file, kwargs)
    return

