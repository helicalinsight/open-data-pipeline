# OpenDataPipeline

[OpenDataPipeline](https://askondata.com/) is an open-source platform that empowers data engineers and analysts to intuitively move, transform, and schedule data using AI.

## Get started

The easiest way to get started with OpenDataPipeline is by using our managed production instance at [opendatapipeline.com](https://app.askondata.com/).

If you prefer to host it yourself, OpenDataPipeline can be set up locally using Docker. Our local setup spins up an Airflow webserver, a Spark cluster, and MongoDB — everything you need for robust data operations.

\# Note: The commands assume you are in the root folder of cloned repository.

1. **Prerequisites**: Ensure you have [Docker](https://www.docker.com/) (v24+) and [Node.js](https://nodejs.org/) (v18+) installed.

2. **Run script**: We have created an easy to use script for the local setup, you can run it by `bash ./odp_open_source_local_setup.sh`

A few notes before you run the script:

a.) You can check out the top configurations in the script to provide custom values

b.) Choose your LLM provider, based on your preferences. You can choose from Ollama, OpenAI, Anthropic, or Google Gemini and set API KEY and MODEL in environment variables (by adding at bottom of `docker/.env.example`)
```
You can also configure the LLM provider using the following environment variables:
- `LLM_PROVIDER`: `ollama`, `openai`, `anthropic`, `google`
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: e.g., `gpt-4o`
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `ANTHROPIC_MODEL`: e.g., `claude-3-5-sonnet-20241022`
- `GOOGLE_API_KEY`: Your Gemini API Key
- `GOOGLE_MODEL`: Your Gemini model to use
- `OLLAMA_BASE_URL`: e.g., `http://localhost:11434`
- `OLLAMA_MODEL`: e.g., `openhermes`
- `LLM_TEMPERATURE`: e.g., `0`
- `LLM_MAX_TOKENS`: e.g., `1000`
```

c.) If you want to update environment configurations, you can modify `docker/.env.example` for setting your preferences. The example configurations are ready to use if you don't want to set any custom configurations.

The script should take about 5-20 minutes to run depending on your machine and internet speed.

3. **Verify the Setup**:
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
- **Data Compute**: Apache Spark, DLT, Pandas
- **Metadata Storage**: MongoDB

## Documentation

For a deep dive into OpenDataPipeline's architecture and capabilities, check out our technical knowledge hubs in [usage documentation](https://app.askondata.com/api/v1/doc)

## Contributing

We welcome contributions to OpenDataPipeline! Whether it's adding new data sources, improving the AI transformation engine, or fixing bugs, your help is appreciated. 

Feel report any bugs or feature in [Issues](https://github.com/helicalinsight/open-data-pipeline/issues).
