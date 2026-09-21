import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext

from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    df_sql_result = copy.deepcopy(df_sql_result)

    g = Ganymede(ganymede_context)
    
    if g.flow_run_id not in df_sql_result["Flowrun"].values:
        g.retrieve_sql(
            f"INSERT INTO test_flow_retry (Flowrun, Retries) VALUES ('{g.flow_run_id}', 1)"
        )
        raise GanymedeException(message="Retry 1", exception_type="Validation")
    
    # Get the retry value for this flow_run_id
    retry = df_sql_result.loc[df_sql_result["Flowrun"] == g.flow_run_id, "Retries"].iloc[0]
    
    if retry < 2:
        g.retrieve_sql(
            f"UPDATE test_flow_retry SET Retries = Retries + 1 WHERE Flowrun = '{g.flow_run_id}'"
        )
        raise GanymedeException(message=f"Retry {retry + 1}", exception_type="Validation")


    return NodeReturn()

