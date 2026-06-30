import unittest
import json
import os
import io
from werkzeug.datastructures import FileStorage
from unittest.mock import patch, MagicMock

import pandas
import pytest

from core.datasource.implementations.google_sheets import GoogleSheets
from src.exceptions.exception import *

test_configs_dir = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations", "test_hooks")
local_json_path = os.path.join(test_configs_dir, "google_sheets_creds-local.json")
default_json_path = os.path.join(test_configs_dir, "google_sheets_creds.json")

json_file_path = os.getenv("AOD_GOOGLE_SHEETS_TEST_CREDS_PATH")
if not json_file_path:
    if os.path.exists(local_json_path):
        json_file_path = local_json_path
    else:
        json_file_path = default_json_path
json_file_path = os.path.abspath(json_file_path)


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestGoogleSheets(unittest.TestCase):
    def setUp(self):
        self.connection_details = {'credentials_object': {"file":json_file_path},
                          'sheet_id': '1eeh7gTEP8xS42N0_IZ2eucJsWX7jpog1cKliqCNWvok'}
        
        # Start patching oauth2client and gspread
        self.patcher_creds = patch("oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name")
        self.patcher_gspread = patch("gspread.authorize")
        
        self.mock_from_json = self.patcher_creds.start()
        self.mock_authorize = self.patcher_gspread.start()
        
        # Build mock clients and sheet structures
        self.mock_client = MagicMock()
        self.mock_spreadsheet = MagicMock()
        self.mock_spreadsheet.title = "students"
        
        self.mock_worksheet = MagicMock()
        self.mock_worksheet.title = "Sheet1"
        self.mock_worksheet.get_all_records.return_value = [
            {"name": "Alice", "age": 20, "marks": 90},
            {"name": "Bob", "age": 21, "marks": 85}
        ]
        
        # Set worksheet retrieval side_effect to raise exception for "Sheet_1"
        def get_worksheet(name):
            if name == "Sheet_1":
                raise Exception("Sheet_1")
            return self.mock_worksheet
        
        self.mock_spreadsheet.worksheet.side_effect = get_worksheet
        self.mock_spreadsheet.worksheets.return_value = [self.mock_worksheet]
        self.mock_spreadsheet.__iter__.return_value = [self.mock_worksheet]
        self.mock_client.open_by_key.return_value = self.mock_spreadsheet
        
        self.mock_authorize.return_value = self.mock_client

    def tearDown(self):
        self.connection_details = None
        self.patcher_creds.stop()
        self.patcher_gspread.stop()
    
    def test_connect(self):
        
        actual_result = GoogleSheets().connect(self.connection_details)
        self.assertIsNotNone(actual_result)

    def test_connection(self):
        actual_result = GoogleSheets().test_connection(self.connection_details)
        self.assertTrue(actual_result)

    def test_fetch_data(self):
        catalog = "Sheet1"
        actual_result = GoogleSheets().fetch_data(self.connection_details, catalog, columns=[])
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertGreater(len(actual_result), 0)
        self.assertEqual(['name', 'age', 'marks'], actual_result.columns.tolist())

    def test_fetch_data_with_columns(self):
        catalog = "Sheet1"
        actual_result = GoogleSheets().fetch_data(self.connection_details, catalog, columns=['name', 'age'])
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))
        self.assertGreater(len(actual_result), 0)
        self.assertEqual(['name', 'age'], actual_result.columns.tolist())

    def test_fetch_data_with_non_existing_work_sheet(self):
        catalog = "Sheet_1"
        with pytest.raises(DatabaseConnectorException) as test_func:
            GoogleSheets().fetch_data(self.connection_details, catalog)
        self.assertEqual("Failed to fetch the data: Sheet_1", str(test_func.value))

    def test_get_metadata(self):
        actual_result = GoogleSheets().get_metadata(self.connection_details)
        # [{'title': 'students', 'value': 'students', 'children': [{'title': 'Sheet1', 'value': 'Sheet1', 'children': []}, {'title': 'Sheet2', 'value': 'Sheet2', 'children': []}, {'title': 'Sheet3', 'value': 'Sheet3', 'children': []}]}]        
        self.assertIsNotNone(actual_result[0]['title'])

    def test_get_columns(self):
        actual_result = GoogleSheets().get_columns(self.connection_details, work_sheet_name="Sheet1")
        self.assertEqual(['name', 'age', 'marks'], actual_result)

    def test_get_columns_with_non_existing_work_sheet(self):
        with pytest.raises(DatabaseConnectorException) as test_func:
            GoogleSheets().get_columns(self.connection_details, work_sheet_name="Sheet_1")
        self.assertEqual("Failed to get columns for sheet Sheet_1: Sheet_1", str(test_func.value))

    