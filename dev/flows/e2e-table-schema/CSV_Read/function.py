import pandas as pd
from io import BytesIO, StringIO
from typing import Dict
from ganymede_sdk.io import NodeReturn


def execute(csv_file: Dict[str, BytesIO], ganymede_context=None) -> NodeReturn:
    table_name = "e2e_table_schema_CSV_Read_results"
    run_id = ganymede_context.run_id

    # Hard-code CSV data with varying column types
    csv_data = """name,age,score,is_active,created_date
Alice,30,95.5,true,2024-01-15
Bob,25,87.3,false,2024-02-20
Charlie,35,91.0,true,2024-03-10"""

    df = pd.read_csv(StringIO(csv_data), parse_dates=["created_date"])
      # Add a column with a unique name each run — spaces force a BQ rename        
    dynamic_col = f"Dynamic Col {ganymede_context.flow_run_id}"
    df[dynamic_col] = "test_value"      

    # Expected inferred types:
    #   name         -> str/object
    #   age          -> int64
    #   score        -> float64
    #   is_active    -> bool/object
    #   created_date -> datetime64

    tables_to_upload = {table_name: df}

    # Append run_id to units so we can verify this specific run wrote the metadata
    tables_measurement_units = {
        table_name: pd.DataFrame({
            "column_name": ["name", "age", "score", "is_active", "created_date"],
            "unit": [
                f"text_label_{run_id}",
                f"years_{run_id}",
                f"points_{run_id}",
                f"flag_{run_id}",
                f"date_recorded_{run_id}",
            ],
        })
    }

    return NodeReturn(
        tables_to_upload=tables_to_upload,
        if_exists="append",
        tables_measurement_units=tables_measurement_units,
    )


