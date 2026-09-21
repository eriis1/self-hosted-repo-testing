import pandas as pd
import json
import requests
import tempfile

from typing import Union, List, Dict


def get_headers(token, content_type='application/json'):
    headers = dict()
    headers["Authorization"] = token
    headers["Content-Type"] = content_type
    headers["charset"] = "utf-8"

    return headers


def api_request(request_method: str, endpoint: str, headers: Dict[str, str], data=None):
    """
    GET request for eLabNext

    Parameters
    ----------
    endpoint: str
        full URL where data is being retrieved from
    request_method: str
        GET, POST, PUT, DELETE, HEAD, PATCH
    headers: Dict[str, str]
        headers to retrieve from
    data: Dict
        data for PUT/POST/PATCH operations
    """

    request_method = request_method.upper()
    return_payload = None

    if request_method == "GET":
        return_payload = json.loads(requests.get(endpoint, headers=headers).text)
    elif request_method == "POST":
        return_payload = json.loads(requests.post(endpoint, data=data, headers=headers).text)
    elif request_method == "PUT":
        return_payload = requests.put(endpoint, data=data, headers=headers).text
    elif request_method == "PATCH":
        return_payload = json.loads(requests.patch(endpoint, data=data, headers=headers).text)
    else:
        raise NotImplementedError(f"Request method {request_method} not yet handled.")

    return return_payload


def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]],
    data_input: Dict[str, bytes],
    base_url: str,
    token: str,
    ganymede_context=None,
) -> None:
    """
    Example demonstrating submission of user-defined SQL query into eLabNext

    Parameters
    ----------
    df_sql_result : Union[pd.DataFrame, List[pd.DataFrame]]
        Table(s) to retrieve from data lake
    base_url : str
        Base URL for eLabNext to retrieve data from / post data to
    token : str
        token used for API access
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Notes
    -----
    See [eLabNext API](https://www.elabjournal.com/docs/api/index) for more details on API usage.
    """
    
    # get BL experiment
    all_experiments = api_request("GET", f"{base_url}/api/v1/experiments", request_header)
    
    experiment_id = all_experiments['data'][1]['experimentID']
    study_id = all_experiments['data'][1]['studyID']
    
    target_experiment = api_request('GET', f'{base_url}/api/v1/experiments/{experiment_id}', request_header)
    
    # Statement of purpose
    sop_section_data = {
        'sectionType': 'PARAGRAPH',
        'sectionHeader': 'SOP'
    }
    sop_section_id = api_request('POST', f'{base_url}/api/v1/experiments/{experiment_id}/sections', request_header, data=sop_section_data)
    
    sop_section_html = """
    <p><!-- x-tinymce/html -->I’m treating an engineered yeast line with isopentyladenine, or IP, using the following concentration range [0.015-5 uM). The yeast cells are engineered with a basic GFP reporter that is expressed in response to IP. We measured GFP fluorescence after 12 hours, at which time we expect the cells to be at steady-state.<br>
    <br><!-- x-tinymce/html -->The protocol is described in more detail here: <a href="http://www.nature.com/nbt/journal/v23/n12/abs/nbt1162.html">Chen et al, Nature Biotech 2005</a>.</p>""".encode('utf-8')

    api_request('PUT', f'{base_url}/api/v1/experiments/sections/{sop_section_id}/html', request_header, 
                data=sop_section_html)
    
    # FCS File
    section_contents = {
        "sectionType": "FILE",
        "sectionHeader": "Raw Data"
    }
    file_section_id = api_request('POST', f'{base_url}/api/v1/experiments/{experiment_id}/sections',
                                  data=json.dumps(section_contents), headers=headers)
    
    fcs_filename = [filename for filename in input_data.items() if filename.endswith('.fcs')][0]
    api_endpoint = f'/api/v1/experiments/sections/{experiment_journal_id}/files?fileName={fcs_filename}'
    file_upload_res = api_request('POST', f'{base_url}{api_endpoint}', headers=headers, 
                                  data=data_input[fcs_filename])
    
    # Excel File
    section_contents = {
        "sectionType": "EXCEL",
        "sectionHeader": "Analyzed Results"
    }
    file_section_id = api_request('POST', f'{base_url}/api/v1/experiments/{experiment_id}/sections',
                                  data=json.dumps(section_contents), headers=headers)
    
    excel_filename = [filename for filename in input_data.items() if filename.endswith('xlsx')][0]
    api_endpoint = f'/api/v1/experiments/sections/{experiment_journal_id}/excel'
    excel_headers = get_header(token, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_upload_res = api_request('PUT', f'{base_url}{api_endpoint}', headers=excel_headers, 
                                  data=data_input[excel_filename])

    # WSP Files
    section_contents = {
        "sectionType": "FILE",
        "sectionHeader": "Gating Results"
    }
    file_section_id = api_request('POST', f'{base_url}/api/v1/experiments/{experiment_id}/sections',
                                  data=json.dumps(section_contents), headers=headers)
    
    wsp_filename = [filename for filename in input_data.items() if filename.endswith('wsp')][0]
    api_endpoint = f'/api/v1/experiments/sections/{experiment_journal_id}/files?fileName={filename}'
    file_upload_res = api_request('POST', f'{base_url}{api_endpoint}', headers=headers, 
                                  data=data_input[wsp_filename])
    
    return None