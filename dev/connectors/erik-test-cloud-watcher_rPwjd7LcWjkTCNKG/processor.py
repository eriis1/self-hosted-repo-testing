from ganymede_sdk.agent.models import FileParam


def execute(new_file: FileParam, **kwargs) -> None:
    print("test")
    filename = new_file.filename.split("/")[-1]
    fp = open(filename, "wb")
    fp.write(new_file.body)
    return

