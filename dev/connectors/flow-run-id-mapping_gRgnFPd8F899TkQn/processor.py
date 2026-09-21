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

    # filename = "changeme.txt"
    # # body = "Hello, World!" # string or bytes can be passed to FileParam object
    # param = "CSV_READ.csv"  # Match to flow
    # param_multi = "CSV_READ_MULTI.csv"

    # new_file = ObservedFile(file_path=filename)
    # # Alternatively these would also work
    # # new_file = FileParam(filename=filename, body=body, param=param) # pass contents without file on system
    # # new_file = FileParam(filename=filename, param=param) # upload without reading

    # new_multi_file_a = ObservedFile(file_path=filename)
    # new_multi_file_b = ObservedFile(file_path=filename)

    params = TriggerFlowParams()

    # params.add_file_param(param_node_key=param, file=new_file)
    # params.add_file_param(param_node_key=param_multi, files=[new_multi_file_a, new_multi_file_b])

    # params.set_text_param("custom param", "new val")

    return params


