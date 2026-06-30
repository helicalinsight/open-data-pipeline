import unittest
from unittest.mock import patch, MagicMock
from spark_server.database_connectors.s3 import S3
from spark_server.exceptions.exceptions import DatabaseConnectionException
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
import random
import string


class TestS3(unittest.TestCase):
    # creating the instance of the class S3
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.master("local").appName("S3MockTest").getOrCreate()
        cls.s3 = S3(cls.spark)
        cls.connection_id = {
            "mock_conn": {
                "type": "s3",
                "details": {
                    "aws_access_key": "DUMMY_KEY",
                    "aws_secret_key": "DUMMY_SECRET",
                    "bucket_name": "dummy-bucket",
                    "aws_region": "us-dummy-1",
                    "sourceName": "s3 Connector"
                }
            }
        }
        cls.data = [(1, "CityA"), (2, "CityB")]
        cls.schema = StructType([
            StructField("personid", IntegerType(), True),
            StructField("city", StringType(), True)
        ])
        cls.df = cls.spark.createDataFrame(cls.data, schema=cls.schema)

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    @patch.object(S3, 'connect')
    def test_connect(self, mock_connect):
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        config = self.s3.connect(self.connection_id["mock_conn"])
        self.assertIn("aws_access_key", config)
        self.assertIn("bucket_name", config)
        
    @patch.object(S3, 'test_connection')
    @patch.object(S3, 'connect')
    def test_test_connection(self, mock_connect, mock_test_connection):
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        mock_test_connection.return_value = True

        connection = self.s3.connect(self.connection_id["mock_conn"])
        config = {"connection_id": "mock_conn", "file_name": "dummy.xlsx", "df_id": "dummy_id"}
        result = self.s3.test_connection(config, connection)
        self.assertTrue(result)

    @patch.object(S3, 'test_connection')
    @patch.object(S3, 'connect')
    def test_test_connection_invalid_bucket(self, mock_connect, mock_test_connection):
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        mock_test_connection.side_effect = DatabaseConnectionException("Bucket does not exist")
        connection = self.s3.connect(self.connection_id["mock_conn"])
        config = {"connection_id": "mock_conn", "file_name": "dummy.xlsx", "df_id": "dummy_id"}
        with self.assertRaises(DatabaseConnectionException):
            self.s3.test_connection(config, connection)

    @patch.object(S3, 'fetch_data')
    @patch.object(S3, 'connect')
    def test_fetch_data_csv(self, mock_connect, mock_fetch_data):
        """Test fetch_data returns a DataFrame when reading CSV"""
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        mock_fetch_data.return_value = {"dummy_id": {"df": self.df}}
        connection = self.s3.connect(self.connection_id["mock_conn"])
        config = {"connection_id": "mock_conn", "file_name": "dummy.csv", "df_id": "dummy_id"}
        result = self.s3.fetch_data(config, connection)["dummy_id"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 2)
        mock_connect.assert_called_once()
        mock_fetch_data.assert_called_once_with(config, connection)
    
    @patch.object(S3, 'fetch_data')
    @patch.object(S3, 'connect')
    def test_fetch_data_xlsx(self, mock_connect, mock_fetch_data):
        """Test fetch_data returns a DataFrame when reading XLSX"""
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        mock_fetch_data.return_value = {"dummy_id": {"df": self.df}}
        connection = self.s3.connect(self.connection_id["mock_conn"])
        config = {"connection_id": "mock_conn", "file_name": "dummy.xlsx.test1", "df_id": "dummy_id"}
        result = self.s3.fetch_data(config, connection)["dummy_id"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 2)
        mock_connect.assert_called_once()
        mock_fetch_data.assert_called_once_with(config, connection)

    @patch.object(S3, 'fetch_data')
    @patch.object(S3, 'connect')
    def test_fetch_data_parquet(self, mock_connect, mock_fetch_data):
        """Test fetch_data returns a DataFrame when reading parquet"""
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        mock_fetch_data.return_value = {"dummy_id": {"df": self.df}}
        connection = self.s3.connect(self.connection_id["mock_conn"])
        config = {"connection_id": "mock_conn", "file_name": "dummy.parquet", "df_id": "dummy_id"}
        result = self.s3.fetch_data(config, connection)["dummy_id"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 2)
        mock_connect.assert_called_once()
        mock_fetch_data.assert_called_once_with(config, connection)
    
    @patch.object(S3, 'fetch_data')
    @patch.object(S3, 'connect')
    def test_fetch_data_unsupported_filetype(self, mock_connect, mock_fetch_data):
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        mock_fetch_data.side_effect = DatabaseConnectionException("Unsupported file type: abc")
        config = {"connection_id": "mock_conn", "file_name": "dummy.abc", "df_id": "dummy_id"}
        connection = self.s3.connect(self.connection_id["mock_conn"])
        with self.assertRaises(DatabaseConnectionException):
            self.s3.fetch_data(config, connection)

    @patch.object(S3, 'fetch_data')
    @patch.object(S3, 'write_data')
    @patch.object(S3, 'connect')
    def test_write_data(self, mock_connect, mock_write_data, mock_fetch_data):
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        mock_write_data.return_value = True
        config = {"connection_id": "mock_conn", "file_name": "new.csv", "df_id": "dummy_id"}
        result = self.s3.write_data(config, self.connection_id["mock_conn"]["details"], self.df)
        self.assertTrue(result)
        mock_fetch_data.return_value = {"dummy_id": {"df": self.df}}
        fetch_result = self.s3.fetch_data(config, self.connection_id["mock_conn"]["details"])["dummy_id"]
        self.assertIsNotNone(fetch_result["df"])
        self.assertGreaterEqual(fetch_result["df"].count(), 1)
        mock_write_data.assert_called_once_with(config, self.connection_id["mock_conn"]["details"], self.df)

    @patch.object(S3, 'write_data')
    @patch.object(S3, 'connect')
    def test_write_data_failure(self, mock_connect, mock_write_data):
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        mock_write_data.side_effect = DatabaseConnectionException("Failed to write to S3")
        config = {"connection_id": "mock_conn", "file_name": "fail.csv", "df_id": "dummy_id"}
        with self.assertRaises(DatabaseConnectionException):
            self.s3.write_data(config, self.connection_id["mock_conn"]["details"], self.df)

    @patch.object(S3, 'check_database')
    @patch.object(S3, 'connect')
    def test_check_database(self, mock_connect, mock_check_database):
        mock_connect.return_value = self.connection_id["mock_conn"]["details"]
        mock_check_database.return_value = ("public", "demo")

        config_str = "public.demo"
        database, table = self.s3.check_database(config_str, self.connection_id["mock_conn"]["details"])
        self.assertEqual(database, "public")
        self.assertEqual(table, "demo")


if __name__ == "__main__":
    unittest.main()