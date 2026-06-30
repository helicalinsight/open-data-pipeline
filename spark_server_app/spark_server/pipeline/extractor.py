
import os
from abc import ABC, abstractmethod

from ..database_connectors.db_provider import DatabaseProvider
from ..file_operations.read import Read
from .dataframes import Dataframes
from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from typing import Optional
from audit_tracker.audit_tracker import AuditTracker

read = Read()
df = Dataframes()
logger = Logger


class Extractor(ABC):
    @abstractmethod
    def execute(self, parameters: dict, connection_id: dict, output, spark: str, config: dict, aod_audit_instance: Optional[AuditTracker] = None) -> dict:
        pass

class ReadFiles(Extractor):
    @logger.generate
    def execute(self, parameters, connection_id, output, spark, config={}, aod_audit_instance: Optional[AuditTracker] = None):
        try:
            dataframes_dict = {}
            logger.info("Reading files....")
            if parameters["file_id"] in list(connection_id.keys()):
                file = connection_id[parameters["file_id"]]["details"]
                file_name = file['file_name']
                file_path = file['file_path']
                file_type = file['file_type']
                columns = file.get("columns", [])
                df_id = output["df_id"]
                alias = output.get("dataframe_alias",file_name) #added utkarsh
                path = os.path.join("file:///", file_path)
                function = getattr(read, file_type)
                if aod_audit_instance is not None:
                    dataframe = aod_audit_instance.record(function)(spark, path, columns=columns, config=config, old_df=None, step_name='read', audit_df_type="spark")
                else:
                    logger.warning("Unable to use audit instance for read_file, falling back to without audit")
                    dataframe = function(spark, path, columns=columns, config=config)
                dataframes_dict[df_id] = {"df": dataframe, "alias": alias}
            else:
                logger.debug("The 'df_id' is missing in connection id.")
                raise Exception(f"Could not find df_id: {df_id} in connection_id: {connection_id}")
            dataframes_dict = df.update(dataframes_dict)
            logger.debug("Returning dataframe dict..")
            return dataframes_dict
        except Exception as e:
            logger.error(f"Operation 'ReadFiles' completed with an exception: {str(e)}")
            raise ExtractException("Failed to read the files.")


class ReadTables(Extractor):
    @logger.generate
    def execute(self, parameters, connection_id, output, spark, config={}, aod_audit_instance: Optional[AuditTracker] = None):
        try:
            logger.info("Reading tables..")
            dataframes_dict = {}
            parameters.update(output)
            logger.debug(f"parameters: {parameters}")
            if parameters["connection_id"] in list(connection_id.keys()):
                conn_id = parameters['connection_id']
                connection_type = connection_id[conn_id]["details"]["type"]
            db = DatabaseProvider.create_object(connection_type, spark)
            connection = db.connect(connection_id[conn_id])
            if db.test_connection(parameters, connection):
                if aod_audit_instance is not None:
                    dataframes_dict = aod_audit_instance.record(db.fetch_data)(parameters, connection, config, old_df=None, step_name='read', audit_df_type="spark")
                else:
                    logger.warning("Unable to use audit instance for auditing read_table step, fallback to without audit")
                    dataframes_dict = db.fetch_data(parameters, connection, config)
            dataframes_dict = df.update(dataframes_dict)
            logger.debug("Returning dataframe dict..")
            return dataframes_dict
        except Exception as e:
            logger.error(f"Operation 'ReadTables' completed with an exception: {str(e)}")
            raise ExtractException("Failed to read the tables.")

class DeleteFile(Extractor):
    @logger.generate
    def execute(self, parameters, connection_id, output, spark, config={}, aod_audit_instance: Optional[AuditTracker] = None):
        logger.info("Deleting file...")
        pass

class ReadS3(Extractor):
    @logger.generate
    def execute(self, parameters, connection_id, output, spark, config={}, aod_audit_instance: Optional[AuditTracker] = None):
        try:
            logger.info("Reading s3..")
            dataframes_dict = {}
            parameters.update(output)
            logger.debug(f"parameters: {parameters}")
            if parameters["connection_id"] in list(connection_id.keys()):
                conn_id = parameters['connection_id']
                connection_type = connection_id[conn_id]["details"]["type"]
            db = DatabaseProvider.create_object(connection_type, spark)
            connection = db.connect(connection_id[conn_id])
            if db.test_connection(parameters, connection):
                if aod_audit_instance is not None:
                    dataframes_dict = aod_audit_instance.record(db.fetch_data)(parameters, connection, config, old_df=None, step_name='read', audit_df_type="spark")
                else:
                    logger.warning("Unable to use audit instance for auditing read_s3 step, fallback to without audit")
                    dataframes_dict = db.fetch_data(parameters, connection, config)
            dataframes_dict = df.update(dataframes_dict)
            logger.debug("Returning dataframe dict..")
            return dataframes_dict
        except Exception as e:
            logger.error(f"Operation 'ReadS3' completed with an exception: {str(e)}")
            raise ExtractException("Failed to read s3 files.")
