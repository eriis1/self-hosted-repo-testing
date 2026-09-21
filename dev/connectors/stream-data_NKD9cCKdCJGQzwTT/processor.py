from gateway.pipeline import StreamDataParams


# Required Function
def execute(**kwargs) -> StreamDataParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    variables = kwargs.get("vars", {})  # variables configured for connection
    labels = kwargs.get("labels", [])  # labels configured for connection

    # Your code here to generate or fetch data to stream
    payload = {"column1": "value1", "column2": 123}
    table_id = "your_table_id"  # Replace with your actual table ID

    return StreamDataParams(table_id=table_id, payload=payload)
