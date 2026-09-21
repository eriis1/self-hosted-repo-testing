from agent_sdk import FileParam, TriggerFlowParams


# Required Function
def execute(**kwargs) -> TriggerFlowParams:
    print("PROCESSING")
    filename = "changeme.csv"
    body = bytes("Hello, World!", "utf-8")
    param = "CSV_READ.csv"  # Match to flow

    new_file_param = FileParam(
        filename=filename,
        body=body,
        param=param,
    )

    return TriggerFlowParams(
        single_file_params={new_file_param.param: new_file_param},
        multi_file_params=None,
        benchling_tag=None,
        additional_params=None,
    )
