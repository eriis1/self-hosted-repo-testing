from ganymede_sdk.agent.models import FileParam, MultiFileParam, TriggerFlowParams


# Required Function
def execute(**kwargs) -> TriggerFlowParams:
    filename = "changeme.txt"
    body = bytes("Hello, World!", "utf-8")
    param = "CSV_READ.csv"  # Match to flow
    param_multi = "CSV_READ_MULTI.csv"

    new_file_param = FileParam(
        filename=filename,
        body=body,
        param=param,
    )

    new_file_multi_param = MultiFileParam(
        files={"file1.txt": body, "file2.txt": body}, param=param_multi
    )

    return TriggerFlowParams(
        single_file_params={new_file_param.param: new_file_param},
        multi_file_params={new_file_multi_param.param: new_file_multi_param},
        benchling_tag=None,
        additional_params=None,
    )
