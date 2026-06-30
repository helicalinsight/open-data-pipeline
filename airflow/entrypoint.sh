#!/bin/bash

echo "Starting Airflow initialization..."

# Initialize Airflow database
echo "Initializing Airflow database..."
airflow db init

# Create Airflow user
echo "Creating Airflow user..."
airflow users create \
  --role Admin \
  --username ${AIRFLOW_USERNAME:-askondata} \
  --password ${AIRFLOW_PASSWORD:-askondata} \
  --email test@askondata.com \
  --firstname askondata \
  --lastname askondata

# Install dependencies
echo "Installing dependencies..."
pip install -r /airflow/requirements.txt

# Set an environment variable (example)
echo "Setting environment variable..."
export MY_ENV_VAR="some_value"

echo "Initialization complete. MY_ENV_VAR is set to $MY_ENV_VAR"

# Keep the container running (for debugging purposes)
exec "$@"