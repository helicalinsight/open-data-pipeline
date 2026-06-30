import unittest
from unittest.mock import Mock, MagicMock, patch
from dlt_server_app.migrations.migration_engine import MigrationEngine


class TestMigrationEngineHelpers(unittest.TestCase):

    def setUp(self):
        self.engine = MigrationEngine(logger=Mock())

    # _extract_per_table_row_counts

    def test_extract_per_table_row_counts_success(self):
        pipeline = Mock()
        pipeline.pipeline_name = "p1"

        pipeline.last_trace.last_normalize_info.row_counts = {
            "customers": 100,
            "_dlt_state": 1
        }

        result = self.engine._extract_per_table_row_counts(pipeline)
        self.assertEqual(result, {"customers": 100, "_dlt_state": 1})

    def test_extract_per_table_row_counts_none_pipeline(self):
        result = self.engine._extract_per_table_row_counts(None)
        self.assertEqual(result, {})

    def test_extract_per_table_row_counts_missing_trace(self):
        pipeline = Mock()
        pipeline.last_trace = None
        result = self.engine._extract_per_table_row_counts(pipeline)
        self.assertEqual(result, {})

    # _extract_schema_info
    def test_extract_schema_info_success(self):
        pipeline = Mock()
        pipeline.pipeline_name = "p1"

        # row_counts determining tables
        pipeline.last_trace.last_normalize_info.row_counts = {
            "customers": 50,
            "_dlt_state": 1
        }

        # schema
        pipeline.default_schema.tables = {
            "customers": {
                "columns": {
                    "id": {"data_type": "bigint"},
                    "name": {"data_type": "text"}
                }
            },
            "_dlt_state": {
                "columns": {"version": {"data_type": "bigint"}}
            }
        }

        result = self.engine._extract_schema_info(load_info=None, pipeline=pipeline)

        self.assertIn("customers", result)
        self.assertNotIn("_dlt_state", result)  # internal table excluded
        self.assertEqual(result["customers"]["column_count"], 2)
        self.assertEqual(result["customers"]["columns"]["id"], "bigint")

    def test_extract_schema_info_empty(self):
        pipeline = Mock()
        pipeline.last_trace.last_normalize_info.row_counts = {}
        pipeline.default_schema.tables = {}

        result = self.engine._extract_schema_info(None, pipeline)
        self.assertEqual(result, {})

    def test_extract_failure_progress_load_failed(self):
        pipeline = Mock()
        pipeline.last_trace.last_normalize_info.row_counts = {
            "customers": 100
        }

        row_counts, step, schema_info = self.engine._extract_failure_progress(pipeline)

        self.assertEqual(step, "load")
        self.assertEqual(row_counts, {"customers": 100})

    def test_extract_failure_progress_normalize_failed(self):
        pipeline = Mock()
        pipeline.last_trace.last_normalize_info = None
        pipeline.last_trace.last_extract_info = Mock()
        pipeline.last_trace.last_extract_info.table_metrics = {
            "customers": Mock(items_count=40)
        }

        row_counts, step, schema_info = self.engine._extract_failure_progress(pipeline)

        self.assertEqual(step, "normalize")
        self.assertEqual(row_counts, {"customers": 40})

    def test_extract_failure_progress_extract_failed(self):
        pipeline = Mock()
        pipeline.last_trace.last_normalize_info = None
        pipeline.last_trace.last_extract_info = None

        row_counts, step, schema_info = self.engine._extract_failure_progress(pipeline)
        self.assertEqual(step, "extract")
        self.assertEqual(row_counts, {})

    def test_extract_failure_progress_none_pipeline(self):
        row_counts, step, schema_info = self.engine._extract_failure_progress(None)
        self.assertEqual(step, "unknown")  # engine returns unknown for None-case
        self.assertEqual(row_counts, {})

    # _echo_function
    def test_echo_function(self):
        result = self.engine._echo_function(4, 5)
        self.assertEqual(result, {"rows": 4, "cols": 5})

    # _extract_row_count fallback
    def test_extract_row_count(self):
        job1 = Mock(metrics={"rows": 20})
        job2 = Mock(metrics={"rows": 30})

        package = Mock(jobs=[job1, job2])
        info = Mock(load_packages=[package])

        result = self.engine._extract_row_count(info)
        self.assertEqual(result, 50)

    def test_extract_row_count_no_metrics(self):
        info = Mock(load_packages=[Mock(jobs=[Mock(metrics={})])])
        result = self.engine._extract_row_count(info)
        self.assertEqual(result, 0)

    # Connection string builder tests

    def test_build_postgres_conn_str(self):
        conn = {
            "db_type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "user",
            "password": "pass"
        }

        result = self.engine._build_connection_string(conn)
        self.assertIn("postgresql://user:", result)
        self.assertIn("@localhost:5432/testdb", result)
        
    def test_build_firebird_conn_str(self):
        conn = {
            "db_type": "firebird",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "user",
            "password": "pass"
        }
        result = self.engine._build_connection_string(conn)
        self.assertIn("firebird+firebird://", result)

    @patch("dlt_server_app.migrations.migration_engine.create_engine")
    def test_engine_cache(self, mock_create_engine):
        conn = {
            "db_type": "postgres",
            "host": "h1",
            "port": 5432,
            "database": "db1",
            "username": "u",
            "password": "p"
        }

        self.engine._sa_engine(conn)
        self.engine._sa_engine(conn)

        # create_engine should be called only once
        self.assertEqual(mock_create_engine.call_count, 1)

    # _apply_transformations

    def test_apply_transformations_selection_and_mapping(self):
        mock_resource = Mock()

        def fake_add_map(func):
            mock_transformed = Mock()
            mock_transformed.apply_hints = Mock()
            return mock_transformed

        mock_resource.add_map = fake_add_map

        transformed = self.engine._apply_transformations(
            source=mock_resource,
            column_selection=["id"],
            column_mapping={"id": "new_id"},
            destination_table="dest",
            mode="append",
            primary_key=["id"]
        )

        transformed.apply_hints.assert_called_once()

    @patch("dlt_server_app.migrations.migration_engine.dlt")
    def test_migrate(self, mock_dlt):
        pipeline = Mock()
        pipeline.run.side_effect = Exception("Boom!")
        mock_dlt.pipeline.return_value = pipeline

        src = {"db_type": "postgres", "host": "h", "port": 1,
               "database": "d", "username": "u", "password": "p"}

        with patch.object(self.engine, "_sa_engine", return_value=Mock()):
            result = self.engine.migrate(
                source_connection=src,
                source_table="t",
                destination_connection=src,
                destination_table="t2",
            )

        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("failed_step", result)


if __name__ == "__main__":
    unittest.main()
