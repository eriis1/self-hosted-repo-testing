import pandas as pd
from typing import Union, Dict, List
import numpy as np


def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    
    df_data = df_sql_result[0].sort_values("Row").reset_index(drop=True)
    df_concentrations = df_sql_result[1].sort_values("Row").reset_index(drop=True)
    df_plate_map = df_sql_result[2].sort_values("Row").reset_index(drop=True)
    df_concentrations_applied = df_sql_result[3].sort_values("Concentration_of_drug").reset_index(drop=True)

    sample_names = df_plate_map["3"].apply(lambda x: x[:-1]).unique().tolist()

    x = df_concentrations.iloc[:, :2].mean(axis=1).values.tolist()
    y = df_data.iloc[:, :2].mean(axis=1).values.tolist()
    
    # Fit a linear regression model to the data
    coefficients = np.polyfit(x, y, 1) 

    df_results = pd.DataFrame()

    for sample_name in sample_names:
        df_sample_results = pd.DataFrame(index=range(df_concentrations_applied.shape[0]))
        df_sample_results["Sample Name"] = sample_name

        concentrations = df_concentrations_applied['ng_uL_1'].values.tolist()
        df_sample_results["Drug Concentrations"] = pd.Series(concentrations)
        
        df_sample_results[["Rep 1 Measurement", "Rep 2 Measurement"]] = df_data.where(df_plate_map.applymap(lambda x: sample_name in x), np.nan).dropna(how='all').dropna(axis=1, how='all').values.reshape(-1, 2)
        # Fitted line parameters
        m, c = coefficients

        # For each sample, calculate the estimated concentration
        df_sample_results["Estimated Marker Concentration Rep 1"] = (df_sample_results["Rep 1 Measurement"] - c) / m
        df_sample_results["Estimated Marker Concentration Rep 2"] = (df_sample_results["Rep 2 Measurement"] - c) / m

        df_results = pd.concat([df_results, df_sample_results])
        
    return df_results

