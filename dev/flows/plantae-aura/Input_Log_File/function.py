import pandas as pd
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn
from ganymede_sdk.file_tag import add_file_tag
import datetime
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def parse_line(line):
    event_dict = {}
    # Extract timestamp
    split_line = line.split(">")
    if len(split_line) < 2:
        # No timestamp
        # print(f"No timestamp in line {line}")
        raise ValueError(f"No timestamp in line {line}")
        event_dict["timestamp"] = None
        offset = 0
    else:
        timestamp_str = split_line[0]
        event_dict["timestamp"] = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        offset = len(timestamp_str) + 1
    return event_dict["timestamp"]


def execute(file_data: dict[str, bytes], ganymede_context: GanymedeContext) -> NodeReturn:
    """
    Processes file data for saving in cloud storage

    Parameters
    ----------
    file_data : dict[str, bytes]
        Bytes object to process, indexed by filename
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/api/GanymedeClass
    """

    first_filename_full, first_file = list(file_data.items())[0]
    first_filename = first_filename_full.split("/")[-1]

    # data_dict = parse_file(first_file, is_filename=False, name=zipname)
    lines = first_file.split(b"\n")
    timestamps = []
    err = False
    for line_idx, line_b in enumerate(lines):
        line = line_b.decode("unicode_escape", errors="replace")
        if not line == "":
            timestamps.append(parse_line(line))
        if "error" in line:
            err = True
    runtime = timestamps[-1] - timestamps[0]
    runtimes_df = pd.DataFrame(
        {"filename": [first_filename], "runtime": [int(runtime.total_seconds())]}
    )

    # return lines
    if err:
        return NodeReturn(
            files_to_upload={first_filename: first_file},
            tags={first_filename: {"tag_type_id": "error_type", "display_value": "pipette"}},
            # tables_to_upload={"Plantae_AURA_Runtimes": runtimes_df},
        )
    else:

        return NodeReturn(
            files_to_upload={first_filename: first_file},
            tables_to_upload={"Plantae_AURA_Runtimes": runtimes_df},
        )