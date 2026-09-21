from typing import Dict, Union, Optional, List
import pandas as pd
import io
import matplotlib.pyplot as plt
import numpy as np


def execute(
    df_sql_result: Optional[Union[pd.DataFrame, List[pd.DataFrame]]],
    ganymede_context=None,
) -> Dict[str, bytes]:
    
    df_data = df_sql_result[0].sort_values("Row")
    df_concentrations = df_sql_result[1].sort_values("Row")
    
    
    x = df_concentrations.iloc[:, :2].mean(axis=1).values.tolist()
    y = df_data.iloc[:, :2].mean(axis=1).values.tolist()

    # Fit a linear regression model to the data
    coefficients = np.polyfit(x, y, 1) 

    # Create a function based on the fit
    linear_fit = np.poly1d(coefficients)

    # Calculate the estimated y values
    y_estimated = linear_fit(x)

    # Plot the original data and the fit
    fig, axs = plt.subplots(figsize=(15, 12), sharex="all", dpi=100)
    plt.rcParams.update({'font.size': 20})

    axs.plot(x, y, 'o', label='Original data')
    axs.plot(x, y_estimated, label='Fitted line')

    plt.xlabel("Concentration")
    plt.ylabel("Measurement")
    plt.title("Least-squares Linear Fit")
    plt.legend()

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    return {"Plate_Reader_Demo_Linear_Fit.png": buffer.read()}

