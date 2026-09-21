from agent_sdk import FileParam, UploadFileParams


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    sdk = kwargs.get("sdk")
    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])   # labels configured for connection

    if sdk:
        connection_tags = sdk.get_connection_tags()
        agent_tags = sdk.get_agent_tags()
        sdk.info(f"Connection tags: {[(t.tag_type_id, t.display_value) for t in connection_tags]}")
        sdk.info(f"Agent tags: {[(t.tag_type_id, t.display_value) for t in agent_tags]}")

    filename = "tag_availability_1.txt"
    body = "Hello, World!"

    new_file_param = FileParam(filename=filename, body=body)

    return UploadFileParams(files=[new_file_param])

