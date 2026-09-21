import pandas as pd                                                                             
from ganymede_sdk import Ganymede, GanymedeContext                                              
from ganymede_sdk.io import NodeReturn                                                          

                                                                                              
def execute(    
  df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:

  g = Ganymede(ganymede_context)

  df = g.retrieve_sql("SELECT * FROM e2e_table_schema_CSV_Read_results")

  expected_columns = {"name", "age", "score", "is_active", "created_date"}
  actual_columns = set(df.columns)

  missing = expected_columns - actual_columns
  if missing:
      raise Exception(f"Missing columns from table: {missing}")

  print(f"All expected columns present: {sorted(expected_columns)}")
  print(f"Actual columns: {sorted(actual_columns)}")
  print(df.head())

  return NodeReturn()