from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .db_connector import DatabaseConnector
import gspread
from google.oauth2 import service_account
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, StringType
from ..pipeline.utilities import Utilities
import os

logger = Logger
utils = Utilities()


class GoogleSheet(DatabaseConnector):
    def __init__(self, spark):
        super().__init__()
        self.spark = spark

    @logger.generate
    def connect(self, connection_id):
        try:
            config = connection_id["details"]
            logger.info("Connecting to Google sheet..")
            SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            SERVICE_ACCOUNT_FILE = config["credentials_object"]["file"]
            SERVICE_ACCOUNT_FILE_PATH = os.path.join("/", SERVICE_ACCOUNT_FILE)
            credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE_PATH, scopes=SCOPES)          
            gc = gspread.authorize(credentials)
            config.update({"gc": gc})
            logger.info(f"Connected to Google sheet successfully.")
            return config
        except Exception as e:
            logger.error(f"Error occured while connecting to Google sheet : {str(e)}")
            raise DatabaseConnectionException(f"Failed to connect to Google sheet.{str(e)}")

    @logger.generate
    def test_connection(self, configuration, connection):
        try:
            logger.info("Testing Google sheet connection...")
            spreadsheet_id = connection['sheet_id']
            gc = connection["gc"]
            sheet = gc.open_by_key(spreadsheet_id)
            worksheet_titles = [ws.title for ws in sheet.worksheets()]
            if len(worksheet_titles) > 0:
                logger.info("Google sheet connection test successful.")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Google sheet. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException(f"Failed to test Google sheet connection.{str(e)}")

    @logger.generate   
    def fetch_data(self, configuration, connection, custom_config={}):
        try:
            dfs = {}
            logger.info("Fetching data from Google sheet.")
            gc = connection["gc"]
            sheet_name = configuration["table_name"]
            config_dict = {"sheet_name": sheet_name}
            config_dict.update(custom_config)
            sheet_id = connection["sheet_id"]
            sheet = gc.open_by_key(sheet_id)
            sheet_instance = sheet.worksheet(config_dict["sheet_name"])
            records_data = sheet_instance.get_all_records()
            df = self.spark.createDataFrame([Row(**d) for d in records_data])
            logger.debug(f"config: {config_dict}")
            if "columns" in configuration and len(configuration["columns"]) > 0:
                columns = configuration['columns']
                df = df.select(columns)
            new_columns = [utils.clean_column_name(col) for col in df.columns]
            df = df.toDF(*new_columns)
            alias=configuration.get("dataframe_alias","googlesheet_"+sheet_id+"_"+sheet_name)
            dfs.update({configuration["df_id"]: {"df": df, "alias": alias}})
            logger.info("Fetched data successfully..")
            return dfs
        except Exception as e:
            logger.error(f"Failed to fetch data from Google sheet. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to fetch data from Google sheet.")

    @logger.generate
    def write_data(self, configuration, connection, dataframe, custom_config={}):
        """
        Writes data to Google sheet database table

        :param configuration: Dictionary consisting of table_id and table with keyspace when provided not in connection
                              or table without keyspace when provided in connection
        :param connection: Dictionary of connection details
        :param dataframe: Spark dataframe with columns and data
        """
        try:
            logger.info("Writing data to google sheet.")
            gc = connection["gc"]
            sheet_name = configuration["table_name"]
            config_dict = {"sheet_name": sheet_name}
            config_dict.update(custom_config)
            sheet_id = connection["sheet_id"]
            sheet = gc.open_by_key(sheet_id)
            sheet_instance = sheet.worksheet(config_dict["sheet_name"])
            mode = config_dict.get("mode") if config_dict.get("mode") else self.DEFAULT_DB_CONNECTOR_MODE
            logger.debug(f"config: {config_dict}")
            if config_dict.get("mode"):
                config_dict.pop("mode")
            if mode == "overwrite":
                data_list = [dataframe.columns] + [list(row.asDict().values()) for row in dataframe.collect()]
                sheet_instance.clear()
                sheet_instance.update('A1', data_list)
            elif mode == "append":
                data_list = [list(row.asDict().values()) for row in dataframe.collect()]
                existing_data = sheet_instance.get_all_values()
                last_row = len(existing_data)
                if last_row > 0:
                    last_row += 1  # Start appending data from the next empty row
                else:
                    last_row = 1  # Start from the first row if sheet is empty
                # Determine the starting cell to append data
                start_cell = f"A{last_row}"
                # Append data to Google Sheet
                sheet_instance.update(start_cell, data_list)

            logger.info(f"Write data to Google sheet database table successful")
            return True
        except Exception as e:
            logger.error(f"Failed to write data to Google sheet database table. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException(f"Failed to write data to Google sheet.")
        
    def check_database(self, configuration, connection):
        try:
            if connection["database"] is None:
                keyspace = configuration.split(".")[0]
                table = configuration.split(".")[1]
            else:
                keyspace = connection["database"]
                table = configuration
            logger.debug(f"Database present, keyspace: {keyspace}, table: {table}")
            return keyspace, table
        except Exception as e:
            logger.error(f"Failed to write data to Google sheet database table. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to check database in Google sheet.")
