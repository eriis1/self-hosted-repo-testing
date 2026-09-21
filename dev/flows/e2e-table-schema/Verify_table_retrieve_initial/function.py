import os
import sys
from ganymede_sdk import retrieve_tables
from ganymede_sdk.flow_runtime import GanymedeException

os.environ["USE_POSTGRES_TABLE_SCHEMA"] = "true"


def execute(df_sql_result, ganymede_context=None):
    table_name = "e2e_table_schema_CSV_Read_results"
    run_id = ganymede_context.run_id

    dynamic_col = f"Dynamic Col {ganymede_context.flow_run_id}"
    bq_col = f"Dynamic_Col_{ganymede_context.flow_run_id}"
    tables, schema_df = retrieve_tables(
        ganymede_context, table_name, get_measurement_units=True
    )

    if table_name not in tables:
        msg = f"Table '{table_name}' not found in retrieve_tables() response"
        print(msg, file=sys.stderr)
        raise GanymedeException(exception_type="validation", message=msg)

    table_schema = schema_df[schema_df["bq_table_name"] == table_name]
    df = tables[table_name]
    if dynamic_col not in df.columns:                                        
      if bq_col in df.columns:                                             
          raise GanymedeException(                                         
              exception_type="validation",                                 
              message=f"Column '{bq_col}' was not renamed to '{dynamic_col}' — api-server schema stale",                               
          )
      else:                                                                
          raise GanymedeException(
              exception_type="validation",
              message=f"Column '{dynamic_col}' missing entirely",
          )
    
    print(f"Schema columns found: {table_schema['pd_field_name'].tolist()}")
    print(f"Full schema:\n{table_schema.to_string()}")

    expected = {
        "name":         {"unit": f"text_label_{run_id}"},
        "age":          {"unit": f"years_{run_id}"},
        "score":        {"unit": f"points_{run_id}"},
        "is_active":    {"unit": f"flag_{run_id}"},
        "created_date": {"unit": f"date_recorded_{run_id}"},
    }

    errors = []

    for col_name, expected_vals in expected.items():
        col_rows = table_schema[table_schema["pd_field_name"] == col_name]
        if col_rows.empty:
            errors.append(f"Column '{col_name}' not found in schema")
            continue

        actual_unit = col_rows.iloc[0]["unit"]
        if actual_unit != expected_vals["unit"]:
            errors.append(
                f"Column '{col_name}': unit={actual_unit}, expected={expected_vals['unit']}"
            )

    if errors:
        error_msg = "Metadata verification failed:\n" + "\n".join(errors)
        print(error_msg, flush=True)
        print(error_msg, file=sys.stderr, flush=True)
        raise GanymedeException(exception_type="validation", message=error_msg)

    print(f"All metadata verified successfully for run_id={run_id}!")
    print(f"Columns checked: {list(expected.keys())}")
    for col_name in expected:
        col_row = table_schema[table_schema["pd_field_name"] == col_name].iloc[0]
        print(f"  {col_name}: unit={col_row['unit']}")


