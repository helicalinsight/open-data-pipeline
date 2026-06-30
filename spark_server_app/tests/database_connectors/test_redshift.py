import unittest
from spark_server.database_connectors.redshift import Redshift
from spark_server.exceptions.exceptions import *
import os
import pytest
from test_setup import TestSetup
import random
import string


@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestRedshift(unittest.TestCase):
    # creating the instance of the class Redshift
    @classmethod
    def setUpClass(cls):
        cls.spark = TestSetup.set_up_spark()
        cls.redshift = Redshift(cls.spark)
        cls.connection_id = {
            "654879fe42a09b96f228302f": {
                "type": "database",
                "details": {
                    "type": "redshift",
                    "sourceName": "Redshift Connector",
                    "username": "admin",
                    "password": "HelicalAdmin1$",
                    "host": "helical-test.982586453799.us-east-1.redshift-serverless.amazonaws.com",
                    "port": 5439,
                    "database": "dev"
                }
            }
        }
    
    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_connect(self):
        config = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        self.assertIsNotNone(config["url"])

    def test_test_connection(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        test_result = self.redshift.test_connection(config, connection)
        self.assertEqual(test_result, True)

    def test_fetch_data(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        result = self.redshift.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "public.demo", "df_id": "65cca96e00df89a55668f3df"}
        result = self.redshift.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_columns(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "columns": ["personid"], "df_id": "65cca96e00df89a55668f3df"}
        result = self.redshift.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        self.assertEqual(["personid"], result["df"].columns)

    def test_fetch_data_with_custom_config_dbtable(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        custom_config={"dbtable": "demo"}  
        result = self.redshift.fetch_data(config, connection, custom_config)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_custom_config_query(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        custom_config={"query": "select * from demo"}  
        result = self.redshift.fetch_data(config, connection, custom_config)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_custom_config_dbtable_query(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        custom_config={"dbtable": "demo", "query": "select * from demo"}
        result = self.redshift.fetch_data(config, connection, custom_config)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_invalid_custom_config(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        custom_config={"dbtable": "student_teacher"}  
        with pytest.raises(DatabaseConnectionException) as test_function:
            self.redshift.fetch_data(config, connection, custom_config)
        self.assertEqual("Failed to fetch data from redshift.", str(test_function.value))
       
    def test_write_data(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random.randint(1, 10), random_values), (random.randint(1, 10), random_values)]
        dataframe = self.spark.createDataFrame(data, ["personid", "city"])
        result = self.redshift.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        result = self.redshift.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_custom_config(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random.randint(1, 10), random_values), (random.randint(1, 10), random_values)]
        custom_config={"mode":"append"}
        dataframe = self.spark.createDataFrame(data, ["personid", "city"])
        result = self.redshift.write_data(config, connection, dataframe, custom_config)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302f", "table_name": "demo", "df_id": "65cca96e00df89a55668f3df"}
        result = self.redshift.fetch_data(config, connection)["65cca96e00df89a55668f3df"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_check_database(self):
        connection = self.redshift.connect(self.connection_id["654879fe42a09b96f228302f"])
        configuration = "public.demo"
        database, table = self.redshift.check_database(configuration, connection)
        self.assertEqual(connection["database"], database)


if __name__ == "__main__":
    unittest.main()