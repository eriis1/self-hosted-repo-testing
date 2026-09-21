from pathlib import Path

from agent_sdk import FileParam, error


def write_file(new_file: FileParam, **kwargs) -> None:
    """
    Saves the file to the path specified by the 'output_path' variable.
    This can be specified by inputting `-v "output_path=/path/"` during agent installation, or by setting the
    variable in the connection UI.
    """
    if new_file.body is None:
        return  # No data to write

    output_path = kwargs.get("vars", {}).get("output_path")
    error(f"Output path: {output_path}")
    if not output_path:
        error(
            "`output_path` is not specified. Please set `output_path`=`/path/to/output` in the connection variables."
        )
        return

    filename = new_file.filename.split("/")[-1]
    path = Path(output_path)
    full_path = path / filename

    with open(full_path, "wb") as fp:
        fp.write(new_file.binary)


def execute(new_file: FileParam, **kwargs) -> None:
    """
    This function will be called when a new file is detected for the flow that this agent is associated with.

    Parameters
    ----------
    new_file : FileParam
        The new file detected in the bucket as a FileParam object.
    **kwargs
        Additional keyword arguments.
    """
    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection

    if "new_files" in kwargs:
        for new_file in kwargs["new_files"]:
            write_file(new_file, **kwargs)
    else:
        write_file(new_file, **kwargs)
