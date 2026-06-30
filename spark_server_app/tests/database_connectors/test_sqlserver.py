import unittest
from spark_server.database_connectors.sqlserver import SQLServer
from spark_server.exceptions.exceptions import *
import os
import pytest
from test_setup import TestSetup
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType
from datetime import datetime


@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestSQLServer(unittest.TestCase):
    # creating the instance of the class SQLServer
    @classmethod
    def setUpClass(cls):
        cls.spark = TestSetup.set_up_spark()
        cls.sqlserver = SQLServer(cls.spark)
        cls.connection_id = {
            "654879fe42a09b96f228302c": {
                "type": "database",
                "details": {
                    "type": "sqlserver",
                    "sourceName": "SQLServer Connector",
                    "host": "localhost",
                    "port": "1433",
                    "username": "SA",
                    "password": "HelicalMsSqlServer@123",
                    "database": "sakila"
                }
            }
        }

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_connect(self):
        config = self.sqlserver.connect(self.connection_id["654879fe42a09b96f228302c"])
        self.assertIsNotNone(config["url"])

    def test_test_connection(self):
        connection = self.sqlserver.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        test_result = self.sqlserver.test_connection(config, connection)
        self.assertEqual(True, test_result)

    def test_fetch_data(self):
        connection = self.sqlserver.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.sqlserver.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_columns(self):
        connection = self.sqlserver.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor", "columns": ["first_name", "last_name"], "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.sqlserver.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        self.assertEqual(["first_name", "last_name"], result["df"].columns)
    
    def test_fetch_data_with_custom_config(self):
        connection = self.sqlserver.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {"dbtable": "(SELECT * FROM actor where actor_id=1) as test"}
        result = self.sqlserver.fetch_data(config, connection, custom_config)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_invalid_table_in_custom_config(self):
        connection = self.sqlserver.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {"dbtable": "actor_1"}
        with pytest.raises(DatabaseConnectionException) as test_function:
            self.sqlserver.fetch_data(config, connection, custom_config)
        self.assertEqual("Failed to fetch the data from database.", str(test_function.value))

    def test_write_data(self):
        """
        Test writing data to SQLServer database table
        """
        connection = self.sqlserver.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        test_data = [
            (3, "Chandler", "Bing", datetime.strptime("2024-02-15 04:34:33", "%Y-%m-%d %H:%M:%S")),
            (4, "Rachel", "Green", datetime.strptime("2024-02-16 06:52:11", "%Y-%m-%d %H:%M:%S"))
        ]
        dataframe = self.spark.createDataFrame(test_data, schema)
        result = self.sqlserver.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.sqlserver.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_custom_config(self):
        """
        Test writing data to SQLServer database table
        """
        connection = self.sqlserver.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        test_data = [
            (1, "Chandler", "Bing", datetime.strptime("2024-02-15 04:34:33", "%Y-%m-%d %H:%M:%S")),
            (2, "Rachel", "Green", datetime.strptime("2024-02-16 06:52:11", "%Y-%m-%d %H:%M:%S"))
        ]
        dataframe = self.spark.createDataFrame(test_data, schema)
        custom_config = {"mode": "append"}
        result = self.sqlserver.write_data(config, connection, dataframe, custom_config)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.sqlserver.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)


if __name__ == "__main__":
    unittest.main()
