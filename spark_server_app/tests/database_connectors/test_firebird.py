import unittest
from spark_server.database_connectors.firebird import Firebird
from spark_server.exceptions.exceptions import *
import os
import pytest
from test_setup import TestSetup
import random
import string


@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestFirebird(unittest.TestCase):
    # creating the instance of the class Firebird
    @classmethod
    def setUpClass(cls):
        cls.spark = TestSetup.set_up_spark()
        cls.firebird = Firebird(cls.spark)
        cls.connection_id = {
            "654879fe42a09b96f228302f": {
                "type": "database",
                "details": {
                    "type": "firebird",
                    "sourceName": "Firebird Connector",
                    "username": "SYSDBA",
                    "password": "Helical@1234",
                    "host": "152.228.161.61",
                    "port": 3050,
                    "database": "employee"
                }
            },
            "654879fe42a09b96f228303f": {
                "type": "database",
                "details": {
                    "type": "firebird",
                    "sourceName": "Firebird Connector",
                    "username": "SYSDBA",
                    "password": "Helical@1234",
                    "host": "152.228.161.61",
                    "port": 3050,
                    "database": "employee",
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
        config = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        self.assertIsNotNone(config["url"])

    def test_test_connection(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "employee", "df_id": "65cca96e00df89a55668f3df"}
        test_result = self.firebird.test_connection(config, connection)
        self.assertEqual(True, test_result)

    def test_fetch_data(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "employee", "df_id": "65cca96e00df89a55668f3df"}
        result = self.firebird.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
    
    def test_fetch_data_with_columns(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "employee", "df_id": "65cca96e00df89a55668f3df", "columns": ["FIRST_NAME","LAST_NAME"]}
        result = self.firebird.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        self.assertEqual(["FIRST_NAME", "LAST_NAME"], result["df"].columns)

    def test_fetch_data_with_custom_config_dbtable(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "employee", "df_id": "65cca96e00df89a55668f3df"}
        custom_config = {"dbtable": "country"}
        result = self.firebird.fetch_data(config, connection, custom_config)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_custom_config_query(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "employee", "df_id": "65cca96e00df89a55668f3df"}
        custom_config = {"query": "select * from country"}
        result = self.firebird.fetch_data(config, connection, custom_config)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_invalid_table_in_custom_config(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "employee", "df_id": "65cca96e00df89a55668f3df"}
        custom_config = {"dbtable": "country_5"}
        with pytest.raises(DatabaseConnectionException) as test_function:
            self.firebird.fetch_data(config, connection, custom_config)
        self.assertEqual("Failed to fetch the data from firebird.", str(test_function.value))

    def test_fetch_data_with_connection_pool(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228303f"])
        config = {"connection_id": "654879fe42a09b96f228303f", "table_name": "employee", "df_id": "65cca96e00df89a55668f3df"}
        result = self.firebird.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    #@pytest.mark.skip("Table has key constraints unable to overwrite")
    def test_write_data(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random_values, random_values)]
        dataframe = self.spark.createDataFrame(data, ["country", "currency"])
        result = self.firebird.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        result = self.firebird.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_custom_config(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random_values, random_values)]
        dataframe = self.spark.createDataFrame(data, ["country", "currency"])
        custom_config = {"dbtable": "country"}
        result = self.firebird.write_data(config, connection, dataframe, custom_config)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        result = self.firebird.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_connection_pool(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228303f"])
        config = {"connection_id": "654879fe42a09b96f228303f", "table_name": "country", "df_id":"65cca96e00df89a55668f3df"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random_values, random_values)]
        dataframe = self.spark.createDataFrame(data, ["country", "currency"])
        result = self.firebird.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228303f", "table_name": "country", "df_id": "65cca96e00df89a55668f3df"}
        result = self.firebird.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_check_database(self):
        connection = self.firebird.connect(self.connection_id["654879fe42a09b96f228302f"])
        configuration = "employee"
        database, table = self.firebird.check_database(configuration, connection)
        self.assertEqual(connection["database"], database)


if __name__ == "__main__":
    unittest.main()
