import requests
import json

import pandas as pd
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn
from ganymede_sdk.editor.secrets import get_secret

DEFAULT_EVENT = {
    "version": "0",
    "id": "da77eb93-75b2-c2a9-942e-79e973ca2a82",
    "detail-type": "v2.entity.registered",
    "source": "aws.partner/benchling.com/pipeline-ganymede-dev/pipeline-ganymede-dev",
    "account": "710795444417",
    "time": "2023-01-20T18:38:14Z",
    "region": "us-east-1",
    "resources": [],
    "detail": {
        "entity": {
            "id": "bfi_i6qhR2dF",
            "name": "qPCR - 004",
            "apiURL": "",
            "fields": {
                "Target Gene": {
                    "type": "text",
                    "value": "B",
                    "isMulti": False,
                    "textValue": "B",
                    "displayValue": "B",
                },
                "qPCR Plate Map": {
                    "type": "blob_link",
                    "value": "797eae5d-00b2-4341-8ce5-3d092492204f",
                    "isMulti": False,
                    "textValue": "plate_map.xlsx",
                    "displayValue": "plate_map.xlsx",
                },
                "Housekeeping Gene": {
                    "type": "text",
                    "value": "A",
                    "isMulti": False,
                    "textValue": "A",
                    "displayValue": "A",
                },
                "QuantStudio Input": {
                    "type": "blob_link",
                    "value": "2f569ae3-fade-48f1-a388-36a4192ca4fe",
                    "isMulti": False,
                    "textValue": "52022_abhinav_raw.csv",
                    "displayValue": "52022_abhinav_raw.csv",
                },
            },
            "schema": {"id": "ts_vAxGCX5x", "name": "Run Submission"},
            "webURL": "",
            "aliases": [],
            "authors": [{"id": "ent_uHprkopF", "name": "", "handle": "Ganymede"}],
            "creator": {"id": "ent_uHprkopF", "name": "", "handle": "Ganymede"},
            "folderId": "lib_wzU6jZhI",
            "createdAt": "2023-01-20T18:38:14.356574+00:00",
            "modifiedAt": "2023-01-20T18:38:14.356574+00:00",
            "registryId": "src_E6a4Cqnu",
            "customFields": {},
            "archiveRecord": None,
            "entityRegistryId": "qpcr-sub004",
            "registrationOrigin": {},
        },
        "schema": {"id": "ts_vAxGCX5x", "name": "Run Submission"},
        "deprecated": False,
        "excludedProperties": [],
        "id": "evt_jzAqd9erheFL",
        "createdAt": "2023-01-20T18:38:14.356574+00:00",
        "eventType": "v2.entity.registered",
    },
}


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
    secret = get_secret("benchling_api_key")
    resp = requests.post(
        "https://dev.ganymede.bio/event/aws",
        headers={"api-key": secret, "Content-Type": "application/json"},
        data=json.dumps(DEFAULT_EVENT),
    )
    print(resp)

    return