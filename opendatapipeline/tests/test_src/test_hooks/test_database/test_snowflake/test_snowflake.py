import json
import os
import unittest
import pandas
import pytest

# from src.hooks.database.snowflake.snowflake import Snowflake
from src.exceptions.exception import *
from core.datasource.implementations.sql_alchemy import SqlAlchemy

json_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "snowflake_creds.json")

with open(json_file_path, "r") as json_file:
    connection_details = json.load(json_file)

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestSnowflake(unittest.TestCase):

    def test_connect_with_vpn(self):
        actual_result = SqlAlchemy().connect(connection_details)
        self.assertIsNotNone(actual_result)

    def test_test_connection_with_vpn(self):
        actual_result = SqlAlchemy().test_connection(connection_details)
        self.assertTrue(actual_result)

    def test_fetch_data_with_vpn(self):
        catalog = "student.student_info.students" if connection_details.get("database") is None else "student_info.students"
        actual_result = SqlAlchemy().fetch_data(connection_details, catalog)
        self.assertIsInstance(actual_result, pandas.DataFrame)
        self.assertFalse(actual_result.empty)

    def test_fetch_data_with_non_existing_database_with_vpn(self):
        catalog = "teacher.student_info.students"
        with pytest.raises(DatabaseConnectorException) as test_function:
            SqlAlchemy().fetch_data(connection_details, catalog)
        self.assertEqual("Failed to fetch the data.", str(test_function.value))

    def test_fetch_data_with_non_existing_table_with_vpn(self):
        catalog = "student.student_info.teachers"
        with pytest.raises(DatabaseConnectorException) as test_function:
            SqlAlchemy().fetch_data(connection_details, catalog)
        self.assertEqual("Failed to fetch the data.", str(test_function.value))

    def test_get_metadata_with_vpn(self):
        actual_result = SqlAlchemy().get_metadata(connection_details)
        self.assertIsNotNone(actual_result[0].get("title"))

    def test_get_columns_with_vpn(self):
        table_name = "PUBLIC.TEST_TABLE"
        actual_result = SqlAlchemy().get_columns(connection_details, table_name)
        self.assertTrue(isinstance(actual_result, list))
        self.assertGreater(len(actual_result), 0)

    # commented testcases with wrong creds because if we give wrong creds multiple times account gets locked
    '''def test_test_connection_with_wrong_creds(self):
        connection_details["username"] = "helical123"
        actual_result = Snowflake().test_connection(connection_details)
        self.assertFalse(actual_result)

    def test_fetch_data_with_wrong_creds(self):
        connection_details["password"] = "helical123"
        catalog = "student.student_info.students"
        actual_result = Snowflake().fetch_data(connection_details, catalog)
        expected_result = None
        self.assertEqual(actual_result, expected_result)

    def test_connect_with_wrong_creds(self):
        connection_details["password"] = "helical123"
        actual_result = Snowflake().connect(connection_details)
        expected_result = None
        self.assertEqual(actual_result, expected_result)'''

if __name__ == '__main__':
    unittest.main()
