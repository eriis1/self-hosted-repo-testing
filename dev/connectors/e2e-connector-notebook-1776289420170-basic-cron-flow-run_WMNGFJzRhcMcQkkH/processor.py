from agent_sdk import ObservedFile, TriggerFlowParams




# Required Function
def execute(**kwargs) -> TriggerFlowParams | None:
    """
    Function to execute on specified cadence


    Returns
    -------
    TriggerFlowParams | None
        Parameters to use in triggered Flow.  If None is specified, then Flow will not be triggered.
    """


    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection


    filename = "changeme.txt"
    # body = "Hello, World!" # string or bytes can be passed to FileParam object


    param = "CSV_Read.csv"  # Match to flow; note that this is case-sensitive
    param_multi = "CSV_Read_Multi.csv"


    new_file = ObservedFile(file_path=filename)


    # Alternatively these would also work
    # new_file = FileParam(filename=filename, body=body, param=param) # pass contents without file on system
    # new_file = FileParam(filename=filename, param=param) # upload without reading


    new_multi_file_a = ObservedFile(file_path=filename)
    new_multi_file_b = ObservedFile(file_path=filename)


    params = TriggerFlowParams()


    params.add_file_param(param_node_key=param, file=new_file)
    params.add_file_param(param_node_key=param_multi, files=[new_multi_file_a, new_multi_file_b])


    params.set_text_param("Input_Param", "new val")


    return params



# E2E Test Code - 1776289420170