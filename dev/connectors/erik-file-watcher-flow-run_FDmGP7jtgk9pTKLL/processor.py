from agent_sdk import ConnectionSDK, FileEvent, TriggerFlowParams


def execute(new_event: FileEvent, sdk: ConnectionSDK, **kwargs) -> TriggerFlowParams | None:
    """
    Called when all glob patterns specified by get_param_mapping have been matched.
    Returning None will not result in no Flow run triggered, but would still capture files matched by get_param_mapping.

    Parameters
    ----------
    new_event : FileEvent
        Dict of FileParam objects indexed by <node name>.<param name>
    """

    single_file_param_key = "CSV_Read.csv"

    params = TriggerFlowParams()

    params.add_file_param(param_node_key=single_file_param_key, file=new_event.new_file)

    return params
