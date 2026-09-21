import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext

# from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn
from ganymede_sdk.flow_runtime import GanymedeException


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    """
    Process tabular data from user-defined SQL query, writing results back to data lake.  Data
    is written to the output bucket.

    Parameters
    ----------
    df_sql_result : pd.DataFrame | list[pd.DataFrame]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.  NodeReturn object takes
        2 parameters:
        - tables_to_upload: dict[str, pd.DataFrame]
            keys are table names, values are pandas DataFrames to upload
        - files_to_upload: dict[str, bytes]
            keys are file names, values are file data to upload

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/GanymedeClass
    """
    df_sql_result = copy.deepcopy(df_sql_result)

    # validate task order
    print(df_sql_result)

    # Validate task execution order
    task_executions = {}
    
    # Group executions by task
    for _, row in df_sql_result.iterrows():
        task = row["Task"]
        execution = pd.to_datetime(row["Execution"])
        task_executions[task] = execution

    # Define task order constraints
    constraints = [
        (["1", "1b", "2", "3"], ["4"]),  # Tasks 1,1b,1c,2,3 before 4
        (["3"], ["5"]),    # Task 3 before 5
        (["1", "2"], ["3"]),                        # Tasks 1,2 before 3
        (["1"], ["2"])                              # Task 1 before 2
    ]
    # Check each constraint
    for before_tasks, after_tasks in constraints:
        for before_task in before_tasks:
            for after_task in after_tasks:
                if task_executions[before_task] >= task_executions[after_task]:
                    raise GanymedeException(
                        message=f"Task order violation: Task {before_task} executed at {task_executions[before_task]} should be before Task {after_task} executed at {task_executions[after_task]}",
                        exception_type="Validation"
                    )
    
    print("Task execution order validation passed")


    return NodeReturn(
        files_to_upload=None,
        tables_to_upload=None,
    )
