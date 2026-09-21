from ganymede_sdk.agent.models import FileParam, MultiFileParam, TriggerFlowParams
from ganymede_sdk.editor import get_secret
import logging
import os
import matplotlib.pyplot as plt
from ganymede_sdk import lib
from ganymede_sdk.editor.secrets import access_secret_version
from io import BytesIO


# Required Function
def execute(**kwargs) -> TriggerFlowParams:

    from google.cloud import storage

    logger = kwargs.get("logger", print)
    logger("starting execute()")

    print("IS AGENT: ", lib._is_agent())
    # # Necessary to authZ with the correct credentials in agent config
    # sa_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "sa.json"))
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path

    logger("accessing secret")
    try:
        storage_client = storage.Client()
        project_id = storage_client.project
        logger("accessing secret")

        env_name = "ganymede-dev"

        secret = access_secret_version(project_id, f"{env_name}-var-example_secret", "latest")

        # secret = get_secret("example_secret")
        logger(f"got secret: {secret}")
    except Exception as e:
        logger("!!!!!! Exception: ", e)
        raise e

    filename = "changeme.csv"
    body = bytes("Hello, World!", "utf-8")
    param = "CSV_Read.csv"
    new_file_param = FileParam(
        filename=filename,
        body=body,
        param=param,
    )
    exported_plots = {}
    test = plt.scatter([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])

    for i in range(0, 10):
        image_data = BytesIO()
        plt.savefig(image_data, format="PNG")
        image_data.seek(0)
        exported_plots[f"test_{i}.png"] = image_data.read()

    multi_param = MultiFileParam(files=exported_plots, param="Image_Read_Multi.image")
    logger("******here*****")

    return None

    return TriggerFlowParams(
        single_file_params={
            "CSV_Read.csv": new_file_param,
            "CSV_Read1.csv": new_file_param,
        },
        multi_file_params={multi_param.param: multi_param},
        benchling_tag=None,
        additional_params=None,
    )