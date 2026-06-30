import unittest
import os
import json
import pandas
import pytest

from core.datasource.implementations.astra import Astra
from src.exceptions.exception import *

json_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "astra_creds.json")

with open(json_file_path, "r") as json_file:
    connection_details = json.load(json_file)

bundle_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "secure-connect-testing-new.zip")
connection_details['bundle'] = {'file': bundle_path}

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestAstra(unittest.TestCase):
    def test_connect_with_vpn(self):
        actual_result = Astra().connect(connection_details)
        self.assertIsNotNone(actual_result[0])

    def test_connection_with_vpn(self):
        actual_result = Astra().test_connection(connection_details)
        self.assertTrue(actual_result)

    def test_fetch_data_with_vpn(self):
        catalog = "helical.test_sample"
        actual_result = Astra().fetch_data(connection_details, catalog)
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertGreater(len(actual_result), 0)

    def test_fetch_data_with_non_existing_table_with_vpn(self):
        catalog = "helical.test_sample1"
        with pytest.raises(DatabaseConnectorException) as test_function:
            Astra().fetch_data(connection_details, catalog)
        self.assertEqual("Failed to fetch the data.", str(test_function.value))


    def test_fetch_data_with_non_existing_keyspace_with_vpn(self):
        catalog = "example_key.test_sample"
        with pytest.raises(DatabaseConnectorException) as test_function:
            Astra().fetch_data(connection_details, catalog)
        self.assertEqual("Failed to fetch the data.", str(test_function.value))

    def test_get_metadata_with_vpn(self):
        actual_result = Astra().get_metadata(connection_details)
        self.assertIsNotNone(actual_result[0].get("title"))

    def test_get_columns_with_vpn(self):
        db_table_name = "helical.test_sample"
        actual_result = Astra().get_columns(connection_details, db_table_name)
        self.assertTrue(isinstance(actual_result, list))
        # self.assertGreater(len(actual_result), 0)


if __name__ == '__main__':
    unittest.main()
