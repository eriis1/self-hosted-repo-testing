from ganymede_sdk.agent.models import FileParam, UploadFileParams


# Required Function
def execute(**kwargs) -> UploadFileParams:
    filename = "changeme.txt"
    body = bytes("Hello, World!", "utf-8")

    print("TESTING NOTEBOOK SAVE NEW BUILD")
    print("test")
    print("test1")

    new_file_param = FileParam(filename=filename, body=body)

    return UploadFileParams(files=[new_file_param])