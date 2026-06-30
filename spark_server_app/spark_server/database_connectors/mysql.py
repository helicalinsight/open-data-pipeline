from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .db_connector import DatabaseConnector
from ..pipeline.utilities import Utilities

logger = Logger
utils = Utilities()


class MySQL(DatabaseConnector):
    """
    A class to interact with MySQL database using PySpark
    """
    def __init__(self, spark):
        """
        Initializes the MySQL connector with a SparkSession

        :param spark: SparkSession object
        """
        super().__init__()
        self.spark = spark

    @logger.generate
    def connect(self, connection_id):
        """
        Connects to MySQL database using connection details from MongoDB

        :param connection_id: Identifier of the MySQL connection in MongoDB
        :return: Dictionary containing MySQL connection details
        """
        try:
            config = connection_id["details"]
            logger.info("Connecting to mysql..")
            logger.debug(f"Connection details: {config}")
            config.update({"driver": "com.mysql.cj.jdbc.Driver"})
            config.update({"url": "jdbc:mysql://" + config["host"] + ":" + str(config["port"]) + "/" + config["database"]})
            conn = config.copy()
            conn["user"] = conn.pop("username") if "username" in conn else conn.pop("user")
            conn.pop("type", None)
            conn.pop("sourceName", None)
            pool = conn.get("connection_pool")
            if pool is None or pool.get("spark_pooling") is None:
                pass
            else:
                conn.update(pool.get("spark_pooling", {}))
            logger.info("Connection to mysql is successfull.")
            return conn
        except Exception as e:
            logger.error(f"Failed to get MySQL connection details. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to connect to mysql.")
        
    @logger.generate
    def test_connection(self, configuration, connection):
        """
        Tests the MySQL connection by reading data from a specified table

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing MySQL connection details
        :return: True if connection test successful, False otherwise
        """
        try:
            logger.info("Testing mysql connection.")
            database, table = self.check_database(configuration['table_name'], connection)
            mysql_properties = {
                'user': connection.get('user', connection.get('username', None)), 
                'password': connection['password'],
                'driver': connection['driver']
            }
            self.spark.read.jdbc(url=connection["url"], table=table, properties=mysql_properties)
            logger.info("MySQL connection test successfull!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MySQL. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException(f"Failed to test mysql connection.{str(e)}")
        
    @logger.generate
    def fetch_data(self, configuration, connection, custom_config={}):
        """
        Fetches data from MySQL table and returns as a dictionary of DataFrames

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing MySQL connection details
        :return: Dictionary containing DataFrame with fetched data
        """
        try:
            dfs = {}
            database, table = self.check_database(configuration["table_name"], connection)
            if "columns" in configuration and len(configuration["columns"]) > 0:
                columns = configuration['columns']
                columns_str = ', '.join(columns)
                query = f"SELECT {columns_str} FROM {table}"
            else:
                query = f"SELECT * FROM {table}"
            logger.info("Fetching the mysql database.")
            config_dict = connection.copy()
            config_dict.update({"query": query})
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
            alias=configuration.get("dataframe_alias","mysql_"+database+"_"+table)
            dfs.update({configuration["df_id"]: {"df": df, "alias": alias}})
            logger.info("Fetched data successfully.")
            return dfs
        except Exception as e:
            logger.error(f"Failed to fetch data from MySQL. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to fetch data."
                                              )
    
    @logger.generate
    def write_data(self, configuration, connection, dataframe, custom_config={}):
        """
        Writes data to MySQL database table

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing MySQL connection details
        :param dataframe: Spark DataFrame containing data to be written
        """
        try:
            database, table = self.check_database(configuration["table_name"], connection)
            logger.info("Writing data to MySQL.")
            config_dict = connection.copy()
            config_dict.update({"dbtable": table})
            config_dict.update(custom_config)
            mode = config_dict.get("mode") if config_dict.get("mode") else self.DEFAULT_DB_CONNECTOR_MODE
            logger.debug(f"config: {config_dict}")
            if config_dict.get("mode"):
                config_dict.pop("mode")
            dataframe.write.format("jdbc").options(**config_dict).mode(mode).save()
            logger.info(f"Write data to MySQL database table successful")
            return True
        except Exception as e:
            logger.error(f"Failed to write data to MySQL database table. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException(f"Failed to write data to mysql.")

    @logger.generate
    def check_database(self, configuration, connection):
        """
        Parses the table name and returns database, schema, and table

        :param configuration: Table name in the format database.schema.table
        :param connection: Dictionary containing MySQL connection details
        :return: Tuple containing database, schema, and table names
        """
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
            logger.error(f"Error occurred while parsing table name. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to check database.")