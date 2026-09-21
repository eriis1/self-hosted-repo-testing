from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import FlowInputFile, FlowInputs


def retrieve_file(
    aws_session,
    s3_file_name: str,
    s3_bucket_name: str,
    triggered_flow_node_name: str,
    triggered_flow_param_name: str,
) -> FlowInputFile:
    """
    Retrieve S3 file

    Parameters
    ----------
    aws_session: AWS Session
        AWS Session
    s3_file_name: str
        Name of file in S3 bucket
    s3_bucket_nam: str
        Name of S3 bucket
    triggered_flow_node_name: str
        Node in triggered flow that will be receiving file input
    triggered_flow_param_name: str
        Parameter for node in triggered flow
    """
    s3_client = aws_session.client("s3")

    file_object = s3_client.get_object(Key=s3_file_name, Bucket=s3_bucket_name)

    file_contents = file_object["Body"].read()

    # remove folder from filename
    filename = s3_file_name.split("/")[-1]

    file = FlowInputFile(
            node_name=triggered_flow_node_name,
            param_name=triggered_flow_param_name,
            files={filename: file_contents},
        )
    
    return file


def execute(
    object_name: str, bucket_name: str, aws_session=None, ganymede_context: GanymedeContext = None
) -> FlowInputs:
    """
    Calls AWS to get data for flow to trigger

    Parameters
    ----------
    object_name : str
        File name in S3 bucket
    bucket_name : str
        Name of S3 bucket
    aws_session: AWS Session
        AWS Session

    Returns
    -------
    FlowInputs
        Object containing data for kicking off subsequent Flow
    """

    # Example file download

    test_file = retrieve_file(aws_session, object_name, bucket_name, "CSV_Read", "csv")

    file_list = [test_file]

    # test_param = get_benchling_value(even::qt_data, "test_param")
    # params_list = FlowInputParam(node_name='Plate_Reader', param_name='param',
    #                              param_value=get_benchling_value(event_data, 'Plate Name'))

    # f = FlowInputs(files=file_list, params=params_list)

    # populate FlowInputs object based on event_data to return
    f = FlowInputs(files=file_list, params=None)

    return f