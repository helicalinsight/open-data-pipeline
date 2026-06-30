import unittest
import json
import os

import pandas
import pytest

# from src.hooks.database.firebird.firebird import Firebird
from core.datasource.implementations.sql_alchemy import SqlAlchemy
from src.exceptions.exception import *

json_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "firebird_creds.json")

with open(json_file_path, "r") as json_file:
    connection_details = json.load(json_file)


@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestFirebird(unittest.TestCase):
    def test_connect_with_vpn(self):
        actual_result = SqlAlchemy().connect(connection_details)
        self.assertIsNotNone(actual_result)

    def test_connection_with_vpn(self):
        actual_result = SqlAlchemy().test_connection(connection_details)
        self.assertTrue(actual_result)

    def test_fetch_data_with_vpn(self):
        catalog = "employee"
        actual_result = SqlAlchemy().fetch_data(connection_details, catalog)
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertGreater(len(actual_result), 0)

    def test_fetch_data_with_non_existing_table_with_vpn(self):
        catalog = "employee1"
        with pytest.raises(DatabaseConnectorException) as test_function:
            SqlAlchemy().fetch_data(connection_details, catalog)
        self.assertEqual("Failed to fetch the data.", str(test_function.value))

    def test_get_metadata_with_vpn(self):
        actual_result = SqlAlchemy().get_metadata(connection_details)
        self.assertIsNotNone(actual_result[0].get("title"))

    def test_get_columns_with_vpn(self):
        table_name = "employee"
        actual_result = SqlAlchemy().get_columns(connection_details, table_name)
        self.assertTrue(isinstance(actual_result, list))
        self.assertGreater(len(actual_result), 0)


if __name__ == '__main__':
    unittest.main()
