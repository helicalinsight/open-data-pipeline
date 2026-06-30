from ..logger.logger import Logger, logger
from .db_connector import DatabaseConnector
from ..exceptions.exceptions import DatabaseConnectionException
from pyspark.sql import SparkSession
from typing import Dict
import copy
from ..pipeline.utilities import Utilities
utils = Utilities()

ORACLE_FIRST_TABLE_TEST_QUERY = 'SELECT * FROM (SELECT * FROM {table} WHERE ROWNUM=1) test_query'


class Oracle(DatabaseConnector):
    """
    Spark Connector Class for Oracle DB
    """
    def __init__(self, spark: SparkSession):
        super().__init__()
        self._spark: SparkSession = spark

    @Logger.generate
    def connect(self, connection_details: Dict) -> Dict:
        try:
            logger.info("Connecting to Oracle db")
            if "details" not in connection_details:
                raise ValueError("'details' is required in connection details")
            conn_details: Dict = copy.deepcopy(connection_details["details"])

            required_keys = ["host", "port", "database", "username"]
            for key in required_keys:
                if key not in conn_details:
                    raise ValueError(f"Unable to connect to Oracle: Required property '{key}' missing")

            # Add driver and url info for database
            conn_details.update({"driver": "oracle.jdbc.OracleDriver"})
            conn_details.update({"url": f"jdbc:oracle:thin:@//{conn_details['host']}:{conn_details['port']}/{conn_details['database']}"})
            logger.info(f"Processed connection url for Oracle - {conn_details['url']}")

            conn_details["user"] = conn_details["username"]
            conn_details.pop("type", None)
            conn_details.pop("sourceName", None)

            # Set up pooling
            pool = conn_details.get("connection_pool", None)
            if not pool or not pool.get("spark_pooling"):
                pass
            else:
                conn_details.update(pool.get("spark_pooling", {}))

            logger.info("Connection to oracledb successful")
            return conn_details
        except Exception as e:
            logger.error(f"Error while connecting to oracle db - {e}")
            raise DatabaseConnectionException("Error while connecting to oracle db") from e

    @Logger.generate
    def test_connection(self, configuration: Dict, connection: Dict) -> bool:
        try:
            logger.info("Testing oracle connection")
            first_table = configuration.get('table_name', None)
            if first_table is None:
                raise ValueError("'table_name' is required configuration")
            
            db, first_table = self.check_database(configuration["table_name"], connection)
            test_query = ORACLE_FIRST_TABLE_TEST_QUERY.format(table=first_table)
            config = copy.deepcopy(connection)
            config.update({"query": test_query})
            self._spark.read.format("jdbc")\
                .option("url", config["url"])\
                .option("user", config["user"])\
                .option("password", config["password"])\
                .option("driver", config["driver"])\
                .option("query", config["query"])\
                .load()
            logger.info("Oracle test connection succesful")
            return True
        except Exception as e:
            logger.error(f"Failed to test connection with oracle - {e}")
            raise DatabaseConnectionException("Failed to test connection with oracle") from e
    
    @Logger.generate
    def fetch_data(self, configuration: Dict, connection: Dict, custom_config=None):
        if custom_config is None:
            custom_config = {}

        try:
            dfs = {}
            db, table = self.check_database(configuration["table_name"], connection)

            if "columns" in configuration and len(configuration["columns"]) > 0:
                columns_str = ', '.join(f'"{col_value}"' for col_value in configuration["columns"])
                query = f"SELECT {columns_str} FROM {table}"
            else:
                query = f"SELECT * FROM {table}"

            config = copy.deepcopy(connection)
            config.update({"query": query})

            config.update(custom_config)
            # Adjust config based on 'query' or 'dbtable' value in custom_config
            if "query" in custom_config:
                config.pop("dbtable", None)
            elif "dbtable" in custom_config:
                config.pop("query", None)

            if "query" in config:
                df = self._execute_spark_read(config, "query")
            elif "dbtable" in config:
                df = self._execute_spark_read(config, "dbtable")
            else:
                raise RuntimeError("Neither 'query' nor 'dbtable' found for oracle query")
            new_columns = [utils.clean_column_name(col) for col in df.columns]
            df = df.toDF(*new_columns)
            alias = configuration.get("dataframe_alias", "oracle_" + db + "_" + table)
            dfs.update({configuration["df_id"]: {"df": df, "alias": alias}})
            logger.info("Fetched data successfully from Oracle.")
            return dfs
        except Exception as e:
            logger.error(f"Error while fetching data from oracle - {e}")
            raise DatabaseConnectionException("Error while fetching data from oracle") from e

    @Logger.generate
    def write_data(self, configuration, connection, dataframe, custom_config=None) -> bool:
        """
        Writes data to Oracle database table

        :param configuration: Dictionary consisting of table_id and table with keyspace when provided not in connection
                              or table without keyspace when provided in connection
        :param connection: Dictionary of connection details
        :param dataframe: Spark dataframe with columns and data
        """
        if custom_config is None:
            custom_config = {}
        try:
            database, table = self.check_database(configuration["table_name"], connection)
            logger.info("Writing data to Oracle")
            config = copy.deepcopy(connection)
            config.update({"dbtable": table})
            config.update(custom_config)
            mode = config.get("mode") if config.get("mode", None) else self.DEFAULT_DB_CONNECTOR_MODE
            if config.get("mode"):
                config.pop("mode")
            dataframe.write.format("jdbc")\
                .option("url", config["url"])\
                .option("user", config["user"])\
                .option("password", config["password"])\
                .option("driver", config["driver"])\
                .option("dbtable", config["dbtable"])\
                .mode(mode).save()
            logger.info("Write data to Oracle database table successful")
            return True
        except Exception as e:
            logger.error(f"Failed to write data to Oracle database table. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to write to Oracle database.") from e

    @Logger.generate
    def check_database(self, table_name, connection):
        try:
            if connection["database"] is None:
                database = table_name.split(".")[0]
                table = table_name.split(".")[1]
            else:
                database = connection["database"]
                schema, out_table = table_name.split('.')
                table = f'"{schema}"."{out_table.upper()}"'
            logger.debug(f"Oracle Database details, database: {database}, table: {table}")
            return database, table
        except Exception as e:
            logger.error(f"Failed to get Oracle database name: {str(e)}")
            raise DatabaseConnectionException("Failed to get Oracle database name") from e

    def _execute_spark_read(self, config, dbtable_or_query: str):
        df = self._spark.read.format("jdbc")\
                .option("url", config["url"])\
                .option("user", config["user"])\
                .option("password", config["password"])\
                .option("driver", config["driver"])\
                .option(dbtable_or_query, config[dbtable_or_query])\
                .load()
        
        return df
    