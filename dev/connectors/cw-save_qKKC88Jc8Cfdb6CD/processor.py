from io import BytesIO
from pathlib import Path

import pandas as pd

from agent_sdk import FileParam


def write_file(new_file: FileParam, kwargs) -> None:
    """
    If you pass in an output_path variable, it will save the file to that path.
    e.g. on agent installation if you provide `-v "output_path=/path/"` the file will be saved there.
    Otherwise, it will save the file to the current working directory.
    """
    filename = new_file.filename.split("/")[-1]
    DEFAULT_PATH = "./"
    path = Path(kwargs.get("vars", {}).get("output_path", DEFAULT_PATH))
    full_path = path / filename
    with open(full_path, "wb") as fp:
        fp.write(new_file.binary)

    # with open(full_path, "r") as fp:
    #     results = fp.read()
    #     print("results1: ", results)

    # with open(full_path, "rb") as fp:
    #     results = fp.read()
    #     print("results2: ", results)

    return


def execute(new_file: FileParam, **kwargs) -> None:
    print("RUNNING PROCESSOR 10/24")
    # Retrieve the instrument_to_s3_map table
    # WHEN THE LINE BELOW IS COMMENTED, THE AGENT WORKS NORMALLY
    # g = Ganymede(flow_run_id='1721921804950')
    # df_mapping = g.retrieve_sql("SELECT * FROM instrument_to_s3_map")

    if "new_files" in kwargs:
        for new_file in kwargs["new_files"]:
            write_file(new_file, kwargs)
    else:
        write_file(new_file, kwargs)
    return


"""
Expected data format
Well,Content,Raw Data (470 1),Raw Data (600 2)
A01,Blank B,0.036,0.039
A02,Control C1,0.051,0.039
A03,Sample X1,0.158,0.042
"""

"""
def trigger_new_instrument_cycle(fn: str, body: bytes):
    fp = open(fn, "wb")
    fp.write(body)
    print(
        "wrote to file, now calling imaginary instrument api over RS422 Serial Com to continue data experiments because previous was succesful. No intervention necessary."
    )
    return


def execute(new_file: FileParam, **kwargs) -> None:
    logger = kwargs["logger"]
    logger("test")
    logger("TEST FROM PROCESSOR")

    print("new_file.filename: ", new_file.filename)
    split = new_file.filename.split("/")
    filename = split[-1]
    df = pd.read_csv(BytesIO(new_file.body))
    print("df: ", df)
    # stddev = df['Raw_Data_600_2_'].std()
    # if stddev < 0.01:
    # trigger_new_instrument_cycle(filename, new_file.body)
    trigger_new_instrument_cycle(filename, new_file.body)
"""

