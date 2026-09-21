from agent_sdk import FileParam, UploadFileParams
import base64
from pathlib import Path
import os
import time
from agent_sdk import info, error, debug, TriggerFlowParams, ObservedFile

from agent_sdk.query import read_sql_query
import glob
from datetime import datetime


def file_param_builder(filename: str):
    # Determines where to upload the file and how to use it in a flow
    flow_name = "hamilton-file-validation"
    param = "Ingest_TRC_File.file_pattern"
    param_node_name = param.split(".")[0]

    # Creates a file object without requiring encoding and all
    # new_file = ObservedFile(filename)
    splitPath = filename.split("\\")
    filename_noext, fileext = os.path.splitext(splitPath[-1])
    timestamp = datetime.today()
    new_file_name = f"{filename_noext}_{timestamp.strftime('%Y%m%d_%H%M')}{fileext}"
    debug(f"new filename for file {filename_noext} is {new_file_name} for param {param_node_name}")

    # Upload to gcs so it can be referenced in a flow
    # gcs_dir = f"{flow_name}/{param_node_name}"
    # upload_time = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    # uploaded_path = agent.StorageClient.save_to_cloud(new_file, gcs_dir)

    # Only the upload path is necessary for this object
    # new_file_param = FileParam(filename=filename, param=param, body="")
    new_file_param = FileParam(
        filename=filename, param=param, upload_filename=new_file_name, tags=[]
    )
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

    info("starting here")
    debug("starting here")

    agent_variables = kwargs.get("vars", {})

    info("got vars? here")
    debug("got vars? here")

    info(f"agent {agent_variables}")
    debug(f"agent {agent_variables}")

    debug(f"kwargs {dir(kwargs)}")

    sdk = kwargs.get("sdk")
    debug(f"sdk {sdk}")

    debug(f"path {sdk.get_var('input_path')}")

    if not agent_variables:
        info("Connection requires parent_dir and file_to_watch to be specified.")
        debug("Connection requires parent_dir and file_to_watch to be specified.")
        return None

    # grab watch_dir, filename, recency_min, and recency_max from variables configurable in UI
    watch_dir = agent_variables.get("input_path", None)
    recency_min = float(agent_variables.get("recency_min", 60))  # 1 min
    recency_max = float(agent_variables.get("recency_max", 1800))  # 30 min

    if not watch_dir:
        print("Connection requires input_path to be specified.")
        info("Connection requires input_path to be specified.")
        debug("Connection requires input_path to be specified.")
        return None

    # Exclude any HxUsbComm files, all other TRCs
    list_of_files_1 = glob.glob(f"{watch_dir}/*.trc")
    list_of_files_2 = glob.glob(f"{watch_dir}/*HxUsb*.trc")
    list_of_files_3 = glob.glob(f"{watch_dir}/ComTrace*.trc")
    list_of_files = [
        f for f in list_of_files_1 if ((f not in list_of_files_2) and (f not in list_of_files_3))
    ]

    file_paths_timestamped = []
    for file_path in list_of_files:
        # debug(f"Checking modified time for file {file_path}")
        last_modified_time = os.stat(file_path).st_mtime
        file_elapsed_time_sec = time.time() - last_modified_time
        # info(f"last modified at {last_modified_time}")
        # info(f"elapsed time since last modification: {file_elapsed_time_sec}")
        if file_elapsed_time_sec > recency_min and file_elapsed_time_sec <= recency_max:
            file_elapsed_time_m, file_elapsed_time_s = divmod(file_elapsed_time_sec, 60)
            debug(
                f"Elapsed time since modification for file {file_path}: {int(file_elapsed_time_m)}:{round(file_elapsed_time_s)}"
            )
            if not os.access(file_path, os.R_OK):
                error(f"Do not have read permissions for file {file_path}")
                return None

            splitPath = file_path.split("\\")
            filename_noext, fileext = os.path.splitext(splitPath[-1])
            already_processed = read_sql_query(
                f"SELECT File_Name FROM Hamilton_File_Validation_Results WHERE File_Name like '{filename_noext}%'"
            )

            debug(f"already_processed {already_processed}")
            if (
                already_processed is not None
                and "File_Name" in already_processed.columns
                and len(already_processed) > 0
            ):
                debug(f"already fully processed file {file_path}, skipping")
                continue

            file_paths_timestamped.append((file_path, file_elapsed_time_sec))

    if len(file_paths_timestamped) == 0:
        info("No new files found")
        # debug("No new file versions found")
        return None
    elif len(file_paths_timestamped) == 1:
        file_path = file_paths_timestamped[0][0]
        debug(f"1 valid file version found, uploading {file_path}")
        file_param = file_param_builder(file_path)

        return UploadFileParams(files=[file_param])

    else:  # More than 1 recently modified TRC file
        filenames = [fp[0] for fp in file_paths_timestamped]
        file_paths_timestamped.sort(key=lambda x: x[1], reverse=True)
        file_path = file_paths_timestamped[0][0]
        info(f"Found multiple valid file versions: {filenames}, uploading {file_path}")
        file_param = file_param_builder(file_path)

        return UploadFileParams(files=[file_param])

    info("No new files found")
    return None
