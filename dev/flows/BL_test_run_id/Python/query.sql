SELECT * FROM BL_test_CSV_Read_results
WHERE __run_id = "{{run_id}}";
SELECT * FROM BL_test_CSV_Read_results
WHERE __run_id_old = FORMAT_TIMESTAMP("%Y-%m-%dT%R:%E6S", TIMESTAMP_MILLIS({{run_id}}));