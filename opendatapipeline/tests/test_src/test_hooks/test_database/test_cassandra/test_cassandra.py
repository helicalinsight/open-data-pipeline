import unittest
import os
import json
import pandas
import pytest

from core.datasource.implementations.cassandra import Cassandra
from src.exceptions.exception import *

json_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "cassandra_creds.json")

with open(json_file_path, "r") as json_file:
    connection_details = json.load(json_file)

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestCassandra(unittest.TestCase):
    def test_connect_with_vpn(self):
        actual_result = Cassandra().connect(connection_details)
        self.assertIsNotNone(actual_result)

    def test_connection_with_vpn(self):
        actual_result = Cassandra().test_connection(connection_details)
        self.assertTrue(actual_result)

    def test_fetch_data_with_vpn(self):
        catalog = "example_keyspace.example_table"
        actual_result = Cassandra().fetch_data(connection_details, catalog)
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertGreater(len(actual_result), 0)

    def test_fetch_data_with_non_existing_table_with_vpn(self):
        catalog = "example_keyspace.example_table1"
        with pytest.raises(DatabaseConnectorException) as test_function:
            Cassandra().fetch_data(connection_details, catalog)
        self.assertEqual("Failed to fetch the data.", str(test_function.value))

    def test_fetch_data_with_non_existing_keyspace_with_vpn(self):
        catalog = "example_key.example_table"
        with pytest.raises(DatabaseConnectorException) as test_function:
            Cassandra().fetch_data(connection_details, catalog)
        self.assertEqual("Failed to fetch the data.", str(test_function.value))

    def test_get_metadata_with_vpn(self):
        actual_result = Cassandra().get_metadata(connection_details)
        self.assertIsNotNone(actual_result[0].get("title"))

    def test_get_columns_with_vpn(self):
        db_table_name = "example_keyspace.example_table"
        actual_result = Cassandra().get_columns(connection_details, db_table_name)
        self.assertTrue(isinstance(actual_result, list))
        self.assertGreater(len(actual_result), 0)
        self.assertEqual(actual_result, ['employee_id', 'employee_name'])

    '''def test_connection_with_wrong_creds(self):
        connection_details['host'] = "57.128.161.231"
        print(connection_details)
        actual_result = Cassandra().test_connection(connection_details)
        self.assertIsNone(actual_result)'''

if __name__ == '__main__':
    unittest.main()
