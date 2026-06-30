import json
import os
import unittest
import pandas
import pytest

from core.datasource.implementations.redshift import Redshift
from src.exceptions.exception import *

json_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "redshift_creds.json")

with open(json_file_path, "r") as json_file:
    connection_details = json.load(json_file)

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestRedshift(unittest.TestCase):

    def test_connect_with_vpn(self):
        actual_result = Redshift().connect(connection_details)
        self.assertIsNotNone(actual_result)

    def test_test_connection_with_vpn(self):
        actual_result = Redshift().test_connection(connection_details)
        self.assertTrue(actual_result)

    def test_fetch_data_with_vpn(self):
        catalog = "test_table1"
        actual_result = Redshift().fetch_data(connection_details, catalog)
        self.assertIsInstance(actual_result, pandas.DataFrame)
        self.assertFalse(actual_result.empty)

    def test_fetch_data_with_non_existing_table_with_vpn(self):
        catalog = "test_table2"
        with pytest.raises(DatabaseConnectorException) as test_function:
            Redshift().fetch_data(connection_details, catalog)
        self.assertEqual("Failed to fetch the data.", str(test_function.value))


    def test_get_metadata_with_vpn(self):
        actual_result = Redshift().get_metadata(connection_details)
        self.assertIsNotNone(actual_result[0].get("title"))

    def test_get_columns_with_vpn(self):
        db_name = "public.test_table1"
        actual_result = Redshift().get_columns(connection_details, db_name)
        self.assertTrue(isinstance(actual_result, list))
        self.assertGreater(len(actual_result), 0)

if __name__ == '__main__':
    unittest.main()
