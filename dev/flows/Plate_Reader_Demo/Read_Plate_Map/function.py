import pandas as pd
from io import BytesIO
from typing import Union, Dict
import string


def execute(
    excel_file: Union[bytes, Dict[str, bytes]], ganymede_context=None
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    df_plate_map = pd.read_excel(excel_file, nrows=8, header=None)
    df_plate_map.columns = range(1, 13)
    df_plate_map.index = list(string.ascii_uppercase)[:8]
    df_plate_map = df_plate_map.reset_index().rename(columns={"index": "Row"})

    df_concentrations_standard_controls = pd.read_excel(excel_file, skiprows=9, usecols="A:B")

    df_concentrations_applied = pd.read_excel(excel_file, skiprows=9, usecols="D:E", nrows=5)

    mapping = {}
    for i, row in df_concentrations_applied.iterrows():
        mapping["Sample A" + str(i + 1)] = row["ng/uL.1"]
        mapping["Sample B" + str(i + 1)] = row["ng/uL.1"]
        mapping["Sample C" + str(i + 1)] = row["ng/uL.1"]
        mapping["Sample D" + str(i + 1)] = row["ng/uL.1"]
        mapping["Sample E" + str(i + 1)] = row["ng/uL.1"]
        mapping["Sample F" + str(i + 1)] = row["ng/uL.1"]
        mapping["Sample G" + str(i + 1)] = row["ng/uL.1"]
        mapping["Sample H" + str(i + 1)] = row["ng/uL.1"]

    df_plate_map.set_index("Row", inplace=True)

    df_concentrations = df_plate_map.replace(mapping)
    df_concentrations[1] = df_plate_map[1].map(
        df_concentrations_standard_controls.set_index("Concentration of viability marker")["ng/uL"]
    )
    df_concentrations[2] = df_plate_map[2].map(
        df_concentrations_standard_controls.set_index("Concentration of viability marker")["ng/uL"]
    )
    df_concentrations = df_concentrations.astype(float)
    df_concentrations = df_concentrations.reset_index().rename(columns={"index": "Row"})
    df_plate_map = df_plate_map.reset_index().rename(columns={"index": "Row"})

    return {
        "Plate_Reader_Demo_Plate_Map": df_plate_map,
        "Plate_Reader_Demo_Concentrations_Standard_Controls": df_concentrations_standard_controls,
        "Plate_Reader_Demo_Concentrations_Applied": df_concentrations_applied,
        "Plate_Reader_Demo_Concentrations": df_concentrations,
    }

# test comment