import unittest
from spark_server.database_connectors.databricks import Databricks
from spark_server.exceptions.exceptions import *
import os
import pytest
from test_setup import TestSetup
import random
import string
from pyspark.sql.types import StructType, StructField, StringType


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestDatabricks(unittest.TestCase):
    # creating the instance of the class Databricks
    @classmethod
    def setUpClass(cls):
        cls.spark = TestSetup.set_up_spark()
        cls.databricks = Databricks(cls.spark)
        cls.connection_id = {
            "654879fe42a09b96f228302f": {
                "type": "database",
                "details": {
                    "type": "databricks",
                    "sourceName": "Databricks Connector",
                    "host": "dbc-c5ea0c5a-5db6.cloud.databricks.com",
                    "http_path": "/sql/1.0/warehouses/9f2b68d1944ee783",
                    "access_token": os.getenv("AOD_DATABRICKS_TOKEN", "dapi_mock_token_123"),
                    "database": "default",
                    "catalog": "workspace"
                }
            },
            "654879fe42a09b96f228303f": {
                "type": "database",
                "details": {
                    "type": "Databricks",
                    "sourceName": "Databricks Connector",
                    "host": "dbc-c5ea0c5a-5db6.cloud.databricks.com",
                    "http_path": "/sql/1.0/warehouses/9f2b68d1944ee783",
                    "access_token": os.getenv("AOD_DATABRICKS_TOKEN", "dapi_mock_token_123"),
                    "database": "default",
                    "catalog": "workspace",
                    "connection_pool": {
                        "pandas_pooling": {
                            "pool_size": "10",
                            "max_overflow": "20",
                            "pool_timeout": "30",
                            "pool_recycle": "1800",
                        },
                        "spark_pooling": {
                            "dbcp.maxTotal": "9",
                            "dbcp.maxIdle": "18",
                            "dbcp.maxWaitMillis": "35000",
                            "dbcp.maxConnLifetimeMillis": "1850000",
                        }
                    }
                }
            }
        }

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_connect(self):
        config = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        print(f"config {config}")
        self.assertIsNotNone(config)

    def test_test_connection(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "test_table", "df_id": "65cca96e00df89a55668f3df"}
        test_result = self.databricks.test_connection(config, connection)
        self.assertEqual(True, test_result)

    def test_fetch_data(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "test_table", "df_id": "65cca96e00df89a55668f3df"}
        result = self.databricks.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
    
    def test_fetch_data_with_columns(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "test_table", "df_id": "65cca96e00df89a55668f3df", "columns": ["id","name"]}
        result = self.databricks.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        self.assertEqual(["id", "name"], result["df"].columns)

    def test_fetch_data_with_custom_config_dbtable(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "test_table", "df_id": "65cca96e00df89a55668f3df"}
        custom_config = {"dbtable": "dummy"}
        result = self.databricks.fetch_data(config, connection, custom_config)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_custom_config_query(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "test_table", "df_id": "65cca96e00df89a55668f3df"}
        custom_config = {"query": "select * from dummy"}
        result = self.databricks.fetch_data(config, connection, custom_config)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_invalid_table_in_custom_config(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "test_table", "df_id": "65cca96e00df89a55668f3df"}
        custom_config = {"dbtable": "country_5"}
        with pytest.raises(DatabaseConnectionException) as test_function:
            self.databricks.fetch_data(config, connection, custom_config)
        self.assertEqual("Failed to fetch the data from Databricks.", str(test_function.value))

    def test_fetch_data_with_connection_pool(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228303f"])
        config = {"connection_id": "654879fe42a09b96f228303f", "table_name": "test_table", "df_id": "65cca96e00df89a55668f3df"}
        result = self.databricks.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    #@pytest.mark.skip("Table has key constraints unable to overwrite")
    def test_write_data(self):
        """
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        #data = [(random_values, random_values)]
        """
        data = [
            ("India", "INR"),
            ("Australia", "AUD")
        ]
        schema = StructType([
            StructField("country", StringType(), True),
            StructField("currency", StringType(), True)
        ])
        print("SparkContext:", self.spark.sparkContext)
        print("JVM:", self.spark.sparkContext._jvm)
        print("Is JVM accessible?", hasattr(self.spark.sparkContext._jvm, 'SimplePythonFunction'))
        dataframe = self.spark.createDataFrame(data, schema)
        dataframe.show()
        """
        result = self.databricks.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        result = self.databricks.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        """

    def test_write_data_with_custom_config(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random_values, random_values)]
        dataframe = self.spark.createDataFrame(data, ["country", "currency"])
        custom_config = {"dbtable": "country"}
        result = self.databricks.write_data(config, connection, dataframe, custom_config)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        result = self.databricks.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_connection_pool(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228303f"])
        config = {"connection_id": "654879fe42a09b96f228303f", "table_name": "country", "df_id":"65cca96e00df89a55668f3df"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random_values, random_values)]
        dataframe = self.spark.createDataFrame(data, ["country", "currency"])
        result = self.databricks.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228303f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        result = self.databricks.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_check_database(self):
        connection = self.databricks.connect(self.connection_id["654879fe42a09b96f228302f"])
        configuration = "employee"
        database, table = self.databricks.check_database(configuration, connection)
        self.assertEqual(connection["database"], database)


if __name__ == "__main__":
    unittest.main()
