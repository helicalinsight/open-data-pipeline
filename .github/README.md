# OpenDataPipeline

[OpenDataPipeline](https://askondata.com/) is an open-source platform that empowers data engineers and analysts to intuitively move, transform, and schedule data using AI.

## Get started

The easiest way to get started with OpenDataPipeline is by using our managed production instance at [opendatapipeline.com](https://app.askondata.com/).

If you prefer to host it yourself, OpenDataPipeline can be set up locally using Docker. Our local setup spins up an Airflow webserver, a Spark cluster, and MongoDB — everything you need for robust data operations.

To set up OpenDataPipeline locally:
1. Ensure you have [Docker](https://www.docker.com/) (v24+) installed.
2. OpenDataPipeline requires a specific directory structure for its containers. Run the following script from the root of the cloned repository to assemble the environment and start the services:

```bash
# Define deployment path
DEPLOY_BASE="~/odp-local-setup"
SETUP_PATH="$DEPLOY_BASE/opendatapipeline"

mkdir -p "$SETUP_PATH"

# 1. Copy shared dependencies to base folder
cp -r odp_code_context "$DEPLOY_BASE/odp_code_context"
cp -r audit_tracker "$DEPLOY_BASE/audit_tracker"
cp -r core "$DEPLOY_BASE/core"

# 2. Copy application components to setup path
cp -r opendatapipeline/src "$SETUP_PATH/opendatapipeline_src"
cp -r airflow "$SETUP_PATH/airflow"
cp -r spark_server_app "$SETUP_PATH/spark_server_app"
cp -r dlt_server_app "$SETUP_PATH/dlt_server_app"
cp -r opendatapipeline/hadoop_local "$SETUP_PATH/hadoop_local"
cp -r inbuilt_modules "$SETUP_PATH/inbuilt_modules"
cp -r docker/opendatapipeline "$SETUP_PATH/opendatapipeline"

# 3. Copy configuration and docker files
# TODO: instructions to be added to create .env file from .env.example
cp docker/.env "$SETUP_PATH/.env"
cp docker/docker-compose.yml "$SETUP_PATH/docker-compose.yml"
cp docker/airflow_docker.Dockerfile "$SETUP_PATH/airflow_docker.Dockerfile"

# 4. Prepare Airflow DAGs directory structure
mkdir -p "$SETUP_PATH/opendatapipeline/data/airflow"
cp -r airflow/dags "$SETUP_PATH/opendatapipeline/data/airflow/dags"

# 5. Build and start services
cd "$SETUP_PATH"
# Start main pipeline services
docker compose --profile dev --env-file .env build --no-cache
docker compose --profile dev --env-file .env up -d
```
3. You can open localhost:3000 to access the OpenDataPipeline.

## Key Features

- **Intuitive Interface**: Easily create, schedule, and manage your data pipelines without writing extensive boilerplate code.
- **Ask AI**: Leverage LLM models (via LangChain) to perform interactive, conversational data transformations.
- **Bring Your Own LLM**: Configure your preferred provider including Ollama, OpenAI, Anthropic, or Google Gemini.
- **Robust EL(T)**: Integrated with [dlt](https://dlthub.com/) to effortlessly load data from messy sources (REST APIs, DBs, files) into well-structured datasets.
- **Scalable Processing**: Built on top of industry-standard big data tools including Apache Airflow for orchestration and Apache Spark for heavy lifting.
- **Flexible Deployment**: Run on a single machine with Docker Compose, or distribute workloads in production using Docker Swarm.

## Architecture

OpenDataPipeline simplifies the modern data stack by unifying:
- **Frontend**: React-based UI for seamless pipeline management.
- **Orchestration**: Apache Airflow scheduler and webserver.
- **Data Compute**: Apache Spark, DLT, Pandas
- **Metadata Storage**: MongoDB

## Documentation

For a deep dive into OpenDataPipeline's architecture and capabilities, check out our technical knowledge hubs in [usage documentation](https://app.askondata.com/api/v1/doc)

## Contributing

We welcome contributions to OpenDataPipeline! Whether it's adding new data sources, improving the AI transformation engine, or fixing bugs, your help is appreciated. 

Feel report any bugs or feature in [Issues](https://github.com/helicalinsight/open-data-pipeline/issues).
