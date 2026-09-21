from gateway.pipeline import StreamTagReadingParams


def execute(params: StreamTagReadingParams, **kwargs) -> StreamTagReadingParams | None:
    """Process an OPC-UA tag reading before streaming to api-server.

    Called once per tag value change received from the OPC-UA server.

    Args:
        params: Contains tag_id (nodeId), value (raw OPC-UA value), data_type
                (declared type string), source_timestamp (ISO-8601), status_code
                (OPC-UA quality code e.g. "Good").
        **kwargs: Standard gateway kwargs: vars (connection variables dict),
                  labels (list of labels), sdk (ConnectionSDK), connection_id,
                  logger.

    Returns:
        StreamTagReadingParams to stream the reading unchanged or modified.
        Return None to skip streaming this reading.
    """
    # Default: pass through unchanged. Customize here to filter, transform, or enrich.
    return params
