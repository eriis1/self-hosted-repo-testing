###
# setup.py
###

import logging
import os
import sys

from ganymede_sdk.editor import ganymede_context_from_env
from ganymede_sdk.io import retrieve_files

logging.info("RUNNING SETUP...")

ganymede_context = ganymede_context_from_env("GANYMEDE_CONTEXT")

os.environ["INPUT_BUCKET"] = ganymede_context.input_bucket
os.environ["OUTPUT_BUCKET"] = ganymede_context.output_bucket
os.environ["GANYMEDE_ENV"] = ganymede_context.ganymede_env

logging.info(f"GANYMEDE_CONTEXT: {ganymede_context}")

for f in sys.argv[1:]:
    f_bytes = list(
        retrieve_files(ganymede_context, f, input_or_output_bucket="output").values()
    ).pop()

    with open(f"/app/input/{f}", "wb") as f:
        f.write(f_bytes)
