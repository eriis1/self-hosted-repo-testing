from ganymede_sdk.agent.models import TriggerFlowParams, FileParam
from datetime import datetime
from ganymede_sdk.io.input import list_files_all


def execute(**kwargs) -> TriggerFlowParams:
    filename = "changeme.txt"
    content_type = "plain/txt"
    body = bytes("Hello, World!", "utf-8")
    param = "CSV_READ.csv"  # Match to flow
    upload_time = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    check_if_already_exists()
    new_file_param = FileParam(
        filename,
        content_type,
        body,
        param,
        "",
        upload_time,
    )

    return TriggerFlowParams(
        single_file_params={new_file_param.param: new_file_param},
        multi_file_params=None,
        benchling_tag=None,
        additional_params=None,
    )


# for files that are older than 1 day don't check if they exist
# need to ensure incomplete files don't get reuploaded all the time
def check_if_already_exists():
    print("before")
    thing = list_files_all(context=None, flow_name="LC-test-luke")  # type: ignore
    print("after")
    print(thing)