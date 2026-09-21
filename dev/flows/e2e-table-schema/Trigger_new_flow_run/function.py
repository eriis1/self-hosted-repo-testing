from io import BytesIO

import pandas as pd
from ganymede_sdk import GanymedeContext
from ganymede_sdk.io import FlowInputFile, FlowInputParam, Tag, FlowInputs  # noqa: F401


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> tuple[str | None, FlowInputs | None]:

    return "e2e-table-schema-subset", FlowInputs()



