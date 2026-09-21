###
# cleanup.py
###
import json
import logging
import os

from ganymede_sdk.editor import ganymede_context_from_env
from ganymede_sdk.storage import upload_data


def cleanup():
    logging.info("RUNNING CLEANUP...")

    ganymede_context = ganymede_context_from_env("GANYMEDE_CONTEXT")

    os.environ["INPUT_BUCKET"] = ganymede_context.input_bucket
    os.environ["OUTPUT_BUCKET"] = ganymede_context.output_bucket
    os.environ["GANYMEDE_ENV"] = ganymede_context.ganymede_env

    # All files passed to return_files will be written to the output bucket
    return_files = []
    for f in os.listdir("/app/output/"):
        upload_data(f"/app/output/{f}", f"{ganymede_context['dag'].dag_id}/{f}")
        upload_data(
            f"/app/output/{f}", f"{ganymede_context['dag'].dag_id}/{ganymede_context.run_id}/{f}"
        )
        return_files.append(f)

    logging.info(f"FILES TO SAVE: {str(return_files)}")
    print(return_files)

    # Filenames written to /airflow/xcom/return.json are captured in metadata
    if not os.path.exists("/airflow/xcom/"):
        os.makedirs("/airflow/xcom/")

    with open("/airflow/xcom/return.json", "w") as f:
        f.write(json.dumps(return_files))


if __name__ == "__main__":
    cleanup()
