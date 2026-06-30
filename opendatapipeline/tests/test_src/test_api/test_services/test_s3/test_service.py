import unittest
from unittest.mock import MagicMock, patch
from src.api.services.s3.service import S3Service
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
import pytest

wc_majority = WriteConcern("majority", wtimeout=1000)


class TestS3Service(unittest.TestCase):
    
    @patch('src.api.services.s3.service.S3Service')
    @patch('src.api.services.s3.service.MongoConnector')
    def test_s3_service_without_valid_data(self, MockMongoConnector, MockS3Service):
        # Mock MongoConnector session
        mock_session = MagicMock()
        mock_session.with_transaction.return_value = ({'success': False, 'msg': 'Invalid request data: {}', 'dataCatalog': None}, 500)
        MockMongoConnector.return_value.client._Database__client.start_session.return_value = mock_session
        
        # Mock the S3Service call
        mock_s3_service = MockS3Service.return_value
        mock_s3_service.list_catalogs.return_value = {'success': False, 'msg': 'Invalid request data: {}', 'dataCatalog': None}

        req_data = {}
        response, status_code = mock_session.with_transaction(lambda s: mock_s3_service.list_catalogs(req_data), 
                                                               read_concern=ReadConcern("local"),
                                                               write_concern=wc_majority,
                                                               read_preference=ReadPreference.PRIMARY)
        expected_code = 500
        expected_output = {'success': False, 'msg': 'Invalid request data: {}', 'dataCatalog': None}
        
        self.assertFalse(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)

    @patch('src.api.services.s3.service.S3Service')
    @patch('src.api.services.s3.service.MongoConnector')
    def test_s3_service_with_correct_data(self, MockMongoConnector, MockS3Service):
        # Mock MongoConnector session
        mock_session = MagicMock()
        mock_session.with_transaction.return_value = ({'success': True, 'msg': 'Request successful', 'dataCatalog': []}, 200)
        MockMongoConnector.return_value.client._Database__client.start_session.return_value = mock_session
        
        # Mock the S3Service call
        mock_s3_service = MockS3Service.return_value
        mock_s3_service.list_catalogs.return_value = {'success': True, 'msg': 'Request successful', 'dataCatalog': []}

        req_data = {
            "source": "s3",
            "connection_id": "654879fe22a09b96f228302b"
        }
        response, status_code = mock_session.with_transaction(lambda s: mock_s3_service.list_catalogs(req_data), 
                                                               read_concern=ReadConcern("local"),
                                                               write_concern=wc_majority,
                                                               read_preference=ReadPreference.PRIMARY)
        expected_code = 200
        self.assertTrue(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_code)

    @patch('src.api.services.s3.service.S3Service')
    @patch('src.api.services.s3.service.MongoConnector')
    def test_list_catalogs_service_exception(self, MockMongoConnector, MockS3Service):
        # Mock MongoConnector session
        mock_session = MagicMock()
        mock_session.with_transaction.return_value = ({'success': False, 'msg': 'Failed to connect to the database.', 'dataCatalog': None}, 500)
        MockMongoConnector.return_value.client._Database__client.start_session.return_value = mock_session
        
        # Mock the S3Service call
        mock_s3_service = MockS3Service.return_value
        mock_s3_service.list_catalogs.return_value = {'success': False, 'msg': 'Failed to connect to the database.', 'dataCatalog': None}

        req_data = {
            "source": "s3",
            "connection_id": "654879fe42a09b96f228302c",
        }
        response, status_code = mock_session.with_transaction(lambda s: mock_s3_service.list_catalogs(req_data), 
                                                               read_concern=ReadConcern("local"),
                                                               write_concern=wc_majority,
                                                               read_preference=ReadPreference.PRIMARY)
        expected_code = 500
        self.assertFalse(response['success'])
        self.assertEqual(response, {'success': False, 'msg': 'Failed to connect to the database.', 'dataCatalog': None})
        self.assertEqual(status_code, expected_code)


if __name__ == '__main__':
    unittest.main()
