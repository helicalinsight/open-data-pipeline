from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .db_connector import DatabaseConnector
from ..pipeline.utilities import Utilities

logger = Logger
utils = Utilities()

class Astra(DatabaseConnector):
    def __init__(self, spark):
        super().__init__()
        self.spark = spark

    @logger.generate
    def connect(self, connection_id):
        try:
            config = connection_id["details"]
            logger.info("Connecting to astra..")
            logger.debug("config", config)
            self.spark.sparkContext.addFile(config["bundle"]["file"])
            self.spark.conf.set("spark.cassandra.connection.config.cloud.path", config["bundle"]["file"].split("/")[-1])
            self.spark.conf.set("spark.cassandra.auth.username", config["client_id"])
            self.spark.conf.set("spark.cassandra.auth.password", config["secret"])
            pool = config.get("connection_pool")
            if pool is None or pool.get("spark_pooling") is None:
                pass
            else:
                pool = pool.get("spark_pooling", {})
                for key, value in pool.items():
                    self.spark.conf.set(key, value)
            logger.info(f"Connected to astra successfully.")
            return config
        except Exception as e:
            logger.error(f"Error occured while connecting to astra : {str(e)}")
            raise DatabaseConnectionException(f"Failed to connect to astra db.{str(e)}")

    @logger.generate
    def test_connection(self, configuration, connection):
        try:
            logger.info("Testing astra connection...")
            first_table = configuration['table_name']
            keyspace, table = self.check_database(first_table, connection)
            self.spark.sql("SHOW NAMESPACES").show()
            self.spark.read.format("org.apache.spark.sql.cassandra").options(
                table=table, keyspace=keyspace
            ).load()
            logger.info("Astra connection test successfull.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Astra. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException(f"Failed to test astra connection.{str(e)}")

    @logger.generate   
    def fetch_data(self, configuration, connection, custom_config={}):
        try:
            dfs = {}
            logger.info("Fetching data from astra.")
            keyspace, table = self.check_database(configuration["table_name"], connection)
            config_dict = {"keyspace": keyspace, "table": table}
            config_dict.update(custom_config)
            logger.debug(f"config: {config_dict}")
            if "columns" in configuration and len(configuration["columns"]) > 0:
                columns = configuration['columns']
                df = self.spark.read.format("org.apache.spark.sql.cassandra").options(**config_dict).load().select(columns)
            else:
                df = self.spark.read.format("org.apache.spark.sql.cassandra").options(**config_dict).load()
            new_columns = [utils.clean_column_name(col) for col in df.columns]
            df = df.toDF(*new_columns)
            alias=configuration.get("dataframe_alias","astra_"+keyspace+"_"+table)
            dfs.update({configuration["df_id"]: {"df": df, "alias": alias}})
            logger.info("Fetched data successfully..")
            return dfs
        except Exception as e:
            logger.error(f"Failed to fetch data from Astra. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to fetch data from astra db.")

    @logger.generate
    def write_data(self, configuration, connection, dataframe, custom_config={}):
        """
        Writes data to Astra database table

        :param configuration: Dictionary consisting of table_id and table with keyspace when provided not in connection
                              or table without keyspace when provided in connection
        :param connection: Dictionary of connection details
        :param dataframe: Spark dataframe with columns and data
        """
        try:
            keyspace, table = self.check_database(configuration["table_name"], connection)
            logger.info("Writing data to Astra.")
            config_dict = {"keyspace": keyspace, "table": table, "confirm.truncate": True}
            config_dict.update(custom_config)
            mode = config_dict.get("mode") if config_dict.get("mode") else self.DEFAULT_DB_CONNECTOR_MODE
            logger.debug(f"config: {config_dict}")
            if config_dict.get("mode"):
                config_dict.pop("mode")
            dataframe.write.format("org.apache.spark.sql.cassandra").options(**config_dict).mode(mode).save()
            logger.info(f"Write data to Astra database table successful")
            return True
        except Exception as e:
            logger.error(f"Failed to write data to Astra database table. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException(f"Failed to write data to astra.")
        
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
            logger.error(f"Failed to write data to Astra database table. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to check database in astra.")
