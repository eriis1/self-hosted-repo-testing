from ganymede_sdk.agent.models import FileParam, UploadFileParams
from agent_sdk.query import read_sql_query


# Required Function
def execute(**kwargs) -> UploadFileParams:
    table = read_sql_query("SELECT * FROM `analysis` LIMIT 25;")
    logger = kwargs.get("logger", print)
    logger("TESTING")
    logger(f"HEREEEEE: {table}")
    filename = "changeme.txt"
    body = bytes("Hello, World!", "utf-8")

    new_file_param = FileParam(filename=filename, body=body)

    return UploadFileParams(files=[new_file_param])


