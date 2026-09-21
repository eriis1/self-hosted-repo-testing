from ganymede_sdk.agent.models import TriggerFlowParams, FileParam
from datetime import datetime


def execute(**kwargs) ->TriggerFlowParams:
    filename = 'changeme.txt'
    content_type = 'plain/txt'
    body = bytes('Hello, World!', 'utf-8')
    param = 'CSV_READ.csv'
    upload_time = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    fp = FileParam(filename, content_type, body, param, '', upload_time)
    return TriggerFlowParams(single_file_params={param: fp},
        multi_file_params=None, benchling_tag=None, additional_params={})
