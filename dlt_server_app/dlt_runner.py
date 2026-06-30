"""
DLT Runner - Entry point for DLT engine execution
Extract migration config from chats collection based on job_id
Extracts connection IDs from chat history and fetches details from connections collection
Saves run details to dms_schedule_progress collection for audit logging
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Dict, Any

# Add paths
sys.path.insert(0, '/opt/airflow/inbuilt_modules')
sys.path.insert(0, '/app')  # Add app path for migration_engine

import dlt
from dlt_server.configurations.mongo_to_yaml_translator import MongoToYamlTranslator
from dlt_server.configurations.prepare_connection_id import PrepareConnectionId
from dlt_server.configurations.configuration import Configuration
from dlt_server.configurations.replace_connections import ReplaceConnections
from dlt_server.configurations.baseConfig.config import localDirectory
from dlt_server.exceptions.exceptions import MainException
from dlt_server.configurations.mongo_to_yaml_translator import mongo_audit_runs, mongo_audit_usage

# Import MongoDB collections for migration helper
from dlt_server.configurations.mongo_to_yaml_translator import mongo_schedule
from dlt_server.connectors.connector import MongoConnector
from core.mongo.mongo_factory import MongoFactory

# Get mongo_connections and mongo_chats
mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
mongo_connections = MongoFactory(mongo_client, "connections")
mongo_chats = MongoFactory(mongo_client, "chats")  # Add chats collection

# Add DMS schedule progress collection for audit logging
mongo_dms_progress = MongoFactory(mongo_client, "dms_schedule_progress")

# Add audit collections for AuditTracker
mongo_audit_runs = MongoFactory(mongo_client, "audit_runs")
mongo_audit_usage = MongoFactory(mongo_client, "audit_usage")

from helper.helper.helper import (
    create_file_operations, 
    create_dataframe_operations, 
    DltReadOrWriteFiles, 
    DltDataframeInformation, 
    JobArguments, 
    Connection
)
from audit_tracker.audit_tracker import AuditTracker, ScheduleRunContext, AuditDFType

# Import Migration Engine
try:
    from migrations.migration_engine import MigrationEngine, migrate_append, migrate_replace, migrate_merge
    MIGRATION_ENGINE_AVAILABLE = True
    logging.info("Migration Engine available")
except ImportError as e:
    MIGRATION_ENGINE_AVAILABLE = False
    logging.warning(f"Migration Engine not available: {e}")

# Initialize DLT components 
mongo_to_yaml = MongoToYamlTranslator()
prepare_connection_id = PrepareConnectionId()
configuration = Configuration()
replace_connections = ReplaceConnections()


class DLTRunner:
    """
    Main runner class for DLT operations
    Handles initialization, execution, and cleanup
    Supports extracting migration config from chats collection (job_id based)
    Saves run details to dms_schedule_progress for audit logging
    """

    def __init__(self, job_id: str, user_id: str, schedule_id: str, run_id: str):
        self.job_id = job_id
        self.user_id = user_id
        self.schedule_id = schedule_id
        self.run_id = run_id
        
        # Initialize MongoToYamlTranslator
        self.mongo_to_yaml = MongoToYamlTranslator()
        
        #  Setup paths - Check if running via Airflow with --volumes-from
        if os.path.exists('/opt/airflow/dlt'):
            # Running via Airflow with --volumes-from
            self.data_dir = Path('/opt/airflow/dlt/dlt_data')
            self.state_dir = Path('/opt/airflow/dlt/dlt_state') / schedule_id
            self.logs_dir = self.state_dir / 'logs'
            self.using_airflow_paths = True
        else:
            # Fallback for standalone testing or direct execution
            self.data_dir = Path('/app/data')
            self.state_dir = Path('/app/.dlt')
            self.logs_dir = self.state_dir / 'logs'
            self.using_airflow_paths = False
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        #  Set DLT_DATA_DIR - use env var if set, otherwise use detected path
        if 'DLT_DATA_DIR' not in os.environ:
            os.environ['DLT_DATA_DIR'] = str(self.state_dir)
        
        # Setup logging
        self._setup_logging()
        
        #  Log configuration
        self.logger.info("="*60)
        self.logger.info("DLT RUNNER CONFIGURATION")
        self.logger.info("="*60)
        self.logger.info(f"Job ID: {self.job_id}")
        self.logger.info(f"Schedule ID: {self.schedule_id}")
        self.logger.info(f"Run ID: {self.run_id}")
        self.logger.info(f"Using Airflow paths: {self.using_airflow_paths}")
        self.logger.info(f"Data directory: {self.data_dir}")
        self.logger.info(f"State directory: {self.state_dir}")
        self.logger.info(f"Logs directory: {self.logs_dir}")
        self.logger.info(f"DLT_DATA_DIR env: {os.environ.get('DLT_DATA_DIR')}")
        self.logger.info("="*60)
        
        self.logger.debug(f"DLT Runner initialized for job_id: {job_id}, schedule_id: {schedule_id}, run_id: {run_id}")
    
    def _setup_logging(self):
        """Setup structured logging for DLT operations"""
        log_file = self.logs_dir / f"dlt_run_{self.run_id}.log"
        
        # Create logger
        self.logger = logging.getLogger('dlt_runner')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [Job:%(job_id)s] [Run:%(run_id)s] - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Add custom fields to all logs
        old_factory = logging.getLogRecordFactory()
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.job_id = self.job_id
            record.run_id = self.run_id
            return record
        logging.setLogRecordFactory(record_factory)
    
    def _save_run_details(self, result: dict):
        """
        Save DMS pipeline run details to dms_schedule_progress collection.
        
        Args:
            result: Migration result dict from migration_engine.migrate()
        """
        try:
            run_record = {
                'schedule_id': self.schedule_id,
                'run_id': self.run_id,
                'job_id': self.job_id,
                'user_id': self.user_id,
                
                # Timing
                'started_at': result.get('started_at'),
                'completed_at': result.get('completed_at'),
                'duration_seconds': result.get('duration_seconds'),
                
                # Status
                'status': 'COMPLETED' if result.get('success') else 'FAILED',
                'failed_step': result.get('failed_step'),
                'error_message': result.get('error'),
                
                # Row Metrics
                'total_rows_transferred': result.get('rows_migrated', 0),
                'row_counts': result.get('row_counts', {}),
                
                # Schema/Column Metrics
                'schema_info': result.get('schema_info', {}),
                
                # DLT Reference
                'dlt_load_id': result.get('dlt_load_id'),
                
                # Additional info
                'source': result.get('source'),
                'destination': result.get('destination'),
                'source_db_type': result.get('source_db_type'),
                'destination_db_type': result.get('destination_db_type'),
                'mode': result.get('mode'),
                'pipeline_name': result.get('pipeline_name'),
                'pipeline_working_dir': result.get('pipeline_working_dir')
            }
            
            # Insert into MongoDB
            mongo_dms_progress.collection.insert_one(run_record)
            
            self.logger.info(f"Saved run details to dms_schedule_progress: schedule_id={self.schedule_id}, run_id={self.run_id}, status={run_record['status']}")
            
        except Exception as e:
            self.logger.error(f"Failed to save run details to MongoDB: {e}")
            # Don't raise - we don't want to fail the migration just because audit logging failed
    
    def load_job_config(self) -> Dict[str, Any]:
        """Load job configuration from the API or local cache"""
        self.logger.debug("Loading job configuration...")
        
        config = {
            "source": {
                "type": "postgres",
                "connection_string": os.getenv("SOURCE_CONNECTION_STRING"),
                "tables": ["users", "orders", "products"]
            },
            "destination": {
                "type": "postgres", 
                "connection_string": os.getenv("DEST_CONNECTION_STRING"),
                "dataset_name": f"cdc_data_{self.schedule_id}"
            },
            "cdc_settings": {
                "mode": "incremental",
                "cursor_column": "updated_at",
                "primary_key": "id"
            },
            "pipeline_code": None
        }
        
        return config
    
    def execute_code_mode(self, config: Dict[str, Any], service_type) -> bool:  
        """
        Execute DLT pipeline in code mode
        This allows running custom DLT code from the ACE editor
        Includes: MigrationEngine in global scope
        """
        try:
            self.logger.debug("Executing DLT pipeline in code mode")
            self.logger.debug(f"Executing for schedule_id: {self.schedule_id}, config: {config}")
            
            # Get code from MongoDB using MongoToYamlTranslator
            self.logger.debug(f"Fetching code from MongoDB for schedule_id: {self.schedule_id}")
            user_code = self.mongo_to_yaml.get_code(self.schedule_id)
            
            connection_id_dict = prepare_connection_id.process(self.schedule_id, self.user_id)
            connection_id_dict = replace_connections.process(connection_id_dict, self.schedule_id, self.user_id)
            config = configuration.get(self.schedule_id)
            self.logger.debug(f"connection_id_dict: {connection_id_dict}")

            # Create DLT engine instances
            file_ops: DltReadOrWriteFiles = create_file_operations("dlt", self.user_id, localDirectory._path)
            df_ops: DltDataframeInformation = create_dataframe_operations("dlt", {})

            # Build tracker 
            aod_audit_tracker = AuditTracker(
                audit_runs_collection=mongo_audit_runs,
                audit_usage_collection=mongo_audit_usage,
                run_context=ScheduleRunContext(
                    user_id=self.user_id,
                    chat_id=self.job_id,
                    schedule_id=self.schedule_id,
                    run_id=self.run_id,
                    execution_type="code",
                    service_type=service_type
                ),
            )

            # Build global scope with Migration Engine
            global_scope = {
                "__name__": "__main__",
                "__package__": None,
                "Connection": Connection(connection_id_dict),
                "connection": connection_id_dict,
                "JobArguments": JobArguments(config),
                "DataframeInformation": df_ops,
                "ReadOrWriteFiles": file_ops,
                "AodAudit": aod_audit_tracker,
                "AuditDFType": AuditDFType,
            }
            
            # Add Migration Engine to global scope if available
            if MIGRATION_ENGINE_AVAILABLE:
                global_scope.update({
                    "MigrationEngine": MigrationEngine,
                    "migrate_append": migrate_append,
                    "migrate_replace": migrate_replace,
                    "migrate_merge": migrate_merge
                })
                self.logger.info("Migration Engine loaded and available in code mode")
                self.logger.info("Mode can be specified explicitly or extracted from JobArguments")
            else:
                self.logger.warning("Migration Engine not available")

            # Execute user code
            exec(user_code, global_scope)

            self.logger.info("Pipeline execution completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing code mode pipeline: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise MainException("Failed to process the code..") from e

    def execute_pipeline_mode(self, config: Dict[str, Any], service_type) -> bool:
        """
        Execute DLT pipeline using predefined configuration
        Extract from chats collection based on job_id
        Mode comes from JobArguments or chat config
        Saves run details to dms_schedule_progress for audit
        """
        try:
            self.logger.info("EXECUTING PIPELINE MODE - MIGRATION FROM CHAT")
            self.logger.info(f"DLT_DATA_DIR: {os.getenv('DLT_DATA_DIR')}")
            self.logger.info(f"Expected working dir: {os.getenv('DLT_DATA_DIR')}/pipelines/...")

            # TODO: We should be able to get rid of the flag "MIGRATION_ENGINE_AVAILABLE" from this file
            if not MIGRATION_ENGINE_AVAILABLE:
                raise Exception("Migration Engine not available")

            # Import the migration helper
            try:
                from migrations.migration_helper import extract_migration_config_from_schedule_pipeline
            except ImportError as e:
                self.logger.error(f"Failed to import migration_helper: {e}")
                self.logger.error("Make sure migration_helper.py is in the migrations/ folder")
                raise

            # Extract migration configuration from schedule collection based on schedule_id
            self.logger.info(f"Extracting migration config from schedule collection")
            self.logger.info(f"  Schedule ID: {self.schedule_id}")
            self.logger.info("  Method: Extract from schedule pipeline → fetch connection details")

            try:
                self.logger.info("Step 1: Reading schedule document from schedule collection...")
                migration_config = extract_migration_config_from_schedule_pipeline(
                    schedule_id=self.schedule_id,
                    mongo_schedule=mongo_schedule,
                    mongo_connections=mongo_connections
                )
                self.logger.info("Successfully extracted config from schedule pipeline")
                # custom_config = configuration.get(self.schedule_id)
                # self.logger.info(f"Custom job arguments : {custom_config}")
                # for key, value in custom_config.items():
                #     if key in migration_config:
                #         # if type of value is dict use .update otherwise assign value
                #         if isinstance(value, dict):
                #             migration_config[key].update(value)
                #         else:
                #             migration_config[key] = value
                # self.logger.info(f"Updated migration config : {migration_config}")
            except Exception as e:
                self.logger.error(f"Failed to extract migration config from schedule: {e}")
                self.logger.error(f"Error type: {type(e).__name__}")
                self.logger.error(f"Error details: {str(e)}")

                # Debugging info
                # TODO: Following is jut debug information in case 'data_migration' step could not be loaded.
                #   We should be able to remove this as well.
                try:
                    from bson import ObjectId
                    success, schedule_doc = mongo_schedule.get_by_id(ObjectId(self.schedule_id))
                    if success and schedule_doc:
                        pipeline = schedule_doc.get('pipeline', [])
                        self.logger.error(f"Debug: Schedule has {len(pipeline)} pipeline steps")

                        has_data_migration = any(s.get('function') == 'data_migration' for s in pipeline)
                        self.logger.error(f"Debug: Has data_migration step: {has_data_migration}")

                        if not has_data_migration:
                            self.logger.error("   Missing data_migration step in schedule pipeline")
                            self.logger.error("   Available functions:")
                            for step in pipeline:
                                func = step.get('function', 'unknown')
                                self.logger.error(f"     - {func}")
                    else:
                        self.logger.error(f"Debug: Schedule document not found for schedule_id: {self.schedule_id}")

                except Exception as debug_error:
                    self.logger.error(f"Could not gather debug info: {debug_error}")

                self.logger.error("Please check that your schedule document has:")
                self.logger.error("  1. pipeline array with data_migration step")
                self.logger.error("  2. source_parameters with connection_id and table_name")
                self.logger.error("  3. destination_parameters with connection_id and table_name")
                self.logger.error("  4. Connection documents exist in connections collection")
                raise

            self.logger.info("Migration configuration extracted from schedule")
            self.logger.info(f"  Source: {migration_config['source_schema']}.{migration_config['source_table']}")
            self.logger.info(f"  Destination: {migration_config['destination_schema']}.{migration_config['destination_table']}")
            self.logger.info(f"  Mode: {migration_config.get('mode', 'replace')}")
            self.logger.info(f"  Migration Type: {migration_config.get('migration_type', 'table-to-table')}")

            # Get JobArguments config (optional overrides)
            try:
                job_config = configuration.get(self.schedule_id)
                job_arguments = JobArguments(job_config)
                ja_config = job_arguments.get() or {}
            except:
                ja_config = {}

            # Mode 
            mode = ja_config.get("migration_mode") or migration_config.get('mode', 'replace')
            self.logger.info(f"  Using mode: {mode}")

            # Keys
            primary_key = ja_config.get("primary_key") or migration_config.get('primary_key')
            if primary_key:
                self.logger.info(f"  Primary key: {primary_key}")

            # Increment key (CDC)
            increment_key = ja_config.get("increment_key") or migration_config.get('increment_key')
            if increment_key:
                self.logger.info(f"  Increment key (CDC): {increment_key}")

            # Query / Where clause - prefer from migration_config (from chat), fallback to JobArguments
            query = migration_config.get('query') or ja_config.get("query") or ja_config.get("source_query")
            where_clause = migration_config.get('where_clause') or ja_config.get("where") or ja_config.get("where_clause")
            
            # Column selection and mapping from migration_config
            column_selection = migration_config.get('column_selection')
            column_mapping = migration_config.get('column_mapping')

            if query:
                q_log = query.strip().replace("\n", " ")
                self.logger.info(f"  Custom query detected (first 200 chars): {q_log[:200]}")
            if where_clause and not query:
                self.logger.info(f"  Where clause detected: {where_clause}")
            if column_selection:
                self.logger.info(f"  Column selection: {column_selection}")
            if column_mapping:
                self.logger.info(f"  Column mapping: {column_mapping}")
            
            # Build audit tracker for DMS pipeline
            aod_audit_tracker = AuditTracker(
                audit_runs_collection=mongo_audit_runs,
                audit_usage_collection=mongo_audit_usage,
                run_context=ScheduleRunContext(
                    user_id=self.user_id,
                    chat_id=self.job_id,
                    schedule_id=self.schedule_id,
                    run_id=self.run_id,
                    execution_type="pipeline",
                    service_type=service_type
                )
            )
            # Initialize migration engine
            migration_engine = MigrationEngine(logger=self.logger)

            # Execute migration
            self.logger.info("STARTING MIGRATION")
            
            #  Use detected path for DuckDB
            if migration_config['destination_connection']['db_type'].lower() == 'duckdb':
                duckdb_path = str(self.data_dir / f"{migration_config['destination_schema']}.duckdb")
                self.logger.info(f"DuckDB path: {duckdb_path}")
            
            #  Get pipelines_dir from env (set by DAG)
            pipelines_dir = os.getenv('DLT_DATA_DIR', str(self.state_dir))

            # (#1576) TEMPORARY FIX: We will use dms_{destination_table} instead of {destination_table}
            # This will help in avoiding case where metadata is not present in destination table already
            destination_table_name = f"dms_{migration_config['destination_table']}"
            
            source_connection = migration_config['source_connection']
            if source_connection.get('db_type') == 'flat_file':
                self.logger.info("Using flat_file source, mapping to migrate_files()")
                from dlt_server.connectors.mongo_operations import MongoOperations
                mongo_ops = MongoOperations()
                
                file_id = source_connection.get('file_id')
                file_name = source_connection.get('file_name', '')
                
                # Retrieve file details
                file_path = mongo_ops.get_filepath_by_file_and_user_id(self.user_id, file_id)
                file_type = mongo_ops.get_filetype_by_file_and_user_id(self.user_id, file_id)
                
                if not file_path:
                    raise ValueError(f"Could not resolve physical file path for file_id: {file_id}")
                
                result = migration_engine.migrate_files(
                    file_path=file_path,
                    file_name=file_name,
                    file_type=file_type,
                    destination_connection=migration_config['destination_connection'],
                    destination_table=destination_table_name,
                    destination_schema=migration_config['destination_schema'],
                    mode=mode,
                    primary_key=primary_key,
                    pipelines_dir=pipelines_dir,
                    audit_tracker=aod_audit_tracker
                )
            else:
                result = migration_engine.migrate(
                    source_connection=migration_config['source_connection'],
                    source_table=migration_config['source_table'],
                    source_schema=migration_config['source_schema'],
                    destination_connection=migration_config['destination_connection'],
                    destination_table=destination_table_name,
                    destination_schema=migration_config['destination_schema'],
                    mode=mode,
                    primary_key=primary_key,
                    query=query,
                    where_clause=where_clause,
                    column_selection=column_selection,
                    column_mapping=column_mapping,
                    increment_key=increment_key,
                    pipelines_dir=pipelines_dir,  #  Use from environment
                    audit_tracker=aod_audit_tracker  # Pass audit tracker
                )
            
            self.logger.info(f"Migration result : {result}")
            
            # Save run details to MongoDB for audit
            self._save_run_details(result)
            
            if result['success']:
                self.logger.info("MIGRATION COMPLETED SUCCESSFULLY")
                self.logger.info(f"  Duration: {result['duration_seconds']:.2f}s")
                self.logger.info(f"  Mode: {result.get('mode', 'unknown')}")
                self.logger.info(f"  DLT Load ID: {result.get('dlt_load_id', 'unknown')}")
                self.logger.info(f"  Source: {result.get('source', 'unknown')}")
                self.logger.info(f"  Destination: {result.get('destination', 'unknown')}")
            else:
                self.logger.error("MIGRATION FAILED")
                self.logger.error(f"  Error: {result.get('error', 'Unknown')}")
                if 'traceback' in result:
                    self.logger.error(f"  Traceback: {result['traceback']}")

            #  Check file creation
            self.logger.info("CHECKING FILE CREATION")
            
            import subprocess
            try:
                # Check state directory
                state_dir_check = str(self.state_dir)
                self.logger.info(f"Checking: {state_dir_check}")
                if os.path.exists(state_dir_check):
                    output = subprocess.check_output(['ls', '-la', state_dir_check], text=True)
                    self.logger.info(f"{state_dir_check} contents:\n{output}")
                else:
                    self.logger.error(f"{state_dir_check} does not exist!")
   
            except Exception as e:
                self.logger.error(f"Error checking directories: {e}")

            # Cleanup
            migration_engine.cleanup()

            return result["success"]

        except Exception as e:
            self.logger.error("PIPELINE MODE FAILED")
            self.logger.error(f"Error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def execute_migration_mode(self, config: Dict[str, Any], service_type) -> bool:
        """Alias for pipeline mode"""
        self.logger.info("Migration mode redirecting to pipeline mode...")
        return self.execute_pipeline_mode(config, service_type)
    
    def run(self, execution_type: str = "code", service_type: str = "dts") -> bool:  
        """
        Main execution method
        Supported execution_types: "code", "pipeline", "migration"
        """
        try:
            self.logger.info(f"Starting DLT pipeline execution in {execution_type} mode")
            
            # Load job configuration
            config = self.load_job_config()
            
            # Execute based on execution_type
            if execution_type == "code":
                return self.execute_code_mode(config, service_type) 
            elif execution_type == "pipeline":
                return self.execute_pipeline_mode(config, service_type)
            elif execution_type == "migration":
                return self.execute_migration_mode(config, service_type)
            else:
                self.logger.error(f"Unknown execution type: {execution_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def cleanup(self):
        """Cleanup resources after execution"""
        self.logger.debug("Cleaning up DLT runner resources")


def main():
    """Main entry point"""
    if len(sys.argv) < 6:
        print("Usage: python dlt_runner.py <job_id> <user_id> <schedule_id> <run_id> <execution_type> <service_type>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    user_id = sys.argv[2]
    schedule_id = sys.argv[3]
    run_id = sys.argv[4]
    execution_type = sys.argv[5]  # code, pipeline, migration
    try:
        service_type = sys.argv[6]
    except IndexError:
        service_type = "dts"
    
    # Initialize runner
    runner = DLTRunner(job_id, user_id, schedule_id, run_id)
    
    try:
        success = runner.run(execution_type=execution_type, service_type=service_type)
        sys.exit(0 if success else 1)
        
    except Exception as e:
        runner.logger.error(f"Fatal error in DLT runner: {str(e)}")
        sys.exit(1)
    finally:
        runner.cleanup()


if __name__ == "__main__":
    main()