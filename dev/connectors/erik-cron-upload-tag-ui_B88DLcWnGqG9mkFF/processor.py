from ganymede_sdk.agent.models import FileParam, UploadFileParams
from ganymede_sdk.agent.tag import add_file_tag


# Required Function
def execute(**kwargs) -> UploadFileParams:
    filename = "changeme.txt"
    body = bytes("Goodnight moon!", "utf-8")

    new_file_param = FileParam(filename=filename, body=body)

    # Add a file tag
    tagged_file_param = add_file_tag(
        file_param=new_file_param, tag_type_id="multi", display_value="From UDC"
    )

    return UploadFileParams(files=[tagged_file_param])
