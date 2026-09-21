###
# setup.py - DO NOT MODIFY
###

import logging
import json
import os
import sys

from ganymede_sdk.editor import ganymede_context_from_env
from ganymede_sdk.io import retrieve_files

logging.info("RUNNING SETUP...")

ganymede_context = ganymede_context_from_env("GANYMEDE_CONTEXT")

ganymede_env_dict = {}
ganymede_env_dict["INPUT_BUCKET"] = ganymede_context.input_bucket
ganymede_env_dict["OUTPUT_BUCKET"] = ganymede_context.output_bucket
ganymede_env_dict["GANYMEDE_ENV"] = ganymede_context.ganymede_env

for k, v in ganymede_env_dict.items():
    os.environ[k] = v

with open("__ganymede_env__.json", "w") as ganymede_env_file:
    ganymede_env_file.write(json.dumps(ganymede_env_dict))

logging.info(f"GANYMEDE_CONTEXT: {ganymede_context}")

for f in sys.argv[1:]:
    f_bytes = list(
        retrieve_files(ganymede_context, f, input_or_output_bucket="output").values()
    ).pop()

    with open(f"/app/input/{f}", "wb") as f:
        f.write(f_bytes)

