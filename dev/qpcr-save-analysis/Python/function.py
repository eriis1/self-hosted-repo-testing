import json
import re

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext
from ganymede_sdk.io import NodeReturn


def to_num(x):
    # pandas-aware NA handling (None, np.nan, pd.NA, etc.)
    if pd.isna(x):
        return None
    # treat empty/whitespace strings as missing too
    if isinstance(x, str) and x.strip() == "":
        return None
    # best-effort numeric conversion
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def qpcr_template_to_dataframe(file_content):
    df = pd.DataFrame([file_content]).drop(columns="analysis")
    return df


def qpcr_template_qpcr_analysis_to_dataframe(file_content):
    data = file_content.get("analysis", {}).get("plate_results", {}).get("data", {})
    if not data:
        return None

    metadata = {
        key: str(val)
        for key, val in file_content.get("analysis", {}).get("plate_results", {}).items()
        if key != "data"
    }
    print(metadata)

    df = pd.concat([pd.DataFrame(records) for records in data.values()]).assign(**metadata)

    cols_to_drop = ["", "__protocol_run_id"]
    df = df.drop(columns=[col for col in df.columns if str(col.strip()) in cols_to_drop])

    return df


def qpcr_template_qpcr_curve_fitting_to_dataframe(file_content):
    data = file_content.get("analysis", {}).get("curve_fitting", {})
    if not data:
        return None

    rows = []
    for comparison, compounds in data.items():
        for compound_id, compound_data in compounds.items():

            # Pop any dynamic keys ending in _abs or _rel, convert to numeric,
            # and add them back into the final row (keys can change over time).
            dynamic_abs_rel = {}
            for k in list(compound_data.keys()):
                if k.endswith("_abs") or k.endswith("_rel"):
                    dynamic_abs_rel[k] = to_num(compound_data.pop(k))

            row = {
                "comparison": comparison,
                "compound_id": compound_id,
                "data_name": compound_data["data_name"],
                "metric_name": compound_data["metric_name"],
                "target_name_hk": compound_data.get("target_name_hk"),
                "condition_hk": compound_data.get("condition_hk"),
                "condition_ic": compound_data.get("condition_ic"),
                "review_status": compound_data["review_status"],
                "r_squared": to_num(compound_data["r_squared"]),
                "fix_hill": compound_data["fix_hill"],
                "hill_slope": to_num(compound_data["hill_slope"]),
                "min_fit": to_num(compound_data["min_fit"]),
                "max_fit": to_num(compound_data["max_fit"]),
                "include_ic_calculations": compound_data["include_ic_calculations"],
                "log_x_axis": compound_data["log_x_axis"],
                "log_y_axis": compound_data["log_y_axis"],
                "curve_model": "3PL" if compound_data["fix_hill"] else "4PL",
                "model_param_A": to_num(compound_data["model_params"]["A"]),
                "model_param_B": to_num(compound_data["model_params"]["B"]),
                "model_param_C": to_num(compound_data["model_params"]["C"]),
                "model_param_D": to_num(compound_data["model_params"]["D"]),
                "bottom_fixed": compound_data["manual_params"]["bottom_checkbox"],
                "manual_bottom_value": to_num(compound_data["manual_params"]["bottom_value"]),
                "top_fixed": compound_data["manual_params"]["top_checkbox"],
                "manual_top_value": to_num(compound_data["manual_params"]["top_value"]),
                "slope_fixed": compound_data["manual_params"]["slope_checkbox"],
                "manual_slope_value": to_num(compound_data["manual_params"]["slope_value"]),
                "custom_ic1_pct": to_num(compound_data["manual_params"]["custom_ic1_pct"]),
                "custom_ic2_pct": to_num(compound_data["manual_params"]["custom_ic2_pct"]),
                "excluded": compound_data["excluded_points"],
                "n_data_points": len(compound_data["current_standard_data"]),
                "n_excluded": len(compound_data["excluded_points"]),
            }

            # add dynamic *_abs/*_rel columns back in
            row.update(dynamic_abs_rel)
            rows.append(row)

    return pd.DataFrame(rows)


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    """
    Process tabular data from user-defined SQL query, writing results back to data lake.  Data
    is written to the output bucket.

    Parameters
    ----------
    df_sql_result : pd.DataFrame | list[pd.DataFrame]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.  NodeReturn object takes
        2 parameters:
        - tables_to_upload: dict[str, pd.DataFrame]
            keys are table names, values are pandas DataFrames to upload
        - files_to_upload: dict[str, bytes]
            keys are file names, values are file data to upload

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/GanymedeClass
    """
    g = Ganymede(ganymede_context)

    run_id = g.flow_run_id
    df_files = g.list_files(flow_input_or_output="input", current_run_id=run_id)

    files_dict = g.retrieve_files(
        df_files["file_name"].tolist(), run_id=run_id, use_full_path=False
    )

    file_name, file_content = list(files_dict.items())[0]
    file_content = json.loads(file_content)

    dfs_out = {}

    if file_content["application"] == "qPCR":
        dfs_out["modular_app_qPCR_templates"] = qpcr_template_to_dataframe(file_content).assign(
            template_file=file_name
        )

        protocol_run_id = str(dfs_out["modular_app_qPCR_templates"]["protocol_run_id"].values[0])

        eln_results = g.retrieve_sql(
            f"SELECT COALESCE(eln_id, '') AS eln FROM qpcr_run_metadata WHERE __run_id = '{protocol_run_id}' LIMIT 1"
        )
        eln = eln_results["eln"].values[0] if not eln_results.empty else "N/A"

        df_qpcr = qpcr_template_qpcr_analysis_to_dataframe(file_content)

        if df_qpcr is not None:
            dfs_out["modular_app_qPCR_analysis"] = df_qpcr

        df_curve_fitting = qpcr_template_qpcr_curve_fitting_to_dataframe(file_content)

        if df_curve_fitting is not None:
            dfs_out["modular_app_qPCR_curve_fitting"] = df_curve_fitting

        for key, val in dfs_out.items():
            val.columns = val.columns.str.lower()
            dfs_out[key] = val.assign(__run_id=run_id, protocol_run_id=protocol_run_id, eln=eln)

    return NodeReturn(tables_to_upload=dfs_out, if_exists="append")