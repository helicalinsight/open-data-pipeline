from pyspark.sql import DataFrame
import os
from abc import ABC, abstractmethod

from ..file_operations.write import Write
from .utilities import Utilities
from ..database_connectors.db_provider import DatabaseProvider
from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from typing import Optional
from audit_tracker.audit_tracker import AuditTracker

write = Write()
logger = Logger


class Loader(ABC):
    @abstractmethod
    def execute(self, dataframe: DataFrame, parameters: dict, connection_id: dict, spark: str,schedule_conf:dict, config: dict):
        """
        Abstract method for executing a loading operation

        :param dataframe: DataFrame to be loaded
        :param user_id: User identifier
        :param chat_id: Chat identifier
        :param parameters: Parameters required for loading
        :param spark: Spark session
        """
        pass


class Export(Loader):
    @logger.generate
    def execute(self, dataframes, parameters, connection_id, spark, schedule_conf, config={}):
        """
        Exports DataFrame to a file in specified format (CSV, Excel, or JSON)

        :param dataframes: Dictionary of DataFrames
        :param parameters: Dictionary of parameters including file_name, df_id, and export_format
        :param connection_id: Connection identifier
        :param spark: Spark session
        :param schedule_conf: Schedule configuration
        :param config: Additional configuration
        """
        try:
            file_id = parameters['df_id']
            dataframe = dataframes[file_id]["df"]

            # Extract parameters
            user_id = parameters['user_id']
            chat_id = parameters['chat_id']
            schedule_id = schedule_conf["schedule_id"]
            run_id = schedule_conf["run_id"]
            
            aod_audit_instance: Optional[AuditTracker] = schedule_conf.get("AodAudit", None)
            
            # Get export format from parameters, default to CSV for backward compatibility
            export_format = (schedule_conf.get('export_format') or 'csv').lower() # default to 'csv' if key is missing, None, or empty string
            
            # Validate export format
            supported_formats = ['csv', 'xlsx', 'json']
            if export_format not in supported_formats:
                logger.warning(f"Unsupported export format '{export_format}', defaulting to CSV")
                export_format = 'csv'
            
            # Create export path
            path = Utilities().create_export_path(user_id, schedule_id, run_id)
            
            # Export based on format
            if export_format == 'csv':
                function = getattr(write, "csv")
            elif export_format == 'xlsx':
                function = getattr(write, "xlsx")
            elif export_format == 'json':
                function = getattr(write, "json")
            else:
                raise NotImplementedError(f"Export not implemented for format {export_format}")
                
            if aod_audit_instance is not None:
                dataframe = aod_audit_instance.record(function)(dataframe, path, config, old_df=dataframe, step_name='export', audit_df_type="spark")
            else:
                logger.warning("Unable to use audit instance for export, falling back to without audit")
                dataframe = function(dataframe, path, config)
            logger.info(f"{export_format} file saved to the path : {path}")
            
        except Exception as e:
            logger.error(f"Failed to execute Export. Operation 'Export' Completed with Exception: {str(e)}")
            raise LoaderException(f"Failed to export in {export_format} format: {str(e)}")


class ExportTables(Loader):
    @logger.generate
    def execute(self, dataframes, parameters, connection_id, spark,schedule_conf, config={}):
        """
        Loads data to Database table

        :param dataframe: Spark dataframe with columns and data
        :param user_id: User identifier
        :param chat_id: Chat identifier
        :param parameters: Dictionary of parameters including connection_id, table_name and df_id
        :param spark: Spark session
        """
        try:
            table_id = parameters['df_id']
            dataframe = dataframes[table_id]["df"]
            aod_audit_instance: Optional[AuditTracker] = schedule_conf.get("AodAudit", None)
            
            connection_type = connection_id[parameters['connection_id']]["details"]["type"]
            db = DatabaseProvider.create_object(connection_type, spark)
            connection = db.connect(connection_id[parameters['connection_id']])
            if db.test_connection(parameters, connection):
                if aod_audit_instance is not None:
                    aod_audit_instance.record(db.write_data)(parameters, connection, dataframe, config, old_df=dataframe, step_name='export', audit_df_type="spark")
                else:
                    logger.warning("Unable to use audit instance for export, falling back to without audit")
                    db.write_data(parameters, connection, dataframe, config)
            logger.info(f"Data saved to the table: {parameters['table_name']}")
        except Exception as e:
            logger.error(f"Failed to execute ExportTables. Operation 'ExportTables' Completed with Exception: {str(e)}")
            raise LoaderException("Failed to export tables.")
