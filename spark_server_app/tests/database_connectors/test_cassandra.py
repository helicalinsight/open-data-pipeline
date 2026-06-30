import unittest
from unittest.mock import MagicMock
from spark_server.database_connectors.cassandra import Cassandra
import os
import pytest
from spark_server.exceptions.exceptions import *
from test_setup import TestSetup
import random
import string


@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestCassandra(unittest.TestCase):
    # creating the instance of the class Cassandra
    @classmethod
    def setUpClass(cls):
        cls.spark = TestSetup.set_up_spark()
        cls.cassandra = Cassandra(cls.spark)
        cls.connection_id = {
            "654879fe42a09b96f228302a": {
                "type": "database",
                "details": {
                    "type": "cassandra",
                    "sourceName": "Cassandra Connector",
                    "username": "test",
                    "password": "test1234",
                    "host": "57.128.161.235",
                    "port": 9042,
                    "database": None
                }
            },
            "654879fe42a09b96f228302d": {
                "type": "database",
                "details": {
                    "type": "cassandra",
                    "sourceName": "Cassandra Connector",
                    "username": "test",
                    "password": "test1234",
                    "host": "57.128.161.235",
                    "port": 9042,
                    "database": "example_keyspace"
                }
            },
            "654879fe42a09b96f228302e": {
                "type": "database",
                "details": {
                    "type": "cassandra",
                    "sourceName": "Cassandra Connector",
                    "username": "test",
                    "password": "test1234",
                    "host": "57.128.161.235",
                    "port": 9042,
                    "database": None,
                    "connection_pool": {
                        "pandas_pooling": {
                            "pool_size": "10",
                            "max_overflow": "20",
                            "pool_timeout": "30",
                            "pool_recycle": "1800",
                        },
                        "spark_pooling": {
                            "spark.cassandra.connection.timeoutBeforeCloseMS": 35000,
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
        # passing database in configuration
        config = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302a"])
        self.assertEqual(config["database"], None)
        # passing database in connection
        config = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302d"])
        self.assertEqual(config["database"], "example_keyspace")
        # passing pool in connection
        config = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302e"])
        self.assertIsNotNone(config["connection_pool"]["spark_pooling"])

    def test_test_connection(self):

        # passing database in configuration
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302a"])
        config = {'connection_id': '654879fe42a09b96f228302a', 'table_name': 'example_keyspace.example_table', "df_id": "65dc3fb832b5b2a5665841fb"}
        test_result = self.cassandra.test_connection(config, connection)
        self.assertEqual(True, test_result)

        # passing database in connection
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302d"])
        config = {'connection_id': '654879fe42a09b96f228302d', 'table_name': 'example_table', "df_id": "65dc3fb832b5b2a5665841fb"}
        test_result = self.cassandra.test_connection(config, connection)
        self.assertEqual(True, test_result)

    def test_fetch_data(self):
        # passing database in configuration
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302a"])
        config = {'connection_id': '654879fe42a09b96f228302a', 'table_name': 'example_keyspace.example_table', 
                  "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {"keyspace":"example_keyspace", "table":"example_table"}
        result = self.cassandra.fetch_data(config, connection, custom_config)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_columns(self):
        # passing database in configuration        
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302a"])
        config = {'connection_id': '654879fe42a09b96f228302a', 'table_name': 'example_keyspace.example_table', "columns": ["employee_id"], "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {"keyspace":"example_keyspace", "table":"example_table"}
        result = self.cassandra.fetch_data(config, connection, custom_config)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        self.assertEqual(["employee_id"], result["df"].columns)

    def test_fetch_data_without_custom_config(self):
        # passing database in configuration        
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302a"])
        config = {'connection_id': '654879fe42a09b96f228302a', 'table_name': 'example_keyspace.example_table', 
                  "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.cassandra.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_invalid_custom_config(self):
        # passing database in configuration        
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302a"])
        config = {'connection_id': '654879fe42a09b96f228302a', 'table_name': 'example_keyspace.example_table', 
                  "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {"keyspace":"example_keyspace1", "table":"example_table"}
        with pytest.raises(DatabaseConnectionException) as test_function:
            self.cassandra.fetch_data(config, connection, custom_config)
        self.assertEqual("Failed to fetch data from cassandra.", str(test_function.value))

    def test_write_data_without_custom_config(self):
        """
        Test writing data to Cassandra database table
        """
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302a"])
        #config = {'c0327e48-1fd7-47b8-bb94-4e37e76ab632': 'example_keyspace.example_table12'}
        config = {'table_name': 'example_keyspace.example_table12', "df_id": "65dc3fb832b5b2a5665841fb"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values)]
        schema = ["employee_id", "name"]
        dataframe = self.spark.createDataFrame(data, schema)
        result=self.cassandra.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {'table_name': 'example_keyspace.example_table12', "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.cassandra.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_custom_config(self):
        """
        Test writing data to Cassandra database table
        """
        #self.cassandra.write_data = MagicMock()
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302a"])
        config = {'table_name': 'example_keyspace.example_table12', "df_id": "65dc3fb832b5b2a5665841fb"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values)]
        schema = ["employee_id", "name"]
        custom_config = {"mode":"append", "table": "example_table12", "keyspace":"example_keyspace"}
        dataframe = self.spark.createDataFrame(data, schema)
        self.assertTrue(self.cassandra.write_data(config, connection, dataframe, custom_config))
        config = {'table_name': 'example_keyspace.example_table12', "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.cassandra.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)


    def test_check_database(self):

        # passing database in configuration
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302a"])
        configuration = "example_keyspace.example_table"
        keyspace, table = self.cassandra.check_database(configuration, connection)
        self.assertEqual(keyspace, configuration.split(".")[0])

        # passing database in connection
        connection = self.cassandra.connect(self.connection_id["654879fe42a09b96f228302d"])
        configuration = "example_table"
        keyspace, table = self.cassandra.check_database(configuration, connection)
        self.assertEqual(keyspace, connection["database"])


if __name__ == '__main__':
    unittest.main()
