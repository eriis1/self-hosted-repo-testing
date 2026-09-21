from typing import Dict, Union, Optional, List
import pandas as pd
import io
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import math

def execute(
    df_sql_result: Optional[Union[pd.DataFrame, List[pd.DataFrame]]],
    ganymede_context=None,
) -> Dict[str, bytes]:
    
    df_results = df_sql_result[0].sort_values(["Sample_Name","Drug_Concentrations"])
    df_concentrations_standard_controls = df_sql_result[1].sort_values("Concentration_of_viability_marker")
    
    IC50 = {}

    # Calculate the number of rows and columns for subplots
    num_samples = len(df_results['Sample_Name'].unique())
    num_cols = 2
    num_rows = (num_samples + num_cols - 1) // num_cols

    # Create the main plot with subplots
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 3.5 * num_rows))
    fig.tight_layout(pad=4.0)
    plt.rcParams.update({'font.size': 10})

    # Flatten the axes array
    axes = np.ravel(axes)

    # Iterate through the samples and plot on separate subplots
    for i, sample in enumerate(df_results['Sample_Name'].unique()):
        sample_data = df_results[df_results['Sample_Name'] == sample]
        # Calculate the average estimated concentration
        sample_data['Avg Concentration'] = sample_data[['Estimated_Marker_Concentration_Rep_1', 'Estimated_Marker_Concentration_Rep_2']].mean(axis=1)
        sample_data.loc[sample_data['Avg Concentration'] < min(df_concentrations_standard_controls['ng_uL']), 'Avg Concentration'] = min(df_concentrations_standard_controls['ng_uL'])
        sample_data.loc[sample_data['Avg Concentration'] > max(df_concentrations_standard_controls['ng_uL']), 'Avg Concentration'] = max(df_concentrations_standard_controls['ng_uL'])

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

            # Generate curve points for plotting
            x = np.linspace(1, 10000, 10000)
            y_fit = sigmoidal_dose_response(x, *fit_params)

            IC50[sample] = inverse_sigmoidal_dose_response( max(df_concentrations_standard_controls['ng_uL'])/2, fit_params[0], fit_params[1], fit_params[2], fit_params[3])

            if math.isnan(IC50[sample]):
                del IC50[sample]
                raise RuntimeError

            # Plotting on the current subplot
            ax = axes[i]
            ax.plot(drug_concentrations, marker_concentration, color='blue', marker='o', linestyle='', label='Data')
            ax.plot(x, y_fit, color='red', label='Fit')
            ax.axvline(x=IC50[sample], color='green', linestyle='--', label='IC50')
            ax.set_xscale('log')
            ax.set_xlabel('Drug Concentrations')
            ax.set_ylabel('Viability (ng/uL)')
#             ax.set_ylim([min(df_concentrations_standard_controls['ng_uL']), max(df_concentrations_standard_controls['ng_uL'])])

            ax.set_title(f'IC50 Curve with Fit {sample}')
            ax.legend()
        except RuntimeError:
            ax = axes[i]
            ax.plot(drug_concentrations, marker_concentration, color='blue', marker='o', linestyle='', label='Data')
            ax.set_xscale('log')
            ax.set_xlabel('Drug Concentrations')
            ax.set_ylabel('Viability (ng/uL)')
            ax.set_title(f'Curve for {sample}')
#             ax.set_ylim([min(df_concentrations_standard_controls['ng_uL']), max(df_concentrations_standard_controls['ng_uL'])])
            ax.legend()


    # Remove empty subplots if there are any
    if len(axes) > num_samples:
        for j in range(num_samples, len(axes)):
            fig.delaxes(axes[j])
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    return {"IC50_Curves.png": buffer.read()}


