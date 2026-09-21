import pandas as pd
import requests
from urllib.parse import urljoin
from ganymede_sdk.io import NodeReturn
from ganymede_sdk.editor import get_secret


def get_data(url: str, path: str, headers=None, params=None) -> dict:
    print(f"Retrieving data for {path}...")

    try:
        res = requests.get(urljoin(url, path), headers=headers, params=params)
        res.raise_for_status()

        return res.json()
    except requests.ConnectionError:
        print(
            """Failed to connect to the server. Check your internet connection or the server's 
               status."""
        )
    except requests.Timeout:
        print("The request timed out. The server did not respond in time.")
    except requests.TooManyRedirects:
        print(
            "Too many redirects. The requested URL might be looping through multiple redirections."
        )
    except requests.RequestException as error:
        print(f"An error occurred while fetching the URL: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None


def post_data(url: str, path: str, headers=None, data=None, params=None) -> dict:
    try:
        res = requests.post(urljoin(url, path), headers=headers, json=data, params=params)
        res.raise_for_status()

        return res.json()
    except requests.ConnectionError:
        print(
            """Failed to connect to the server. Check your internet connection or the server's 
               status."""
        )
    except requests.Timeout:
        print("The request timed out. The server did not respond in time.")
    except requests.TooManyRedirects:
        print(
            "Too many redirects. The requested URL might be looping through multiple redirections."
        )
    except requests.RequestException as error:
        print(f"An error occurred while posting data to the URL: {error}")
    except ValueError:  # This will catch JSON decoding errors
        print("Failed to decode the server's response.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None


def execute(ganymede_context=None) -> NodeReturn:
    """
    Demonstrates access of generic API

    Parameters
    ----------
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.  NodeReturn object takes
        2 parameters:
        - tables_to_upload: Dict[str, pd.DataFrame]
            keys are table names, values are pandas DataFrames to upload
        - files_to_upload: Dict[str, bytes]
            keys are file names, values are file data to upload

    """
    # Retrieves secrets from the Ganymede environment.  Secret configuration can be configured
    # within the Environment Settings panel as described in the Ganymede documentation:
    # https://docs.ganymede.bio/AdminControls.
    api_url = get_secret("api_url")
    api_key = get_secret("api_key")

    headers = {"x-api-key": api_key, "application": "application/vnd.api+json"}

    # demonstrates GET and POST requests
    output_data = get_data(api_url, "get/endpoint", headers=headers)

    data_to_send = {
        "key1": "value1",
        "key2": "value2",
    }
    output_data2 = post_data(api_url, "post/endpoint", headers=headers, data=data_to_send)

    return NodeReturn(
        tables_to_upload={
            "api_data_get": pd.json_normalize(output_data),
            "api_data_post": pd.json_normalize(output_data2),
        }
    )
