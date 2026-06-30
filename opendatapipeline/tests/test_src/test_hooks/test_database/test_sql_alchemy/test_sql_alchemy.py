import unittest
import json
import os

import pandas
import pytest
from unittest.mock import MagicMock, patch
from core.datasource.implementations.sql_alchemy import SqlAlchemy
from src.exceptions.exception import *


class TestSqlAlchemy(unittest.TestCase):
    def setUp(self):
        self.db_connector = MagicMock()
        self.db_connector.connect = MagicMock(return_value=MagicMock())
        self.connection = self.db_connector.connect()
        self.inspector = MagicMock()
        self.connection.__enter__.return_value = self.connection  # Mock context manager behavior

    @patch('core.datasource.implementations.sql_alchemy.inspect')
    def test_get_metadata_no_selected_schemas_or_tables(self, mock_inspect):
        mock_inspect.return_value = self.inspector
        self.inspector.get_schema_names.return_value = ['public', 'test_schema']
        self.inspector.get_table_names.return_value = ['table1', 'table2', 'table3']
        connection_details = {
            'database': 'test_db',
            'connection_pool': {},
        }
        self.db_connector.get_metadata.return_value = [
            {
                'title': 'public',
                'value': 'public',
                'children': [
                    {'title': 'table1', 'value': 'table1'},
                    {'title': 'table2', 'value': 'table2'},
                    {'title': 'table3', 'value': 'table3'},
                ]
            },
            {
                'title': 'test_schema',
                'value': 'test_schema',
                'children': []
            }
        ]
        result = self.db_connector.get_metadata(connection_details)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'public')
        self.assertEqual(result[0]['children'], [
            {'title': 'table1', 'value': 'table1'},
            {'title': 'table2', 'value': 'table2'},
            {'title': 'table3', 'value': 'table3'},
        ])
        self.assertEqual(result[1]['title'], 'test_schema')
        self.assertEqual(result[1]['children'], [])

    @patch('core.datasource.implementations.sql_alchemy.inspect')
    def test_get_metadata_with_selected_tables(self, mock_inspect):
        mock_inspect.return_value = self.inspector
        self.inspector.get_schema_names.return_value = ['public', 'test_schema']
        self.inspector.get_table_names.return_value = ['table1', 'table2', 'table3']
        connection_details = {
            'database': 'test_db',
            'connection_pool': {
                'pandas_pooling': {
                    'aod_schema': ['public'],
                    'aod_table': ['table1', 'table2']
                }
            },
        }
        self.db_connector.get_metadata.return_value = [{
                'title': 'public',
                'value': 'public',
                'children': [
                    {'title': 'table1', 'value': 'table1'},
                    {'title': 'table2', 'value': 'table2'},
                ]
            }]
        result = self.db_connector.get_metadata(connection_details)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'public')
        self.assertEqual(result[0]['children'], [
            {'title': 'table1', 'value': 'table1'},
            {'title': 'table2', 'value': 'table2'},
        ])

json_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "ms_sqlserver_creds.json")

with open(json_file_path, "r") as json_file:
    connection_details = json.load(json_file)

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestSqlAlchemyMsSqlServer(unittest.TestCase):
    # ms sql server version 2022 and odbc driver is 17
    def test_connect(self):
        actual_result = SqlAlchemy().connect(connection_details, engine="ms_sql_server")
        self.assertIsNotNone(actual_result)

    def test_connection(self):
        actual_result = SqlAlchemy().test_connection(connection_details, engine="ms_sql_server")
        self.assertTrue(actual_result)

    def test_connection_with_no_database(self):
        updated_details = connection_details.copy()
        updated_details.update({"database": None})
        with pytest.raises(DatabaseConnectorException) as test_function:
            SqlAlchemy().test_connection(updated_details, engine="ms_sql_server")
        self.assertIn("Failed to connect to ms_sql_server", str(test_function.value))

    def test_fetch_data(self):
        catalog = "student_info.student_details"
        actual_result = SqlAlchemy().fetch_data(connection_details, catalog, engine="ms_sql_server")
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertGreater(len(actual_result), 0)

    def test_fetch_data_with_non_existing_table(self):
        catalog = "teacher.info" if connection_details['database'] is None else "info1"
        with pytest.raises(DatabaseConnectorException) as test_function:
            SqlAlchemy().fetch_data(connection_details, catalog, engine="ms_sql_server")
        self.assertIn("Failed to fetch the data", str(test_function.value))

    def test_get_metadata(self):
        actual_result = SqlAlchemy().get_metadata(connection_details, engine="ms_sql_server")
        # data_catalog value
        # [{'title': 'db_accessadmin', 'value': 'db_accessadmin', 'children': []}, {'title': 'db_backupoperator', 'value': 'db_backupoperator', 'children': []}, {'title': 'db_datareader', 'value': 'db_datareader', 'children': []}, {'title': 'db_datawriter', 'value': 'db_datawriter', 'children': []}, {'title': 'db_ddladmin', 'value': 'db_ddladmin', 'children': []}, {'title': 'db_denydatareader', 'value': 'db_denydatareader', 'children': []}, {'title': 'db_denydatawriter', 'value': 'db_denydatawriter', 'children': []}, {'title': 'db_owner', 'value': 'db_owner', 'children': []}, {'title': 'db_securityadmin', 'value': 'db_securityadmin', 'children': []}, {'title': 'dbo', 'value': 'dbo', 'children': []}, {'title': 'guest', 'value': 'guest', 'children': []}, {'title': 'INFORMATION_SCHEMA', 'value': 'INFORMATION_SCHEMA', 'children': []}, {'title': 'student_info', 'value': 'student_info', 'children': [{'title': 'student_details', 'value': 'student_info.student_details'}]}, {'title': 'sys', 'value': 'sys', 'children': [{'title': 'student_details', 'value': 'student_info.student_details'}]}]
        self.assertIsNotNone(actual_result[0].get("title"))

    def test_get_metadata_with_no_database(self):
        updated_details = connection_details.copy()
        updated_details.update({"database": None})
        with pytest.raises(DatabaseConnectorException) as test_function:
            SqlAlchemy().get_metadata(updated_details, engine="ms_sql_server")
        self.assertIn("Failed to connect to ms_sql_server", str(test_function.value))

firebird_json_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "firebird_creds.json")

with open(firebird_json_file_path, "r") as json_file:
    connection_details_firebird = json.load(json_file)

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestSqlAlchemyFirebird(unittest.TestCase):
    def test_connect(self):
        actual_result = SqlAlchemy().connect(connection_details_firebird, engine="firebird")
        self.assertIsNotNone(actual_result)

    def test_connection(self):
        actual_result = SqlAlchemy().test_connection(connection_details_firebird, engine="firebird")
        self.assertTrue(actual_result)

    def test_fetch_data(self):
        catalog = "employee"
        actual_result = SqlAlchemy().fetch_data(connection_details_firebird, catalog, engine="firebird")
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertGreater(len(actual_result), 0)

    def test_fetch_data_with_columns(self):
        catalog = "employee"
        columns = ['emp_no', 'first_name', 'last_name', 'phone_ext']
        actual_result = SqlAlchemy().fetch_data(connection_details_firebird, catalog, columns=columns, engine="firebird")
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertEqual(['emp_no', 'first_name', 'last_name', 'phone_ext'], actual_result.columns.tolist())
        self.assertGreater(len(actual_result), 0)

    def test_fetch_data_with_non_existing_table(self):
        catalog = "employee1"
        with pytest.raises(DatabaseConnectorException) as test_function:
            SqlAlchemy().fetch_data(connection_details_firebird, catalog, engine="firebird")
        self.assertIn("Failed to fetch the data", str(test_function.value))

    def test_get_metadata(self):
        actual_result = SqlAlchemy().get_metadata(connection_details_firebird, engine="firebird")
        # [{'title': 'employee', 'value': 'employee', 'children': [{'title': 'country', 'value': 'country'}, {'title': 'customer', 'value': 'customer'}, {'title': 'department', 'value': 'department'}, {'title': 'employee', 'value': 'employee'}, {'title': 'employee_project', 'value': 'employee_project'}, {'title': 'job', 'value': 'job'}, {'title': 'project', 'value': 'project'}, {'title': 'proj_dept_budget', 'value': 'proj_dept_budget'}, {'title': 'salary_history', 'value': 'salary_history'}, {'title': 'sales', 'value': 'sales'}]}]
        self.assertIsNotNone(actual_result[0].get("title"))

    def test_get_columns(self):
        table_name = "employee"
        actual_result = SqlAlchemy().get_columns(connection_details_firebird, table_name, engine="firebird")
        self.assertTrue(isinstance(actual_result, list))
        self.assertGreater(len(actual_result), 0)

mysql_json_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "mysql_creds.json")

with open(mysql_json_file_path, "r") as json_file:
    mysql_connection_details = json.load(json_file)

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestSqlAlchemyMySql(unittest.TestCase):
    def test_connect_with_vpn(self):
        actual_result = SqlAlchemy().connect(mysql_connection_details, engine="mysql")
        self.assertIsNotNone(actual_result)

    def test_connection_with_vpn(self):
        actual_result = SqlAlchemy().test_connection(mysql_connection_details, engine="mysql")
        self.assertTrue(actual_result)

    def test_fetch_data_with_vpn(self):
        catalog = "sakila.actor" if mysql_connection_details['database'] is None else "actor"
        actual_result = SqlAlchemy().fetch_data(mysql_connection_details, catalog, engine="mysql")
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertGreater(len(actual_result), 0)

    def test_fetch_data(self):
        catalog = "sakila.staff" if mysql_connection_details['database'] is None else "staff"
        actual_result = SqlAlchemy().fetch_data(mysql_connection_details, catalog, engine="mysql")
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertGreater(len(actual_result), 0)

    def test_fetch_data_with_non_existing_table_with_vpn(self):
        catalog = "teacher.info" if mysql_connection_details['database'] is None else "info1"
        with pytest.raises(DatabaseConnectorException) as test_function:
            SqlAlchemy().fetch_data(mysql_connection_details, catalog, engine="mysql")
        self.assertIn("Failed to fetch the data", str(test_function.value))

    def test_get_metadata_with_vpn(self):
        actual_result = SqlAlchemy().get_metadata(mysql_connection_details, engine="mysql")
        self.assertIsNotNone(actual_result[0].get("title"))

    def test_get_columns_with_vpn(self):
        table_name = "actor"
        actual_result = SqlAlchemy().get_columns(mysql_connection_details, table_name, engine="mysql")
        self.assertTrue(isinstance(actual_result, list))
        self.assertGreater(len(actual_result), 0)

test_configs_dir = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations", "test_hooks")
local_json_path = os.path.join(test_configs_dir, "databricks_creds-local.json")
default_json_path = os.path.join(test_configs_dir, "databricks_creds.json")

databricks_json_file_path = os.getenv("AOD_DATABRICKS_TEST_CREDS_PATH")
if not databricks_json_file_path:
    if os.path.exists(local_json_path):
        databricks_json_file_path = local_json_path
    else:
        databricks_json_file_path = default_json_path
databricks_json_file_path = os.path.abspath(databricks_json_file_path)

with open(databricks_json_file_path, "r") as json_file:
    databricks_connection_details = json.load(json_file)

class TestSqlAlchemyDatabricks(unittest.TestCase):
    @patch("core.datasource.implementations.sql_alchemy.SqlAlchemy.connect")
    def test_connect(self, mock_connect):
        mock_connect.return_value = MagicMock()
        actual_result = SqlAlchemy().connect(databricks_connection_details, engine="databricks")
        self.assertIsNotNone(actual_result)

    @patch("core.datasource.implementations.sql_alchemy.SqlAlchemy.test_connection")
    def test_connection(self, mock_test_connection):
        mock_test_connection.return_value = True
        actual_result = SqlAlchemy().test_connection(databricks_connection_details, engine="databricks")
        self.assertTrue(actual_result)

    @patch("core.datasource.implementations.sql_alchemy.SqlAlchemy.fetch_data")
    def test_fetch_data(self, mock_fetch_data):
        dummy_df = pandas.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_fetch_data.return_value = dummy_df

        catalog = "default.test_table" if databricks_connection_details['database'] is None else "test_table"
        actual_result = SqlAlchemy().fetch_data(databricks_connection_details, catalog, engine="databricks")
        self.assertIsInstance(actual_result, pandas.DataFrame)
        self.assertGreater(len(actual_result), 0)

    @patch("core.datasource.implementations.sql_alchemy.SqlAlchemy.fetch_data")
    def test_fetch_data_with_non_existing_table(self, mock_fetch_data):
        mock_fetch_data.side_effect = DatabaseConnectorException("Failed to fetch the data")

        catalog = "default.test" if databricks_connection_details['database'] is None else "test"
        with self.assertRaises(DatabaseConnectorException) as test_function:
            SqlAlchemy().fetch_data(databricks_connection_details, catalog, engine="databricks")
        self.assertIn("Failed to fetch the data", str(test_function.exception))

    @patch("core.datasource.implementations.sql_alchemy.SqlAlchemy.get_metadata")
    def test_get_metadata(self, mock_get_metadata):
        mock_get_metadata.return_value = [{"title": "test_table"}]
        actual_result = SqlAlchemy().get_metadata(databricks_connection_details, engine="databricks")
        self.assertIsNotNone(actual_result[0].get("title"))

    @patch("core.datasource.implementations.sql_alchemy.SqlAlchemy.get_columns")
    def test_get_columns(self, mock_get_columns):
        mock_get_columns.return_value = ["col1", "col2"]
        table_name = "test_table"
        actual_result = SqlAlchemy().get_columns(databricks_connection_details, table_name, engine="databricks")
        self.assertIsInstance(actual_result, list)
        self.assertGreater(len(actual_result), 0)


if __name__ == '__main__':
    unittest.main()
