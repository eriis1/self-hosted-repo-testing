import pandas as pd
from ganymede_sdk import GanymedeContext, get_secret
from ganymede_sdk.io import NodeReturn
from urllib.parse import urljoin
import math
import requests
from ganymede_sdk.lib import _is_editor_notebook


def create_airtable_records_from_dataframe(df: pd.DataFrame, base_id: str, table_id: str):
    """
    Inserts each row of a Pandas DataFrame as a new record into an existing
    Airtable table (table_name) within the base identified by base_id.

    Parameters
    ----------
    base_id: str
        The ID of the Airtable base (e.g., 'appXXXXXXXXXXXXXX').
    table_id: str
        The name of the table in Airtable where you want to insert records (e.g., 'tblXXXXXXXXXXXXXX').
    df: pd.DataFrame
        The DataFrame containing the data to upload. Each column corresponds to a field in Airtable.

    Notes
    -----
    - The table must already exist in Airtable.
    - Column names in the DataFrame should match your Airtable field names
      (or you may need to rename them).
    - We insert records in batches of up to 10 to handle Airtable's batch
      creation limits.
    """

    airtable_key = get_secret("airtable_pat")
    url = "https://api.airtable.com/v0/"

    for elem in [base_id, table_id]:
        if elem is not None:
            url = urljoin(url + "/", elem)

    # Set up the headers with our PAT (as a Bearer token)
    headers = {
        "Authorization": f"Bearer {airtable_key}",
        "Content-Type": "application/json",
    }

    # Convert the DataFrame rows into a list of Airtable record objects
    records = []
    for _, row in df.iterrows():
        record_fields = row.to_dict()  # e.g. {"Name": "Alice", "Age": 25, ...}
        records.append({"fields": record_fields})

    # Airtable allows up to 10 records per request when doing batch create
    batch_size = 10
    total_records = len(records)
    num_batches = math.ceil(total_records / batch_size)

    inserted_count = 0
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = start_idx + batch_size
        batch_records = records[start_idx:end_idx]

        # Make the POST request to create (insert) the records in this batch
        response = requests.post(url, headers=headers, json={"records": batch_records})

        if response.status_code in (200, 201):
            # If creation succeeded, increment inserted_count by number of records created
            data = response.json()
            inserted_count += len(data.get("records", []))
        else:
            # Handle error (print the message, log it, or raise an exception)
            print(
                f"Error creating records in batch {i+1}/{num_batches} "
                f"(HTTP {response.status_code}): {response.text}"
            )
            # Optionally raise an exception or continue to next batch
            # raise Exception(f"Failed to create records: {response.text}")

    print(f"Inserted {inserted_count} out of {total_records} records.")


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    """
    Export data from Ganymede to Airtable.

    Parameters
    ----------
    df_sql_result : pd.DataFrame | list[pd.DataFrame]
        Data to export to Airtable
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage
    """
    if isinstance(df_sql_result, list):
        df_sql_result = df_sql_result[0]

    base_id = "appbJuH7KuPE5sw2P"
    table_id = "tblhOzrfc19fp0ZPq"

    if _is_editor_notebook():
        df = pd.DataFrame({"Name": ["John"], "Notes": ["Test export from notebook"]})
    else:
        df = pd.DataFrame({"Name": ["Jack"], "Notes": ["Test export from composer"]})

    create_airtable_records_from_dataframe(df, base_id, table_id)