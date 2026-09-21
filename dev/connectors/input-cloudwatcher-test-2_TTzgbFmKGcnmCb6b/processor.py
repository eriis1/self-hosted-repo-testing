from ganymede_sdk.agent.models import FileParam
from typing import List


def execute(new_file: FileParam, **kwargs) -> None:
    if "new_files" in kwargs:
        for new_file in kwargs["new_files"]:
            write_file(new_file)
    else:
        write_file(new_file)
    return


def write_file(new_file: FileParam) -> None:
    filename = new_file.filename.split("/")[-1]
    fp = open(filename, "wb")
    fp.write(new_file.body)
    return
