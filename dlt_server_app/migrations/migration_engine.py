# /migrations/migration_engine.py - Multi-RDBMS Migration Engine (Airflow paths compatible)
"""
Migration Engine for DLT - Support for ALL RDBMS
Supports: PostgreSQL, MySQL, MSSQL, Oracle, Snowflake, BigQuery, Redshift, DuckDB, SQLite
- Uses DLT verified source for table ingestion (sql_table)
- Adds custom query support via a DLT resource when `query` or `where_clause` is provided
- Connection pooling for source databases
- Proper batch yielding for performance
- Compatible with Airflow mounted paths
- Audit logging with row_counts, schema_info, and failure progress capture
"""

import logging
import traceback
import os
from datetime import datetime, date, timezone
from decimal import Decimal
import uuid
from typing import Dict, List, Optional, Any, Literal, Union

import dlt
from dlt.sources.sql_database import sql_table
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus

try:
    from audit_tracker.audit_tracker import AuditTracker
except ImportError as e:
    AuditTracker = None
    logging.warning(f"AuditTracker not available: {e}")


# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ------------------------------------------------------------------------------
# Types
# ------------------------------------------------------------------------------
DatabaseType = Literal[
    "postgresql", "postgres",
    "mysql",
    "mssql", "sqlserver",
    "oracle",
    "snowflake",
    "bigquery",
    "redshift",
    "duckdb",
    "sqlite",
    "firebird",
    "google_sheets"
]

from core.datasource.connector import DataSourceConnector

# ------------------------------------------------------------------------------
# Migration Engine
# ------------------------------------------------------------------------------
class MigrationEngine:
    """
    Dynamic Migration Engine supporting all RDBMS.
    - Table ingestion (sql_table)
    - Custom SQL query ingestion via a DLT resource when `query` or `where_clause` is given
    - Connection pooling for source databases
    - Proper batch processing for performance
    - Compatible with Airflow mounted paths
    - Audit logging with detailed row_counts, schema_info, and failure progress
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.execution_metadata = {}
        self.datasource = DataSourceConnector()
        self._engine_cache: Dict[str, Any] = {}  # Cache for source engines

    # ---------- helpers ----------
    def _engine_key(self, connection: Dict[str, Any]) -> str:
        """Generate a unique key for caching engines"""
        db_type = self._normalize_db_type(str(connection.get('db_type', '')))
        return f"{db_type}:{connection.get('host')}:{connection.get('port')}:{connection.get('database')}:{connection.get('username')}"

    def _normalize_db_type(self, db_type: str) -> str:
        db_type = str(db_type).lower()
        mapping = {
            "postgresql": "postgres",
            "mssql": "ms_sql_server",
            "sqlserver": "ms_sql_server"
        }
        return mapping.get(db_type, db_type)

    def _sa_engine(self, connection: Dict[str, Any], role: str = "src"):
        """Build or reuse a pooled SQLAlchemy engine for source queries"""
        key = self._engine_key(connection)
        
        if key in self._engine_cache:
            self.logger.debug(f"Reusing cached engine for {role}")
            return self._engine_cache[key]
        
        raw_db_type = str(connection.get("db_type", "postgresql")).lower()
        db_type = self._normalize_db_type(raw_db_type)
        
        # Engine configuration with connection pooling (optimized settings)
        engine_kwargs = {
            "pool_pre_ping": True,
            "pool_size": 20,        # Increased from 10 to 20
            "max_overflow": 40,     # Increased from 20 to 40
            "pool_timeout": 30,
            "pool_recycle": 1800,  # Recycle connections after 30 minutes
            "future": True
        }
        
        # Database-specific configurations
        if raw_db_type in ("mssql", "sqlserver"):
            engine_kwargs["fast_executemany"] = True
        
        self.logger.info(f"Creating new pooled engine for {role} ({db_type})")
        
        # update connection dict so core.datasource gets the mapped type
        conn_for_core = dict(connection)
        conn_for_core["db_type"] = db_type
        
        connector = self.datasource.create(db_type)
        engine = connector.get_engine(conn_for_core, **engine_kwargs)
        self._engine_cache[key] = engine
        
        return engine

    def _build_connection_string(self, connection: Dict[str, Any]) -> str:
        raw_db_type = connection.get("db_type", "postgresql")
        db_type = self._normalize_db_type(raw_db_type)
        
        # update connection dict so core.datasource gets the mapped type
        conn_for_core = dict(connection)
        conn_for_core["db_type"] = db_type

        self.logger.info(f"Building connection string for {db_type}")
        connector = self.datasource.create(db_type)
        conn_string = connector.get_connection_string(conn_for_core)

        # Mask password in logs
        if "password" in connection:
            safe_conn = {k: v if k != "password" else "***" for k, v in connection.items()}
            self.logger.info(f"Connection params: {safe_conn}")

        return conn_string

    def _validate_connection(self, connection: Dict[str, Any], name: str):
        db_type = connection.get("db_type", "postgresql").lower()
        common_required = ["db_type"]
        db_specific_required = {
            "postgresql": ["host", "port", "database", "username", "password"],
            "postgres":   ["host", "port", "database", "username", "password"],
            "mysql":      ["host", "port", "database", "username", "password"],
            "mssql":      ["host", "port", "database", "username", "password"],
            "sqlserver":  ["host", "port", "database", "username", "password"],
            "firebird":   ["host", "port", "database", "username", "password"],
            "oracle":     ["host", "port", "username", "password"],
            # "snowflake":  ["account", "username", "password", "database", "warehouse"],
            "bigquery":   ["project_id", "dataset"],
            "redshift":   ["host", "port", "database", "username", "password"],
            "duckdb":     ["database"],
            "sqlite":     ["database"],
            # "google_sheets": ["credentials_object", "sheet_id"],
        }
        required = common_required + db_specific_required.get(db_type, [])
        missing = [field for field in required if field not in connection or not connection[field]]
        if missing:
            raise ValueError(f"Missing required fields in {name} for {db_type}: {missing}")
        self.logger.info(f"  {name} validated ({db_type})")

    def _validate_mode(self, mode: str):
        valid_modes = ["append", "replace", "merge"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")
        self.logger.info(f"  Mode '{mode}' validated")

    def _determine_data_dir(self) -> str:
        """
        Determine the appropriate data directory based on environment.
        Returns path for DuckDB and other file-based destinations.
        """
        # Check if running via Airflow with --volumes-from
        if os.path.exists('/opt/airflow/dlt/dlt_data'):
            data_dir = '/opt/airflow/dlt/dlt_data'
            self.logger.info(f"  Using Airflow data directory: {data_dir}")
            return data_dir
        else:
            data_dir = '/app/data'
            self.logger.info(f"  Using default data directory: {data_dir}")
            return data_dir

    # ---------- AUDIT: Row Counts Extraction ----------
    def _extract_per_table_row_counts(self, pipeline: "dlt.Pipeline") -> dict:
        """
        Extract per-table row counts from pipeline trace.
        Source: pipeline.last_trace.last_normalize_info.row_counts
        
        Returns:
            dict: Per-table row counts, e.g., {"customers": 1500, "_dlt_pipeline_state": 1}
        """
        try:
            if pipeline and pipeline.last_trace and pipeline.last_trace.last_normalize_info:
                row_counts = pipeline.last_trace.last_normalize_info.row_counts or {}
                self.logger.debug(f"Extracted row_counts for pipeline '{pipeline.pipeline_name}': {row_counts}")
                return dict(row_counts)
        except Exception as e:
            self.logger.warning(f"Could not extract row counts: {e}")
            return {}
        
        self.logger.warning("Missing data: row counts information is not available, returning empty dictionary")
        return {}
    
    # ---------- AUDIT: Schema Info Extraction ----------
    def _extract_schema_info(self, load_info: "dlt.LoadInfo", pipeline: "dlt.Pipeline" = None) -> dict:
        """
        Extract column count and data types for actual data tables only.
        Uses row_counts table names to identify actual data tables.
        """
        schema_info = {}
        actual_tables = set()
        
        # Get actual table names from row_counts (excludes _dlt_ tables automatically based on data)
        try:
            if pipeline and pipeline.last_trace and pipeline.last_trace.last_normalize_info:
                row_counts = pipeline.last_trace.last_normalize_info.row_counts or {}
                actual_tables = {
                        table_name for table_name in row_counts.keys()
                        if not table_name.startswith('_dlt_')
                    }
                self.logger.debug(f"Actual data tables from row_counts: {actual_tables}")
        except Exception as e:
            self.logger.warning(f"Could not get table names from row_counts: {e}")
        
        # Extract schema only for actual tables
        if pipeline and actual_tables:
            try:
                if hasattr(pipeline, 'default_schema') and pipeline.default_schema:
                    tables = pipeline.default_schema.tables
                    if tables:
                        for table_name in actual_tables:
                            if table_name in tables:
                                table_info = tables[table_name]
                                columns = table_info.get("columns", {})
                                if columns:
                                    # Filter out _dlt_ columns
                                    filtered_columns = {
                                        col_name: col_info.get('data_type', 'unknown')
                                        for col_name, col_info in columns.items()
                                        # Uncomment below line to also exclude _dlt_ columns
                                        # if not col_name.startswith('_dlt_')
                                    }
                                    schema_info[table_name] = {
                                        'column_count': len(filtered_columns),
                                        'columns': filtered_columns
                                    }
                        if schema_info:
                            self.logger.info(f"Extracted schema_info for actual tables: {list(schema_info.keys())}")
            except Exception as e:
                self.logger.warning(f"Could not extract schema: {e}")
        
        return schema_info


    # ---------- AUDIT: Failure Progress Extraction ----------
    def _extract_failure_progress(self, pipeline) -> tuple:
        """
        Extract whatever progress was made before a failure.
        DLT saves progress after each step: EXTRACT → NORMALIZE → LOAD
        
        Returns:
            tuple: (row_counts: dict, failed_step: str, schema_info: dict)
            - row_counts: Per-table row counts from the last completed step
            - failed_step: Which step failed ('extract', 'normalize', 'load', 'unknown')
            - schema_info: Column count and types (if available from pipeline schema)
        """
        row_counts = {}
        failed_step = "unknown"
        schema_info = {}
        
        try:
            if pipeline and pipeline.last_trace:
                # Check normalize info first (most complete)
                if pipeline.last_trace.last_normalize_info:
                    normalize_info = pipeline.last_trace.last_normalize_info
                    if hasattr(normalize_info, 'row_counts') and normalize_info.row_counts:
                        row_counts = dict(normalize_info.row_counts)
                        failed_step = "load"  # Normalize completed, so load failed
                        self.logger.info(f"Failure progress: Normalize completed, load failed. Rows: {row_counts}")
                
                # Check extract info if normalize not available
                elif pipeline.last_trace.last_extract_info:
                    extract_info = pipeline.last_trace.last_extract_info
                    failed_step = "normalize"  # Extract completed, so normalize failed
                    
                    # Try to get row counts from extract_info.table_metrics
                    if hasattr(extract_info, 'table_metrics') and extract_info.table_metrics:
                        for table_name, metrics in extract_info.table_metrics.items():
                            if hasattr(metrics, 'items_count'):
                                row_counts[table_name] = metrics.items_count
                    self.logger.info(f"Failure progress: Extract completed, normalize failed. Rows: {row_counts}")
                
                else:
                    failed_step = "extract"  # Extract failed
                    self.logger.info("Failure progress: Extract failed, no rows captured")
            
            # Try to extract schema info from pipeline even on failure
            # Reuse the existing _extract_schema_info method with None for load_info
            schema_info = self._extract_schema_info(None, pipeline)
                        
        except Exception as e:
            self.logger.warning(f"Could not extract failure progress: {e}")
            failed_step = "unknown"
        
        return row_counts, failed_step, schema_info


    def _echo_function(self,rows: int, cols: int):
        """
        Echo function for AuditTracker.
        Returns rows and cols for audit recording.
        """
        return {
            "rows": rows,
            "cols": cols
        }


    # ---------- main entry ----------
    def migrate(self,
                source_connection: Dict[str, Any],
                source_table: str,
                destination_connection: Dict[str, Any],
                destination_table: str,
                mode: str = "replace",
                source_schema: str = "public",
                destination_schema: str = "public",
                primary_key: Optional[List[str]] = None,
                increment_key: Optional[Union[str, List[str]]] = None,
                column_selection: Optional[List[str]] = None,
                column_mapping: Optional[Dict[str, str]] = None,
                where_clause: Optional[str] = None,
                query: Optional[str] = None,
                pipeline_name: Optional[str] = None,
                pipelines_dir: Optional[str] = None,
                batch_size: int = 50000,
                # Destination pooling parameters
                dest_pool_size: int = 20,
                dest_max_overflow: int = 40,
                dest_pool_timeout: int = 30,
                dest_pool_recycle: int = 1800,
                audit_tracker=None,
                **kwargs) -> Dict[str, Any]:
        """
        Execute migration using DLT.
        - If `query` or `where_clause` is provided, a custom DLT resource is used (streaming via SQLAlchemy).
        - Otherwise, the verified source `sql_table` is used.
        - Respects pipelines_dir from environment or parameter
        - Returns detailed audit info including row_counts, schema_info, and failure progress
        """

        start_time = datetime.now(timezone.utc)
        pipeline = None  # Initialize for failure handling

        try:
            self.logger.info("MIGRATION ENGINE - EXECUTION START")

            # STEP 1: VALIDATE
            self.logger.info("Step 1: Validating inputs...")
            self._validate_connection(source_connection, "source_connection")
            self._validate_connection(destination_connection, "destination_connection")
            self._validate_mode(mode)

            if mode == "merge" and not primary_key:
                raise ValueError("primary_key is required for merge mode")
            
            if mode == "replace":
                primary_key = None

            source_db_type = source_connection.get("db_type", "postgresql")
            dest_db_type = destination_connection.get("db_type", "postgresql")

            self.logger.info(f"Source DB: {source_db_type}")
            self.logger.info(f"Destination DB: {dest_db_type}")
            self.logger.info("All inputs validated")

            # Force schema to None for schema-less databases
            if source_db_type in ["firebird", "sqlite"]:
                source_schema = None
            if dest_db_type in ["firebird", "sqlite"]:
                destination_schema = None

            # STEP 2: BUILD CONNECTION STRINGS
            self.logger.info("Step 2: Building connection strings...")
            # TODO: We directly pass engine instance now, so source_conn_string is not needed
            if source_db_type == "google_sheets":
                source_conn_string = "google_sheets://dummy" # This is not used
            else:
                source_conn_string = self._build_connection_string(source_connection)
            dest_conn_string = self._build_connection_string(destination_connection)

            self.logger.info(f"Source: {source_schema}.{source_table} ({source_db_type})")
            self.logger.info(f"Destination: {destination_schema}.{destination_table} ({dest_db_type})")
            self.logger.info(f"Mode: {mode.upper()}")

            # STEP 3: CONNECT TO SOURCE (table vs custom query)
            self.logger.info("Step 3: Connecting to source...")

            use_query = bool(query) or bool(where_clause) or (isinstance(increment_key, (list, tuple)) and len(increment_key) > 1)
            source_resource = None

            # TODO: Use query should also interact with the DataConnector layer to form query
            #   that is specific to db_type
            if source_db_type == "google_sheets":
                self.logger.info("Using native Google Sheets extractor via core connector...")
                
                # TODO: Below is a hacky way to fix the volume mounting mismatch (in other engines we directly refer hadoop_local/ 
                #   but in dlt server, it is mapped to /hadoop_local/)
                # If source_connection['credentials_object']['file'] does not start with a '/', append '/' to it
                if not source_connection.get('credentials_object', {}).get('file', '/').startswith('/'):
                    source_connection['credentials_object']['file'] = '/' + source_connection['credentials_object']['file']

                @dlt.resource(
                    name=destination_table,
                    write_disposition=mode,
                    primary_key=primary_key
                )
                def google_sheets_source():
                    """Native DLT resource for Google Sheets using our core connector"""
                    connector = self.datasource.create("google_sheets")
                    
                    self.logger.info(f"Fetching data from Google Sheets worksheet: {source_table}")
                    df = connector.fetch_data(
                        connection_details=source_connection,
                        catalog=source_table,
                        num_rows=None  # Ensure we fetch all rows
                    )
                    
                    # Transform to dicts and yield in batches for performance
                    records = df.to_dict(orient="records")
                    batch = []
                    batch_size_local = batch_size
                    for row in records:
                        batch.append(row)
                        if len(batch) >= batch_size_local:
                            yield batch
                            batch = []
                    if batch:
                        yield batch

                source_resource = google_sheets_source
            elif use_query:
                # Compose final SQL if only where_clause provided
                final_sql = query
                if not final_sql:
                    # Improved SQL construction
                    if source_schema:
                        ident = f"{source_schema}.{source_table}"
                    else:
                        ident = source_table
                    
                    if where_clause:
                        final_sql = f"SELECT * FROM {ident} WHERE {where_clause}"
                    else:
                        final_sql = f"SELECT * FROM {ident}"

                # Log query (truncated for safety)
                query_preview = final_sql.strip().replace("\n", " ")[:200]
                self.logger.info(f"Using custom SQL query: {query_preview}...")
                
                # Proper batch yielding
                @dlt.resource(
                    name=destination_table,
                    write_disposition=mode,
                    primary_key=primary_key
                )
                def query_source():
                    """Custom query source with batched yielding for performance"""
                    eng = self._sa_engine(source_connection, role="src")
                    try:
                        with eng.connect() as conn:
                            result = conn.execution_options(stream_results=True).execute(text(final_sql))
                            batch = []
                            batch_size_local = batch_size  # Batch size for yielding
                            
                            for row in result.mappings():
                                batch.append(dict(row))
                                if len(batch) >= batch_size_local:
                                    yield batch  # Yield entire batch
                                    batch = []
                            
                            # Yield remaining rows
                            if batch:
                                yield batch
                    except Exception as e:
                        self.logger.error(f"Error executing query: {e}")
                        raise

                source_resource = query_source

            else:
                self.logger.info("Using verified source: sql_table")
                source_engine = self._sa_engine(source_connection, role="src")
                source_resource = sql_table(
                    credentials=source_engine,
                    table=source_table,
                    schema=source_schema,
                    chunk_size=batch_size
                )

            # STEP 4: TRANSFORMATIONS / HINTS
            actual_increment_key = None
            if increment_key and mode in ("append", "merge"):
                if isinstance(increment_key, (list, tuple)):
                    if len(increment_key) == 1:
                        actual_increment_key = increment_key[0]
                    elif len(increment_key) > 1:
                        # Build synthetic column mapping for multi-column cursor.
                        # Values are converted to JSON-safe types so DLT can
                        # serialize the cursor checkpoint without crashing on
                        # datetime / Decimal / UUID / bytes column values.
                        def add_synthetic_cursor(row):
                            row["_dms_increment_key"] = [
                                MigrationEngine._to_json_safe(row.get(col))
                                for col in increment_key
                            ]
                            return row
                        source_resource = source_resource.add_map(add_synthetic_cursor)
                        actual_increment_key = "_dms_increment_key"
                else:
                    actual_increment_key = increment_key

            if column_selection or column_mapping:
                self.logger.info("Step 4: Applying transformations...")
                source_resource = self._apply_transformations(
                    source_resource,
                    column_selection,
                    column_mapping,
                    destination_table,
                    mode,
                    primary_key,
                    increment_key
                )
            else:
                self.logger.info("Step 4: Configuring resource hints...")
                hints = {
                    "table_name": destination_table,
                    "write_disposition": mode
                }
                if primary_key and mode != "replace":
                    hints["primary_key"] = primary_key
                    self.logger.info(f"  Primary key: {primary_key}")
                
                if actual_increment_key:
                    hints["incremental"] = dlt.sources.incremental(actual_increment_key)
                    self.logger.info(f"  Incremental key (CDC): {actual_increment_key}")
                    if actual_increment_key == "_dms_increment_key":
                        hints["columns"] = {"_dms_increment_key": {"data_type": "json"}}

                source_resource.apply_hints(**hints)
                self.logger.info("  Resource configured")

            # STEP 5: CREATE DLT PIPELINE
            if not pipeline_name:
                timestamp = int(start_time.timestamp())
                pipeline_name = f"migration_{source_table}_to_{destination_table}_{timestamp}"

            self.logger.info(f"Step 5: Creating DLT pipeline: {pipeline_name}")

            # Use engine_args parameter (from DLT source code)
            engine_args = {
                "pool_size": dest_pool_size,
                "max_overflow": dest_max_overflow,
                "pool_timeout": dest_pool_timeout,
                "pool_pre_ping": True,
                "pool_recycle": dest_pool_recycle,
            }

            # Add database-specific configs
            if dest_db_type in ("postgresql", "postgres"):
                engine_args["executemany_mode"] = "values_plus_batch"
                engine_args["executemany_batch_page_size"] = 10000
                engine_args["insertmanyvalues_page_size"] = 10000

            if dest_db_type in ("mssql", "sqlserver"):
                engine_args["fast_executemany"] = True
            
            self.logger.info(f"Destination engine_args: pool_size={dest_pool_size}, max_overflow={dest_max_overflow}")

            #  Determine data directory for file-based destinations
            data_dir = self._determine_data_dir()

            #  Handle DuckDB destination path
            if dest_db_type == "duckdb":
                # Use determined data directory
                duckdb_path = f"{data_dir}/{destination_schema}.duckdb"
                dest_conn_string = f"duckdb:///{duckdb_path}"
                self.logger.info(f"  DuckDB path: {duckdb_path}")

            # Create destination based on type with engine_args
            if dest_db_type in ["postgresql", "postgres"]:
                destination = dlt.destinations.sqlalchemy(
                    credentials=dest_conn_string,
                    engine_args=engine_args
                )
                self.logger.info(f"Using SQLAlchemy destination for {dest_db_type}")
            elif dest_db_type in ["mysql", "mssql", "sqlserver", "oracle", "duckdb", "sqlite"]:
                destination = dlt.destinations.sqlalchemy(
                    credentials=dest_conn_string,
                    engine_args=engine_args
                )
                self.logger.info(f"Using SQLAlchemy destination for {dest_db_type}")
            elif dest_db_type == "snowflake":
                destination = dlt.destinations.snowflake(dest_conn_string)
                self.logger.info("Using native Snowflake destination")
            elif dest_db_type == "bigquery":
                destination = dlt.destinations.bigquery(dest_conn_string)
                self.logger.info("Using native BigQuery destination")
            elif dest_db_type == "redshift":
                destination = dlt.destinations.redshift(dest_conn_string)
                self.logger.info("Using native Redshift destination")
            else:
                destination = dlt.destinations.sqlalchemy(
                    credentials=dest_conn_string,
                    engine_args=engine_args
                )
                self.logger.info(f"Using SQLAlchemy destination (fallback) for {dest_db_type}")
            
            #  EXPLICITLY SET pipelines_dir
            # Priority: parameter > environment variable > default
            if pipelines_dir is None:
                pipelines_dir = os.getenv('DLT_DATA_DIR')
            
            if pipelines_dir is None:
                # Determine based on environment
                if os.path.exists('/opt/airflow/dlt/dlt_state'):
                    pipelines_dir = '/opt/airflow/dlt/dlt_state'
                else:
                    pipelines_dir = '/app/.dlt'
            
            self.logger.info(f"Using pipelines_dir: {pipelines_dir}")

            pipeline = dlt.pipeline(
                pipeline_name=pipeline_name,
                destination=destination,
                dataset_name=destination_schema,
                pipelines_dir=pipelines_dir
            )

            self.logger.info(f"Pipeline created")
            self.logger.info(f"Pipeline working_dir: {pipeline.working_dir}")

            # STEP 6: EXECUTE MIGRATION
            self.logger.info("Step 6: Executing migration...")
            self.logger.info(f"Write mode: {mode}")
            info = pipeline.run(source_resource)

            # STEP 7: EXTRACT RESULTS (with AUDIT fields)
            self.logger.info("Step 7: Processing results...")

            # Get all load_ids as list
            dlt_load_id = info.loads_ids if info.loads_ids else []

            if dlt_load_id:
                self.logger.info(f"  DLT Load IDs: {dlt_load_id}")

            has_failed = info.has_failed_jobs

            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            # AUDIT: Extract detailed row counts from pipeline trace
            row_counts = self._extract_per_table_row_counts(pipeline)
            
            # Calculate total rows from row_counts (exclude internal DLT tables)
            rows_migrated = sum(
                count for table, count in row_counts.items()
                if not table.startswith('_dlt_')
            )
            
            # Fallback to old method if row_counts is empty
            if rows_migrated == 0:
                rows_migrated = self._extract_row_count(info)
            
            # AUDIT: Extract schema info
            schema_info = self._extract_schema_info(info,pipeline)

            # Calculate total columns from schema_info
            total_cols = sum(
                table_info.get('column_count', 0) 
                for table_info in schema_info.values()
            )

            # AUDIT: Record to AuditTracker 
            if audit_tracker:
                try:
                    audit_tracker.record(self._echo_function)(
                        rows_migrated, 
                        total_cols, 
                        old_df=None, 
                        step_name='dms_migration_step'
                    )
                    self.logger.info(f"Audit recorded: rows={rows_migrated}, cols={total_cols}")
                except Exception as e:
                    self.logger.warning(f"Failed to record audit: {e}")

            result = {
                "success": not has_failed,
                "source": f"{source_schema}.{source_table}",
                "destination": f"{destination_schema}.{destination_table}",
                "source_db_type": source_db_type,
                "destination_db_type": dest_db_type,
                "mode": mode,
                "rows_migrated": rows_migrated,
                "row_counts": row_counts,           # AUDIT: Per-table row counts
                "schema_info": schema_info,         # AUDIT: Column count and types
                "failed_step": None,                # AUDIT: No failure
                "duration_seconds": round(duration, 2),
                "dlt_load_id": dlt_load_id, # Get all load_ids

                "pipeline_name": pipeline_name,
                "pipeline_working_dir": pipeline.working_dir,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "error": None
            }

            self.logger.info("=" * 70)
            if has_failed:
                self.logger.error("MIGRATION FAILED")
                result["error"] = "DLT reported failed jobs"
                result["success"] = False
            else:
                self.logger.info("MIGRATION COMPLETED SUCCESSFULLY")
                self.logger.info(f"Rows migrated: {rows_migrated:,}")
                self.logger.info(f"Row counts per table: {row_counts}")
                self.logger.info(f"Duration: {duration:.2f} seconds")
                if rows_migrated > 0 and duration > 0:
                    rate = int(rows_migrated / duration)
                    self.logger.info(f"  Rate: {rate:,} rows/second")
            self.logger.info("=" * 70)
            self.logger.info(f"DLT Load ID: {dlt_load_id}")
            self.logger.info(f"Pipeline working_dir: {pipeline.working_dir}")
            self.logger.info(f"Source: {source_db_type} → Destination: {dest_db_type}")

            self.execution_metadata = result
            self.logger.info(f"Migration result : {result}")
            return result
        
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            error_msg = str(e)
            error_trace = traceback.format_exc()

            self.logger.error("=" * 70)
            self.logger.error(" MIGRATION FAILED")
            self.logger.error("=" * 70)
            self.logger.error(f"Error: {error_msg}")
            self.logger.error(error_trace)

            # AUDIT: Extract failure progress (whatever was completed before failure)
            row_counts, failed_step, schema_info = self._extract_failure_progress(pipeline)
            rows_migrated = sum(
                count for table, count in row_counts.items() 
                if not table.startswith('_dlt_')
            )
            
            self.logger.info(f"Failure progress captured - Step: {failed_step}, Rows: {rows_migrated}")

            result = {
                "success": False,
                "source": f"{source_schema}.{source_table}" if 'source_table' in locals() else "unknown",
                "destination": f"{destination_schema}.{destination_table}" if 'destination_table' in locals() else "unknown",
                "source_db_type": source_connection.get("db_type", "unknown"),
                "destination_db_type": destination_connection.get("db_type", "unknown"),
                "mode": mode if 'mode' in locals() else "unknown",
                "rows_migrated": rows_migrated,
                "row_counts": row_counts,           # AUDIT: Partial row counts on failure
                "schema_info": schema_info,         # AUDIT: Schema info (if available)
                "failed_step": failed_step,         # AUDIT: Which step failed
                "duration_seconds": round(duration, 2),
                "dlt_load_id": None,
                "pipeline_name": pipeline_name if 'pipeline_name' in locals() else None,
                "pipeline_working_dir": pipeline.working_dir if pipeline else None,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "error": error_msg,
                "traceback": error_trace
            }
            self.execution_metadata = result
            self.logger.info(f"Migration result : {result}")
            return result

    def migrate_files(self,
                      file_path: str,
                      file_name: str,
                      file_type: str,
                      destination_connection: Dict[str, Any],
                      destination_table: str,
                      mode: str = "replace",
                      destination_schema: str = "public",
                      primary_key: Optional[List[str]] = None,
                      pipeline_name: Optional[str] = None,
                      pipelines_dir: Optional[str] = None,
                      batch_size: int = 50000,
                      dest_pool_size: int = 20,
                      dest_max_overflow: int = 40,
                      dest_pool_timeout: int = 30,
                      dest_pool_recycle: int = 1800,
                      audit_tracker=None,
                      **kwargs) -> Dict[str, Any]:
        """
        Execute file migration using DLT, dynamically chunking files via Pandas
        """
        start_time = datetime.now(timezone.utc)
        pipeline = None

        try:
            self.logger.info("MIGRATION ENGINE (FILES) - EXECUTION START")
            self._validate_connection(destination_connection, "destination_connection")
            self._validate_mode(mode)

            if mode == "merge" and not primary_key:
                raise ValueError("primary_key is required for merge mode")
            if mode == "replace":
                primary_key = None

            dest_db_type = destination_connection.get("db_type", "postgresql")
            dest_conn_string = self._build_connection_string(destination_connection)

            self.logger.info(f"Source File: {file_path} ({file_type})")
            self.logger.info(f"Destination: {destination_schema}.{destination_table} ({dest_db_type})")

            import pandas as pd
            import numpy as np

            @dlt.resource(
                name=destination_table,
                write_disposition=mode,
                primary_key=primary_key
            )
            def file_source(_file_path, _file_type, _batch_size):
                self.logger.info(f"Fetching data from flat file: {_file_path}")
                file_ext = _file_type.lower() if _file_type else _file_path.split('.')[-1].lower()
                # TODO: Below adjustment is done to overcome the discrepancy in hadoop_local volume mapping in dlt server
                #   . We store paths as "hadoop_local/..." in db but the volume mapping is "/hadoop_local/..."
                if not _file_path.startswith("/"):
                    _file_path = "/" + _file_path

                try:
                    if file_ext in ["csv", ".csv"]:
                        chunks = pd.read_csv(_file_path, chunksize=_batch_size)
                        for chunk in chunks:
                            chunk = chunk.replace({np.nan: None})
                            yield chunk.to_dict(orient="records")
                    elif file_ext in ["json", ".json"]:
                        df = pd.read_json(_file_path)
                        df = df.replace({np.nan: None})
                        records = df.to_dict(orient="records")
                        for i in range(0, len(records), _batch_size):
                            yield records[i:i + _batch_size]
                    elif file_ext in ["xlsx", "xls", ".xlsx", ".xls"]:
                        import re

                        # TODO: below implementation does not pick up num_rows from settings
                        
                        # TODO: For current DMS setup, we read all columns of the excel file.
                        df = pd.read_excel(_file_path, engine="openpyxl")
                        df.columns = [re.sub('[^0-9a-zA-Z]+', '_', c) for c in map(str.lower, df.columns)]
                        df[df.select_dtypes(include=['object']).columns] = df.select_dtypes(include=['object']).apply(lambda col: col.astype(str).where(~col.isna(), col))

                        df = df.replace({np.nan: None})

                        records = df.to_dict(orient="records")
                        for i in range(0, len(records), _batch_size):
                            yield records[i:i + _batch_size]
                    else:
                        raise ValueError(f"Unsupported file type: {file_ext}")
                except Exception as e:
                    self.logger.error(f"Error reading flat file chunk: {e}")
                    raise

            source_resource = file_source(file_path, file_type, batch_size)

            if not pipeline_name:
                timestamp = int(start_time.timestamp())
                # Handle pipeline names securely
                safe_file_name = "".join(x for x in file_name if x.isalnum())
                pipeline_name = f"migration_file_{safe_file_name}_to_{destination_table}_{timestamp}"

            engine_args = {
                "pool_size": dest_pool_size,
                "max_overflow": dest_max_overflow,
                "pool_timeout": dest_pool_timeout,
                "pool_pre_ping": True,
                "pool_recycle": dest_pool_recycle,
            }

            if dest_db_type in ("postgresql", "postgres"):
                engine_args["executemany_mode"] = "values_plus_batch"
                engine_args["executemany_batch_page_size"] = 10000
                engine_args["insertmanyvalues_page_size"] = 10000

            if dest_db_type in ("mssql", "sqlserver"):
                engine_args["fast_executemany"] = True

            data_dir = self._determine_data_dir()
            if dest_db_type == "duckdb":
                duckdb_path = f"{data_dir}/{destination_schema}.duckdb"
                dest_conn_string = f"duckdb:///{duckdb_path}"

            if dest_db_type in ["postgresql", "postgres", "mysql", "mssql", "sqlserver", "oracle", "duckdb", "sqlite"]:
                destination = dlt.destinations.sqlalchemy(credentials=dest_conn_string, engine_args=engine_args)
            elif dest_db_type == "snowflake":
                destination = dlt.destinations.snowflake(dest_conn_string)
            elif dest_db_type == "bigquery":
                destination = dlt.destinations.bigquery(dest_conn_string)
            elif dest_db_type == "redshift":
                destination = dlt.destinations.redshift(dest_conn_string)
            else:
                destination = dlt.destinations.sqlalchemy(credentials=dest_conn_string, engine_args=engine_args)

            if pipelines_dir is None:
                pipelines_dir = os.getenv('DLT_DATA_DIR')
            if pipelines_dir is None:
                if os.path.exists('/opt/airflow/dlt/dlt_state'):
                    pipelines_dir = '/opt/airflow/dlt/dlt_state'
                else:
                    pipelines_dir = '/app/.dlt'

            pipeline = dlt.pipeline(
                pipeline_name=pipeline_name,
                destination=destination,
                dataset_name=destination_schema,
                pipelines_dir=pipelines_dir
            )

            info = pipeline.run(source_resource)

            dlt_load_id = info.loads_ids if info.loads_ids else []
            has_failed = info.has_failed_jobs
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            row_counts = self._extract_per_table_row_counts(pipeline)
            rows_migrated = sum(count for table, count in row_counts.items() if not table.startswith('_dlt_'))
            if rows_migrated == 0:
                rows_migrated = self._extract_row_count(info)

            schema_info = self._extract_schema_info(info, pipeline)
            total_cols = sum(table_info.get('column_count', 0) for table_info in schema_info.values())

            if audit_tracker:
                try:
                    audit_tracker.record(self._echo_function)(
                        rows_migrated, 
                        total_cols, 
                        old_df=None, 
                        step_name='dms_migration_step'
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to record audit: {e}")

            result = {
                "success": not has_failed,
                "source": file_name,
                "destination": f"{destination_schema}.{destination_table}",
                "source_db_type": "flat_file",
                "destination_db_type": dest_db_type,
                "mode": mode,
                "rows_migrated": rows_migrated,
                "row_counts": row_counts,
                "schema_info": schema_info,
                "failed_step": None,
                "duration_seconds": round(duration, 2),
                "dlt_load_id": dlt_load_id,
                "pipeline_name": pipeline_name,
                "pipeline_working_dir": pipeline.working_dir,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "error": "DLT reported failed jobs" if has_failed else None
            }

            self.execution_metadata = result
            return result

        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            error_msg = str(e)
            error_trace = traceback.format_exc()

            self.logger.error(" MIGRATION (FILES) FAILED")
            self.logger.error(f"Error: {error_msg}")
            
            row_counts, failed_step, schema_info = self._extract_failure_progress(pipeline)
            rows_migrated = sum(count for table, count in row_counts.items() if not table.startswith('_dlt_'))
            
            result = {
                "success": False,
                "source": file_name,
                "destination": f"{destination_schema}.{destination_table}",
                "source_db_type": "flat_file",
                "destination_db_type": destination_connection.get("db_type", "unknown") if destination_connection else "unknown",
                "mode": mode,
                "rows_migrated": rows_migrated,
                "row_counts": row_counts,
                "schema_info": schema_info,
                "failed_step": failed_step,
                "duration_seconds": round(duration, 2),
                "dlt_load_id": None,
                "pipeline_name": pipeline_name,
                "pipeline_working_dir": pipeline.working_dir if pipeline else None,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "error": error_msg,
                "traceback": error_trace
            }
            self.execution_metadata = result
            return result

    # ---------- utilities ----------
    def _extract_row_count(self, info) -> int:
        """Extract row count from DLT info (fallback method)."""
        try:
            rows = 0
            if hasattr(info, "load_packages"):
                for package in info.load_packages:
                    if hasattr(package, "jobs"):
                        for job in package.jobs:
                            if hasattr(job, "metrics") and "rows" in job.metrics:
                                rows += job.metrics["rows"]
            return rows
        except Exception as e:
            self.logger.warning(f"Could not extract row count: {e}")
            return 0

    def _apply_transformations(self,
                               source,
                               column_selection: Optional[List[str]],
                               column_mapping: Optional[Dict[str, str]],
                               destination_table: str,
                               mode: str,
                               primary_key: Optional[List[str]],
                               increment_key: Optional[Union[str, List[str]]] = None) -> Any:
        """
        Apply column selection/mapping using add_map
        """
        is_multi_column = isinstance(increment_key, (list, tuple)) and len(increment_key) > 1
        
        def transform_row(row):
            """Transform a single row according to selection and mapping rules"""
            # Extract synthetic cursor value from original row before selection.
            # Values are converted to JSON-safe types so DLT can serialize the
            # cursor checkpoint without crashing on datetime/Decimal/UUID/bytes.
            cursor_val = None
            if is_multi_column:
                cursor_val = [
                    MigrationEngine._to_json_safe(row.get(col))
                    for col in increment_key
                ]

            # Apply column selection
            if column_selection:
                filtered_row = {col: row.get(col) for col in column_selection if col in row}
            else:
                filtered_row = dict(row)

            # Apply column mapping
            if column_mapping:
                final_row = {}
                for old_name, value in filtered_row.items():
                    new_name = column_mapping.get(old_name, old_name)
                    final_row[new_name] = value
            else:
                final_row = filtered_row

            # Inject synthetic column if multi-column
            if is_multi_column:
                final_row["_dms_increment_key"] = cursor_val

            return final_row

        # Log transformations
        if column_selection:
            self.logger.info(f"Column selection: {column_selection}")
        if column_mapping:
            self.logger.info(f"Column mapping: {column_mapping}")

        # Use add_map to transform the source
        transformed = source.add_map(transform_row)
        
        # Apply hints to the transformed resource
        hints = {
            "table_name": destination_table,
            "write_disposition": mode
        }
        if primary_key:
            hints["primary_key"] = primary_key
            
        actual_increment_key = None
        if increment_key and mode in ("append", "merge"):
            if is_multi_column:
                actual_increment_key = "_dms_increment_key"
            elif isinstance(increment_key, (list, tuple)):
                actual_increment_key = increment_key[0]
            else:
                actual_increment_key = increment_key
                
        if actual_increment_key:
            hints["incremental"] = dlt.sources.incremental(actual_increment_key)
            self.logger.info(f"  Incremental key (CDC): {actual_increment_key}")
            if actual_increment_key == "_dms_increment_key":
                hints["columns"] = {"_dms_increment_key": {"data_type": "json"}}
            
        transformed.apply_hints(**hints)
        
        return transformed

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata from the last migration execution"""
        return self.execution_metadata

    def cleanup(self):
        """Close all cached engine connections"""
        for key, engine in self._engine_cache.items():
            try:
                engine.dispose()
                self.logger.info(f"Disposed engine: {key}")
            except Exception as e:
                self.logger.warning(f"Error disposing engine {key}: {e}")
        self._engine_cache.clear()

    @staticmethod
    def _to_json_safe(val):
        """Convert a value to a JSON-serializable type.

        DLT serializes the incremental cursor checkpoint to JSON. Native Python
        types like datetime, Decimal, UUID, and bytes are not handled by the
        stdlib json encoder, so we normalise them here before they are stored
        in the synthetic ``_dms_increment_key`` column.

        ISO 8601 strings sort lexicographically in the same order as the
        underlying datetimes, so DLT's ``>=`` cursor comparison still works
        correctly after conversion.
        """
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        if isinstance(val, Decimal):
            return str(val)
        if isinstance(val, (bytes, bytearray)):
            return val.decode("utf-8", errors="replace")
        if isinstance(val, uuid.UUID):
            return str(val)
        # int, float, str, bool, None are already JSON-safe
        return val


# ------------------------------------------------------------------------------
# Convenience helpers
# ------------------------------------------------------------------------------
def migrate_append(source_connection: Dict[str, Any],
                   source_table: str,
                   destination_connection: Dict[str, Any],
                   destination_table: str,
                   dest_pool_size: int = 10,
                   dest_max_overflow: int = 20,
                   **kwargs) -> Dict[str, Any]:
    """Convenience function for append mode migration"""
    engine = MigrationEngine()
    try:
        return engine.migrate(
            source_connection=source_connection,
            source_table=source_table,
            destination_connection=destination_connection,
            destination_table=destination_table,
            mode="append",
            dest_pool_size=dest_pool_size,
            dest_max_overflow=dest_max_overflow,
            **kwargs
        )
    finally:
        engine.cleanup()


def migrate_replace(source_connection: Dict[str, Any],
                    source_table: str,
                    destination_connection: Dict[str, Any],
                    destination_table: str,
                    dest_pool_size: int = 10,
                    dest_max_overflow: int = 20,
                    **kwargs) -> Dict[str, Any]:
    """Convenience function for replace mode migration"""
    engine = MigrationEngine()
    try:
        return engine.migrate(
            source_connection=source_connection,
            source_table=source_table,
            destination_connection=destination_connection,
            destination_table=destination_table,
            mode="replace",
            dest_pool_size=dest_pool_size,
            dest_max_overflow=dest_max_overflow,
            **kwargs
        )
    finally:
        engine.cleanup()


def migrate_merge(source_connection: Dict[str, Any],
                  source_table: str,
                  destination_connection: Dict[str, Any],
                  destination_table: str,
                  primary_key: List[str],
                  dest_pool_size: int = 10,
                  dest_max_overflow: int = 20,
                  **kwargs) -> Dict[str, Any]:
    """Convenience function for merge mode migration"""
    engine = MigrationEngine()
    try:
        return engine.migrate(
            source_connection=source_connection,
            source_table=source_table,
            destination_connection=destination_connection,
            destination_table=destination_table,
            mode="merge",
            primary_key=primary_key,
            dest_pool_size=dest_pool_size,
            dest_max_overflow=dest_max_overflow,
            **kwargs
        )
    finally:
        engine.cleanup()