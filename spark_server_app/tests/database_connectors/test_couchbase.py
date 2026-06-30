# import unittest
# import os
# import pytest
# from test_setup import TestSetup
# from spark_server.database_connectors.couchbase import Couchbase
# from spark_server.exceptions.exceptions import DatabaseConnectionException
# from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType, MapType
# from pyspark.sql.functions import col, lit
# from datetime import datetime


# # @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
# class TestCouchbase(unittest.TestCase):
#     """Test suite for Spark-based Couchbase connector"""
    
#     @classmethod
#     def setUpClass(cls):
#         """Set up test class with Spark session and Couchbase connector"""
#         cls.spark = TestSetup.set_up_spark()
#         cls.couchbase = Couchbase(cls.spark)
        
#         # Test connection configurations
#         cls.connection_id = {
#             "687dc956a1d271c7cf93f4fe": {
#                 "type": "database",
#                 "details": {
#                     "type": "couchbase",
#                     "sourceName": "Couchbase Test Connector",
#                     "host": "164.52.218.57",
#                     "port": 8091,
#                     "username": "dbuser",
#                     "password": "dbpass",
#                     "bucket": "test_bucket"
#                 }
#             }
#         }
    
#     @classmethod
#     def tearDownClass(cls):
#         """Clean up Spark session"""
#         cls.spark.stop()

#     # ========================
#     # CONNECTION TESTS
#     # ========================
    
#     def test_connect(self):
#         """Test basic connection to Couchbase"""
#         config = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         self.assertIsNotNone(config)
#         self.assertIn("connection_string", config)
#         self.assertIn("host", config)
#         self.assertIn("bucket", config)
#         self.assertEqual(config["bucket"], "test_bucket")
#         self.assertTrue(config["connection_string"].startswith("couchbase://"))
    
#     def test_connect_with_missing_parameters(self):
#         """Test connection failure with missing required parameters"""
#         invalid_connection = {
#             "type": "database",
#             "details": {
#                 "type": "couchbase",
#                 "host": "164.52.218.57"
#                 # Missing username, password, bucket
#             }
#         }
        
#         with self.assertRaises(DatabaseConnectionException):
#             self.couchbase.connect(invalid_connection)
    
#     def test_connect_with_custom_port(self):
#         """Test connection with custom port"""
#         custom_port_connection = self.connection_id["654879fe42a09b96f228302c"].copy()
#         custom_port_connection["details"]["port"] = 8092
        
#         config = self.couchbase.connect(custom_port_connection)
#         self.assertIsNotNone(config)
#         self.assertIn("connection_string", config)

#     # ========================
#     # CONNECTION TEST VALIDATION
#     # ========================
    
#     def test_test_connection(self):
#         """Test connection validation"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "_default._default",
#             "df_id": "test_df_id"
#         }
        
#         try:
#             test_result = self.couchbase.test_connection(config, connection)
#             self.assertTrue(test_result)
#         except DatabaseConnectionException as e:
#             if "empty" in str(e).lower() or "no data" in str(e).lower():
#                 self.skipTest("Test collection is empty - connection test requires data")
#             else:
#                 raise
    
#     def test_test_connection_with_scope_collection(self):
#         """Test connection validation with specific scope and collection"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "test_scope.test_collection",
#             "df_id": "test_df_id"
#         }
        
#         try:
#             test_result = self.couchbase.test_connection(config, connection)
#             self.assertTrue(test_result)
#         except DatabaseConnectionException as e:
#             if "does not exist" in str(e).lower() or "not found" in str(e).lower():
#                 self.skipTest("Test scope/collection does not exist")
#             else:
#                 # Test should still validate the connection logic
#                 self.assertIn("Failed to test Couchbase connection", str(e))

#     # ========================
#     # DATA FETCHING TESTS
#     # ========================
    
#     def test_fetch_data_default_collection(self):
#         """Test fetching data from default collection"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "_default._default",
#             "df_id": "test_fetch_df"
#         }
        
#         try:
#             result = self.couchbase.fetch_data(config, connection)
#             self.assertIn("test_fetch_df", result)
#             self.assertIsNotNone(result["test_fetch_df"]["df"])
#             self.assertIn("alias", result["test_fetch_df"])
            
#             df = result["test_fetch_df"]["df"]
#             self.assertGreaterEqual(df.count(), 0)  # Allow empty results
            
#         except DatabaseConnectionException as e:
#             if "empty" in str(e).lower() or "no data" in str(e).lower():
#                 self.skipTest("Default collection is empty")
#             else:
#                 raise
    
#     def test_fetch_data_with_scope_collection(self):
#         """Test fetching data from specific scope and collection"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "test_scope.users",
#             "df_id": "test_scoped_df"
#         }
        
#         try:
#             result = self.couchbase.fetch_data(config, connection)
#             self.assertIn("test_scoped_df", result)
#             df = result["test_scoped_df"]["df"]
#             self.assertIsNotNone(df)
            
#         except DatabaseConnectionException as e:
#             if "does not exist" in str(e).lower():
#                 self.skipTest("Test scope/collection does not exist")
#             else:
#                 raise
    
    
#     def test_fetch_data_with_custom_alias(self):
#         """Test fetching data with custom DataFrame alias"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "_default._default",
#             "dataframe_alias": "custom_couchbase_data",
#             "df_id": "test_alias_df"
#         }
        
#         try:
#             result = self.couchbase.fetch_data(config, connection)
#             self.assertIn("test_alias_df", result)
#             self.assertEqual(result["test_alias_df"]["alias"], "custom_couchbase_data")
            
#         except DatabaseConnectionException as e:
#             if "empty" in str(e).lower():
#                 self.skipTest("Collection is empty")
#             else:
#                 raise
    
#     def test_fetch_data_with_connection_pool(self):
#         """Test fetching data with connection pooling configuration"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302d"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302d",
#             "table_name": "_default._default",
#             "df_id": "test_pooled_df"
#         }
        
#         try:
#             result = self.couchbase.fetch_data(config, connection)
#             self.assertIn("test_pooled_df", result)
#             df = result["test_pooled_df"]["df"]
#             self.assertIsNotNone(df)
            
#         except DatabaseConnectionException as e:
#             if "empty" in str(e).lower():
#                 self.skipTest("Collection is empty for pooling test")
#             else:
#                 raise
    
#     def test_fetch_data_nonexistent_collection(self):
#         """Test fetching data from non-existent collection"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "nonexistent_scope.nonexistent_collection",
#             "df_id": "test_error_df"
#         }
        
#         with self.assertRaises(DatabaseConnectionException) as context:
#             self.couchbase.fetch_data(config, connection)
        
#         self.assertIn("Failed to fetch data from Couchbase", str(context.exception))

#     # ========================
#     # DATA WRITING TESTS
#     # ========================
    
#     def test_write_data_basic(self):
#         """Test writing basic data to Couchbase"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "_default.test_write_collection",
#             "df_id": "test_write_df"
#         }
        
#         # Create test DataFrame
#         schema = StructType([
#             StructField("__META_ID", StringType(), True),
#             StructField("id", IntegerType(), True),
#             StructField("name", StringType(), True),
#             StructField("email", StringType(), True),
#             StructField("created_at", TimestampType(), True)
#         ])
        
#         test_data = [
#             ("user_001", 1, "John Doe", "john@example.com", 
#              datetime.strptime("2024-01-15 10:30:00", "%Y-%m-%d %H:%M:%S")),
#             ("user_002", 2, "Jane Smith", "jane@example.com", 
#              datetime.strptime("2024-01-16 14:45:00", "%Y-%m-%d %H:%M:%S"))
#         ]
        
#         dataframe = self.spark.createDataFrame(test_data, schema)
        
#         try:
#             result = self.couchbase.write_data(config, connection, dataframe)
#             self.assertTrue(result)
            
#             # Verify data was written by reading it back
#             read_config = {
#                 "connection_id": "654879fe42a09b96f228302c",
#                 "table_name": "_default.test_write_collection",
#                 "df_id": "test_read_back_df"
#             }
            
#             read_result = self.couchbase.fetch_data(read_config, connection)
#             read_df = read_result["test_read_back_df"]["df"]
#             self.assertGreaterEqual(read_df.count(), 2)
            
#         except Exception as e:
#             if "permission" in str(e).lower() or "unauthorized" in str(e).lower():
#                 self.skipTest("Insufficient permissions for write operations")
#             else:
#                 raise
    
#     def test_write_data_with_custom_id_field(self):
#         """Test writing data with custom ID field"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "_default.test_custom_id_collection",
#             "id_field": "custom_id",
#             "df_id": "test_custom_id_df"
#         }
        
#         schema = StructType([
#             StructField("custom_id", StringType(), True),
#             StructField("data", StringType(), True)
#         ])
        
#         test_data = [
#             ("custom_001", "Test Data 1"),
#             ("custom_002", "Test Data 2")
#         ]
        
#         dataframe = self.spark.createDataFrame(test_data, schema)
        
#         try:
#             result = self.couchbase.write_data(config, connection, dataframe)
#             self.assertTrue(result)
            
#         except Exception as e:
#             if "permission" in str(e).lower():
#                 self.skipTest("Insufficient permissions for write operations")
#             else:
#                 raise
    
#     def test_write_data_with_custom_config(self):
#         """Test writing data with custom configuration"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "_default.test_custom_config_collection",
#             "df_id": "test_custom_config_df"
#         }
        
#         schema = StructType([
#             StructField("__META_ID", StringType(), True),
#             StructField("value", IntegerType(), True)
#         ])
        
#         test_data = [
#             ("config_001", 100),
#             ("config_002", 200)
#         ]
        
#         dataframe = self.spark.createDataFrame(test_data, schema)
#         custom_config = {
#             "mode": "append",  # This should be converted to overwrite
#             "durabilityLevel": "MAJORITY"
#         }
        
#         try:
#             result = self.couchbase.write_data(config, connection, dataframe, custom_config)
#             self.assertTrue(result)
            
#         except Exception as e:
#             if "permission" in str(e).lower():
#                 self.skipTest("Insufficient permissions for write operations")
#             else:
#                 raise
    
#     def test_write_data_with_meta_id_rename(self):
#         """Test writing data with _meta_id field (should be renamed to __META_ID)"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "_default.test_meta_rename_collection",
#             "df_id": "test_meta_rename_df"
#         }
        
#         schema = StructType([
#             StructField("_meta_id", StringType(), True),  # This should be renamed
#             StructField("content", StringType(), True)
#         ])
        
#         test_data = [
#             ("meta_001", "Content 1"),
#             ("meta_002", "Content 2")
#         ]
        
#         dataframe = self.spark.createDataFrame(test_data, schema)
        
#         try:
#             result = self.couchbase.write_data(config, connection, dataframe)
#             self.assertTrue(result)
            
#         except Exception as e:
#             if "permission" in str(e).lower():
#                 self.skipTest("Insufficient permissions for write operations")
#             else:
#                 raise

#     # UTILITY TESTS

    
#     def test_check_database_default_collection(self):
#         """Test database parsing for default collection"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         configuration = "_default"
        
#         bucket, table_identifier = self.couchbase.check_database(configuration, connection)
#         self.assertEqual(bucket, "test_bucket")
#         self.assertEqual(table_identifier, "_default")
    
#     def test_check_database_scope_collection(self):
#         """Test database parsing for scope.collection format"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
#         configuration = "test_scope.test_collection"
        
#         bucket, table_identifier = self.couchbase.check_database(configuration, connection)
#         self.assertEqual(bucket, "test_bucket")
#         self.assertEqual(table_identifier, "test_scope.test_collection")
    
#     def test_check_database_missing_bucket(self):
#         """Test database parsing with missing bucket in connection"""
#         invalid_connection = {"host": "test", "username": "test", "password": "test"}
#         configuration = "test_collection"
        
#         with self.assertRaises(DatabaseConnectionException):
#             self.couchbase.check_database(configuration, invalid_connection)
    
#     def test_normalize_null_values(self):
#         """Test null value normalization functionality"""
#         # Create test DataFrame with various null representations
#         schema = StructType([
#             StructField("normal_field", StringType(), True),
#             StructField("null_field", StringType(), True),
#             StructField("empty_field", StringType(), True),
#             StructField("nan_field", StringType(), True),
#             StructField("nested_field", MapType(StringType(), StringType()), True)
#         ])
        
#         test_data = [
#             ("valid_data", None, "", "nan", {"key": "value"}),
#             ("another_valid", "null", "", "nan", {"nested": "data"})
#         ]
        
#         df = self.spark.createDataFrame(test_data, schema)
#         normalized_df = self.couchbase._normalize_null_values(df)
        
#         self.assertIsNotNone(normalized_df)
#         self.assertEqual(df.count(), normalized_df.count())
#         self.assertEqual(len(df.columns), len(normalized_df.columns))


# if __name__ == "__main__":
#     unittest.main(verbosity=2)



# -------------------------------------------------------------------------

# import unittest
# from spark_server.database_connectors.couchbase import Couchbase
# from spark_server.exceptions.exceptions import *
# import os
# import pytest
# from test_setup import TestSetup  # Import corrected setup
# from pyspark.sql.types import StructType, StructField, IntegerType, StringType

# class TestCouchbase(unittest.TestCase):
    
#     @classmethod
#     def setUpClass(cls):
#         # Use the corrected setup with proper credentials
#         cls.spark = TestSetup.set_up_spark()
#         cls.couchbase = Couchbase(cls.spark)
        
#         # Updated connection configuration with CORRECT details
#         cls.connection_id = {
#             "687dc956a1d271c7cf93f4fe": {
#                 "type": "database",
#                 "details": {
#                     "type": "couchbase",
#                     "sourceName": "Couchbase Connector",
#                     "host": "164.52.218.57",      # Correct host
#                     "port": "8091",               # Management port
#                     "username": "dbuser",         # Correct username
#                     "password": "dbpass",         # Correct password
#                     "bucket": "test_bucket"       # Correct bucket
#                 }
#             },
#         }

#     @classmethod
#     def tearDownClass(cls):
#         if hasattr(cls, 'spark') and cls.spark:
#             cls.spark.stop()

#     def test_environment_check(self):
#         """Test that Couchbase configuration is properly set"""
#         spark_conf = self.spark.sparkContext.getConf()
        
#         # Verify Couchbase configurations are set
#         connection_string = spark_conf.get("spark.couchbase.connectionString", None)
#         username = spark_conf.get("spark.couchbase.username", None)
#         bucket = spark_conf.get("spark.couchbase.implicitBucket", None)
        
#         self.assertIsNotNone(connection_string, "Couchbase connection string should be set")
#         self.assertIsNotNone(username, "Couchbase username should be set")
#         self.assertIsNotNone(bucket, "Couchbase bucket should be set")
        
#         # Verify correct values
#         self.assertEqual(connection_string, "couchbase://164.52.218.57")
#         self.assertEqual(username, "dbuser")
#         self.assertEqual(bucket, "test_bucket")
        
#         print(f" Couchbase connection string: {connection_string}")
#         print(f" Couchbase username: {username}")
#         print(f" Couchbase bucket: {bucket}")

#     def test_connect(self):
#         """Test connection method with correct credentials"""
#         config = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
        
#         # Verify connection configuration
#         self.assertIsNotNone(config["connection_string"])
#         self.assertEqual(config["connection_string"], "couchbase://164.52.218.57")
#         self.assertEqual(config["username"], "dbuser")
#         self.assertEqual(config["password"], "dbpass")
#         self.assertEqual(config["bucket"], "test_bucket")
        
#         print(f" Connection config: {config}")

#     def test_fetch_data_inventory_products(self):
#         """Test fetching data from the specific collection: test_bucket.inventory.products"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
        
#         # Use your specific collection: test_bucket.inventory.products
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "inventory.products",  # scope.collection format
#             "df_id": "test_inventory_products"
#         }
        
#         try:
#             result = self.couchbase.fetch_data(config, connection)["test_inventory_products"]
#             self.assertIsNotNone(result["df"])
            
#             # Check if we have data
#             row_count = result["df"].count()
#             print(f" Fetched {row_count} rows from inventory.products")
            
#             # Show schema
#             print(" Schema:")
#             result["df"].printSchema()
            
#             # Show sample data (first few rows)
#             if row_count > 0:
#                 print(" Sample data:")
#                 result["df"].show(5, truncate=False)
            
#         except Exception as e:
#             print(f" Fetch failed: {str(e)}")
#             # This might still fail if there's no data in the collection
#             # but at least we can see if the connection works
#             raise

#     def test_write_data_to_inventory_products(self):
#         """Test writing data to inventory.products collection"""
#         connection = self.couchbase.connect(self.connection_id["654879fe42a09b96f228302c"])
        
#         config = {
#             "connection_id": "654879fe42a09b96f228302c",
#             "table_name": "inventory.products",
#             "df_id": "test_write_products"
#         }

#         # Create test data for products
#         schema = StructType([
#             StructField("__META_ID", StringType(), True),
#             StructField("product_name", StringType(), True),
#             StructField("price", IntegerType(), True),
#             StructField("category", StringType(), True)
#         ])

#         test_data = [
#             ("product_001", "Test Product 1", 100, "Electronics"),
#             ("product_002", "Test Product 2", 200, "Books")
#         ]

#         dataframe = self.spark.createDataFrame(test_data, schema)

#         try:
#             result = self.couchbase.write_data(config, connection, dataframe)
#             self.assertTrue(result)
#             print(" Successfully wrote test data to inventory.products")
            
#         except Exception as e:
#             print(f" Write failed: {str(e)}")
#             raise

# if __name__ == "__main__":
#     unittest.main(verbosity=2)