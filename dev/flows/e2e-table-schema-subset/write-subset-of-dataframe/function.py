import pandas as pd                                                                             
from ganymede_sdk import GanymedeContext                                                        
from ganymede_sdk.io import NodeReturn


def execute(
  df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:

  df = pd.DataFrame({
      "name": [str(ganymede_context.run_id)],
      "age": [0],
      "score": [0.0],
  })

  return NodeReturn(
      tables_to_upload={"e2e_table_schema_CSV_Read_results": df},
      if_exists="append",
  )

