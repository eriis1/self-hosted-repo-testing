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


def execute(new_file: FileParam, **kwargs) -> None:
    if "new_files" in kwargs:
        for new_file in kwargs["new_files"]:
            write_file(new_file)
    else:
        write_file(new_file)
    return
