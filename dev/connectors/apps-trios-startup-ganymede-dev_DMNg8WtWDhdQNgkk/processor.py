from ganymede_sdk.agent.models import FileParam
from typing import List
import os


def execute(new_file: FileParam, **kwargs) -> None:
    if "new_files" in kwargs:
        for new_file in kwargs["new_files"]:
            write_file(new_file)
    else:
        write_file(new_file)
    return


def write_file(new_file: FileParam) -> None:
    filename = new_file.filename.split("/")[-1]
    save_path = "C:\\Users\\appuser\\Desktop\\Input_files"
    print(f"Saving file {filename} to {save_path}")
    full_path = os.path.join(save_path, filename)
    fp = open(full_path, "wb")
    fp.write(new_file.body)
    return
