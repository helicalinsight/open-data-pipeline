import unittest
from unittest.mock import patch
import os
import shutil
import sys
import io
import contextlib
import duckdb
import pytest

import dlt_server_app.dlt_runner as main

# ---- constants used by the end-to-end test ----
SCHEDULE_ID   = "65cb43f2007a5f38718b9d6c"   
DUCKDB_PATH   = "/app/data/e2e.duckdb"
PIPELINES_DIR = "/app/.dlt"
PIPELINE_NAME = "e2e_pipeline"
SCHEMA        = "e2e_ds"
TABLE         = "entries"

class TestDLTRunnerMain(unittest.TestCase):
    @patch('sys.argv', ['dlt_runner.py', 'job1', 'user1', '65cb43f2007a5f38718b9d6c', 'run1', 'code'])
    def test_main_code_success(self):
        """
        Test successful execution of main() with 'code' execution type.
        
        Verifies that when DLTRunner.run() returns True, main() exits with code 0.
        Uses mocked DLTRunner methods to simulate successful code execution.
        
        Expected behavior:
        - main() should call sys.exit(0) when runner succeeds
        - DLTRunner.run() and cleanup() methods are properly invoked
        """
        with patch.object(main.DLTRunner, 'run', return_value=True), \
             patch.object(main.DLTRunner, 'cleanup', return_value=None):
            with self.assertRaises(SystemExit) as cm:
                main.main()
            self.assertEqual(cm.exception.code, 0)

    @patch('sys.argv', ['dlt_runner.py', 'job1', 'user1', '65cb43f2007a5f38718b9d6c', 'run1', 'pipeline'])
    def test_main_pipeline_success(self):
        with patch.object(main.DLTRunner, 'run', return_value=True), \
             patch.object(main.DLTRunner, 'cleanup', return_value=None):
            with self.assertRaises(SystemExit) as cm:
                main.main()
            self.assertEqual(cm.exception.code, 0)

    @patch('sys.argv', ['dlt_runner.py'])
    def test_main_missing_args(self):
        # Not enough args -> main() should sys.exit(1)
        with self.assertRaises(SystemExit) as cm:
            main.main()
        self.assertEqual(cm.exception.code, 1)

    @patch('sys.argv', ['dlt_runner.py', 'job1', 'user1', '65cb43f2007a5f38718b9d6c', 'run1', 'code'])
    def test_main_run_failure(self):
        # Simulate failure in DLTRunner.run() -> main() should sys.exit(1)
        with patch.object(main.DLTRunner, 'run', return_value=False), \
             patch.object(main.DLTRunner, 'cleanup', return_value=None):
            with self.assertRaises(SystemExit) as cm:
                main.main()
            self.assertEqual(cm.exception.code, 1)
    
    @patch('sys.argv', ['dlt_runner.py', 'job1', 'user1', '65cb43f2007a5f38718b9d6c', 'run1', 'code'])
    def test_dlt_pipeline_code(self):
        # Pretend the runner succeeded so main() should sys.exit(0)
        with patch.object(main.DLTRunner, 'run', return_value=True), \
             patch.object(main.DLTRunner, 'cleanup', return_value=None):
            with self.assertRaises(SystemExit) as cm:
                main.main()
            self.assertEqual(cm.exception.code, 0)

    # ---------- Real end-to-end test that actually executes the DLT code ----------
    def test_dlt_pipeline_code_e2e(self):
        """
        End-to-end integration test for DLT pipeline execution.
        
        This is a comprehensive test that actually executes the DLT code without
        mocking the runner. It tests the complete workflow from execution to
        data persistence and state management.
        
        Test workflow:
        1. Cleans up any previous test artifacts (DuckDB file and DLT state)
        2. Executes main() with a real schedule ID that should create test data
        3. Verifies DuckDB file creation at the expected mounted location
        4. Validates that the correct test data was inserted into the database
        5. Confirms DLT state directory was created (supports multiple layouts)
        
        Expected outcomes:
        - DuckDB file created at /app/data/e2e.duckdb
        - Test data: [(1, "a"), (2, "b"), (3, "c")] in e2e_ds.entries table
        - DLT pipeline state directory created under /app/.dlt
        - main() exits with code 0
        
        This test covers:
        - Real DLT pipeline execution
        - Data persistence verification
        - State management across different DLT versions
        - File system integration
        """

        # Clean any previous artifacts for deterministic run
        if os.path.exists(DUCKDB_PATH):
            os.remove(DUCKDB_PATH)

        # Remove only this pipeline's state dir (cover current + other known layouts)
        for candidate in [
            os.path.join(PIPELINES_DIR, PIPELINE_NAME),                # current layout
            os.path.join(PIPELINES_DIR, "pipelines", PIPELINE_NAME),   # dlt >= 1.14 alt layout
            os.path.join(PIPELINES_DIR, "state", PIPELINE_NAME),       # older layout
        ]:
            if os.path.isdir(candidate):
                shutil.rmtree(candidate, ignore_errors=True)

        # Call main() with real execution (no patching DLTRunner.run here)
        with patch('sys.argv', ['dlt_runner.py', 'jobX', 'userX', SCHEDULE_ID, 'runX', 'code']):
            with self.assertRaises(SystemExit) as cm:
                main.main()
            self.assertEqual(cm.exception.code, 0, "DLTRunner main() did not exit with code 0")

        # Verify DuckDB file was written at the mounted location
        self.assertTrue(os.path.exists(DUCKDB_PATH), f"DuckDB not found at {DUCKDB_PATH}")

        # Verify the data
        con = duckdb.connect(DUCKDB_PATH)
        try:
            rows = con.execute(f'SELECT id, val FROM "{SCHEMA}"."{TABLE}" ORDER BY id').fetchall()
            self.assertEqual(rows, [(1, "a"), (2, "b"), (3, "c")], f"Unexpected rows: {rows}")
        finally:
            con.close()

        # --- Robust DLT state assertion across versions/layouts ---
        self.assertTrue(os.path.isdir(PIPELINES_DIR), f"DLT state root missing: {PIPELINES_DIR}")

        candidates = [
            os.path.join(PIPELINES_DIR, PIPELINE_NAME),                # current layout
            os.path.join(PIPELINES_DIR, "pipelines", PIPELINE_NAME),   # dlt >= 1.14 alt layout
            os.path.join(PIPELINES_DIR, "state", PIPELINE_NAME),       # older layout
        ]
        found = any(os.path.isdir(p) for p in candidates)

        if not found:
            for root, dirs, files in os.walk(PIPELINES_DIR):
                if os.path.basename(root) == PIPELINE_NAME:
                    found = True
                    break

        if not found:
            try:
                non_hidden = [e for e in os.listdir(PIPELINES_DIR) if not e.startswith(".")]
            except FileNotFoundError:
                non_hidden = []
            found = bool(non_hidden)

        self.assertTrue(
            found,
            f"DLT state for pipeline '{PIPELINE_NAME}' not found under {PIPELINES_DIR}. "
            f"Top-level contents: {os.listdir(PIPELINES_DIR) if os.path.isdir(PIPELINES_DIR) else 'N/A'}"
        )


    def test_dlt_schedule_prints_hi(self):
        """
        Execute DLTRunner.main() with the schedule that contains code: print("hi")
        and verify that "hi" appears on stdout and main exits with code 0.
        """
        argv = [
            'dlt_runner.py',
            'print_hi_job',                 # job_id (arbitrary)
            'dlt_test_user',        # user_id that matches the seeded schedule
            '65cb43f2007a5f38718b9abc',         # schedule_id -> prints("hi")
            'run2',                 # run_id (arbitrary)
            'code',                 # execution_type
        ]

        buf = io.StringIO()
        with patch.object(sys, 'argv', argv):
            with contextlib.redirect_stdout(buf):
                with self.assertRaises(SystemExit) as cm:
                    main.main()

        out = buf.getvalue()
        self.assertEqual(cm.exception.code, 0, f"main() exited non-zero. Output:\n{out}")
        self.assertIn("hi", out, f"'hi' not found in output:\n{out}")


    def test_people_schedule_e2e(self):
        """
        End-to-end test for the 'people' dataset schedule execution.
        
        Tests a complete DLT pipeline that processes people data and stores it
        in a separate DuckDB file. This test verifies the execution of a different
        schedule with different data schema and content.
        
        Test workflow:
        1. Cleans up any previous people.duckdb file
        2. Executes main() with the people schedule ID
        3. Verifies people.duckdb file creation
        4. Validates the people data was correctly inserted
        
        Expected data structure:
        - Schema: people_ds
        - Table: people
        - Data: [(101, "Grace Hopper"), (102, "Linus Torvalds"), (103, "Katherine Johnson")]
        
        Expected outcomes:
        - people.duckdb file created at /app/data/people.duckdb
        - Correct people data inserted and retrievable
        - main() exits with code 0
        
        This test covers:
        - Alternative dataset processing
        - Multiple DuckDB file management
        - Different schema and table structures
        """
        DUCKDB_PATH = "/app/data/people.duckdb"
        if os.path.exists(DUCKDB_PATH):
            os.remove(DUCKDB_PATH)

        with patch('sys.argv', ['dlt_runner.py', 'jobP', 'userP', '65cb43f2007a5f38718b9d7f', 'runP', 'code']):
            with self.assertRaises(SystemExit) as cm:
                main.main()
            self.assertEqual(cm.exception.code, 0)

        self.assertTrue(os.path.exists(DUCKDB_PATH), "people.duckdb was not created")
        con = duckdb.connect(DUCKDB_PATH)
        rows = con.execute('SELECT id, name FROM "people_ds"."people" ORDER BY id').fetchall()
        assert rows == [
            (101, "Grace Hopper"),
            (102, "Linus Torvalds"),
            (103, "Katherine Johnson"),
        ]
        con.close()

    def test_read_duckdb_e2e(self):
        """Simple reader to validate e2e.duckdb contents independently."""
        if not os.path.exists(DUCKDB_PATH):
            self.skipTest(f"{DUCKDB_PATH} not found — run the writer test first.")

        con = duckdb.connect(DUCKDB_PATH)
        try:
            # Verify schema & table exist
            schemas = {row[0] for row in con.execute(
                "SELECT schema_name FROM information_schema.schemata"
            ).fetchall()}
            self.assertIn(SCHEMA, schemas, f"Schema '{SCHEMA}' not found")

            tables = {(row[0], row[1]) for row in con.execute(
                "SELECT table_schema, table_name FROM information_schema.tables"
            ).fetchall()}
            self.assertIn((SCHEMA, TABLE), tables, f"Table {SCHEMA}.{TABLE} not found")

            # Verify data
            rows = con.execute(f'SELECT id, val FROM "{SCHEMA}"."{TABLE}" ORDER BY id').fetchall()
            self.assertEqual(rows, [(1, "a"), (2, "b"), (3, "c")])
        finally:
            con.close()


if __name__ == '__main__':
    unittest.main()
