import pandas as pd
import pyopenms as oms
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import NodeReturn


def execute(lcms_file_paths: list[str], ganymede_context: GanymedeContext) -> NodeReturn:
    """
    Function to process LCMS file data

    Parameters
    ----------
    lcms_file_paths : str
        Path to LCMS file to be read
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage
    """
    # observe sample file path
    lcms_file_path = lcms_file_paths[0]

    exp = oms.MSExperiment()
    oms.MzMLFile().load(lcms_file_path, exp)

    spectrum_dict = {}
    for idx, spectrum in enumerate(exp):
        mz, intensity = spectrum.get_peaks()
        spectrum_dict.update({f"spectrum{idx}": {"mz": mz, "intensity": intensity}})

    df_out = pd.DataFrame.from_dict(spectrum_dict)
    return NodeReturn(tables_to_upload={"lcms_spectra": df_out})
