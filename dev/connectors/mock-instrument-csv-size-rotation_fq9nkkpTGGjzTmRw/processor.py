import os
import numpy as np
import pandas as pd
from io import BytesIO, StringIO
import glob

from agent_sdk import UploadFileParams
from datetime import datetime

rows = 128
columns = 64
MAX_SIZE = 50 # MB

# This instrument appends to a CSV file (`csv_size_rotate_DATETIME.csv`) which is populated with rows x columns of random float values between 0 and 5. 
# Once the CSV file reaches 50mb or a custom max_size variable, then a new CSV file is created with an incrementing suffix.
# It does not upload files to the cloud, it's intended to be used with another file watcher agent

def get_latest_file_in_dir(directory):
    list_of_files = glob.glob(f'{directory}/*.csv') # * means all if need specific format then *.csv
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def is_max_size(file_name, max_size):
    file_stats = os.stat(file_name)
    size = file_stats.st_size / (1024 * 1024)
    return size >= max_size

# Required Function
def execute(**kwargs) -> UploadFileParams:
    vars: dict[str, str] = kwargs.get("vars", {})
    max_size = MAX_SIZE

    name_message = "csv_size_rotate_"
    if vars.get("name_message"):
        name_message = vars["name_message"]
    output_path =  "C:\\MockInstruments\\csv_size_rotate"
    if vars.get("output_path"):
        output_path = vars["output_path"]
    os.makedirs(output_path, exist_ok=True)

    if vars.get("max_size"):
        max_size = float(vars["max_size"])

    # Generate the random float values between 0 and 5
    data = np.random.uniform(0, 5, size=(rows, columns))

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    current_datetime_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = os.path.join(output_path, f"{name_message}{current_datetime_stamp}.csv")

    latest_file = get_latest_file_in_dir(output_path)
    if latest_file and not is_max_size(latest_file, max_size=max_size):
        existing_df = pd.read_csv(latest_file)
        existing_df.columns = existing_df.columns.map(int)
        df = pd.concat([df, existing_df])
        filename = latest_file

    # Use StringIO to convert DataFrame to CSV format in memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    with open(filename, "w") as file:
        file.write(csv_buffer.getvalue())

    return UploadFileParams(files=[])
