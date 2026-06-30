# DLT Server Application

The `dlt_server_app` is the one of the engines for executing data pipelines and migrations within the Ask On Data ecosystem. It acts as a bridge between scheduled Airflow jobs and the underlying data sources/destinations. It supports running custom Python/DLT scripts as well as executing pre-configured, scalable data migration pipelines (including CDC, full loads, and flat-file processing).

## Core Execution Flow

When a task is triggered, the execution follows this lifecycle:

1. **Initialization**: The main entry point (`dlt_runner.py`) is invoked with specific identifiers (`job_id`, `user_id`, `schedule_id`, `run_id`). It sets up structured logging and local workspaces (data, state, and logs directories).
2. **Configuration Loading**: Connection details, pipeline settings, and custom code are fetched securely from MongoDB collections (`chats`, `connections`, `schedule`).
3. **Execution Modes**: The runner supports different execution types:
   - **Code Mode (`code`)**: Fetches custom user-defined code from the database and executes it dynamically. The script runs in an isolated global scope populated with necessary SDK tools (`MigrationEngine`, `Connection`, `ReadOrWriteFiles`, etc.).
   - **Pipeline/Migration Mode (`pipeline` or `migration`)**: Extracts structured migration configurations (source/destination tables, mapping, CDC increment keys) and relies on the `MigrationEngine` to perform the data movement automatically. It handles different ingestion modes (`append`, `replace`, `merge`).
4. **Audit and Tracking**: During execution, the `AuditTracker` monitors resource usage. Upon completion, the engine logs the migration outcome (success/failure, row counts, execution time) into the `dms_schedule_progress` collection for real-time tracking in the UI.
5. **Cleanup**: Releases resources, closes connections, and cleans up temporary state files.

## Directory Structure

```text
dlt_server_app/
├── Dockerfile.dlt           # Docker container definition
├── requirements.txt         # Python dependencies
├── dlt_runner.py            # Main entry point
├── __init__.py              # Python package marker
├── dlt_server/              # DLT server core modules (configurations, connectors, models, etc.)
├── migrations/              # Migration scripts and engines
├── pipelines/               # Pipeline templates
│   ├── __init__.py
│   └── cdc_template.py      # Sample CDC template
├── tests/                   # Application test suite
├── build_docker.sh          # Docker build script
├── test_dlt_runner.sh       # Script to test DLT runner locally
├── test_migration_engine.py # Migration engine test script
└── README.md                # This file
```

## Setup Instructions

1. **Build the Docker image:**
   ```bash
   ./build_docker.sh
   ```

2. **Test the setup:**
   ```bash
   ./test_dlt_runner.sh
   ```

## Volume Mapping

The application uses the following volume mappings:
- `./airflow/dlt/dlt_data` → `/app/data` (logs and temporary files)
- `./airflow/dlt/dlt_state/{schedule_id}` → `/app/.dlt` (DLT state per schedule)

## Usage

The DLT runner is called from Airflow with the following parameters:
- `job_id`: Unique identifier for the job
- `user_id`: User who created the job
- `schedule_id`: Schedule identifier
- `run_id`: Unique run identifier
- `execution_type`: Type of execution (`code`, `pipeline`, or `migration`)
- `service_type` (optional): Service calling the runner (defaults to `dts`)

Example:
```bash
python dlt_runner.py job123 user456 schedule789 run001 pipeline dts
```
