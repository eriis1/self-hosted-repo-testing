import os
from agent_sdk import FileParam, TriggerFlowParams


def execute(**kwargs) -> TriggerFlowParams | None:
    param = "CSV_Read.csv"  # match your flow node name exactly
    test_file = "/tmp/cron_test.csv"

    if not os.path.exists(test_file):
        with open(test_file, "w") as f:
            f.write("id,value\n1,hello\n")

    params = TriggerFlowParams()
    params.add_file_param(
        param_node_key=param, file=FileParam(filename=test_file, param=param)
    )
    return params
