import pandas as pd
from typing import Union, Dict, List
from scipy.optimize import curve_fit
import math


def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    import numpy as np
    df_results = df_sql_result[0].sort_values(["Sample_Name","Drug_Concentrations"])
    df_concentrations_standard_controls = df_sql_result[1].sort_values("Concentration_of_viability_marker")
  
    IC50 = {}

    for sample in df_results['Sample_Name'].unique():
        sample_data = df_results[df_results['Sample_Name'] == sample]

        # Calculate the average estimated concentration
        sample_data['Avg Concentration'] = sample_data[['Estimated_Marker_Concentration_Rep_1', 'Estimated_Marker_Concentration_Rep_2']].mean(axis=1)

        drug_concentrations = sample_data['Drug_Concentrations']
        marker_concentration = sample_data['Avg Concentration']

        # Sigmoidal dose-response model
        def sigmoidal_dose_response(x, IC50, Hill_slope, E_min, E_max):
            return E_min + (E_max - E_min) / (1 + (x / IC50) ** Hill_slope)

        def inverse_sigmoidal_dose_response(y, IC50, Hill_slope, E_min, E_max):
            return IC50 * ((E_max - E_min) / (y - E_min) - 1) ** (1 / Hill_slope)


        # Fit curve
        initial_guess = [500, 1, min(df_concentrations_standard_controls['ng_uL']), max(df_concentrations_standard_controls['ng_uL'])]

        try:
            fit_params, _ = curve_fit(sigmoidal_dose_response, drug_concentrations, marker_concentration, p0=initial_guess)

            IC50[sample] = inverse_sigmoidal_dose_response( max(df_concentrations_standard_controls['ng_uL'])/2, fit_params[0], fit_params[1], fit_params[2], fit_params[3])

            if math.isnan(IC50[sample]):
                del IC50[sample]
                raise RuntimeError
        except RuntimeError:
            IC50[sample] = "Undefined"
            pass
                
    return pd.DataFrame(IC50, index = ["IC50_Value"]).T.reset_index().rename(columns = {"index": "Sample Name"})
