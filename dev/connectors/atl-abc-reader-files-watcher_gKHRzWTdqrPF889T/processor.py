import base64
from pathlib import Path
import os
import time
from agent_sdk import info, error, debug, FileParam, TriggerFlowParams, ObservedFile
import glob
from datetime import datetime

# TODO remove
import agent


print("hello world 05/29")

def file_param_builder(filename: str, param: str, instrument_id: str = None):
    # Determines where to upload the file and how to use it in a flow
    flow_name = "abc-reader-file-validation"
    param_node_name = param.split(".")[0]

    # Creates a file object without requiring encoding and all
    # new_file = ObservedFile(filename)
    splitPath = filename.split("\\")
    filename_noext, fileext = os.path.splitext(splitPath[-1])
    timestamp = datetime.today()
    if instrument_id is None:
        new_file_name = f"{filename_noext}_{timestamp.strftime('%Y%m%d_%H%M')}{fileext}"
    else:
        new_file_name = (
            f"{filename_noext}_{instrument_id}_{timestamp.strftime('%Y%m%d_%H%M')}{fileext}"
        )
    debug(f"new filename for file {filename_noext} is {new_file_name} for param {param_node_name}")

    # Upload to gcs so it can be referenced in a flow
    # gcs_dir = f"{flow_name}/{param_node_name}"
    # upload_time = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    # uploaded_path = agent.StorageClient.save_to_cloud(new_file, gcs_dir)

    # Only the upload path is necessary for this object
    # new_file_param = FileParam(filename=filename, param=param, body="")
    new_file_param = FileParam(filename=filename, param=param, upload_filename=new_file_name, body=b"Hello, World!")
    # It is a bug that these cannot be passed in directly to the constructor
    # new_file_param.upload_ts = upload_time
    # new_file_param.upload_path = uploaded_path

    return new_file_param


# Required Function
def execute(**kwargs) -> TriggerFlowParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    agent_variables = kwargs.get("vars", {})
    if not agent_variables:
        info("Connection requires parent_dir and file_to_watch to be specified.")
        return None

    # # grab watch_dir, filename, recency_min, and recency_max from variables configurable in UI
    watch_dir = agent_variables.get("input_path", None)
    # recency_min = float(agent_variables.get("recency_min", 60))  # 1 min
    # recency_max = float(agent_variables.get("recency_max", 1800))  # 30 min
    instrument_id = agent_variables.get("instrument_id", None)
    
    # system_log_trigger = False
    # run_log_trigger = False
    system_log_dir = os.path.join(watch_dir, "System Logs")
    run_data_dir = os.path.join(watch_dir, "Run Data")

    # system_log_pattern = os.path.join(
    #     system_log_dir, "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].txt"
    # )
    # # Run logs and well logs are inside the run's folder
    # run_log_pattern = os.path.join(run_data_dir, "*", "Run_Logs", "RunLog.txt")
    # well_log_pattern = os.path.join(run_data_dir, "*", "Well_Logs", "*.json")

    # # The active system log is the one whose filename is the most recent date, so it should be last when sorted alphabetically:
    # system_log_list = sorted(glob.glob(system_log_pattern))
    # if not len(system_log_list) > 0:
    #     info("No system logs found")
    #     return None

    # system_log_filepath = system_log_list[-1]
    # last_modified_time = os.stat(system_log_filepath).st_mtime
    # sys_file_elapsed_time_sec = time.time() - last_modified_time
    # # info(f"system log: elapsed time since last modification: {sys_file_elapsed_time_sec}")
    # if sys_file_elapsed_time_sec > recency_min and sys_file_elapsed_time_sec <= recency_max:
    #     file_elapsed_time_m, file_elapsed_time_s = divmod(sys_file_elapsed_time_sec, 60)
    #     debug(
    #         f"Elapsed time since modification for file {system_log_filepath}: {int(file_elapsed_time_m)}:{round(file_elapsed_time_s)}"
    #     )
    #     if not os.access(system_log_filepath, os.R_OK):
    #         error(f"Do not have read permissions for file {system_log_filepath}")
    #         return None
    #     system_log_trigger = True
    #     debug(f"1 valid system log file version found, will be uploading {system_log_filepath}")
    # else:
    #     debug("No new system log file versions, but run logs could have new version")

    # # Now look at run logs:
    # run_log_list = glob.glob(run_log_pattern)
    # info(f"run log list: {run_log_list}")
    # run_log_paths_timestamped_valid = []
    # run_log_paths_timestamped_older = []
    # for run_log_path in run_log_list:
    #     last_modified_time = os.stat(run_log_path).st_mtime
    #     file_elapsed_time_sec = time.time() - last_modified_time
    #     # info(f"last modified at {last_modified_time}")
    #     # info(f"run log: elapsed time since last modification: {file_elapsed_time_sec}")
    #     if file_elapsed_time_sec > recency_min and file_elapsed_time_sec <= recency_max:
    #         file_elapsed_time_m, file_elapsed_time_s = divmod(file_elapsed_time_sec, 60)
    #         debug(
    #             f"Elapsed time since modification for file {run_log_path}: {int(file_elapsed_time_m)}:{round(file_elapsed_time_s)}"
    #         )
    #         if not os.access(run_log_path, os.R_OK):
    #             error(f"Do not have read permissions for file {run_log_path}")
    #             return None
    #         run_log_paths_timestamped_valid.append((run_log_path, file_elapsed_time_sec))
    #     else:
    #         run_log_paths_timestamped_older.append((run_log_path, file_elapsed_time_sec))
    # # info(f"valid timestamped run log list: {run_log_paths_timestamped_valid}")
    # # info(f"older timestamped run log list: {run_log_paths_timestamped_older}")

    # if len(run_log_paths_timestamped_valid) == 0 and len(run_log_paths_timestamped_older) > 0:
    #     debug("No new run log versions found, system log could still be new")
    #     filenames = [fp[0] for fp in run_log_paths_timestamped_older]
    #     run_log_paths_timestamped_older.sort(key=lambda x: x[1])
    #     run_log_filepath = run_log_paths_timestamped_older[0][0]
    # elif len(run_log_paths_timestamped_valid) == 1:
    #     run_log_filepath = run_log_paths_timestamped_valid[0][0]
    #     debug(f"1 valid file version found, will be uploading {run_log_filepath}")
    #     run_log_trigger = True
    # elif len(run_log_paths_timestamped_valid) > 1:
    #     filenames = [fp[0] for fp in run_log_paths_timestamped_valid]
    #     run_log_paths_timestamped_valid.sort(key=lambda x: x[1])
    #     run_log_filepath = run_log_paths_timestamped_valid[0][0]
    #     info(
    #         f"Found multiple valid run log file versions: {filenames}, choosing {run_log_filepath}"
    #     )
    #     run_log_trigger = True
    # else:
    #     info("No run logs found")
    #     return None
    system_log_trigger = True
    system_log_filepath = os.path.join(system_log_dir, "8675309.txt")
    run_log_filepath = os.path.join(run_data_dir, "Run_Logs", "RunLog.txt")
    well_log_filepath = os.path.join(run_data_dir, "Well_Logs", "alpha-123.json")
    if system_log_trigger or run_log_trigger:  # TODO separate out if necessary
        # debug("File trigger valid")
        system_log_file_param = file_param_builder(
            system_log_filepath, "Ingest_System_Log.file_pattern", instrument_id=instrument_id
        )
        # Add instrument_id to ensure unique filenames
        run_log_file_param = file_param_builder(
            run_log_filepath, "Ingest_Run_Log.file_pattern", instrument_id=instrument_id
        )
        # well_log_filepath = os.path.abspath(
        #     glob.glob(
        #         os.path.join(os.path.dirname(run_log_filepath), os.pardir, "Well_Logs", "*.json")
        #     )[0]
        # )
        well_log_file_param = file_param_builder(
            well_log_filepath, "Ingest_Well_Log.file_pattern", instrument_id=instrument_id
        )
        return TriggerFlowParams(
            single_file_params={
                "Ingest_System_Log.file_pattern": system_log_file_param,
                "Ingest_Run_Log.file_pattern": run_log_file_param,
                "Ingest_Well_Log.file_pattern": well_log_file_param,
            },
            multi_file_params=None,
            benchling_tag=None,
            additional_params={},
        )
    else:
        return None



