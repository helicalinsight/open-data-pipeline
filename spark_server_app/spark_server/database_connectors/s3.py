from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .db_connector import DatabaseConnector
from ..pipeline.utilities import Utilities
import boto3

logger = Logger
utils = Utilities()

class S3(DatabaseConnector):
    """
    A class to interact with S3 storage using PySpark
    """
    def __init__(self, spark):
        """
        Initializes the S3 connector with a SparkSession

        :param spark: SparkSession object
        """
        super().__init__()
        self.spark = spark

    @logger.generate
    def connect(self, connection_id):
        """
        Connects to S3 database using connection details from MongoDB

        :param connection_id: Identifier of the S3 connection in MongoDB
        :return: Dictionary containing S3 connection details
        """
        try:
            logger.info("Connecting to s3..")
            config = connection_id["details"]
            self.spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.access.key", config["aws_access_key"])
            self.spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.secret.key", config["aws_secret_key"])
            self.spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.endpoint", "s3.amazonaws.com")
            self.spark.sparkContext._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            self.spark.sparkContext._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.path.style.access", "true")
            self.spark.sparkContext._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")
            self.spark.sparkContext._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")

            logger.debug(f"Connection_details: {config}")
            conn = config.copy()
            conn.pop("type", None)
            conn.pop("sourceName", None)
            logger.info("Connection to S3 is successfull.")
            return conn
        except Exception as e:
            logger.error(f"Failed to get S3 connection details. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to connect to S3 database.")
        
    @logger.generate
    def test_connection(self, configuration, connection):
        """
        Tests the S3 connection by reading data from a specified bucket.

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing S3 connection details
        :return: True if connection test successful, False otherwise
        """
        try:
            logger.info("Testing S3 connection.")
            bucket_name = connection["bucket_name"]
            s3_path = f"s3a://{bucket_name}/"

            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            path = self.spark._jvm.org.apache.hadoop.fs.Path(s3_path)

            fs = self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(
                self.spark._jvm.java.net.URI.create(s3_path),
                hadoop_conf
            )

            if not fs.exists(path):
                raise Exception("Bucket does not exist or is inaccessible")

            status = fs.listStatus(path)
            files = [str(f.getPath().toString()) for f in status]
            for file in files:
                logger.info(file)

            logger.info("S3 connection test successful!")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to S3. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException("Failed to test S3 connection.")
    
    @logger.generate
    def fetch_data(self, configuration, connection, custom_config={}):
        """
        Fetches data from S3 table and returns as a dictionary of DataFrames

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing S3 connection details
        :return: Dictionary containing DataFrame with fetched data
        """
        try:
            dfs = {}
            logger.info("Fetching the S3 files.")
            bucket_name = connection["bucket_name"]
            file_key = configuration["file_name"]
            sheet_name = None
            if file_key.count(".") == 2:
                for ext in ("xlsx", "xls"):
                    dot_ext = f".{ext}."
                    if dot_ext in file_key:
                        parts = file_key.split(dot_ext, 1)
                        if len(parts) == 2:
                            file_key = f"{parts[0]}.{ext}"
                            sheet_name = parts[1].strip()
                        break
            try:
                file_extension = file_key.lower().split(".")[-1]
                s3_path = f"s3a://{bucket_name}/{file_key}"
                if file_extension == "csv":
                    df = self.spark.read.csv(s3_path, header=True, inferSchema=True)

                elif file_extension in ["parquet", "pq"]:
                    df = self.spark.read.parquet(s3_path)

                elif file_extension in ["xls", "xlsx"]:
                    df = self.spark.read.format("com.crealytics.spark.excel") \
                                .option("header", "true") \
                                .option("inferSchema", "true") \
                                .option("dataAddress", f"'{sheet_name}'!A1") \
                                .load(s3_path)
                    
                elif file_extension == "json":
                    df = self.spark.read.json(s3_path, multiLine=True)

                else:
                    raise DatabaseConnectionException(f"Unsupported file type: {file_extension}")
                logger.info("Fetched data from S3 successfully.")
            except Exception as e:
                logger.error(f"Failed to fetch data from S3: {str(e)}")
                raise DatabaseConnectionException(f"Failed to fetch S3 data due to {str(e)}") from e

            alias=configuration.get("dataframe_alias","s3_"+file_key)
            dfs.update({configuration["df_id"]: {"df": df, "alias": alias}})
            
            logger.info("Fetched data successfully.")
            return dfs
        except Exception as e:
            logger.error(f"Failed to fetch data from S3. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException(f"Failed to fetch data from S3.")
        
    @logger.generate
    def write_data(self, configuration, connection, dataframe, custom_config={}):
        """
        Writes data to S3

        :param configuration: Dictionary containing configuration details
        :param connection: Dictionary containing S3 connection details
        :param dataframe: Spark DataFrame containing data to be written
        """
        try:
            logger.info("Writing data to S3")
            bucket_name = connection["bucket_name"]
            file_key = configuration["table_name"]
            config_dict = connection.copy()
            mode = config_dict.get("mode") if config_dict.get("mode") else self.DEFAULT_S3_CONNECTOR_MODE
            logger.debug(f"config: {config_dict}")
            if config_dict.get("mode"):
                config_dict.pop("mode")
            output_path = f"s3a://{bucket_name}/{file_key}"
            dataframe.write.mode(mode).csv(output_path, header=True)
            logger.info(f"Write data to S3 database table successful")
            return True
        except Exception as e:
            logger.error(f"Failed to write data to S3 database table. Operation Completed with Exception: {str(e)}")
            raise DatabaseConnectionException(f"{str(e)}")
        
    @logger.generate
    def check_database(self, configuration, connection):
        """
        Parses the table name and returns database, schema, and table

        :param configuration: Table name in the format database.schema.table
        :param connection: Dictionary containing S3 connection details
        :return: Tuple containing database, schema, and table names
        """
        pass
