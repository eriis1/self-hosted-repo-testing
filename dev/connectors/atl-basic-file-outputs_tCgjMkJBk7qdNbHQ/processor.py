import csv
import os
import random
import time
from collections import namedtuple
from datetime import datetime, timezone

import agent.logger as agent_logger
from agent_sdk import UploadFileParams
import string
import pypdfium2 as pdfium

agent_logger.debug("pypdfium2 version:", pdfium.PYPDFIUM_INFO)

# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    vars: dict[str, str] = kwargs.get("vars", {})

    output_dir = vars.get("output_dir", "")
    agent_logger.debug(f"{vars=}")
    agent_logger.debug(f"{output_dir=}")
    if not output_dir:
        raise RuntimeError(
            "Cannot write instrument files until the `output_dir` var is specified in the connection config."
        )

    row_count = int(vars.get("row_count", 8))
    col_count = int(vars.get("col_count", 12))

    cell_count = row_count * col_count

    group_id = str(int(time.time()))
    dir_name = os.path.join(output_dir, group_id)
    agent_logger.debug(f"dir_name: {dir_name}")

    files_used = []  # Maintain list of files that are added
    well_headers = "index, well, filename\n"
    well_results = well_headers
    for idx in range(cell_count):
        well_results += f"{idx}, {random.randint(100,999)}, {''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}.csv\n"

    agent_logger.debug(f"{well_results=}")
    os.makedirs(dir_name, exist_ok=True)
    with open(os.path.join(dir_name, f"sample_{group_id}.csv"), "w") as f:
        f.write(well_results)

    with open(os.path.join(dir_name, f"dont_run_{group_id}.csv"), "w") as f:
        f.write(well_results)

    with open(os.path.join(dir_name, f"sample_{group_id}.txt"), "w") as f:
        f.write(str(random.randbytes(random.randint(0, 256))))

    return None

