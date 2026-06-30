import unittest
from unittest.mock import patch
from src.api.services.data_loads.utils import DataLoadsUtilities

from src.models.connector import MongoConnector

mongo_client = MongoConnector().client
session = mongo_client._Database__client.start_session()

class TestDataLoadsUtilities(unittest.TestCase):

    def test_separate_catalog_with_file_name_success(self):
        input_dict = {
            "source": "database",
            "details": {
                "connection_id": "conn_123",
                "chat_id": "chat_123",
                "file_name": "file_123",
                "user_id": "user_123",
                "database_name": "db_name",
                "catalog": {
                    "catalog_1": ["col1", "col2"],
                    "catalog_2": ["col3", "col4"]
                }
            }
        }

        expected_output = [
            {
                "source": "database",
                "details": {
                    "connection_id": "conn_123",
                    "chat_id": "chat_123",
                    "type": "table",
                    "file_name": "catalog_1",
                    "catalog": "catalog_1",
                    "columns": ["col1", "col2"],
                    "user_id": "user_123",
                    "database_name": "db_name"
                }
            },
            {
                "source": "database",
                "details": {
                    "connection_id": "conn_123",
                    "chat_id": "chat_123",
                    "type": "table",
                    "file_name": "catalog_2",
                    "catalog": "catalog_2",
                    "columns": ["col3", "col4"],
                    "user_id": "user_123",
                    "database_name": "db_name"
                }
            }
        ]

        status, result = DataLoadsUtilities().separate_catalog_with_file_name(input_dict)

        self.assertTrue(status)
        self.assertEqual(result, expected_output)

    def test_separate_catalog_with_file_name_with_source_id(self):
        input_dict = {
            "source": "database",
            "details": {
                "connection_id": "conn_123",
                "chat_id": "chat_123",
                "file_name": "file_123",
                "user_id": "user_123",
                "database_name": "db_name",
                "catalog": {
                    "catalog_1": ["col1", "col2"],
                    "catalog_2": ["col3", "col4"]
                },
                "source_id": "source_123"
            }
        }

        expected_output = [
            {
                "source": "database",
                "details": {
                    "connection_id": "conn_123",
                    "chat_id": "chat_123",
                    "type": "table",
                    "file_name": "catalog_1",
                    "catalog": "catalog_1",
                    "columns": ["col1", "col2"],
                    "user_id": "user_123",
                    "database_name": "db_name",
                    "source_id": "source_123"
                }
            },
            {
                "source": "database",
                "details": {
                    "connection_id": "conn_123",
                    "chat_id": "chat_123",
                    "type": "table",
                    "file_name": "catalog_2",
                    "catalog": "catalog_2",
                    "columns": ["col3", "col4"],
                    "user_id": "user_123",
                    "database_name": "db_name",
                    "source_id": "source_123"
                }
            }
        ]

        status, result = DataLoadsUtilities().separate_catalog_with_file_name(input_dict)

        self.assertTrue(status)
        self.assertEqual(result, expected_output)

    def test_process_type_for_files_success(self):
        input_dict = {
            "details": {
                "type": "data.csv"
            }
        }

        expected_output = {
            "details": {'file_id': None, 'type': 'csv'}
        }

        status, result = DataLoadsUtilities().process_type_for_files(input_dict)

        self.assertTrue(status)
        self.assertEqual(result, expected_output)

    
if __name__ == '__main__':
    unittest.main()
