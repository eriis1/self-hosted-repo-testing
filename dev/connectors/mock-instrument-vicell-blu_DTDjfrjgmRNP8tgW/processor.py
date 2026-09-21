import os
import shutil
import numpy as np
import pandas as pd
from io import BytesIO, StringIO

from agent_sdk import UploadFileParams
from datetime import datetime, timedelta

import agent_sdk

# This agent is configured to act like an instrument
# It will copy a CSV and PDF from # C:\MockInstruments\sample_files and name them with the timestamp
# It does not upload files to the cloud, it's intended to be used with another file watcher agent


def check_if_time_past(file_path, interval_s):
    try:
        # Read the timestamp from the file
        with open(file_path, "r") as file:
            file_timestamp_str = file.read().strip()

        # Convert the file timestamp to a datetime object
        file_timestamp = datetime.fromisoformat(file_timestamp_str)

        # Get the current time
        current_time = datetime.now()

        # Check if the timestamp is more than an hour old
        if current_time - file_timestamp > timedelta(seconds=int(interval_s)):
            agent_sdk.debug("Updated the file with the current timestamp")
            # Update the file with the current timestamp
            with open(file_path, "w") as file:
                current_timestamp_str = current_time.isoformat()
                file.write(current_timestamp_str)
            return True
        else:
            agent_sdk.debug(
                f"Timestamp is less than an {interval_s} seconds old, no update needed."
            )
            return False
    except FileNotFoundError:
        agent_sdk.error("File not found. Creating a new file with the current timestamp.")
        with open(file_path, "w") as file:
            current_timestamp_str = datetime.now().isoformat()
            file.write(current_timestamp_str)
        agent_sdk.error("New file created with the current timestamp.")
        return False
    except ValueError:
        agent_sdk.error("File contains an invalid timestamp format.")
        return False
    except Exception as e:
        agent_sdk.error(f"An error occurred: {e}")
        return False


# Required Function
def execute(**kwargs) -> UploadFileParams:
    vars: dict[str, str] = kwargs.get("vars", {})
    output_interval_s = "3600"
    if vars.get("output_interval_s"):
        output_interval_s = vars["output_interval_s"]
    name_message = ""
    if vars.get("name_message"):
        name_message = vars["name_message"]
    output_path = "C:\\Program Files\\Ganymede\\agents\\test_lab\\ViCell Files\\staging_vicell_blu"
    if vars.get("output_path"):
        output_path = vars["output_path"]
    os.makedirs(output_path, exist_ok=True)

    current_datetime_stamp = datetime.now().strftime("%Y%m%d_%H%M")
    if not check_if_time_past(os.path.join(output_path, "last_update.txt"), output_interval_s):
        return UploadFileParams(files=[])
    base_path = "C:\\Program Files\\Ganymede\\agents\\test_lab\\ViCell Files\\sample_files"
    dest_path = "C:\\Program Files\\Ganymede\\agents\\test_lab\\ViCell Files\\staging_vicell_blu"
    agent_sdk.info(f"Copying {base_path}\\vicell_sample.csv -> {dest_path}\\{current_datetime_stamp}.csv")
    shutil.copyfile(f"{base_path}\\vicell_sample.csv", f"{dest_path}\\{current_datetime_stamp}.csv")
    
    agent_sdk.info(f"Copying {base_path}\\vicell_sample.pdf, {dest_path}\\{current_datetime_stamp}.pdf")
    shutil.copyfile(f"{base_path}\\vicell_sample.pdf", f"{dest_path}\\{current_datetime_stamp}.pdf")
    
    return UploadFileParams(files=[])
