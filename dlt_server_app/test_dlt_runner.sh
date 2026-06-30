#!/bin/bash

echo "Testing DLT Runner..."

# Get the absolute path to the current directory
CURRENT_DIR=$(pwd)

# Test with sample parameters
docker run --rm \
    -v "$CURRENT_DIR/airflow/dlt/dlt_data:/app/data" \
    -v "$CURRENT_DIR/airflow/dlt/dlt_state/test_schedule:/app/.dlt" \
    open-data-pipeline-dlt-task-image \
    python dlt_runner.py test_job test_user test_schedule test_run_001 dts

echo "Test completed. Check logs in ./airflow/dlt/dlt_data/logs/"
