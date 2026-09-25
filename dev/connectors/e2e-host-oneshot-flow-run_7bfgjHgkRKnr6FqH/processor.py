# E2E Test Code - 1790311233208
from agent_sdk import FileParam, TriggerFlowParams
from datetime import datetime
import tempfile
import os

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Required Function
def execute(**kwargs) -> TriggerFlowParams | None:
    """
    One-time execution of a Flow with file upload.

    Returns
    -------
    TriggerFlowParams | None
        Files and parameters to trigger Flow with; if set to None, then no files will be uploaded.
    """
    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection

    # Create CSV content directly
    file_content = "id,name,value\n1,test,100\n2,sample,200\n"
    
    # Create a physical temporary file
    temp_dir = tempfile.gettempdir()
    filename = f"e2e_host_oneshot_flow_run_{get_timestamp()}.csv"
    file_path = os.path.join(temp_dir, filename)
    
    # Write content to the temporary file
    with open(file_path, 'w') as f:
        f.write(file_content)
    
    # Create a TriggerFlowParams object
    params = TriggerFlowParams()
    param_key = "CSV_Read.csv"  # Match to flow; note that this is case-sensitive
    
    # Add file to TriggerFlowParams using the physical file path
    params.add_file_param(
        param_node_key=param_key,
        file=FileParam(filename=file_path, param=param_key)
    )
    
    return params
