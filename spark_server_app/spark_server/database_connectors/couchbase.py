from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .db_connector import DatabaseConnector
from ..pipeline.utilities import Utilities
from pyspark.sql.functions import col, when, lit
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, MapType

logger = Logger
utils = Utilities()


class Couchbase(DatabaseConnector):
    def __init__(self, spark):
        super().__init__()
        self.spark = spark

    @logger.generate
    def connect(self, connection_id):
        """
        Connect to Couchbase - SparkSession is already configured in main.py
        """
        try:
            config = connection_id["details"]
            logger.info("Connecting to Couchbase...")
            
            # Verify connection details
            required_params = ["host", "username", "password", "bucket"]
            missing_params = [param for param in required_params if not config.get(param)]
            if missing_params:
                logger.error(f"Missing required Couchbase parameters: {missing_params}")
                raise ValueError(f"Missing required parameters: {missing_params}")
            
            # Build connection string 
            host = config["host"]
            connection_string = f"couchbase://{host}"
            config.update({"connection_string": connection_string})
            
            logger.info(" Connected to Couchbase successfully.")
            
            return config
        except Exception as e:
            logger.error(f" Error occurred while connecting to Couchbase: {str(e)}")
            raise DatabaseConnectionException("Failed to connect to Couchbase.")

    @logger.generate
    def test_connection(self, configuration, connection):
        """
        Test Couchbase connection
        """
        try:
            logger.info(" Testing Couchbase connection...")
            table_name = configuration['table_name']
            bucket, table_identifier = self.check_database(table_name, connection)
            
            # Parse scope and collection
            if "." in table_identifier:
                scope, collection = table_identifier.split(".", 1)
            else:
                scope, collection = "_default", table_identifier
            
            logger.info(f"Testing: bucket={bucket}, scope={scope}, collection={collection}")
            
            test_df = self.spark.read \
                .format("couchbase.query") \
                .option("bucket", bucket) \
                .option("scope", scope) \
                .option("collection", collection) \
                .load()
            
            # Get sample results
            result = test_df.take(3)
            row_count = len(result)
            column_count = len(test_df.columns)
            
            logger.info(f" Connection test successful!")
            
            if row_count > 0:
                sample_data = result[0].asDict()
                logger.info(f" Sample columns: {list(sample_data.keys())[:5]}")
            
            return True
            
        except Exception as e:
            logger.error(f" Connection test failed: {str(e)}")
            raise DatabaseConnectionException("Failed to test Couchbase connection.")

    @logger.generate
    def fetch_data(self, configuration, connection, custom_config={}):
        """
        Fetch data from Couchbase preserving original document structure
        """
        try:
            logger.info(" Starting Couchbase data fetch operation...")
            dfs = {}
            
            # Get table details
            bucket, table_identifier = self.check_database(configuration["table_name"], connection)
            
            # Parse scope and collection
            if "." in table_identifier:
                scope, collection = table_identifier.split(".", 1)
            else:
                scope, collection = "_default", table_identifier
            
            logger.info(f" Target: bucket='{bucket}', scope='{scope}', collection='{collection}'")
            
            # Build reader
            reader = self.spark.read \
                .format("couchbase.query") \
                .option("bucket", bucket) \
                .option("scope", scope) \
                .option("collection", collection)
            
            # Load data preserving original structure
            logger.info(" Loading data with original document structure preserved...")
            df = reader.load()
            
            # Get initial statistics
            original_count = df.count()
            logger.info(f" Raw Query Results: {original_count:,} rows, {len(df.columns)} columns")
            
            if original_count == 0:
                logger.warning(" No data found!")
                alias = configuration.get("dataframe_alias", f"couchbase_{bucket}_{scope}_{collection}")
                empty_df = self.spark.createDataFrame([], StructType([StructField("empty", StringType(), True)]))
                dfs.update({configuration["df_id"]: {"df": empty_df, "alias": alias}})
                return dfs
            
            # Apply basic null value normalization only
            logger.info(" Applying basic null value normalization...")
            normalized_df = self._normalize_null_values(df)
            
            # Final statistics
            final_count = normalized_df.count()
            logger.info(f" Final Results: {final_count:,} rows, {len(normalized_df.columns)} columns")
            
            # Create result
            alias = configuration.get("dataframe_alias", f"couchbase_{bucket}_{scope}_{collection}")
            dfs.update({configuration["df_id"]: {"df": normalized_df, "alias": alias}})

            return dfs
            
        except Exception as e:
            logger.error(f" Error occurred while fetching data from Couchbase: {str(e)}")
            raise DatabaseConnectionException("Failed to fetch data from Couchbase.")

    @logger.generate  
    def write_data(self, configuration, connection, dataframe, custom_config={}):
        """
        Write data to Couchbase preserving document structure
        """
        try:
            logger.info(" Writing data to Couchbase...")
            
            # Get target details
            bucket, table_identifier = self.check_database(configuration["table_name"], connection)
            
            # Parse scope and collection
            if "." in table_identifier:
                scope, collection = table_identifier.split(".", 1)
            else:
                scope, collection = "_default", table_identifier
            
            logger.info(f" Target: bucket='{bucket}', scope='{scope}', collection='{collection}'")
            
            row_count = dataframe.count()
            logger.info(f" Data to write: {row_count:,} rows, {len(dataframe.columns)} columns")

            write_df = dataframe
            
            # Ensure correct ID column name for Couchbase
            if "_meta_id" in write_df.columns:
                write_df = write_df.withColumnRenamed("_meta_id", "__META_ID")
                logger.info(" Renamed _meta_id to __META_ID for Couchbase compatibility")
            
            # Configure write options
            config_dict = {
                "bucket": bucket, 
                "scope": scope, 
                "collection": collection
            }
            config_dict.update(custom_config)
            
            # Set write mode (Couchbase doesn't support 'append')
            mode = config_dict.get("mode", "overwrite")
            if mode == "append":
                mode = "overwrite"
                logger.info(" Changed 'append' mode to 'overwrite' - Couchbase doesn't support append")
            
            if "mode" in config_dict:
                config_dict.pop("mode")
            
            # Set ID field
            id_field = configuration.get("id_field") or custom_config.get("id_field", "__META_ID")
            if id_field and id_field in write_df.columns:
                config_dict["idField"] = id_field
                logger.info(f" ID field: {id_field}")
            
            # Execute write operation
            logger.info(" Executing write operation...")
            write_df.write \
                .format("couchbase.kv") \
                .options(**config_dict) \
                .mode(mode) \
                .save()
            
            logger.info(f" Successfully written {row_count:,} rows to {bucket}.{scope}.{collection}")
            return True
            
        except Exception as e:
            logger.error(f" Error occurred while writing to Couchbase: {str(e)}")
            raise DatabaseConnectionException("Failed to write to Couchbase.")

    def _normalize_null_values(self, dataframe):
        """
        Normalize various null representations to proper nulls
        Preserves nested structure while cleaning null values
        """
        try:
            logger.info(" Normalizing null values while preserving document structure...")
            
            normalized_columns = []
            
            for field in dataframe.schema.fields:
                column_name = field.name
                
                # Only normalize string fields that might contain null representations
                # Leave complex types (structs, arrays, maps) unchanged
                if isinstance(field.dataType, (StructType, ArrayType, MapType)):
                    # Keep complex types as-is
                    normalized_columns.append(col(column_name))
                    logger.info(f" Preserved complex field: {column_name} ({field.dataType})")
                else:
                    # Convert various null representations to proper null for primitive types
                    normalized_col = when(
                        (col(column_name).isNull()) | 
                        (col(column_name) == "nan") | 
                        (col(column_name) == "null") | 
                        (col(column_name) == ""), 
                        lit(None)
                    ).otherwise(col(column_name)).alias(column_name)
                    
                    normalized_columns.append(normalized_col)
            
            result_df = dataframe.select(*normalized_columns)
            logger.info(f" Null normalization completed - {len(normalized_columns)} fields processed")
            return result_df
            
        except Exception as e:
            logger.error(f" Null normalization failed: {str(e)}")
            return dataframe

    def check_database(self, configuration, connection):
        """
        Parse table configuration to extract bucket and table identifier
        """
        try:
            bucket = connection.get("bucket")
            
            if not bucket:
                logger.error("Bucket not specified in connection details")
                raise ValueError("Bucket is required in connection details")
            
            # Parse table_name for scope.collection format
            if "." in configuration:
                scope, collection = configuration.split(".", 1)
                table_identifier = f"{scope}.{collection}"
            else:
                table_identifier = configuration
            
            return bucket, table_identifier
            
        except Exception as e:
            logger.error(f"Error occurred while checking database in Couchbase: {str(e)}")
            raise DatabaseConnectionException("Failed to check Couchbase database.")