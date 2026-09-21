import pandas as pd
from typing import Union, Dict
from synergy_file_reader import SynergyFile
from tempfile import NamedTemporaryFile
import re
from datetime import datetime

def convert_time_and_date(input_string):
    # Define regular expressions for Date and Time
    date_pattern = r"Date\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})"
    time_pattern = r"Time\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})"

    # Replace Date and Time in the input string
    output_string = input_string
    for match in re.finditer(date_pattern, input_string):
        date_obj = datetime.strptime(match.group(1), '%Y-%m-%d')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        output_string = re.sub(date_pattern, f"Date\t{formatted_date}", output_string)

    for match in re.finditer(time_pattern, input_string):
        time_obj = datetime.strptime(match.group(2), '%H:%M:%S')
        formatted_time = time_obj.strftime('%H:%M:%S')
        output_string = re.sub(time_pattern, f"Time\t{formatted_time}", output_string)

    datetime_pattern = r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})"

    # Replace date-time in the input string
    for match in re.finditer(datetime_pattern, input_string): 
        full_datetime = f"{match.group(1)} {match.group(2)}"
        datetime_obj = datetime.strptime(full_datetime, '%Y-%m-%d %H:%M:%S')
        formatted_time_out = datetime_obj.strftime('%H:%M:%S')
        output_string = output_string.replace(full_datetime, formatted_time_out)

    return output_string, formatted_time_out

def execute(synergy_file: Dict[str, bytes], ganymede_context=None) -> Dict[str, pd.DataFrame]:
    """
    Processes Synergy text file(s) into data tables stored in data lake

    Parameters
    ----------
    synergy_file : Dict[str, bytes]
        Synergy text files, indexed by file name
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    Dict[str, pd.DataFrame]
        Tables to store in data lake
    """

    df_metadata = pd.DataFrame()
    df_data = pd.DataFrame()
    for filename, contents in synergy_file.items():
        with NamedTemporaryFile() as file:
            text = pd.read_excel(contents, dtype=str).to_csv(sep="\t",index=False, header=False)

            # text = text.split("Results")[0].rstrip()
            text = text.split("Procedure Details")[0] + "Procedure Details\n" + text.split("Procedure Details")[1]
            text, formatted_time = convert_time_and_date(text)
            text = [line.strip() if line[0] != "\t" else line.rstrip()[1:] for line in text.splitlines()]
            text = "\n".join(text)


            text = text.replace("Results", "")
            wavelength = re.findall('Wavelengths:\s+(\d+)', text)
            text = text.split("	1	")[0] + f"{wavelength[0]}\n\t1	" + text.split("	1	")[1]

            file.write(text.encode("iso-8859-1"))
            file.seek(0)
            synergy_file = SynergyFile(file.name, verbose=True)
            
        for plate in synergy_file:
            df_metadata_temp = pd.DataFrame().from_dict(dict(zip(plate.metadata.keys(), [[x] for x in plate.metadata.values()])), orient='index').T
            df_metadata_temp.index = [0]

            df_metadata = pd.concat([df_metadata, df_metadata_temp])

            df_data_temp = pd.Series(plate.data).unstack().unstack().droplevel(0, axis = 1)

            df_data = pd.concat([df_data, df_data_temp])

    df_data = df_data.reset_index().rename(columns={"index": "Row"})

    return {"Plate_Reader_Demo_Metadata": df_metadata, "Plate_Reader_Demo_Data": df_data}



