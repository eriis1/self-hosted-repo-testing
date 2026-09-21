###
# setup.py
###

import logging
from ganymede_sdk.editor.context import ganymede_context_from_env
from ganymede_sdk.io import retrieve_files

ganymede_context = ganymede_context_from_env("GANYMEDE_CONTEXT")
logging.info(f"GANYMEDE_CONTEXT: {ganymede_context}")

reference_genome_bytes = (
    retrieve_files(ganymede_context, "reference_genome.fa", input_or_output_bucket="input")
    .values()
    .pop()
)

with open("/input/reference_genome.fa", "wb") as f:
    f.write(reference_genome_bytes)




