import unittest
from src.api.services.export_config.utils import ExportUtils

class TestExportUtils(unittest.TestCase):

    def test_generate_parameters_with_valid_data(self):
        details = {
            "type": "database",
            "files_list": [{"file_id": "file123"}],
            "connection_id": "conn_456",
            "catalog": [{"table": "table1"}, {"table": "table2"}]
        }
        success, parameters = ExportUtils().generate_parameters(details)
        expected_parameters = [{
            "database": {
                "catalog": {
                    "file123": {"table": "table1"},
                    "file123": {"table": "table2"}
                }
            }
        }]
        self.assertTrue(success)
        self.assertEqual(parameters, expected_parameters)

    def test_generate_parameters_with_single_catalog(self):
        details = {
            "type": "database",
            "files_list": [{"file_id": "file123"}],
            "connection_id": "conn_456",
            "catalog": {"table": "table1"}
        }
        success, parameters = ExportUtils().generate_parameters(details)
        expected_parameters = [{
            "database": {
                "catalog": {
                    "file123": {"table": "table1"}
                }
            }
        }]
        self.assertTrue(success)
        self.assertEqual(parameters, expected_parameters)

    def test_generate_parameters_with_missing_files_list(self):
        details = {
            "type": "database",
            "connection_id": "conn_456",
            "catalog": [{"table": "table1"}]
        }
        success, parameters = ExportUtils().generate_parameters(details)
        self.assertTrue(success)
        self.assertEqual(parameters, [])

    def test_generate_parameters_with_invalid_type(self):
        details = {
            "type": "invalid_type",
            "files_list": [{"file_id": "file123"}],
            "connection_id": "conn_456",
            "catalog": [{"table": "table1"}]
        }
        success, parameters = ExportUtils().generate_parameters(details)
        self.assertTrue(success)
        self.assertEqual(parameters, [])

    def test_generate_parameters_with_no_files_list(self):
        details = {
            "type": "database",
            "files_list": [],
            "connection_id": "conn_456",
            "catalog": [{"table": "table1"}]
        }
        success, parameters = ExportUtils().generate_parameters(details)
        self.assertTrue(success)
        self.assertEqual(parameters, [])

    def test_generate_parameters_with_invalid_catalog(self):
        details = {
            "type": "database",
            "files_list": [{"file_id": "file123"}],
            "connection_id": "conn_456",
            "catalog": None
        }
        success, parameters = ExportUtils().generate_parameters(details)
        self.assertTrue(success)
        self.assertEqual(parameters, [])

    def test_generate_parameters_with_missing_type(self):
        details = {
            "files_list": [{"file_id": "file123"}],
            "connection_id": "conn_456",
            "catalog": [{"table": "table1"}]
        }
        success, parameters = ExportUtils().generate_parameters(details)
        self.assertTrue(success)
        self.assertEqual(parameters, [])

if __name__ == '__main__':
    unittest.main()
