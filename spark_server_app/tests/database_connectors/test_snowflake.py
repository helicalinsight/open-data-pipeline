import unittest
from spark_server.database_connectors.snowflake import Snowflake
import os
import pytest
from test_setup import TestSetup
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType
from datetime import datetime


@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestSnowflake(unittest.TestCase):
    # creating the instance of the class Snowflake
    @classmethod
    def setUpClass(cls):
        cls.spark = TestSetup.set_up_spark()
        cls.snowflake = Snowflake(cls.spark)
        cls.connection_id = {
            "654879fe42a09b96f228302e": {
                "type": "database",
                "details": {
                    "type": "snowflake",
                    "sourceName": "Snowflake Connector",
                    "sfDatabase": "sakila",
                    "sfPassword": "SampleUser123",
                    "sfUser": "sampletest",
                    "sfAccountIdentifier": "ttggoiw-xy98467",
                    "sfSchema": "PUBLIC",
                    "sfWarehouse": "MY_WAREHOUSE"
                }
            },
            "654879fe42a09b96f228302f": {
                "type": "database",
                "details": {
                    "type": "snowflake",
                    "sourceName": "Snowflake Connector",
                    "sfDatabase": None,
                    "sfPassword": "SampleUser123",
                    "sfUser": "sampletest",
                    "sfAccountIdentifier": "ttggoiw-xy98467",
                    "sfSchema": "PUBLIC",
                    "sfWarehouse": "MY_WAREHOUSE"
                }
            }
        }

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_connect(self):
        config = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        self.assertEqual("sakila", config["sfDatabase"])
        config = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302f"])
        self.assertEqual(None, config["sfDatabase"])

    def test_test_connection(self):
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        config = {'connection_id': '654879fe42a09b96f228302e', 'table_name': 'public.actor', "df_id": "65cca96e00df89a55668f3df"}
        test_result = self.snowflake.test_connection(config, connection)
        self.assertEqual(True, test_result)
        
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {'connection_id': '654879fe42a09b96f228302f', 'table_name': 'sakila.public.actor', "df_id":
                  "65cca96e00df89a55668f3df"}
        test_result = self.snowflake.test_connection(config, connection)
        self.assertEqual(True, test_result)

    def test_fetch_data(self):
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        config = {'connection_id': '654879fe42a09b96f228302e', 'table_name': 'public.actor', "df_id": "65cca96e00df89a55668f3df"}
        result = self.snowflake.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {'connection_id': '654879fe42a09b96f228302f', 'table_name': 'sakila.public.actor', "df_id": "65cca96e00df89a55668f3df"}
        result = self.snowflake.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_columns(self):
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        config = {'connection_id': '654879fe42a09b96f228302e', 'table_name': 'public.actor', "df_id":
                  "65cca96e00df89a55668f3df", "columns": ["FIRST_NAME", "LAST_NAME"]}
        result = self.snowflake.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        self.assertTrue(["FIRST_NAME", "LAST_NAME"], result["df"].columns)

        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {'connection_id': '654879fe42a09b96f228302f', 'table_name': 'sakila.public.actor', "df_id":
                  "65cca96e00df89a55668f3df", "columns": ["FIRST_NAME", "LAST_NAME"]}
        result = self.snowflake.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        self.assertTrue(["FIRST_NAME", "LAST_NAME"], result["df"].columns)

    def test_fetch_data_with_custom_config(self):
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        config = {'connection_id': '654879fe42a09b96f228302e', 'table_name': 'public.actort1', "df_id":
                  "65cca96e00df89a55668f3df"}
        custom_config = {"dbtable": "actor"}
        result = self.snowflake.fetch_data(config, connection, custom_config)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        """
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {'connection_id': '654879fe42a09b96f228302f', 'table_name': 'sakila.public.actor', "df_id":
                  "65cca96e00df89a55668f3df"}
        custom_config = {"dbtable": "country1"}
        result = self.snowflake.fetch_data(config, connection, custom_config)
        self.assertIsNotNone(result)
        self.assertTrue("65cca96e00df89a55668f3df" in result.keys())
        """

    def test_fetch_data_with_custom_config_wrong_query_parameter(self):
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        config = {'connection_id': '654879fe42a09b96f228302e', 'table_name': 'public.actor', "df_id":
                  "65cca96e00df89a55668f3df"}
        custom_config = {"quer": "SELECT * FROM country where country like 'India'"}
        # takes table from config
        result = self.snowflake.fetch_data(config, connection, custom_config)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data(self):
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        config = {'connection_id': '654879fe42a09b96f228302e', 'table_name': 'public.actor_1', "df_id": "65cca96e00df89a55668f3df"}
        schema = StructType([
            StructField("actor_id", IntegerType(), True),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        test_data = [
            (1, "Chandler", "Bing", datetime.strptime("2024-02-15 04:34:33", "%Y-%m-%d %H:%M:%S")),
            (2, "Rachel", "Green", datetime.strptime("2024-02-16 06:52:11", "%Y-%m-%d %H:%M:%S"))
        ]
        dataframe = self.spark.createDataFrame(test_data, schema)
        result = self.snowflake.write_data(config, connection, dataframe)
        self.assertTrue(result)
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        config = {'connection_id': '654879fe42a09b96f228302e', 'table_name': 'public.actor_1', "df_id": "65cca96e00df89a55668f3df"}
        result = self.snowflake.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_custom_config(self):
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        config = {'connection_id': '654879fe42a09b96f228302e', 'table_name': 'public.actor_1', "df_id": "65cca96e00df89a55668f3df"}
        schema = StructType([
            StructField("actor_id", IntegerType(), True),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        test_data = [
            (3, "Chandler", "Bing", datetime.strptime("2024-02-15 04:34:33", "%Y-%m-%d %H:%M:%S")),
            (4, "Rachel", "Green", datetime.strptime("2024-02-16 06:52:11", "%Y-%m-%d %H:%M:%S"))
        ]
        dataframe = self.spark.createDataFrame(test_data, schema)
        custom_config = {"mode": "append"}
        result = self.snowflake.write_data(config, connection, dataframe, custom_config)
        self.assertTrue(result)
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        config = {'connection_id': '654879fe42a09b96f228302e', 'table_name': 'public.actor_1', "df_id": "65cca96e00df89a55668f3df"}
        result = self.snowflake.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_check_database(self):
        # passing database in connection
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302e"])
        configuration = "example_schema.example_table"
        database, schema, table = self.snowflake.check_database(configuration, connection)
        self.assertEqual(connection["sfDatabase"], database)

        # passing database in configuration
        connection = self.snowflake.connect(self.connection_id["654879fe42a09b96f228302f"])
        configuration = "example_database.example_schema.example_table"
        database, schema, table = self.snowflake.check_database(configuration, connection)
        self.assertEqual(configuration.split(".")[0], database)


if __name__ == '__main__':
    unittest.main()
