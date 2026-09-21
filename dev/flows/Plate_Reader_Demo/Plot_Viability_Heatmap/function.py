from typing import Dict, Union, Optional, List
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns


def execute(
    df_sql_result: Optional[Union[pd.DataFrame, List[pd.DataFrame]]],
    ganymede_context=None,
) -> Dict[str, bytes]:
    df1 = df_sql_result[0]
    df2 = df_sql_result[1]
    df3 = df_sql_result[2]
    df4 = df_sql_result[3]

    df2 = df2.merge(df3, left_on="Drug_Concentrations", right_on="ng_uL_1")
    df2["Sample Name Combined"] = df2["Sample_Name"].astype(str) + df2[
        "Concentration_of_drug"
    ].astype(str)

    df2.drop(columns=["Concentration_of_drug", "ng_uL_1"], inplace=True)

    # Create a new dataframe for the annotations
    annot_data = df1.copy()

    # Reshape the data to match the layout of df1
    heatmap_data = df1.copy()
    for i in range(heatmap_data.shape[0]):
        for j in range(1, heatmap_data.shape[1]):
            sample_name = heatmap_data.iloc[i, j]
            value = (
                df2.loc[
                    df2["Sample Name Combined"] == sample_name,
                    "Estimated_Marker_Concentration_Rep_1",
                ].values
                / 10
            )
            if len(value) > 0 and not (value[0] in heatmap_data.values):
                heatmap_data.iloc[i, j] = value[0]
                annot_data.iloc[i, j] = " {}\n{:.2f}%".format(sample_name, value[0])
            elif len(value) > 0:
                value = (
                    df2.loc[
                        df2["Sample Name Combined"] == sample_name,
                        "Estimated_Marker_Concentration_Rep_2",
                    ].values
                    / 10
                )
                heatmap_data.iloc[i, j] = value[0]
                annot_data.iloc[i, j] = " {}\n{:.2f}%".format(sample_name, value[0])
            else:
                value = (
                    df4.loc[df4["Concentration_of_viability_marker"] == sample_name, "ng_uL"].values
                    / 10
                )
                heatmap_data.iloc[i, j] = value[0]
                annot_data.iloc[i, j] = " {}\n{:.2f}%".format(sample_name, value[0])
    # Create the heatmap
    # print(heatmap_data)
    plt.figure(figsize=(25, 12))
    ax = sns.heatmap(
        heatmap_data.iloc[:, 1:].astype(float),
        cmap="viridis",
        annot=annot_data.iloc[:, 1:],
        fmt="",
        cbar=False,
    )
    plt.title("Platemap With Viability")
    ax.set_yticklabels(heatmap_data["Row"].values)

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=300)
    buffer.seek(0)

    return {"Plate_Viability_Heatmap.png": buffer.read()}