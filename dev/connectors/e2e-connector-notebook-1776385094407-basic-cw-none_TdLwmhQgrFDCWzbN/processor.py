from pathlib import Path


from agent_sdk import FileParam




def write_file(new_file: FileParam, **kwargs) -> None:
    """
    If you pass in 'output_path' as a variable to the agent, this function will save the file to that path.
    This can be specified by inputting `-v "output_path=/path/"` during agent installation, or by setting the
    variable in the connection UI.


    If not specified, the file will be saved to the current working directory of the agent executable.
    """
    if new_file.body is None:
        return  # No data to write


    filename = new_file.filename.split("/")[-1]
    DEFAULT_PATH = "./"
    path = Path(kwargs.get("vars", {}).get("output_path", DEFAULT_PATH))
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



# E2E Test Code - 1776385094407