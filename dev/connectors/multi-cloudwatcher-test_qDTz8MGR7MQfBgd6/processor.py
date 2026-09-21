from ganymede_sdk.agent.models import FileParam


def execute(new_file: FileParam, **kwargs) -> None:
    filename = new_file.filename.split("/")[-1]
    fp = open("test2_" + filename, "wb")
    fp.write(new_file.body)
    return


