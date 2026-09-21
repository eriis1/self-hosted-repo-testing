import pandas as pd
from typing import Union, List
from ganymede_sdk.io import NodeReturn
from io import BytesIO


def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None
) -> NodeReturn:
    # remove fields that do not contain well measurements
    df_wells = df_sql_result[
        ~df_sql_result["field"].isin(["Cycle Nr.", "Time [s]", "Temp. [°C]"])
    ].copy()

    # Demonstrate Pandera
    # excel_schema.validate(df_wells)

    # calculate absorbance difference
    df_wells["run_diff"] = df_wells["run2"] - df_wells["run1"]
    print("a")

    return NodeReturn(
        tables_to_upload={"results": df_wells},
    )
