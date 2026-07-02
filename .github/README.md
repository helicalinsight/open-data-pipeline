# OpenDataPipeline

[OpenDataPipeline](https://app.askondata.com/) is an open-source platform that empowers data engineers and analysts to intuitively move, transform, and schedule data using AI.

## Get started

The easiest way to get started with OpenDataPipeline is by using our managed production instance at [opendatapipeline.com](https://app.askondata.com/).

If you prefer to host it yourself, OpenDataPipeline can be set up locally using Docker. Our local setup spins up an Airflow webserver, a Spark cluster, and MongoDB — everything you need for robust data operations.

To set up OpenDataPipeline locally:

\# Note: The commands assume you are in the root folder of cloned repository.

1. **Prerequisites**: Ensure you have [Docker](https://www.docker.com/) (v24+) and [Node.js](https://nodejs.org/) (v18+) installed.

2. **Build the Frontend (FE)**:
   Before deploying the containers, compile the frontend application:
   ```bash
   cd client
   export REACT_APP_SERVER_ENVIRONMENT="dev"
   # Note: (Optional) Ask the administrator for the REACT_APP_CLIENT_ID if Google OAuth is required
   export REACT_APP_CLIENT_ID=""
   npm install --force
   CI=false npm run build
   cd ..
   ```
   This compiles the React assets into `client/build/` and generates the entry template at `templates/index.html`.

3. **Configure Environment Variables**:
   Copy `docker/.env.example` to `docker/.env` 
   `cp docker/.env.example docker/.env`

4. **Assemble the Environment & Start Services**:
   Run the following commands from the root of the cloned repository to set up the container directories and launch Docker Compose:
   ```bash
   # Define deployment base path (using $HOME ensures proper expansion in double quotes)
   DEPLOY_BASE="$HOME/odp-local-setup"
   SETUP_PATH="$DEPLOY_BASE/opendatapipeline"

   mkdir -p "$SETUP_PATH"

   # 1. Copy shared dependencies to base folder
   cp -r odp_code_context "$DEPLOY_BASE/odp_code_context"
   cp -r audit_tracker "$DEPLOY_BASE/audit_tracker"
   cp -r core "$DEPLOY_BASE/core"

   # 2. Copy application components to setup path
   cp -r opendatapipeline/src "$SETUP_PATH/opendatapipeline_src"
   cp opendatapipeline/requirements.txt "$SETUP_PATH/opendatapipeline_src/requirements.txt"
   cp opendatapipeline/pyproject.toml "$SETUP_PATH/opendatapipeline_src/pyproject.toml"
   cp opendatapipeline/setup.cfg "$SETUP_PATH/opendatapipeline_src/setup.cfg"
   cp opendatapipeline/setup.py "$SETUP_PATH/opendatapipeline_src/setup.py"
   cp -r airflow "$SETUP_PATH/airflow"
   cp -r spark_server_app "$SETUP_PATH/spark_server_app"
   cp -r dlt_server_app "$SETUP_PATH/dlt_server_app"
   cp -r opendatapipeline/hadoop_local "$SETUP_PATH/hadoop_local"
   cp -r opendatapipeline/inbuilt_modules "$SETUP_PATH/inbuilt_modules"
   cp -r docker/opendatapipeline "$SETUP_PATH/opendatapipeline"

   # 3. Copy Frontend (FE) build and templates
   mkdir -p "$SETUP_PATH/opendatapipeline_src/api/static/react"
   cp -r client/build/. "$SETUP_PATH/opendatapipeline_src/api/static/react"
   cp -r templates "$SETUP_PATH/opendatapipeline_src/api/templates"

   # 4. Copy configuration and Docker files
   cp docker/.env "$SETUP_PATH/.env"
   cp docker/docker-compose.yml "$SETUP_PATH/docker-compose.yml"
   cp docker/airflow_docker.Dockerfile "$SETUP_PATH/airflow_docker.Dockerfile"

   # 5. Prepare Airflow DAGs directory structure
   mkdir -p "$SETUP_PATH/opendatapipeline/data/airflow"
   cp -r airflow/dags "$SETUP_PATH/opendatapipeline/data/airflow/dags"

   # 6. Build and start services
   cd "$SETUP_PATH"
   docker compose --profile dev build --no-cache
   docker compose --profile dev up -d
   ```

5. **Verify the Setup**:
   Monitor the container health status:
   ```bash
   watch docker ps
   ```
   Once all containers are healthy, access the application at `https://localhost`.

---

## Developer / Admin Tips

### Restart Server Automatically After File Changes (Hot Reload)
To enable automatic reloading during backend development:
1. Open the file `opendatapipeline_src/run.py` inside your setup directory (e.g. `$SETUP_PATH/opendatapipeline_src/run.py`).
2. Add `'--reload',` immediately after `'gunicorn'` in the command arguments.

### Grant Admin Access Locally
To assign the `admin` role to a local user:
1. Find your MongoDB primary container name (e.g., `docker ps | grep mongo_primary`).
2. Open a shell inside the container:
   ```bash
   docker exec -it <container_name> bash
   ```
3. Connect to the MongoDB shell:
   ```bash
   mongosh --username askondata --port 27021 --authenticationDatabase user_sessions
   ```
   *(Password is `askondata`)*
4. Run the update command in the database shell:
   ```javascript
   use user_sessions
   db.users.updateOne({ email: "your_email@example.com" }, { $set: { role: "admin" } })
   ```

### Check Logs
You can inspect the application logs at:
- `$SETUP_PATH/opendatapipeline/logs/askondata`

---

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
- **Data Compute**: Apache Spark
- **Metadata Storage**: MongoDB and PostgreSQL.

## Documentation

For a deep dive into OpenDataPipeline's architecture and capabilities, check out our technical knowledge hubs in [usage documentation](https://app.askondata.com/api/v1/doc)

## Contributing

We welcome contributions to OpenDataPipeline! Whether it's adding new data sources, improving the AI transformation engine, or fixing bugs, your help is appreciated. 

Feel report any bugs or feature in [Issues](https://github.com/helicalinsight/open-data-pipeline/issues).
