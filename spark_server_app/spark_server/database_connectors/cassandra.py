from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .db_connector import DatabaseConnector
from ..pipeline.utilities import Utilities

logger = Logger
utils = Utilities()


class Cassandra(DatabaseConnector):
    def __init__(self, spark):
        super().__init__()
        self.spark = spark

    @logger.generate
    def connect(self, connection_id):
        try:
            config = connection_id["details"]
            logger.info("connecting to cassandra.")
            logger.info(f"cassandra connection details: {config}")
            # self.spark.conf.set("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0")
            # self.spark.conf.set('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension')
            # self.spark.conf.set('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog')
            self.spark.conf.set("spark.cassandra.connection.host", config["host"])
            self.spark.conf.set("spark.cassandra.connection.port", config["port"])
            self.spark.conf.set("spark.cassandra.auth.username", config["username"])
            self.spark.conf.set("spark.cassandra.auth.password", config["password"])
            pool = config.get("connection_pool")
            if pool is None or pool.get("spark_pooling") is None:
                pass
            else:
                pool = pool.get("spark_pooling", {})
                for key, value in pool.items():
                    self.spark.conf.set(key, value)
            # self.spark.conf.set("fs.defaultFS", config["hdfs_uri"])
            logger.info("Connected to cassandra successfully.")
            return config
        except Exception as e:
            logger.error(f"Error occurred while connecting to cassandra: {str(e)}")
            raise DatabaseConnectionException("Failed to connect to cassandra.")

    @logger.generate
    def test_connection(self, configuration, connection):
        try:
            first_table = configuration['table_name']
            logger.info(f"cassandra connection details: {configuration}, {connection}")
            keyspace, table = self.check_database(first_table, connection)
            self.spark.read.format("org.apache.spark.sql.cassandra").options(
                    keyspace=keyspace,
                    table=table
            ).load()
            logger.info("Cassandra connection test successful!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Cassandra. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to test cassandra connection.")

    @logger.generate
    def fetch_data(self, configuration, connection, custom_config={}):
        try:
            dfs = {}
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
            alias=configuration.get("dataframe_alias","cassandra"+keyspace+"_"+table)
            dfs.update({configuration["df_id"]: {"df": df, "alias": alias}})
            logger.info("Fetched data successfully.")
            return dfs
        except Exception as e:
            logger.error(f"Error occurred while fetching data from cassandra: {str(e)}")
            raise DatabaseConnectionException("Failed to fetch data from cassandra.")

    @logger.generate
    def write_data(self, configuration, connection, dataframe, custom_config={}):
        """
        Writes data to Cassandra database table

        :param configuration: Dictionary consisting of table_id and table with keyspace when provided not in connection
                              or table without keyspace when provided in connection
        :param connection: Dictionary of connection details
        :param dataframe: Spark dataframe with columns and data
        """
        try:
            keyspace, table = self.check_database(configuration["table_name"], connection)
            logger.info("Writing data to cassandra.")
            config_dict = {"keyspace": keyspace, "table": table, "confirm.truncate": True}
            config_dict.update(custom_config)
            mode = config_dict.get("mode") if config_dict.get("mode") else self.DEFAULT_DB_CONNECTOR_MODE
            logger.debug(f"config: {config_dict}")
            if config_dict.get("mode"):
                config_dict.pop("mode")
            dataframe.write.format("org.apache.spark.sql.cassandra").options(**config_dict).mode(mode).save()
            logger.info(f"Write data to Cassandra database table successful")
            return True
        except Exception as e:
            logger.error(f"Error occurred while writing to cassandra: {str(e)}")
            raise DatabaseConnectionException("Failed to write to cassandra.")
           
    def check_database(self, configuration, connection):
        try:
            if connection["database"] is None:
                keyspace = configuration.split(".")[0]
                table = configuration.split(".")[1]
            else:
                keyspace = connection["database"]
                table = configuration
            logger.debug(f"Database details, keyspace: {keyspace}, table: {table}")
            logger.debug("Database exists..")
            return keyspace, table
        except Exception as e:
            logger.error(f"Error occurred while checking database in cassandra: {str(e)}")
            raise DatabaseConnectionException("Failed to check cassandra database.")
