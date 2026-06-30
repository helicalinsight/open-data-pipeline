from spark_server.logger.logger import Logger, logger
from spark_server.exceptions.exceptions import *
from spark_server.database_connectors.db_connector import DatabaseConnector
from spark_server.pipeline.utilities import Utilities
from pyspark.sql.types import *
import os

logger = Logger
utils = Utilities()


class Databricks(DatabaseConnector):
    """
    A class to interact with Databricks database using PySpark
    """
    def __init__(self, spark):
        """
        Initializes the Databricks connector with a SparkSession

        :param spark: SparkSession object
        """
        super().__init__()
        self.spark = spark

    @logger.generate
    def connect(self, connection_id):
        """
        Connects to Databricks database using connection details from MongoDB

        :param connection_id: Identifier of the Databricks connection in MongoDB
        :return: Dictionary containing Databricks connection details
        """
        try:
            config = connection_id["details"]
            catalog = config.get("catalog")
            logger.info("Connecting to Databricks..")
            logger.debug(f"Connection details: {config}")
            config.update({"spark.databricks.service.client.enabled": "true"})
            config.update({"spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem"})
            config.update({"spark.databricks.service.token": "<DATABRICKS_ACCESS_TOKEN>"})
            config.update({"spark.databricks.service.address": "https://<DATABRICKS_WORKSPACE>"})
            config.update({"spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension"})
            config.update({"spark.delta.logStore.class": "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore"})
            config.update({"spark.sql.warehouse.dir": "/user/hive/warehouse"})
            
            conn = config.copy()
            conn.pop("type", None)
            conn.pop("sourceName", None)
            pool = conn.get("connection_pool")
            if pool is None or pool.get("spark_pooling") is None:
                pass
            else:
                conn.update(pool.get("spark_pooling", {}))
            logger.info("Connection to Databricks is successfull.")
            return conn
        except Exception as e:
            logger.error(f"Failed to get Databricks connection details. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to connect to Databricks.")

    @logger.generate
    def test_connection(self, configuration, connection):
        """
        Tests the Databricks connection by reading data from a specified table

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing Databricks connection details
        :return: True if connection test successful, False otherwise
        """
        try:
            logger.info("Testing Databricks connection.")
            database, table = self.check_database(configuration["table_name"], connection)
            config_dict = connection.copy()
            url = (
                f"jdbc:databricks://{config_dict['host']}:443/"
                f"default;transportMode=http;"
                f"ssl=1;"
                f"httpPath={config_dict['http_path']};"
                f"AuthMech=3;"
                f"UID=token;"
                f"PWD={config_dict['access_token']}"
            )
            catalog = config_dict.get("catalog")
            query = f"(SELECT * FROM {catalog}.{database}.{table} LIMIT 1) AS temp"
            options = {
                "url": url,
                "dbtable": query,
                "driver": "com.databricks.client.jdbc.Driver"
            }
            self.spark.read.format("jdbc").options(**options).load().limit(1)
            logger.info("Databricks connection test successful!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Databricks. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to test Databricks connection.")

    @logger.generate
    def fetch_data(self, configuration, connection, custom_config={}):
        """
        Fetches data from Databricks table and returns as a dictionary of DataFrames

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing Databricks connection details
        :return: Dictionary containing DataFrame with fetched data
        """
        try:
            dfs = {}
            database, table = self.check_database(configuration["table_name"], connection)
            logger.info("Fetching the Databricks database.")
            catalog = connection.get("catalog")
            config_dict = connection.copy()
            url = (
                f"jdbc:databricks://{config_dict['host']}:443/"
                f"default;transportMode=http;"
                f"ssl=1;"
                f"httpPath={config_dict['http_path']};"
                f"AuthMech=3;"
                f"UID=token;"
                f"PWD={config_dict['access_token']};"
                f"UseNativeQuery=0"
            )
            if "columns" in configuration and len(configuration["columns"]) > 0:
                columns = configuration['columns']
                columns_str = ', '.join([f"`{col}`" for col in columns])
                query = f"SELECT {columns_str} FROM `{catalog}`.`{database}`.`{table}`"
            else:
                # Refer Databricks Datasource Support - Design Document - https://onedrive.live.com/personal/ebf620ef57de80fa/_layouts/15/doc.aspx?sourcedoc={74518fd9-747c-4bf7-b14b-84e98a780d95}&action=edit
                schema_query = f"(SELECT column_name, data_type FROM {catalog}.information_schema.columns WHERE table_name = '{table}') AS t"
                options = {
                    "url": url,
                    "dbtable": schema_query,
                    "driver": "com.databricks.client.jdbc.Driver"
                }
                df_schema_info = self.spark.read.format("jdbc").options(**options).load()
                columns = [row["column_name"] for row in df_schema_info.collect()]
                columns_str = ", ".join([f"`{col}`" for col in columns])
                query = f"SELECT {columns_str} FROM `{catalog}`.`{database}`.`{table}`"
            config_dict.update({"query": query})
            config_dict.update(custom_config)
            if "query" and "dbtable" in config_dict:
                if "query" in custom_config:
                    config_dict.pop("dbtable", None) 
                elif "dbtable" in custom_config:
                    config_dict.pop("query", None)
            logger.debug(f"config: {config_dict}")            
            
            options = {
                "url": url,
                "dbtable": f"({query}) as t",
                "driver": "com.databricks.client.jdbc.Driver"
            }
            df = self.spark.read.format("jdbc").options(**options).load()
            new_columns = [utils.clean_column_name(col) for col in df.columns]
            df = df.toDF(*new_columns)
            alias=configuration.get("dataframe_alias","databricks"+database+"_"+table)
            dfs.update({configuration["df_id"]: {"df": df, "alias": alias}})
            logger.info("Fetched data successfully.")
            return dfs
        except Exception as e:
            logger.error(f"Failed to fetch data from Databricks. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to fetch the data from Databricks.")

    @logger.generate
    def write_data(self, configuration, connection, dataframe, custom_config={}):
        """
        Writes data to Databricks database table

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing Databricks connection details
        :param dataframe: Spark DataFrame containing data to be written
        """
        # Refer Databricks Datasource Support - Design Document - https://onedrive.live.com/personal/ebf620ef57de80fa/_layouts/15/doc.aspx?sourcedoc={74518fd9-747c-4bf7-b14b-84e98a780d95}&action=edit
        logger.warning("Write to Databricks is not implemented.")
        return True
        
    @logger.generate
    def check_database(self, configuration, connection):
        """
        Parses the table name and returns database, schema, and table

        :param configuration: Table name in the format database.schema.table
        :param connection: Dictionary containing Databricks connection details
        :return: Tuple containing database, schema, and table names
        """
        logger.info(f"connection {connection}")
        logger.info(f"configuration {configuration}")
        try:
            schema, table = configuration.split(".", 1)
            logger.debug(f"Database details, database: {schema}, table: {table}")
            logger.debug("Database exists..")
            return schema, table
        except Exception as e:
            logger.error(f"Error occurred while parsing table name. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to check database in Databricks.")