# dlt_server_app/tests/test_dlt_runner.py
import logging
import os
import sys
import subprocess
from pathlib import Path
from types import SimpleNamespace
from bson import ObjectId
from pymongo import MongoClient

REPO_ROOT = Path(__file__).resolve().parents[2]  # -> /workspace
RUNNER_PATH = REPO_ROOT / "dlt_server_app" / "dlt_runner.py"

def _mongo():
    host = os.getenv("MONGO_HOST", "localhost")
    return MongoClient(f"mongodb://{host}:27017/", serverSelectionTimeoutMS=2000)

def _seed_schedule(schedule_id_hex: str, code: str):
    """Insert/overwrite a minimal schedule doc with inline 'code'."""
    client = _mongo()
    db = client["user_sessions"]
    coll = db["schedule"]
    _id = ObjectId(schedule_id_hex)
    coll.delete_one({"_id": _id})
    coll.insert_one({
        "_id": _id,
        "user_id": "pytest-user",
        "chat_id": "pytest-chat",
        "schedule_name": "pytest-schedule",
        "code": code,
        "pipeline": [],
        "next": []
    })
    return client  # so caller can optionally clean up

def _run_runner(job_id: str, user_id: str, schedule_id: str, run_id: str, mode: str = "code"):
    """Invoke dlt_runner as a separate process to mimic real usage."""
    env = os.environ.copy()
    # In case helper libs were installed as editable or need PYTHONPATH
    env.setdefault("PYTHONPATH", str(REPO_ROOT))
    cmd = [sys.executable, str(RUNNER_PATH), job_id, user_id, schedule_id, run_id, mode]
    return subprocess.run(cmd, cwd=str(REPO_ROOT), text=True, capture_output=True)

def test_runner_executes_print_hi(tmp_path):
    """Smoke test: runner executes inline user code that prints 'Hi'."""
    schedule_id = "65cb43f2007a5f38718b9e01"  # any valid 24-char hex
    _seed_schedule(schedule_id, 'print("Hi")')

    res = _run_runner("job-hi", "user-hi", schedule_id, "run-hi", "code")
    # If it fails, include stdout/stderr in assertion message
    assert res.returncode == 0, f"stdout:\n{res.stdout}\n\nstderr:\n{res.stderr}"
    # Accept either stdout or stderr (logging handlers may mix)
    output = (res.stdout + "\n" + res.stderr).lower()
    assert "hi" in output, f"'Hi' not found in output:\n{res.stdout}\n{res.stderr}"

def test_runner_executes_duckdb_pipeline(tmp_path):
    """End-to-end: runner executes DLT → DuckDB pipeline and writes a DB file."""
    duck_path = "/app/data/runner_test.duckdb"
    # Use a unique run id so the log file path is unique as well
    run_id = "run-duck"

    # Minimal DLT code that writes one row to a DuckDB file under /app/data
    # and stores state under /app/.dlt (matching your runner defaults).
    dlt_code = f'''
import dlt
pipe = dlt.pipeline(
    pipeline_name="runner_test",
    destination=dlt.destinations.duckdb("{duck_path}"),
    dataset_name="runner_ds",
    pipelines_dir="/app/.dlt",
    progress="log",
)
rows = [{{"id": 1, "name": "Ada"}}]
info = pipe.run(rows, table_name="people", write_disposition="replace")
print("DONE", info.loads_ids)
'''

    schedule_id = "65cb43f2007a5f38718b9e02"
    _seed_schedule(schedule_id, dlt_code)

    res = _run_runner("job-duck", "user-duck", schedule_id, run_id, "code")
    assert res.returncode == 0, f"stdout:\n{res.stdout}\n\nstderr:\n{res.stderr}"

    # Verify the DuckDB file was created and is non-empty
    duck_file = Path(duck_path)
    assert duck_file.exists(), f"DuckDB file not found: {duck_file}"
    assert duck_file.stat().st_size > 0, f"DuckDB file is empty: {duck_file}"

    # Verify a log file was produced by the runner
    log_file = Path("/app/logs") / f"dlt_run_{run_id}.log"
    assert log_file.exists(), f"Expected log file not found: {log_file}"


def test_pipeline_mode_uses_chat_config(monkeypatch):
    """Pipeline mode pulls chat config and passes it to MigrationEngine."""
    from dlt_server_app import dlt_runner
    schedule_id_obj = ObjectId()
    job_id = str(ObjectId())
    user_id = "user-pipeline"
    schedule_id = str(schedule_id_obj)
    run_id = "run-pipeline"

    source_conn_id = "691ec96bab28b704165df87e"
    dest_conn_id = "691ecb06450f3ce4e011ff67"

    schedule_doc = {
        "_id": schedule_id_obj,
        "pipeline": [
            {
                "function": "data_migration",
                "mode": "replace",
                "source_parameters": {
                    "connection_id": source_conn_id,
                    "table_name": "public.actor_src",
                },
                "destination_parameters": {
                    "connection_id": dest_conn_id,
                    "table_name": "public.actor_target",
                },
                "primary_key": "actor_id",
                "migration_type": "table-to-table",
            }
        ],
    }

    def _connection_doc(hex_id, host):
        return {
            "_id": ObjectId(hex_id),
            "type": "postgres",
            "connection_details": {
                "host": host,
                "port": 5432,
                "database": f"{host}_db",
                "username": f"{host}_user",
                "password": "secret",
            },
        }

    source_conn_doc = _connection_doc(source_conn_id, "source-host")
    dest_conn_doc = _connection_doc(dest_conn_id, "dest-host")

    class FakeCollection:
        def __init__(self, docs):
            self.docs = docs

        def get_by_id(self, _id):
            doc = self.docs.get(_id) or self.docs.get(str(_id))
            return True, doc

    monkeypatch.setattr(
        dlt_runner,
        "mongo_schedule",
        FakeCollection({schedule_id_obj: schedule_doc, schedule_id: schedule_doc}),
    )
    monkeypatch.setattr(
        dlt_runner,
        "mongo_connections",
        FakeCollection(
            {
                ObjectId(source_conn_id): source_conn_doc,
                source_conn_id: source_conn_doc,
                ObjectId(dest_conn_id): dest_conn_doc,
                dest_conn_id: dest_conn_doc,
            }
        ),
    )

    monkeypatch.setattr(dlt_runner, "MIGRATION_ENGINE_AVAILABLE", True)

    monkeypatch.setattr(
        dlt_runner, "configuration", SimpleNamespace(get=lambda _sid: {})
    )

    class DummyJobArguments:
        def __init__(self, config):
            self._config = config

        def get(self):
            return self._config

    monkeypatch.setattr(dlt_runner, "JobArguments", DummyJobArguments)

    captured = {}

    class FakeMigrationEngine:
        def __init__(self, logger=None):
            self.logger = logger

        def migrate(self, **kwargs):
            captured.update(kwargs)
            return {"success": True, "duration_seconds": 0.1}

        def cleanup(self):
            captured["cleanup_called"] = True

    monkeypatch.setattr(dlt_runner, "MigrationEngine", FakeMigrationEngine)

    runner = object.__new__(dlt_runner.DLTRunner)
    runner.job_id = job_id
    runner.user_id = user_id
    runner.schedule_id = schedule_id
    runner.run_id = run_id
    runner.logger = logging.getLogger("pipeline-test")

    success = runner.execute_pipeline_mode(config={})

    assert success is True
    assert captured["source_table"] == "actor_src"
    assert captured["destination_table"] == "actor_target"
    assert captured["source_schema"] == "public"
    assert captured["destination_schema"] == "public"
    assert captured["mode"] == "replace"
    assert captured["primary_key"] == "actor_id"
    assert captured["source_connection"]["host"] == "source-host"
    assert captured["destination_connection"]["host"] == "dest-host"
    assert captured["cleanup_called"] is True
