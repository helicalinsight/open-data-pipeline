import unittest
from spark_server.configurations.prepare_connection_id import PrepareConnectionId
from unittest.mock import patch, MagicMock
import pytest
from spark_server.exceptions.exceptions import *

class TestPrepareConnectionId(unittest.TestCase):
    
    @patch('spark_server.configurations.prepare_connection_id.mongo_schedule')
    def test_get_chat_history(self, mock_mongo_schedule):
        mock_chat = {'pipeline': [{'message': 'Hello'}]}
        mock_mongo_schedule.get_by_id.return_value = mock_chat
        result = PrepareConnectionId().get_chat_history('schedule_id')
        self.assertEqual(result, [{'message': 'Hello'}])
        mock_mongo_schedule.get_by_id.assert_called_once_with('schedule_id')
    
    @patch('spark_server.configurations.prepare_connection_id.mongo_schedule')
    def test_get_chat_history_not_found(self, mock_mongo_schedule):
        mock_mongo_schedule.get_by_id.return_value = None
        with pytest.raises(UtilsException) as test_function:      
            PrepareConnectionId().get_chat_history('schedule_id')
        self.assertEqual("Failed to get chat history.", str(test_function.value))
        mock_mongo_schedule.get_by_id.assert_called_once_with('schedule_id')
    
    @patch('spark_server.configurations.prepare_connection_id.mongo_schedule')
    def test_get_chat_history_exception(self, mock_mongo_schedule):
        mock_mongo_schedule.get_by_id.side_effect = Exception('Database error')
        with pytest.raises(UtilsException) as test_function:      
            PrepareConnectionId().get_chat_history('schedule_id')
        self.assertEqual("Failed to get chat history.", str(test_function.value))
        mock_mongo_schedule.get_by_id.assert_called_once_with('schedule_id')
    
    @patch('spark_server.configurations.prepare_connection_id.mongo_files')
    def test_get_file_details_of_user(self, mock_mongo_files):
        mock_files = {
            'files': [{
                'file_id': 'file_id',
                'file_name': 'file_name',
                'full_name': 'file_name.txt',
                'file_type': '.txt',
                'metadata': {},
                'json_path': 'path/to/json',
                'available': True
            }]
        }
        mock_mongo_files.get_by_user_id.return_value = mock_files
        result = PrepareConnectionId().get_file_details_of_user('file_id', 'user_id')
        expected_result = {
            'file_name': 'file_name.txt',
            'file_type': 'txt'
        }
        self.assertEqual(result, expected_result)
        mock_mongo_files.get_by_user_id.assert_called_once_with('user_id')
    
    @patch('spark_server.configurations.prepare_connection_id.mongo_connections')
    def test_get_connection_details(self, mock_mongo_connections):
        mock_conn_details = {
            'type': 'database',
            'connection_details': {
                'sourceName': 'source_name',
                'other_detail': 'detail_value'
            }
        }
        mock_mongo_connections.get_by_id.return_value = mock_conn_details
        result = PrepareConnectionId().get_connection_details('connection_id')
        expected_result = {
            'type': 'database',
            'other_detail': 'detail_value'
        }
        self.assertEqual(result, expected_result)
        mock_mongo_connections.get_by_id.assert_called_once_with('connection_id')
    
    @patch('spark_server.configurations.prepare_connection_id.PrepareConnectionId.get_connection_details')
    @patch('spark_server.configurations.prepare_connection_id.PrepareConnectionId.get_file_details_of_user')
    @patch('spark_server.configurations.prepare_connection_id.PrepareConnectionId.get_chat_history')
    def test_process_success(self, mock_get_chat_history, mock_get_file_details_of_user, mock_get_connection_details):
        mock_get_chat_history.return_value = [
            {'function': 'read_files', 'parameters': {'file_id': 'file_id1'}},
            {'function': 'read_tables', 'parameters': {'connection_id': 'conn_id1'}},
            {'function': 'export_tables', 'parameters': {'connection_id': 'conn_id2'}}
        ]
        mock_get_file_details_of_user.return_value = {'file_name': 'file_name.txt', 'file_type': 'txt'}
        mock_get_connection_details.return_value = {'type': 'database', 'other_detail': 'detail_value'}
        result = PrepareConnectionId().process('schedule_id', 'user_id')
        expected_result = {'file_id1': {'type': 'file', 'details': {'file_name': 'file_name.txt', 'file_type': 'txt'}}, 'conn_id1': {'type': 'database', 'details': {'type': 'database', 'other_detail': 'detail_value'}}}
        self.assertEqual(result, expected_result)
        mock_get_chat_history.assert_called_once_with('schedule_id')
        mock_get_file_details_of_user.assert_called_once_with('file_id1', 'user_id')
        mock_get_connection_details.assert_any_call('conn_id1')

    def test_process(self):
        result = PrepareConnectionId().process("65cb43f2007a5f38718b8d6c", "6641ad931a3ba5058c56af19")
        expected_result = {'6659a8f3aea87247ea56711d': {'type': 'database', 'details': {'host': '57.128.161.235', 'port': 5432, 'username': 'airflow', 'password': 'Helical@1234', 'database': 'sakila', 'connection_pool': {'pool_size': '10', 'max_overflow': '20', 'pool_timeout': '30', 'pool_recycle': '1800'}, 'type': 'postgres'}}}
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()