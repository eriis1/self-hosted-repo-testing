from agent_sdk import FileParam, TriggerFlowParams
from pathlib import Path
import os
import time
from agent_sdk import info, error
import glob

# Required Function
def execute(**kwargs) -> TriggerFlowParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    agent_variables = kwargs.get('vars', {})
    if not agent_variables:
        info('Connection requires parent_dir and file_to_watch to be specified.')
        return None

    # grab watch_dir, filename, recency_min, and recency_max from variables configurable in UI
    watch_dir = agent_variables.get('parent_dir', None)
    recency_min = float(agent_variables.get('recency_min', 0))
    recency_max = float(agent_variables.get('recency_max', 86400)) # one day

    if not watch_dir:
        print('Connection requires watch_dir to be specified.')
        return None
    list_of_files = glob.glob(f'{watch_dir}/*.csv')

    file_params = []
    for file_path in list_of_files:
        file_elapsed_time = time.time() - os.stat(file_path).st_mtime
        if file_elapsed_time >= recency_min and file_elapsed_time < recency_max:
            if not os.access(file_path, os.R_OK):
                error(f'Do not have read permissions for file {file_path}')
                return None
            with open(file_path, 'rb') as f:
                body = f.read()
                splitPath = file_path.split('\\')
                file_params.append(FileParam(filename=splitPath[-1], body=body, param="CSV_Read.csv"))
    if (len(file_params) > 0):    
        print(type(file_params[0]))
        print(file_params[0])
        return TriggerFlowParams(single_file_params={"CSV_Read.csv":file_params[0]}, multi_file_params=None, benchling_tag=None, additional_params={})

    return None


