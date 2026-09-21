SELECT * FROM ganymede_dev.example_results
WHERE __run_id = FORMAT_TIMESTAMP("%Y-%m-%dT%R:%E6S", TIMESTAMP_MILLIS({{run_id}}))
AND __input_file_name = "{{ params['Ingest_Data.csv'] }}"