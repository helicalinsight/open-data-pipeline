import unittest
from unittest.mock import MagicMock
from spark_server.database_connectors.astra import Astra
from spark_server.exceptions.exceptions import *
from pyspark.sql import SparkSession
import os
import pytest
from test_setup import TestSetup
import string
import random
 

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestAstra(unittest.TestCase):
    # creating the instance of the class Astra
    @classmethod
    def setUpClass(cls):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        cls.spark = TestSetup.set_up_spark()
        cls.astra = Astra(cls.spark)
        path = os.path.join(base_path, "spark_server", "database_connectors", "connector_jars", "astra", "secure-connect-test-astra-db.zip").replace('\\','/')
        cls.connection_id = {
            "654879fe42a09b96f228302b": {
                "type": "database",
                "details": {
                    "type": "astra",
                    "sourceName": "Astra Connector",
                    "username": "pooja.ts@helicaltech.com",
                    "password": "Helicalastra@123",
                    "host": "https://astra.datastax.com",
                    "bundle": {'file': f'file:///{path}'},
                    'client_id': 'aZfUhnoxPkhSoaRLTKiphxCj',
                    'database': None,
                    "secret": "g8UOiwUpg+S0FNp9LLGE1BdaCFpqYbnW,l0uQkDc._AfmtxASQJy,0CMKZ4KKSAl+J,ZksRIprPtsBX6DtckKg11pIu,KZ97Zr8v6Sv6JsBP3RZ,2nHI7WDvMhWI+hxA",
                }
            },
            "654879fe42a09b96f228302c": {
                "type": "database",
                "details": {
                    "type": "astra",
                    "sourceName": "Astra Connector",
                    "username": "pooja.ts@helicaltech.com",
                    "password": "Helicalastra@123",
                    "host": "https://astra.datastax.com",
                    "bundle": {'file': f'file:///{path}'},
                    'client_id': 'aZfUhnoxPkhSoaRLTKiphxCj',
                    'database': None,
                    "secret": "g8UOiwUpg+S0FNp9LLGE1BdaCFpqYbnW,l0uQkDc._AfmtxASQJy,0CMKZ4KKSAl+J,ZksRIprPtsBX6DtckKg11pIu,KZ97Zr8v6Sv6JsBP3RZ,2nHI7WDvMhWI+hxA",
                    "connection_pool": {
                        "pandas_pooling": {
                            "pool_size": "10",
                            "max_overflow": "20",
                            "pool_timeout": "30",
                            "pool_recycle": "1800",
                        },
                        "spark_pooling": {
                            "spark.cassandra.connection.timeoutMS": 35000,
                            "spark.cassandra.connection.localConnectionsPerExecutor": 9
                        }
                    }
                }
            }
        }

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_connect(self):
        config = self.astra.connect(self.connection_id["654879fe42a09b96f228302b"])
        self.assertIsNotNone(config)
        # passing pool in connection
        config = self.astra.connect(self.connection_id["654879fe42a09b96f228302c"])
        self.assertIsNotNone(config["connection_pool"]["spark_pooling"])

    def test_test_connection(self):
        connection = self.astra.connect(self.connection_id["654879fe42a09b96f228302b"])
        config = {'connection_id': '654879fe42a09b96f228302b', 'table_name': 'example_keyspace.users', "df_id": "65dc3fb832b5b2a5665841fb"}
        test_result = self.astra.test_connection(config, connection)
        self.assertEqual(True, test_result)

    def test_fetch_data(self):
        connection = self.astra.connect(self.connection_id["654879fe42a09b96f228302b"])
        config = {'table_name': 'example_keyspace.users', "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.astra.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_columns(self):
        connection = self.astra.connect(self.connection_id["654879fe42a09b96f228302b"])
        config = {'table_name': 'example_keyspace.users', "columns": ["firstname", "lastname"], "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.astra.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        self.assertEqual(["firstname", "lastname"], result["df"].columns)

    def test_fetch_data_with_custom_config_dbtable(self):
        connection = self.astra.connect(self.connection_id["654879fe42a09b96f228302b"])
        config = {'table_name': 'example_keyspace.users', "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {'table':'users_1'}
        result = self.astra.fetch_data(config, connection, custom_config)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_invalid_custom_config(self):
        connection = self.astra.connect(self.connection_id["654879fe42a09b96f228302b"])
        config = {'table_name': 'example_keyspace.users', "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config={'table':'users_3'}
        with pytest.raises(DatabaseConnectionException) as test_function:
            self.astra.fetch_data(config, connection, custom_config)
        self.assertEqual("Failed to fetch data from astra db." , str(test_function.value))

    def test_write_data(self):
        """
        Test writing data to Astra database table
        """
        connection = self.astra.connect(self.connection_id["654879fe42a09b96f228302b"])
        config = {'table_name': 'example_keyspace.users_1', "df_id": "65dc3fb832b5b2a5665841fb"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values)]
        schema = ["employee_id", "name"]
        dataframe = self.spark.createDataFrame(data, schema)
        result = self.astra.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {'table_name': 'example_keyspace.users_1', "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.astra.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_custom_config(self):
        """
        Test writing data to Astra database table
        """
        connection = self.astra.connect(self.connection_id["654879fe42a09b96f228302b"])
        config = {'table_name': 'example_keyspace.users_1', "df_id": "65dc3fb832b5b2a5665841fb"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values)]
        schema = ["employee_id", "name"]
        custom_config={"mode": "append"}
        dataframe = self.spark.createDataFrame(data, schema)
        result = self.astra.write_data(config, connection, dataframe, custom_config)
        self.assertTrue(result)
        config = {'table_name': 'example_keyspace.users_1', "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.astra.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_check_database(self):
        connection = self.astra.connect(self.connection_id["654879fe42a09b96f228302b"])
        configuration = "example_keyspace.users"
        keyspace, table = self.astra.check_database(configuration, connection)
        self.assertEqual(keyspace, configuration.split(".")[0])


if __name__ == '__main__':
    unittest.main()
