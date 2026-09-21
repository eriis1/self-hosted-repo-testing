"""
  index, well, filename, sample_desc  
  Format idx:0, matrix:A1, fn: 2018_07_03_1A2_0001.png, descriptor: <below>
    1 wash_well per row
    4 buffers
    1 empty
    sample A sample B random for the rest
"""

import csv
import os
import random
import time
from collections import namedtuple
from datetime import datetime, timezone

import agent.logger as agent_logger
from agent_sdk import UploadFileParams

file_probability = namedtuple("file_probability", ["filename", "probability"])


def create_file_list(file_count: int) -> list[file_probability]:
    curr_iter_files: list[file_probability] = []
    current_date = datetime.now(timezone.utc)
    current_timestamp_string = current_date.strftime("%Y%m%d_%H%M%S")

    for index in range(file_count):
        rand_int = random.randint(0, 5000)
        file = f"{rand_int} {current_timestamp_string}.fcs"
        curr_iter_files.append(file_probability(filename=file, probability=random.random()))

    curr_iter_files.sort(key=lambda x: x.probability)
    agent_logger.debug(f"curr_iter_files: {curr_iter_files}")
    return curr_iter_files


def determine_filename(file_list: list[file_probability]) -> str:
    current_rand = random.random()

    for index in range(len(file_list)):
        if index == len(file_list) - 1:
            continue

        next_row = file_list[index + 1]

        print(f"{index=} w current_rand: {current_rand}, {next_row[1]=} w {next_row.probability}")
        if current_rand < next_row.probability:
            return file_list[index].filename

    print(f"{current_rand=} Last file name: {file_list[-1].filename}. {index=}")
    last_file_name = file_list[-1].filename
    return last_file_name


def number_to_cell(x: int, col_count: int):
    cell_row = x // col_count
    cell_col = x % col_count
    letter = "ABCDEFGH"[cell_row]

    return f"{letter}{cell_col}"


def generate_descriptors(row_count: int, col_count: int, buffer_total: int) -> dict[int, str]:
    descriptor_map = {}
    cell_count = row_count * col_count

    # Add a single 'empty'
    empty = random.randint(0, cell_count)
    descriptor_map[empty] = "empty"

    # Add 'buffer' for a certain number of random cells
    buffer_count = 0
    while buffer_count <= buffer_total:
        new_buffer = random.randint(0, cell_count)
        if new_buffer == empty:
            continue

        descriptor_map[new_buffer] = "buffer"
        buffer_count += 1

    # One 'wash_well' per row
    current_row = 0
    while current_row <= row_count:
        column_to_select = random.randint(0, col_count)
        cell = (current_row * row_count) + column_to_select
        if cell in descriptor_map:
            continue

        descriptor_map[cell] = "wash_well"
        current_row += 1

    return descriptor_map


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    vars: dict[str, str] = kwargs.get("vars", {})

    output_dir = vars.get("output_dir")
    if not output_dir:
        raise TypeError(
            "Cannot write instrument files until the `output_dir` var is specified in the connection config."
        )

    file_count = int(vars.get("file_count", 12))
    row_count = int(vars.get("row_count", 8))
    col_count = int(vars.get("col_count", 12))
    buffer_count = int(vars.get("buffer_count", 4))
    max_time_between_file_writes = int(vars.get("max_time_between_file_writes", 0.1))

    cell_count = row_count * col_count

    file_options = create_file_list(file_count)
    descriptors = generate_descriptors(
        row_count=row_count, col_count=col_count, buffer_total=buffer_count
    )

    group_id = str(int(time.time()))
    dir_name = os.path.join(output_dir, group_id)
    agent_logger.debug(f"dir_name: {dir_name}")

    files_used = []  # Maintain list of files that are added
    well_headers = "index, well, filename, sample_desc\n"
    well_results = well_headers
    for idx in range(cell_count):
        file_name = determine_filename(file_options)
        # file_name = file_options[idx % len(file_options)].filename
        if idx not in descriptors:

            if file_name not in files_used:
                files_used.append(file_name)

            descriptors[idx] = random.choice(["sample A", "sample B"])
        well_results += (
            f"{idx}, {number_to_cell(idx, col_count)}, {file_name}, {descriptors[idx]}\n"
        )

    print("well_results: ", well_results)
    os.makedirs(dir_name, exist_ok=True)
    with open(os.path.join(dir_name, f"{group_id}.csv"), "w") as f:
        f.write(well_results)

    for filename in files_used:
        with open(os.path.join(dir_name, filename), "w") as f:
            f.write(str(random.randbytes(random.randint(0, 256))))
    print("filename: ", filename)
    time.sleep(random.randint(0, max_time_between_file_writes))

    with open(os.path.join(dir_name, f"{group_id}.csv"), "r") as f:
        wells_reader = csv.reader(f)
        for row in wells_reader:
            print("row: ", row)