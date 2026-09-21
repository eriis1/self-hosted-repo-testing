import os
import numpy as np
import pandas as pd
from io import BytesIO, StringIO


from agent_sdk import (
    FileParam,
    UploadFileParams,
)

from datetime import datetime, timedelta

rows = 128
columns = 64

# This agent is configured to act like an instrument
# It will generate a CSV file once an hour and write it out to the network drive
# It does not upload files to the cloud, it's intended to be used with another file watcher agent


def check_if_time_past(file_path, interval_s):
    try:
        # Read the timestamp from the file
        with open(file_path, "r") as file:
            file_timestamp_str = file.read().strip()

        # Convert the file timestamp to a datetime object
        file_timestamp = datetime.strptime(file_timestamp_str, "%Y-%m-%d_%H-%M-%S")

        # Get the current time
        current_time = datetime.now()

        # Check if the timestamp is more than an hour old
        if current_time - file_timestamp > timedelta(seconds=int(interval_s)):
            # Update the file with the current timestamp
            with open(file_path, "w") as file:
                current_timestamp_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")
                file.write(current_timestamp_str)
            return True
        else:
            print("Timestamp is less than an hour old, no update needed.")
            return False
    except FileNotFoundError:
        print("File not found. Creating a new file with the current timestamp.")
        with open(file_path, "w") as file:
            current_timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file.write(current_timestamp_str)
        print("New file created with the current timestamp.")
        return False
    except ValueError:
        print("File contains an invalid timestamp format.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
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
    output_path = "C:\\MockInstruments\\simple_csv"
    if vars.get("output_path"):
        output_path = vars["output_path"]
    os.makedirs(output_path, exist_ok=True)
    # Generate the random float values between 0 and 5
    data = np.random.uniform(0, 5, size=(rows, columns))

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    # Use StringIO to convert DataFrame to CSV format in memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    current_datetime_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = os.path.join(output_path, f"simple_csv{name_message}{current_datetime_stamp}.csv")
    if not check_if_time_past("last_update.txt", output_interval_s):
        return UploadFileParams(files=[])
    with open(filename, "w") as file:
        file.write(csv_buffer.getvalue())

    # Return nothing since another agent will handle the uploads
    return UploadFileParams(files=[])