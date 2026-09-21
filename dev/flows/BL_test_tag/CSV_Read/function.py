import pandas as pd
from io import BytesIO
from typing import Dict
from ganymede_sdk.io import NodeReturn
from ganymede_sdk.file_tag import add_file_tag


def execute(csv_file: Dict[str, BytesIO], ganymede_context=None) -> NodeReturn:
    """
    Processes CSV file(s) (passed to function as BytesIO file-like objects) into data tables
    stored in data lake

    Parameters
    ----------
    csv_file : Dict[str, BytesIO]
        CSV files, indexed by file name
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.
    """

    file_path = ganymede_context.inputs["csv"]
    filename = "2023-Nov-28_LAPEG600_LCT_WC_DS5p4-1_10-500mJ_1100mW_1.zip"
    x = 5

    dt, print_name, operator, run_type, printer, range, dosage, replicate = filename.split(".")[
        0
    ].split("_")

    add_file_tag(input_file_path=file_path, tag_type_id="run_date", display_value=dt)
    add_file_tag(input_file_path=file_path, tag_type_id="sample", display_value=print_name)
    add_file_tag(input_file_path=file_path, tag_type_id="user", display_value=operator)
    add_file_tag(input_file_path=file_path, tag_type_id="run_type", display_value=run_type)
    add_file_tag(input_file_path=file_path, tag_type_id="instrument_multi", display_value=printer)
    add_file_tag(input_file_path=file_path, tag_type_id="run_param_multi", display_value=range)
    add_file_tag(input_file_path=file_path, tag_type_id="run_param_multi", display_value=dosage)

    results_dict = dict()

    if len(csv_file) > 1:
        for filename, file_contents in csv_file.items():
            results_dict[filename] = pd.read_csv(file_contents)
    else:
        return NodeReturn(tables_to_upload={"results": pd.read_csv(list(csv_file.values()).pop())})

    return NodeReturn(tables_to_upload=results_dict)
