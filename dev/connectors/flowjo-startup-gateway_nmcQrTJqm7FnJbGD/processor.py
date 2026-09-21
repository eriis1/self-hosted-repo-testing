import os

from agent_sdk import FileParam, debug


def write_file(new_file: FileParam) -> None:
    if new_file.body is None:
        return  # No data to write

    filename = new_file.filename.split("/")[-1]
    save_path = "C:\\Users\\appuser\\Desktop\\Input_files"
    debug(f"Saving file {filename} to {save_path}")

    full_path = os.path.join(save_path, filename)
    with open(full_path, "wb") as fp:
        fp.write(new_file.binary)
    return


def execute(file_params: list[FileParam], **kwargs) -> None:
    for file_param in file_params:
        write_file(file_param)
    return
