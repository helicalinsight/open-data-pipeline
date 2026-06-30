from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .db_connector import DatabaseConnector
from ..pipeline.utilities import Utilities

logger = Logger
utils = Utilities()

class Postgres(DatabaseConnector):
    def __init__(self, spark):
        super().__init__()
        self.spark = spark

    @logger.generate
    def connect(self, connection_id):
        try:
            logger.info("Connecting to postgres..")
            config = connection_id["details"]
            logger.debug(f"Connection_details: {config}")
            config.update({"driver": "org.postgresql.Driver"})
            config.update({"url": "jdbc:postgresql://"+config["host"]+":"+str(config["port"])+"/"+config["database"]})
            conn = config.copy()
            conn["user"] = conn.pop("username")
            conn.pop("type", None)
            conn.pop("sourceName", None)
            pool = conn.get("connection_pool")
            if pool is None or pool.get("spark_pooling") is None:
                pass
            else:
                conn.update(pool.get("spark_pooling", {}))
            logger.info("Connection to postgres is successfull.")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to Postgres. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to connect to postgres.")

    @logger.generate
    def test_connection(self, configuration, connection):
        try:
            logger.info("Testing postgres connection.")
            first_table = configuration['table_name']
            database, table = self.check_database(first_table, connection)
            test_query = "(SELECT * FROM " + table + " LIMIT 1) AS test_query"
            config_dict = connection.copy()
            config_dict.update({"dbtable": test_query})
            self.spark.read.format("jdbc").options(**config_dict).load()
            logger.info("Postgres connection test successful!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Postgres. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to test postgres connection.")

    @logger.generate
    def fetch_data(self, configuration, connection, custom_config={}):
        try:
            dfs = {}
            database, table = self.check_database(configuration["table_name"], connection)
            if "columns" in configuration and len(configuration["columns"]) > 0:
                columns = configuration['columns']
                columns_str = ', '.join(columns)
                query = f"SELECT {columns_str} FROM {table}"
            else:
                query = f"SELECT * FROM {table}"
            config_dict = connection.copy()
            config_dict.update({"query": query})
            logger.info("Fetching the postgres database.")
            config_dict.update(custom_config)
            if "query" and "dbtable" in config_dict:
                if "query" in custom_config:
                    config_dict.pop("dbtable", None) 
                elif "dbtable" in custom_config:
                    config_dict.pop("query", None)
            logger.debug(f"config: {config_dict}")
            df = self.spark.read.format("jdbc").options(**config_dict).load()
            new_columns = [utils.clean_column_name(col) for col in df.columns]
            df = df.toDF(*new_columns)
            alias=configuration.get("dataframe_alias","postgres_"+database+"_"+table)
            dfs.update({configuration["df_id"]: {"df": df, "alias": alias}})
            logger.info("Fetched data successfully.")
            return dfs
        except Exception as e:
            logger.error(f"Error occured while fetching data from postgres: {str(e)}")
            raise DatabaseConnectionException(f"Failed to fetch the data from database.")

    @logger.generate
    def write_data(self, configuration, connection, dataframe, custom_config={}):
        """
        Writes data to Postgres database table

        :param configuration: Dictionary consisting of table_id and table with keyspace when provided not in connection
                              or table without keyspace when provided in connection
        :param connection: Dictionary of connection details
        :param dataframe: Spark dataframe with columns and data
        """
        try:
            database, table = self.check_database(configuration["table_name"], connection)
            logger.info("Writing data to postgres")
            config_dict = connection.copy()
            config_dict.update({"dbtable": table})
            config_dict.update(custom_config)
            logger.debug(f"config: {config_dict}")
            mode = config_dict.get("mode") if config_dict.get("mode") else self.DEFAULT_DB_CONNECTOR_MODE
            if config_dict.get("mode"):
                config_dict.pop("mode")
            dataframe.write.format("jdbc").options(**config_dict).mode(mode).save()
            logger.info(f"Write data to Postgres database table successful")
            return True
        except Exception as e:
            logger.error(f"Failed to write data to Postgres database table. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException(f"Failed to write to postgres database.")
        
    def check_database(self, configuration, connection):
        try:
            if connection["database"] is None:
                database = configuration.split(".")[0]
                table = configuration.split(".")[1]
            else:
                database = connection["database"]
                table = configuration
            logger.debug(f"Database details, database: {database}, table: {table}")
            logger.debug("Database exists..")
            return database, table
        except Exception as e:
            logger.error(f"Failed to check postgres database: {str(e)}")
            raise DatabaseConnectionException("Failed to check database.")
