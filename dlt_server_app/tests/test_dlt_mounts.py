
import os
import shutil
import duckdb
import dlt
import glob

def test_dlt_mounts_and_state():
   
    DUCKDB_PATH = "/app/data/mounts_simple.duckdb"     # should be mounted to repo's airflow/dlt/dlt_data
    PIPELINES_DIR = "/app/.dlt"                        # should be mounted to repo's airflow/dlt/dlt_state
    PIPELINE_NAME = "mounts_simple"
    DATASET = "mount_ds"
    TABLE = "people"

     # --- clean any prior artifacts for a deterministic test run ---
    if os.path.exists(DUCKDB_PATH):
        os.remove(DUCKDB_PATH)

    pipeline_state_dir = os.path.join(PIPELINES_DIR, "pipelines", PIPELINE_NAME)
    if os.path.isdir(pipeline_state_dir):
        shutil.rmtree(pipeline_state_dir)

    # --- run a tiny DLT pipeline that writes one row to DuckDB ---
    pipe = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination = dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name = DATASET,
        pipelines_dir = PIPELINES_DIR,
        progress = "log",
    )

    rows = [{"id": 1, "name": "Ada"}]
    info = pipe.run(rows, table_name=TABLE, write_disposition="replace")

    # --- assert DuckDB file exists in the mounted location ---
    assert os.path.exists(DUCKDB_PATH), f"DuckDB file not found at {DUCKDB_PATH}"

    # --- query DuckDB to confirm data landed where we expect ---
    con = duckdb.connect(DUCKDB_PATH)
    schemas = con.execute("SELECT schema_name FROM information_schema.schemata").fetchall()
    assert (DATASET,) in schemas, f"Schema {DATASET} not found in DuckDB"

    tables = con.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema = ?
    """, [DATASET]).fetchall()
    assert (DATASET, TABLE) in tables, f"Table {DATASET}.{TABLE} not found"

    fetched = con.execute(f"SELECT id, name FROM {DATASET}.{TABLE} ORDER BY id").fetchall()
    assert fetched == [(1, "Ada")], f"Unexpected rows: {fetched}"

    # --- assert DLT state exists in the mounted state directory ---
    assert os.path.isdir(PIPELINES_DIR), f"DLT pipelines_dir missing: {PIPELINES_DIR}"

    # --- basic sanity on load info ---
    assert isinstance(info.loads_ids, list) and info.loads_ids, "DLT did not record any loads"


DUCKDB_PATH   = "/app/data/mounts_v114.duckdb"
PIPELINES_DIR = "/app/.dlt"
PIPELINE_NAME = "mounts_v114"
DATASET       = "mount_ds"
TABLE         = "people"

# This testcase -writes a row to DuckDB at your mounted /app/data.
# verifies the row landed
# checks the state folder and finds a state file
# confirms _dlt_* system tables exist in DuckDB

def _find_state_file(root: str) -> str | None:
    # common names across dlt 1.14+
    for name in ("pipeline_state.json", "state.json"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            return p
    # fallback: any *state*.json
    matches = glob.glob(os.path.join(root, "*state*.json"))
    return matches[0] if matches else None

def test_dlt_mounts_and_state_for_114():
    # Clean previous artifacts
    if os.path.exists(DUCKDB_PATH):
        os.remove(DUCKDB_PATH)

    # remove any prior local state for this pipeline in either layout
    for candidate in (
        os.path.join(PIPELINES_DIR, "pipelines", PIPELINE_NAME),
        os.path.join(PIPELINES_DIR, PIPELINE_NAME),
    ):
        if os.path.isdir(candidate):
            shutil.rmtree(candidate)

    # Run a tiny dlt pipeline
    pipe = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name=DATASET,
        pipelines_dir=PIPELINES_DIR,
        progress="log",
    )
    info = pipe.run([{"id": 1, "name": "Ada"}], table_name=TABLE, write_disposition="replace")

    # DuckDB file exists and contains expected row
    assert os.path.exists(DUCKDB_PATH), f"DuckDB not found at {DUCKDB_PATH}"
    con = duckdb.connect(DUCKDB_PATH)
    rows = con.execute(f"SELECT id, name FROM {DATASET}.{TABLE}").fetchall()
    assert rows == [(1, "Ada")], f"Unexpected rows: {rows}"

    # Accept both possible local-state layouts:
    #   A) /app/.dlt/pipelines/<pipeline_name>/
    #   B) /app/.dlt/<pipeline_name>/
    assert os.path.isdir(PIPELINES_DIR), f"DLT pipelines_dir missing: {PIPELINES_DIR}"

    state_dir = None
    possible_roots = [
        os.path.join(PIPELINES_DIR, "pipelines", PIPELINE_NAME),
        os.path.join(PIPELINES_DIR, PIPELINE_NAME),
    ]
    for p in possible_roots:
        if os.path.isdir(p):
            state_dir = p
            break

    if state_dir is None:
        # Fallback: find any *state*.json that includes the pipeline name in its path
        matches = glob.glob(os.path.join(PIPELINES_DIR, "**", "*state*.json"), recursive=True)
        matches = [m for m in matches if PIPELINE_NAME in m]
        if matches:
            state_dir = os.path.dirname(matches[0])

    # If still not found, show what’s actually there to aid debugging
    if state_dir is None:
        listing = []
        for root, dirs, files in os.walk(PIPELINES_DIR):
            listing.append(f"{root} :: dirs={dirs} files={files}")
        raise AssertionError(
            f"Could not locate local state for pipeline '{PIPELINE_NAME}' under {PIPELINES_DIR}.\n"
            + "\n".join(listing[:200])
        )

    state_file = _find_state_file(state_dir)
    assert state_file and os.path.getsize(state_file) > 0, f"No state file found in {state_dir}"

    # Check system tables exist in DuckDB
    tables = con.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema = ?
    """, [DATASET]).fetchall()
    dlt_tables = {name for (_, name) in tables if name.startswith("_dlt_")}
    assert {"_dlt_loads", "_dlt_pipeline_state", "_dlt_version"}.issubset(dlt_tables), f"Missing _dlt_* tables: {dlt_tables}"

    # Basic sanity on load info
    assert isinstance(info.loads_ids, list) and info.loads_ids, "DLT did not record any loads"
