from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .db_connector import DatabaseConnector
from ..pipeline.utilities import Utilities

logger = Logger
utils = Utilities()


class Snowflake(DatabaseConnector):
    """
    A class to interact with Snowflake database using PySpark
    """
    def __init__(self, spark):
        """
        Initializes the Snowflake connector with a SparkSession

        :param spark: SparkSession object
        """
        super().__init__()
        self.spark = spark

    @logger.generate
    def connect(self, connection_id):
        """
        Connects to Snowflake database using connection details from MongoDB

        :param connection_id: Identifier of the Snowflake connection in MongoDB
        :return: Dictionary containing Snowflake connection details
        """
        try:
            logger.info("Connecting to snowflake..")
            config = connection_id["details"]
            logger.debug(f"connection details: {config}")

            # 1. Standardize and resolve both generic and sf-prefixed keys
            sf_user = config.get("sfUser") or config.get("username")
            sf_password = config.get("sfPassword") or config.get("password")
            sf_account = config.get("sfAccountIdentifier") or config.get("host")
            sf_database = config.get("sfDatabase") or config.get("database")
            sf_schema = config.get("sfSchema") or config.get("schema")
            sf_warehouse = config.get("sfWarehouse") or config.get("warehouse")

            if not sf_account:
                raise KeyError("Missing Snowflake host or sfAccountIdentifier in connection details.")
            sf_url = f"{sf_account}.snowflakecomputing.com"

            # 2. Build a clean, flat connection options dictionary (only strings)
            conn = {}
            if sf_user:
                conn["sfUser"] = str(sf_user)
            if sf_password:
                conn["sfPassword"] = str(sf_password)
            if sf_url:
                conn["sfUrl"] = str(sf_url)
            if sf_database:
                conn["sfDatabase"] = str(sf_database)
            if sf_schema:
                conn["sfSchema"] = str(sf_schema)
            if sf_warehouse:
                conn["sfWarehouse"] = str(sf_warehouse)
            
            # 3. Handle Spark connection pooling options cleanly (no nested dicts left behind)
            pool = config.get("connection_pool", {})
            if pool and pool.get("spark_pooling"):
                # Ensure all pool config options are converted to strings for PySpark compatibility
                spark_pooling = {k: str(v) for k, v in pool.get("spark_pooling", {}).items()}
                conn.update(spark_pooling)
            
            logger.info("Connection to snowflake is done successfully.")
            return conn
        except Exception as e:
            logger.error(f"Failed to get Snowflake connection details. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to connect to snowflake.")

    @logger.generate
    def test_connection(self, configuration, connection):
        """
        Tests the Snowflake connection by reading data from a specified table

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing Snowflake connection details
        :return: True if connection test successful, False otherwise
        """
        try:
            logger.info("Testing snowflake connection.")
            # remove any unwanted variables before connecting to any database.
            connection.pop("database",None)
            first_table = configuration['table_name']
            database, schema, table = self.check_database(first_table, connection)
            if connection["sfDatabase"] is None:
                connection.update({"sfDatabase": database})
            connection.update({"sfSchema": schema})
            connection.pop("dbtable",None)
            query=f"SELECT * FROM {first_table} LIMIT 1"
            self.spark.read.format("net.snowflake.spark.snowflake").options(**connection).option("query",query).load()
            logger.info("Snowflake connection test successful!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to test snowflake connection.")
        
    @logger.generate
    def fetch_data(self, configuration, connection, custom_config={}):
        """
        Fetches data from Snowflake table and returns as a dictionary of DataFrames

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing Snowflake connection details
        :return: Dictionary containing DataFrame with fetched data
        """
        try:
            dfs = {}
            database, schema, table = self.check_database(configuration["table_name"], connection)
            if connection["sfDatabase"] is None:
                connection.update({"sfDatabase": database})
            connection.update({"sfSchema": schema})
            if "columns" in configuration and len(configuration["columns"]) > 0:
                columns = configuration['columns']
                columns_str = ', '.join(columns)
                query = f"SELECT {columns_str} FROM {database}.{schema}.{table}"
            else:
                query = f"SELECT * FROM {database}.{schema}.{table}"
            logger.info("Fetching the snowflake database.")
            config_dict = connection.copy()
            config_dict.update({"query": query})
            config_dict.update(custom_config)
            if "query" and "dbtable" in config_dict:
                if "query" in custom_config:
                    config_dict.pop("dbtable", None) 
                elif "dbtable" in custom_config:
                    config_dict.pop("query", None)
            logger.debug(f"config: {config_dict}")
            df = self.spark.read.format("net.snowflake.spark.snowflake").options(**config_dict).load()
            new_columns = [utils.clean_column_name(col) for col in df.columns]
            df = df.toDF(*new_columns)
            alias=configuration.get("dataframe_alias","snowflake_"+database+"_"+table)
            dfs.update({configuration["df_id"]: {"df": df, "alias": alias}})
            logger.info("Fetched data successfully.")
            return dfs
        except Exception as e:
            logger.error(f"Failed to fetch data from Snowflake. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to fetch data fom snowflake.")
        
    @logger.generate
    def write_data(self, configuration, connection, dataframe, custom_config={}):
        """
        Writes data to Snowflake database table

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing Snowflake connection details
        :param dataframe: Spark DataFrame containing data to be written
        """
        try:
            database, schema, table = self.check_database(configuration["table_name"], connection)
            if connection["sfDatabase"] is None:
                connection.update({"sfDatabase": database})
            connection.update({"sfSchema": schema})
            connection.update({"dbtable": table})
            logger.info("Saving the snowflake database.")
            config_dict = connection.copy()
            config_dict.update(custom_config)
            logger.debug(f"config: {config_dict}")
            mode = config_dict.get("mode") if config_dict.get("mode") else self.DEFAULT_DB_CONNECTOR_MODE
            if config_dict.get("mode"):
                config_dict.pop("mode")
            dataframe.write.format("net.snowflake.spark.snowflake").options(**config_dict).mode(mode).save()
            logger.info(f"Write data to Snowflake database table successful")
            return True
        except Exception as e:
            logger.error(f"Failed to write data to Snowflake database table. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to write to snowflake database.")

    @logger.generate
    def check_database(self, configuration, connection):
        """
        Parses the table name and returns database, schema, and table

        :param configuration: Table name in the format database.schema.table
        :param connection: Dictionary containing Snowflake connection details
        :return: Tuple containing database, schema, and table names
        """
        try:
            if connection["sfDatabase"] is None:
                database = configuration.split(".")[0]
                schema = configuration.split(".")[1]
                table = configuration.split(".")[2]
            else:
                database = connection["sfDatabase"]
                schema = configuration.split(".")[-2]
                table = configuration.split(".")[-1]
            logger.debug(f"Database details, database: {database}, schema: {schema}, table: {table}")
            logger.debug("Database exists..")
            return database, schema, table
        except Exception as e:
            logger.error(f"Error occurred while parsing table name. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to check database.")