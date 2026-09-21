from ganymede_sdk.agent.models import FileParam, UploadFileParams
from agent_sdk.query import read_sql_query


# Required Function
def execute(**kwargs) -> UploadFileParams:
    logger = kwargs["logger"]

    benchling_table = read_sql_query("SELECT * FROM `BL_test_CSV_Read_results` LIMIT 25;")
    logger("HEREEEEEEEEEE")
    logger("SQL QUERY TABLE: ")
    logger(benchling_table)

    
    filename = "changeme.txt"
    body = bytes("Hello, World!", "utf-8")

    new_file_param = FileParam(filename=filename, body=body)

    return UploadFileParams(files=[new_file_param])

