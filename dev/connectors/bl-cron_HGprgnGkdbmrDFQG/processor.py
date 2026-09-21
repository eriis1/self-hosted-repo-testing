from agent_sdk import FileParam, TriggerFlowParams, notify, info


# Required Function
def execute(**kwargs) -> TriggerFlowParams | None:
    info(f"kwargs dict: {kwargs}")
    keys = str(kwargs.get("vars", {}).keys())
    vals = str(kwargs.get("vars", {}).values())
    info(f'keys: {keys}')
    info(f'vals: {vals}')
    return None
    # filename = "changeme.txt"
    # body = "Hello, World!"
    # param = "CSV_READ.csv"  # Match to flow

    # notify("test sending daily email from connection")

    # new_file_param = FileParam(filename=filename, body=body, param=param)

    # return TriggerFlowParams(
    #     single_file_params={"CSV_Read.csv": new_file_param, "CSV_Read1.csv": new_file_param},
    #     benchling_tag=None,
    #     additional_params=None,
    # )


