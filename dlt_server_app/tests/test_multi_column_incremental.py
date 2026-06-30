import pytest
import os
import dlt
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from unittest.mock import patch, MagicMock
from migrations.migration_engine import MigrationEngine

def test_multi_column_incremental(tmp_path):
    # 1. Create a source SQLite engine
    src_engine = create_engine("sqlite:///:memory:", future=True)
    metadata = MetaData()
    src_table = Table(
        "test_table",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("col1", String),
        Column("col2", Integer)
    )
    metadata.create_all(src_engine)

    # Insert initial rows
    with src_engine.begin() as conn:
        conn.execute(
            src_table.insert(),
            [
                {"id": 1, "col1": "A", "col2": 10},
                {"id": 2, "col1": "A", "col2": 20},
                {"id": 3, "col1": "B", "col2": 5},
            ]
        )

    # 2. Setup MigrationEngine and patch internal methods to run in-memory SQLite to DuckDB
    engine = MigrationEngine()
    
    dummy_connection = {
        "db_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "test",
        "username": "user",
        "password": "pwd"
    }

    # Patch sqlalchemy destination to use native duckdb destination for the test pipeline
    duckdb_dest = dlt.destinations.duckdb(f"{tmp_path}/test_db.duckdb")

    with patch.object(engine, "_sa_engine", return_value=src_engine), \
         patch.object(engine, "_build_connection_string", return_value="sqlite:///:memory:"), \
         patch.object(engine, "_determine_data_dir", return_value=str(tmp_path)), \
         patch("dlt.destinations.sqlalchemy", return_value=duckdb_dest):
        
        # First migration run
        result = engine.migrate(
            source_connection=dummy_connection,
            source_table="test_table",
            source_schema=None,
            destination_connection=dummy_connection,
            destination_table="target_table",
            mode="append",
            increment_key=["col1", "col2"],
            pipeline_name="test_pipeline_multi_inc",
            pipelines_dir=str(tmp_path)
        )
        assert result["success"] is True
        assert result["rows_migrated"] == 3

        # Seed more rows in source SQLite
        with src_engine.begin() as conn:
            conn.execute(
                src_table.insert(),
                [
                    {"id": 4, "col1": "A", "col2": 15}, # less than ("B", 5) -> should be filtered
                    {"id": 5, "col1": "B", "col2": 4},  # less than ("B", 5) -> should be filtered
                    {"id": 6, "col1": "B", "col2": 10}, # greater than ("B", 5) -> should be loaded
                    {"id": 7, "col1": "C", "col2": 1},  # greater than ("B", 5) -> should be loaded
                ]
            )

        # Second migration run
        result2 = engine.migrate(
            source_connection=dummy_connection,
            source_table="test_table",
            source_schema=None,
            destination_connection=dummy_connection,
            destination_table="target_table",
            mode="append",
            increment_key=["col1", "col2"],
            pipeline_name="test_pipeline_multi_inc",
            pipelines_dir=str(tmp_path)
        )
        assert result2["success"] is True
        assert result2["rows_migrated"] == 2
