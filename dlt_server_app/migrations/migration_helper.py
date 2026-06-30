"""
Migration Helper - Extract connection details from MongoDB
Support for all RDBMS types + Chat Collection Extraction
"""

import logging
from typing import Dict, Any, Optional
from bson import ObjectId

logger = logging.getLogger(__name__)


class MigrationConfigExtractor:
    """
    Extracts migration configuration from MongoDB schedule/chat and connection documents
    Returns properly formatted source/destination connection dicts for MigrationEngine
    Supports all database types + chat collection extraction
    """
    
    def __init__(self, mongo_schedule, mongo_connections):
        """
        Initialize with MongoDB collections
        
        Args:
            mongo_schedule: MongoFactory instance for schedule collection (or chats collection)
            mongo_connections: MongoFactory instance for connections collection
        """
        self.mongo_schedule = mongo_schedule
        self.mongo_connections = mongo_connections
    
    def get_connection_by_id(self, connection_id: str) -> Dict[str, Any]:
        """Get connection details from connections collection"""
        try:
            if isinstance(connection_id, str):
                connection_id = ObjectId(connection_id)
            
            success, conn_doc = self.mongo_connections.get_by_id(connection_id)
            
            if not success or not conn_doc:
                raise ValueError(f"Connection not found: {connection_id}")
            
            return conn_doc
            
        except Exception as e:
            logger.error(f"Error getting connection {connection_id}: {e}")
            raise
    
    def extract_connection_dict(self, connection_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract connection parameters from connection document
        
        Args:
            connection_doc: Connection document from MongoDB
        
        Returns:
            Dict with db_type and connection parameters
        """
        try:
            conn_details = connection_doc.get('connection_details', {})
            logger.info(f"Connection_doc : {connection_doc}")
            # Get database type (critical!)
            db_type = connection_doc.get('type', '').lower()
            logger.info(f"Connection type : {db_type}")
            
            logger.debug(f"Extracting connection for database type: {db_type}")
            
            # Add db_type to connection dict
            conn_details['db_type'] = db_type
            
            logger.debug(f"Extracted connection: {conn_details.get('sourceName', 'unknown')} ({db_type})")
            
            return conn_details
            
        except Exception as e:
            logger.error(f"Error extracting connection dict: {e}")
            raise

    
    def extract_from_schedule_pipeline(self, schedule_id: str) -> Dict[str, Any]:
        """
        Extract migration configuration from schedule collection based on schedule_id
        Parses the pipeline array to find data_migration function
        Supports custom-sql migration type with query extraction
        
        Args:
            schedule_id: MongoDB ObjectId of the schedule document
            
        Returns:
            Dict with migration configuration including query if custom-sql
        """
        try:
            if isinstance(schedule_id, str):
                schedule_id = ObjectId(schedule_id)
            
            # Get schedule document from schedule collection
            success, schedule_doc = self.mongo_schedule.get_by_id(schedule_id)
            logger.info(f"Processing schedule doc : {schedule_doc}")
            
            if not success or not schedule_doc:
                raise ValueError(f"Schedule document not found: {schedule_id}")
            
            logger.info(f"Processing schedule: {schedule_doc.get('schedule_name', 'Unnamed')}")
        
            pipeline = schedule_doc.get('pipeline', [])

            if not pipeline:
                raise ValueError("Pipeline is empty or not found in schedule document")

            # Handle case where pipeline is a single dict (not a list)
            if isinstance(pipeline, dict):
                # pipeline IS the migration step directly
                if pipeline.get('function') == 'data_migration':
                    migration_step = pipeline
                    logger.info(f"Found data_migration step: {migration_step}")
                else:
                    raise ValueError("Pipeline dict does not contain data_migration function")
            elif isinstance(pipeline, list):
                #logic for list of steps
                logger.info(f"Found {len(pipeline)} steps in pipeline")
                
                if not pipeline:
                    raise ValueError("Pipeline is empty or not found in schedule document")
                
                # Find data_migration step
                migration_step = None
                for step in pipeline:
                    logger.info(f"Checking step: {step}")
                    if isinstance(step, dict) and step.get('function') == 'data_migration':
                        migration_step = step
                        logger.info(f"Found data_migration step: {step}")
                        break
                
                if not migration_step:
                    raise ValueError("Could not find data_migration step in schedule pipeline")
            else:
                raise ValueError(f"Unexpected pipeline type: {type(pipeline)}")

                
            if not migration_step:
                raise ValueError("Could not find data_migration step in schedule pipeline")
            
            # Apply job arguments to modify YAML step parameters
            config = schedule_doc.get('configurations', {})
            for key, job_args in config.items():
                if key.startswith('__data_migration__') and isinstance(job_args, dict):
                    logger.info(f"Applying job arguments for data_migration: {job_args}")
                    
                    def deep_update(d, u):
                        import collections.abc
                        for k, v in u.items():
                            if isinstance(v, collections.abc.Mapping):
                                current = d.get(k, {})
                                if current is None:
                                    current = {}
                                d[k] = deep_update(current, v)
                            else:
                                d[k] = v
                        return d
                        
                    migration_step = deep_update(migration_step, job_args)
                    break
            
            # Extract source and destination parameters
            source_params = migration_step.get('source_parameters', {})
            dest_params = migration_step.get('destination_parameters', {})
            
            source_conn_id = source_params.get('connection_id')
            source_file_id = source_params.get('file_id')
            source_file_name = source_params.get('file_name', '')
            source_table_full = source_params.get('table_name', '')
            
            dest_conn_id = dest_params.get('connection_id')
            dest_table_full = dest_params.get('table_name', '')
            
            logger.info(f"Source: connection_id={source_conn_id}, file_id={source_file_id}, table={source_table_full}")
            logger.info(f"Destination: connection_id={dest_conn_id}, table={dest_table_full}")
            
            if not source_conn_id and not source_file_id:
                raise ValueError("Missing connection_id or file_id in source parameters")
            if not dest_conn_id:
                raise ValueError("Missing connection_id in destination parameters")
            
            # Parse schema.table format
            if '.' in source_table_full:
                source_schema, source_table = source_table_full.split('.', 1)
            else:
                source_schema = None
                source_table = source_table_full
            
            if '.' in dest_table_full:
                dest_schema, dest_table = dest_table_full.split('.', 1)
            else:
                dest_schema = None
                dest_table = dest_table_full
            
            # Fetch connection details from connections collection (or build explicitly for file_id)
            if source_file_id:
                logger.info(f"Building source connection for flat file: {source_file_id}")
                source_connection = {
                    'db_type': 'flat_file',
                    'file_id': source_file_id,
                    'file_name': source_file_name
                }
            else:
                logger.info(f"Fetching source connection: {source_conn_id}")
                source_conn_doc = self.get_connection_by_id(source_conn_id)
                logger.info("Extracting connection details...")
                source_connection = self.extract_connection_dict(source_conn_doc)
            
            logger.info(f"  Source: {source_connection.get('db_type', 'unknown')}")
            
            logger.info(f"Fetching destination connection: {dest_conn_id}")
            dest_conn_doc = self.get_connection_by_id(dest_conn_id)
            destination_connection = self.extract_connection_dict(dest_conn_doc)
            logger.info(f"  Destination: {destination_connection.get('db_type', 'unknown')}")
            
            # Use schema from connection if not in table name
            if not source_schema:
                source_schema = source_connection.get('schema', 'public')
            if not dest_schema:
                dest_schema = destination_connection.get('schema', 'public')
            
            # Get mode from migration step
            mode = migration_step.get('mode', 'replace')
            
            # Get primary_key if exists (for merge mode)
            primary_key = migration_step.get('primary_key')
            
            # Get migration_type and service info
            migration_type = migration_step.get('migration_type', 'table-to-table')
            service = migration_step.get('service', 'DMS')
            
            # Extract query, where_clause, columns, and column_mapping
            query = migration_step.get('query')
            where_clause = migration_step.get('where_clause')
            columns = source_params.get('columns', [])
            column_mapping = migration_step.get('column_mapping', {})
            column_selection = source_params.get('columns')  # List of columns to select
            increment_key = migration_step.get('increment_key')  # CDC cursor column
            
            logger.info(f"  Mode: {mode}")
            logger.info(f"  Migration Type: {migration_type}")
            logger.info(f"  Service: {service}")
            logger.info(f"  Primary key: {primary_key if primary_key else 'None'}")
            
            # Log query-related parameters
            if migration_type == 'custom-sql':
                if query:
                    query_preview = query.strip().replace('\n', ' ')[:200]
                    logger.info(f"  Custom SQL Query detected: {query_preview}...")
                else:
                    logger.warning("  Migration type is 'custom-sql' but no query found!")
            
            if where_clause:
                logger.info(f"  Where clause: {where_clause}")
            
            if columns:
                logger.info(f"  Column selection: {columns}")
            
            if column_mapping:
                logger.info(f"  Column mapping: {column_mapping}")
            
            return {
                'source_connection': source_connection,
                'destination_connection': destination_connection,
                'source_table': source_table,
                'destination_table': dest_table,
                'source_schema': source_schema,
                'destination_schema': dest_schema,
                'mode': mode,
                'primary_key': primary_key,
                'migration_type': migration_type,
                'service': service,
                'query': query,  # Custom SQL query
                'where_clause': where_clause,  # WHERE clause
                'column_selection': column_selection,  # Column selection
                'column_mapping': column_mapping,  #  Column mapping
                'increment_key': increment_key  # CDC cursor column
            }
            
        except Exception as e:
            logger.error(f"Error extracting from chat history: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def extract_from_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """
        Extract migration configuration from schedule document
        Handles all database types
        """
        try:
            if isinstance(schedule_id, str):
                schedule_id = ObjectId(schedule_id)
            
            success, schedule_doc = self.mongo_schedule.get_by_id(schedule_id)
            
            if not success or not schedule_doc:
                raise ValueError(f"Schedule not found: {schedule_id}")
            
            logger.info(f"Processing schedule: {schedule_doc.get('schedule_name', 'Unnamed')}")
            
            config = schedule_doc.get('configurations', {})
            
            if not config:
                raise ValueError("No configurations found in schedule")
            
            # Extract source connection
            source_conn_config = config.get('source_connection')
            if source_conn_config and isinstance(source_conn_config, dict):
                source_connection = self._extract_connection_from_config(source_conn_config)
                logger.info(f"  Source connection extracted: {source_connection.get('db_type', 'unknown')}")
            else:
                raise ValueError("source_connection not found or invalid in configurations")
            
            # Extract destination connection
            dest_conn_config = config.get('destination_connection')
            if dest_conn_config and isinstance(dest_conn_config, dict):
                destination_connection = self._extract_connection_from_config(dest_conn_config)
                logger.info(f"  Destination connection extracted: {destination_connection.get('db_type', 'unknown')}")
            else:
                raise ValueError("destination_connection not found or invalid in configurations")
            
            # Extract other migration parameters
            source_table = config.get('source_table')
            destination_table = config.get('destination_table')
            mode = config.get('mode', 'replace')
            primary_key = config.get('primary_key')
            source_schema = source_connection.get('schema', 'public')
            destination_schema = destination_connection.get('schema', 'public')
            
            logger.info(f"  Source: {source_schema}.{source_table} ({source_connection.get('db_type')})")
            logger.info(f"  Destination: {destination_schema}.{destination_table} ({destination_connection.get('db_type')})")
            logger.info(f"  Mode: {mode}")
            
            return {
                'source_connection': source_connection,
                'destination_connection': destination_connection,
                'source_table': source_table,
                'destination_table': destination_table,
                'source_schema': source_schema,
                'destination_schema': destination_schema,
                'mode': mode,
                'primary_key': primary_key
            }
            
        except Exception as e:
            logger.error(f"Error extracting from schedule {schedule_id}: {e}")
            raise
    
    def _extract_connection_from_config(self, conn_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract connection dict from inline configuration
        Handles all database types
        """
        db_type = conn_config.get('db_type', 'postgresql').lower()
        return {**conn_config, 'db_type': db_type}
    
    def extract_from_pipeline_and_connections(self, schedule_id: str) -> Dict[str, Any]:
        """
        Extract connection IDs from pipeline steps and fetch details from connections collection
        """
        try:
            if isinstance(schedule_id, str):
                schedule_id = ObjectId(schedule_id)
            
            success, schedule_doc = self.mongo_schedule.get_by_id(schedule_id)
            
            if not success or not schedule_doc:
                raise ValueError(f"Schedule not found: {schedule_id}")
            
            logger.info(f"Processing schedule: {schedule_doc.get('schedule_name', 'Unnamed')}")
            
            pipeline = schedule_doc.get('pipeline', [])
            logger.info(f"Found {len(pipeline)} steps in pipeline")
            logger.info(f"Pipeline : {pipeline} ")
            
            if not pipeline:
                raise ValueError("Pipeline is empty or not found in schedule document")
            
            # Find read_tables step (source)
            source_conn_id = None
            source_table = None
            source_schema = None
            
            for step in pipeline:
                if step.get('function') == 'read_tables':
                    source_conn_id = step.get('parameters', {}).get('connection_id')
                    table_name = step.get('parameters', {}).get('table_name', '')
                    if '.' in table_name:
                        source_schema, source_table = table_name.split('.', 1)
                        logger.info(f"source_schema : {source_schema} ")
                    else:
                        source_schema = None  # Will be set from connection
                        source_table = table_name
                    logger.info(f"Found source: connection_id={source_conn_id}, table={table_name} ,schema = {source_schema}")
                    break
            
            if not source_conn_id:
                raise ValueError("Could not find read_tables step with connection_id in pipeline")
            
            # Find export_table step (destination)
            dest_conn_id = None
            dest_table = None
            dest_schema = None
            
            for step in pipeline:
                if step.get('function') == 'export_table':
                    dest_conn_id = step.get('parameters', {}).get('connection_id')
                    table_name = step.get('parameters', {}).get('table_name', '')
                    if '.' in table_name:
                        dest_schema, dest_table = table_name.split('.', 1)
                    else:
                        dest_schema = None  # Will be set from connection
                        dest_table = table_name
                    logger.info(f"Found destination: connection_id={dest_conn_id}, table={table_name}")
                    break
            
            if not dest_conn_id:
                raise ValueError("Could not find export_table step with connection_id in pipeline")
            
            # Fetch connection details
            logger.info(f"Fetching source connection: {source_conn_id}")
            source_conn_doc = self.get_connection_by_id(source_conn_id)
            
            logger.info(f"Fetching destination connection: {dest_conn_id}")
            dest_conn_doc = self.get_connection_by_id(dest_conn_id)
            
            # Extract connection dicts (now supports all DB types)
            logger.info("Extracting connection details...")
            source_connection = self.extract_connection_dict(source_conn_doc)
            logger.info(f"  Source: {source_connection.get('db_type', 'unknown')}")
            
            destination_connection = self.extract_connection_dict(dest_conn_doc)
            logger.info(f"  Destination: {destination_connection.get('db_type', 'unknown')}")
            
            # Use schema from connection if not in table name
            if not source_schema:
                source_schema = source_connection.get('schema', 'public')
            if not dest_schema:
                dest_schema = destination_connection.get('schema', 'public')
            
            # Get mode from configurations
            config = schedule_doc.get('configurations', {})
            mode = config.get('mode', 'replace')
            primary_key = config.get('primary_key')
            
            logger.info(f"  Mode: {mode}")
            logger.info(f"  Primary key: {primary_key if primary_key else 'None'}")
            
            return {
                'source_connection': source_connection,
                'destination_connection': destination_connection,
                'source_table': source_table,
                'destination_table': dest_table,
                'source_schema': source_schema,
                'destination_schema': dest_schema,
                'mode': mode,
                'primary_key': primary_key
            }
            
        except Exception as e:
            logger.error(f"Error extracting from pipeline: {e}")
            raise


def extract_migration_config(schedule_id: str, mongo_schedule, mongo_connections=None) -> Dict[str, Any]:
    """
    Convenience function to extract migration configuration
    """
    extractor = MigrationConfigExtractor(mongo_schedule, mongo_connections)
    
    try:
        return extractor.extract_from_schedule(schedule_id)
    except Exception as e:
        logger.warning(f"Could not extract from schedule config: {e}")
        
        if mongo_connections:
            logger.info("Trying to extract from pipeline and connections...")
            return extractor.extract_from_pipeline_and_connections(schedule_id)
        else:
            raise


def extract_migration_config_from_schedule_pipeline(schedule_id: str, mongo_schedule, mongo_connections) -> Dict[str, Any]:
    """
    Convenience function to extract migration configuration from schedule's pipeline
    
    Args:
        schedule_id: MongoDB ObjectId of the schedule document
        mongo_schedule: MongoFactory instance for schedule collection
        mongo_connections: MongoFactory instance for connections collection
    
    Returns:
        Dict with migration configuration extracted from schedule pipeline
    """
    extractor = MigrationConfigExtractor(mongo_schedule, mongo_connections)
    return extractor.extract_from_schedule_pipeline(schedule_id)