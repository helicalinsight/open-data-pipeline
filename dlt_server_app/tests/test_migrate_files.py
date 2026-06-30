import pytest
import os
import pandas as pd
from unittest.mock import MagicMock, patch
from migrations.migration_engine import MigrationEngine

@pytest.fixture
def temp_csv_file(tmp_path):
    file_path = tmp_path / "test_data.csv"
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"]
    })
    df.to_csv(file_path, index=False)
    return str(file_path)

@patch("dlt.pipeline")
@patch("migrations.migration_engine.MigrationEngine._build_connection_string")
def test_migrate_files_csv(mock_build_conn_string, mock_pipeline, temp_csv_file, caplog):
    mock_build_conn_string.return_value = "postgresql://user:pwd@localhost:5432/testdb"
    
    mock_pipeline_instance = MagicMock()
    mock_pipeline.return_value = mock_pipeline_instance
    
    mock_info = MagicMock()
    mock_info.loads_ids = ["test_load_id"]
    mock_info.has_failed_jobs = False
    mock_pipeline_instance.run.return_value = mock_info
    
    engine = MigrationEngine()
    engine._extract_per_table_row_counts = MagicMock(return_value={"target_table": 3})
    engine._extract_schema_info = MagicMock(return_value={"target_table": {"column_count": 2}})
    engine._determine_data_dir = MagicMock(return_value="/tmp")
    
    dest_connection = {
        "db_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "testdb",
        "username": "user",
        "password": "pwd"
    }

    result = engine.migrate_files(
        file_path=temp_csv_file,
        file_name="test_data",
        file_type="csv",
        destination_connection=dest_connection,
        destination_table="target_table"
    )

    assert result["success"] is True
    assert result["source"] == "test_data"
    assert result["source_db_type"] == "flat_file"
    mock_pipeline.assert_called()
    mock_pipeline_instance.run.assert_called()
