def test_pytest_boots():
    # If this runs, your compose.test.yml + test-runner.Dockerfile is wired
    assert True

def test_can_import_dlt():
    import dlt
    assert getattr(dlt, "__version__", None) is not None

"""
Verification tests to ensure dlt_server_app environment is ready.
- Imports key dependencies
- Confirms DuckDB works
- Runs a tiny DLT -> DuckDB pipeline
"""

import os


def test_imports():
    """All critical packages import cleanly."""
    print("Checking imports...")
    import dlt
    print(f"✓ dlt imported (v{dlt.__version__})")

    import sqlglot
    print(f"✓ sqlglot imported (v{sqlglot.__version__})")

    import duckdb as _duckdb
    print("✓ duckdb imported")

    import pandas as _pd
    import numpy as _np
    print("✓ pandas & numpy imported")

    import sqlalchemy as _sa
    print(f"✓ SQLAlchemy imported (v{_sa.__version__})")

    import pydantic as _pyd
    print(f"✓ pydantic imported (v{_pyd.__version__})")

    import requests as _req
    print("✓ requests imported")

    import pytest as _pytest
    print(f"✓ pytest imported (v{_pytest.__version__})")

    # quick sqlglot parse sanity (catches previous UNION/Datatype issues)
    from sqlglot import parse_one
    assert parse_one("SELECT 1").sql().upper() == "SELECT 1"
    print("✓ sqlglot basic parsing works")


def test_duckdb_in_memory():
    """DuckDB can execute basic SQL."""
    import duckdb

    con = duckdb.connect(":memory:")
    con.execute("create table t(a int)")
    con.execute("insert into t values (1), (2)")
    cnt = con.execute("select count(*) from t").fetchone()[0]
    assert cnt == 2
    print("✓ DuckDB :memory: create/insert/select works")
    con.close()


# def test_dlt_minimal_pipeline_duckdb(tmp_path):
#     """
#     Run a tiny DLT pipeline writing two rows into a local DuckDB file.
#     Verifies rowcount via DuckDB afterwards.
#     """
#     import dlt
#     import duckdb
#     from sqlglot import parse_one

#     # keep pipeline isolation local & writable
#     pipelines_dir = tmp_path / "pipelines"
#     pipelines_dir.mkdir(parents=True, exist_ok=True)
#     db_path = tmp_path / "verify.duckdb"

#     # Create destination spec. Prefer typed destination to pass a file path.
#     try:
#         from dlt.destinations import duckdb as dlt_duckdb

#         # Most DLT versions accept Credentials(database=...)
#         try:
#             creds = dlt_duckdb.Credentials(database=str(db_path))
#             destination = dlt_duckdb(credentials=creds)
#         except Exception:
#             # Fallback to passing raw string (some versions coerce this)
#             destination = dlt_duckdb(credentials=str(db_path))
#     except Exception as e:
#         # If for some reason duckdb destination is unavailable, skip gracefully
#         import pytest
#         pytest.skip(f"DuckDB destination unavailable in this dlt build: {e}")
#         return

#     pipeline = dlt.pipeline(
#         pipeline_name="setup_check",
#         destination=destination,
#         dataset_name="setup_ds",
#         pipelines_dir=str(pipelines_dir),
#     )

#     # Tiny in-memory resource
#     rows = [{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}]

#     # Should not raise; returns LoadInfo
#     load_info = pipeline.run(rows, table_name="items")
#     assert load_info is not None
#     print(f"✓ DLT pipeline ran (loads: {load_info.loads_ids})")

#     # Verify rows landed — DLT uses <schema>__<table> naming on DuckDB
#     con = duckdb.connect(str(db_path))
#     # Confirm the table exists by listing and looking for our table
#     tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
#     print(f"Tables in DuckDB: {tables}")
#     # Try both possible namings
#     candidates = ["items", "setup_ds__items"]
#     existing = [t for t in candidates if t in tables]
#     assert existing, "Loaded table not found in DuckDB"
#     table_name = existing[0]

#     cnt = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
#     assert cnt == 2, f"Expected 2 rows, found {cnt}"
#     print("✓ Verified 2 rows in DuckDB via DLT load")
#     con.close()
