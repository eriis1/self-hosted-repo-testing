import pandas as pd
import numpy as np
from io import BytesIO
from typing import Union, Dict
from ganymede_sdk.io import NodeReturn

# from ganymede_sdk.api.benchling import Benchling
from ganymede_sdk.file_tag import add_file_tag


def create_metadata_df(df):
    # Get the column names from the header row
    column_names1 = df.columns.tolist()

    # Get the column names from the 3rd row

    column_names2 = df.iloc[1].dropna().values.tolist()

    # Create dataframes from the first and third row
    df1 = pd.DataFrame([df.iloc[0].values.tolist()[: len(column_names1)]], columns=column_names1)
    df2 = pd.DataFrame([df.iloc[2].values.tolist()[: len(column_names2)]], columns=column_names2)

    # Concatenate the dataframes
    new_df = pd.concat([df1, df2], axis=1)

    return new_df


def create_total_df(df):
    total_row = df[df.iloc[:, 0] == "Total"]
    total_df = pd.DataFrame([total_row.values[0]], columns=total_row.columns)
    total_df = total_df.loc[:, total_df.columns.dropna()]
    total_df = total_df.loc[:, total_df.columns != "NA"]
    return total_df


def drop_total_and_nan_rows(df):
    # Find the indexes of rows which have 'Total' or 'NaN' in the first column
    indices_to_drop = df[df.iloc[:, 0].isin(["Total", np.nan])].index

    # Drop these rows from the dataframe
    df = df.drop(indices_to_drop)

    return df


def convert_columns(df):
    # convert numeric columns to appropriate data type
    df["minimum diameter m"] = pd.to_numeric(df["minimum diameter m"], errors="raise")
    df["maximum diameter m"] = pd.to_numeric(df["maximum diameter m"], errors="raise")
    df["Cell sharpness"] = pd.to_numeric(df["Cell sharpness"], errors="raise")
    df["Minimum circularity"] = pd.to_numeric(df["Minimum circularity"], errors="raise")
    df["Viable spot brightness (%)"] = pd.to_numeric(
        df["Viable spot brightness (%)"], errors="raise"
    )
    df["Viable spot area (%)"] = pd.to_numeric(df["Viable spot area (%)"], errors="raise")
    df["Viable spot brightness (%)"] = pd.to_numeric(
        df["Viable spot brightness (%)"], errors="raise"
    )
    df["Dilution"] = pd.to_numeric(df["Dilution"], errors="raise")
    df["Concentration Adjustment Factor (%)"] = pd.to_numeric(
        df["Concentration Adjustment Factor (%)"], errors="raise"
    )
    df["Dilution"] = pd.to_numeric(df["Dilution"], errors="raise")
    df["Total (x10^6) cells/mL"] = pd.to_numeric(df["Total (x10^6) cells/mL"], errors="raise")
    df["viability"] = pd.to_numeric(df["viability"], errors="raise")
    df["Viable (x10^6) cells/mL"] = pd.to_numeric(df["Viable (x10^6) cells/mL"], errors="raise")
    df["average diameter m"] = pd.to_numeric(df["average diameter m"], errors="raise")
    df["average viable diameter m"] = pd.to_numeric(df["average viable diameter m"], errors="raise")
    df["Average circularity"] = pd.to_numeric(df["Average circularity"], errors="raise")
    df["Average viable circularity"] = pd.to_numeric(
        df["Average viable circularity"], errors="raise"
    )
    df["Images for analysis"] = pd.to_numeric(df["Images for analysis"], errors="raise")
    df["Images"] = pd.to_numeric(df["Images"], errors="raise")
    df["Aspiration cycles"] = pd.to_numeric(df["Aspiration cycles"], errors="raise")
    df["Mixing cycles"] = df["Mixing cycles"].astype(int)
    df["Cell count"] = pd.to_numeric(df["Cell count"], errors="raise")
    df["Viable cells"] = pd.to_numeric(df["Viable cells"], errors="raise")
    df["Average cells per image"] = pd.to_numeric(df["Average cells per image"], errors="raise")
    df["Average background intensity"] = pd.to_numeric(
        df["Average background intensity"], errors="raise"
    )
    df["Bubble count"] = pd.to_numeric(df["Bubble count"], errors="raise")
    df["COLUMN"] = df["COLUMN"].astype(int)
    df["Cluster count"] = pd.to_numeric(df["Cluster count"], errors="raise")
    df["Reanalysis by"] = df["Reanalysis by"].fillna("").astype(str)
    df["Tag"] = df["Tag"].fillna("").astype(str)
    df["Reanalysis date/time"] = pd.to_datetime(df["Reanalysis date/time"])
    df["Analysis date/time"] = pd.to_datetime(df["Analysis date/time"])
    df["In service date"] = pd.to_datetime(df["In service date"])
    df["Effective expiration"] = pd.to_datetime(df["Effective expiration"])
    df["Expiration"] = pd.to_datetime(df["Expiration"])

    return df


def convert_columns_raw(df):
    df["Cell count"] = pd.to_numeric(df["Cell count"], errors="raise")
    df["Viable cells"] = pd.to_numeric(df["Viable cells"], errors="raise")
    df["Total (x10^6) cells/mL"] = pd.to_numeric(df["Total (x10^6) cells/mL"], errors="raise")
    df["Viable (x10^6) cells/mL"] = pd.to_numeric(df["Viable (x10^6) cells/mL"], errors="raise")
    df["viability"] = pd.to_numeric(df["Viability (%)"], errors="raise")
    df["average diameter m"] = pd.to_numeric(df["average diameter m"], errors="raise")
    df["Average viable diameter m"] = pd.to_numeric(df["Average viable diameter m"], errors="raise")
    df["Average circularity"] = pd.to_numeric(df["Average circularity"], errors="raise")
    df["Average viable circularity"] = pd.to_numeric(
        df["Average viable circularity"], errors="raise"
    )
    df["Average cells per image"] = pd.to_numeric(df["Average cells per image"], errors="raise")
    df["Average background intensity"] = pd.to_numeric(
        df["Average background intensity"], errors="raise"
    )
    df["Bubble count"] = pd.to_numeric(df["Bubble count"], errors="raise")
    df["Cluster count"] = pd.to_numeric(df["Cluster count"], errors="raise")
    return df


def add_tags(file_data, ganymede_context):

    for filename in file_data.keys():
        add_file_tag(
            input_file_path=filename,
            tag_type_id="data_source_type",
            display_value="Internal Instrument",
            bucket="input",
        )
        add_file_tag(
            filename,
            "data_lifecycle_stage",
            display_value="Instrument Export",
            bucket="input",
        )
        add_file_tag(
            filename, "instrument_type", display_value="Viable Cell Counter", bucket="input"
        )


def execute(
    csv_file: Dict[str, BytesIO], ganymede_context=None
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:

    # b = Benchling(ganymede_context)

    df = pd.read_csv(list(csv_file.values()).pop())

    metadata_df = create_metadata_df(df)

    results_df = df.iloc[4:, :].copy()
    results_df.columns = df.iloc[3]

    filename = ganymede_context.params["Read_Single_Measurement_File.csv"].split("/")[-1]

    # Drop columns with 'NA' or nan names
    results_df = results_df.loc[:, results_df.columns.dropna()]
    results_df = results_df.loc[:, results_df.columns != "NA"]

    totals_df = create_total_df(results_df)
    results_df = drop_total_and_nan_rows(results_df)

    # combine metadata and totals
    totals_and_metadata_df = pd.concat([metadata_df, totals_df], axis=1)
    totals_and_metadata_df.reset_index(drop=True, inplace=True)
    results_df.reset_index(drop=True, inplace=True)

    # grab instrument identifier from input param
    totals_and_metadata_df["instrument_used"] = ganymede_context.params[
        "Input_ViCell_Instrument.param"
    ].split("\\")[-1]

    # parse sample name from file name

    totals_and_metadata_df["vicellsamp_id"] = filename.split("/")[-1].split("_")[0]

    print(totals_and_metadata_df)
    # rename columns for compatability
    totals_and_metadata_df.rename(
        columns={
            "Minimum Diameter (µm)": "minimum diameter m",
            "Maximum Diameter (µm)": "maximum diameter m",
            "Average diameter (µm)": "average diameter m",
            "Average viable diameter (µm)": "average viable diameter m",
            "analysis_date_time": "analysis_datetime",
            "Sample ID": "sample_name",
            "Viability (%)": "viability",
        },
        inplace=True,
    )

    results_df.rename(
        columns={
            "Average diameter (µm)": "average diameter m",
            "Average viable diameter (µm)": "Average viable diameter m",
        },
        inplace=True,
    )

    totals_and_metadata_df.drop(columns=["Image#"], inplace=True)
    totals_and_metadata_df = convert_columns(totals_and_metadata_df)

    print("results_df columns", results_df.columns)
    results_df = convert_columns_raw(results_df)
    print("results_df columns", results_df.columns)

    totals_and_metadata_df["__input_filename"] = filename
    results_df["__input_filename"] = filename

    # put sample_id on raw results
    vicellsamp_id = totals_and_metadata_df["vicellsamp_id"].iloc[0]
    results_df["vicellsamp_id"] = vicellsamp_id

    totals_and_metadata_df["__run_id"] = ganymede_context.run_id
    totals_and_metadata_df["__run_id_v2"] = int(ganymede_context.flow_run_id)
    totals_and_metadata_df["__input_filename"] = filename
    results_df["__run_id"] = ganymede_context.run_id
    results_df["__run_id_v2"] = int(ganymede_context.flow_run_id)
    results_df["__input_filename"] = filename

    # if len(totals_and_metadata_df.columns) > 0:
    #     totals_and_metadata_df = totals_and_metadata_df.reindex(columns=[''])

    dict_out = {
        "ViCell_Blu_Totals_and_Metadata": totals_and_metadata_df,
        "results": results_df,
    }

    add_tags(csv_file, ganymede_context)
    return NodeReturn(tables_to_upload=dict_out, wait_for_job=True)