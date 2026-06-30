### Run backend unit tests inside Docker with debugger and Mongo

Prereqs:
- Docker Desktop/Engine running.
- Repo cloned to WSL
- VS code connected to WSL repo (optional but will be needed when you want to trigger debugger)

Steps:

1) Start the test stack (Mongo + test runner waiting for debugger):

Go to the repo in WSL and run
```bash
sudo docker compose -f docker/compose.test.yml up --build --no-cache --force-recreate
```

This will:
- Start Mongo with auth and a replica set
- Patch `opendatapipeline/src/configurations/config/config-test.ini` to use host `mongo` and username `admin`
- Install dependencies for both `opendatapipeline` and `spark_server_app` projects
- Start the test runner and wait for a debugger on port 5678, then run `pytest` when attached

2) Attach debugger from VS Code/Cursor:

- Use the "Attach to pytest in Docker (debugpy)" launch configuration
- It maps `${workspaceFolder}` to `/workspace` (mounted by compose)

3) Control which tests run:

- Set `PYTEST_ARGS` env before up, or pass inline:

```bash
# Run all tests (both opendatapipeline and spark_server_app)
sudo docker compose -f docker/compose.test.yml up --build

# Run only opendatapipeline tests
sudo PYTEST_ARGS="opendatapipeline/tests" docker compose -f docker/compose.test.yml up --build

# Run only spark_server_app tests
sudo PYTEST_ARGS="spark_server_app/tests" docker compose -f docker/compose.test.yml up --build

# Run specific test files
sudo PYTEST_ARGS="opendatapipeline/tests -k your_test" docker compose -f docker/compose.test.yml up --build
sudo PYTEST_ARGS="spark_server_app/tests/test_main.py" docker compose -f docker/compose.test.yml up --build
```

4) Stop the stack and clean volumes:

```bash
sudo docker compose -f docker/compose.test.yml down -v
```

## Test Suites

### opendatapipeline Tests
- Location: `opendatapipeline/tests/`
- Dependencies: Installed from `opendatapipeline/requirements.txt`

### spark_server_app Tests
- Location: `spark_server_app/tests/`
- Dependencies: PySpark 3.3.3, PyMongo, MongoMock, Pandas, PyYAML
- Includes: Pipeline tests, database connector tests, file operation tests

## Verification

To verify the setup works correctly:

```bash
# Check that all dependencies are installed
sudo docker compose -f docker/compose.test.yml exec test_runner pip list | grep -E "(pyspark|pymongo|mongomock)"

# Test PySpark functionality
sudo docker compose -f docker/compose.test.yml exec test_runner python -c "import pyspark; print('PySpark OK')"

# Run verification script
sudo docker compose -f docker/compose.test.yml exec test_runner python spark_server_app/verify_setup.py
```

Notes:
- Test Mongo credentials: admin/admin, database: user_sessions_test
- `APP_ENVIRONMENT` is set to `test` inside the test runner
- If running on WSL2, ensure Docker is reachable and port 5678 is free
- PySpark tests require Java 11 (automatically installed in Docker)
- Both test suites can run independently or together


