import pandas as pd
from ganymede_sdk import GanymedeContext, get_secret
from ganymede_sdk.io import NodeReturn
from urllib.parse import urljoin
import requests


def get_airtable_table(base_id: str, table_id: str) -> pd.DataFrame:
    """
    Request Airtable table data

    Parameters
    ----------
    base_id : str
        Airtable base ID; begins with "app
    table_id : str
        Airtable table ID; begins with "tbl"

    Returns
    -------
    pd.DataFrame
        Contents of Airtable table
    """

    airtable_key = get_secret("airtable_pat")
    url = "https://api.airtable.com/v0/"

    for elem in [base_id, table_id]:
        if elem is not None:
            url = urljoin(url + "/", elem)

    headers = {"Authorization": f"Bearer {airtable_key}"}
    res = requests.get(url, headers=headers)

    df = pd.DataFrame.from_records([rec["fields"] for rec in res.json()["records"]])
    return df


def execute(ganymede_context: GanymedeContext) -> NodeReturn:
    """
    Ingest data from Airtable to Ganymede.

    Parameters
    ----------
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage
    """

    base_id = "appbJuH7KuPE5sw2P"
    table_id = "tblhOzrfc19fp0ZPq"

    df = get_airtable_table(base_id, table_id)

    return NodeReturn(tables_to_upload={"ganymede_table": df})