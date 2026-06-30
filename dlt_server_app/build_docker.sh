#!/bin/bash

echo "Building DLT Docker image..."

# Build the DLT container
docker build -f Dockerfile.dlt -t open-data-pipeline-dlt-task-image .

echo "DLT Docker image built successfully!"
echo "You can now run it with:"
echo "docker run --rm open-data-pipeline-dlt-task-image python dlt_runner.py <job_id> <user_id> <schedule_id> <run_id> <service_type>"
