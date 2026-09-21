from io import BytesIO

import pandas as pd
from ganymede_sdk import GanymedeContext, Ganymede
from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import FlowInputFile, FlowInputParam, Tag, FlowInputs  # noqa: F401
from openapi_client.models.task_param_value import TaskParamValue


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> tuple[str, FlowInputs]:
    """
    Processes data, then triggers downstream Flow.

    FlowInputs holds the inputs for the Flow to trigger.

    There are three types of inputs for Flows:
    - files: Files to be passed to the Flow to trigger
    - params: Input parameters to be passed to the Flow to trigger
    - tags: Flow Tags to be passed to the Flow to trigger

    Parameters
    ----------
    df_sql_result : pd.DataFrame | list[pd.DataFrame]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    tuple[str, FlowInputs]
        Tuple where first element is the ID of the flow to trigger
        and second element is the FlowInputs class containing all inputs for the flow to trigger

    Notes
    -----
    The ID for the triggered flow can be found by navigating to the flow in the Ganymede UI
    and clicking on Manage.  The ID is an immutable string found on the Configuration panel.

    Use ?FlowInputs in the Juppyter notebook to see the class definition for FlowInputs.
    Use ?FlowInputFile in the Jupyter notebook to see the class definition for FlowInputFile.
    """

    g = Ganymede(ganymede_context)

    xml_file = g.retrieve_files_current_run(flow_input_or_output="input")
    xml_file = {k: v for k, v in xml_file.items() if k.lower().endswith(".xml")}

    if len(xml_file) > 1:
        raise GanymedeException(exception_type="Validation", message="Only expecting one XML file")

    filename = list(xml_file.keys())[0]
    file_contents = xml_file[filename]
    bio = BytesIO(file_contents)
    bio.seek(0)

    task_params = [
        TaskParamValue(task="Parse_XML", param="xml", value=filename, data_type="File", multi=False)
    ]

    # populate FlowInputs object based on event_data to return
    f = FlowInputs(task_params=task_params, params=None, tags=None)

    return "austen-trigger-pod-new-4-1", f