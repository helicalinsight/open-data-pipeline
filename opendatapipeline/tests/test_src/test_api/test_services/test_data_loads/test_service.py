import unittest
from unittest.mock import patch
import pytest
from src.api.services.data_loads.service import DataLoadService

from src.models.connector import MongoConnector

from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)

mongo_client = MongoConnector().client
session = mongo_client._Database__client.start_session()

class TestDataLoadService(unittest.TestCase):

    @patch('src.api.services.data_loads.utils.DataLoadsUtilities.process_type_for_files')
    @patch('src.api.services.data_loads.service.MetaProcessor.execute')
    @patch('src.api.services.data_loads.service.MongoFactory.get_by_id_and_value')
    def test_load_file_to_job_success(self, mock_get_by_id_and_value, mock_execute, mock_process_type_for_files):
        mock_process_type_for_files.return_value = (True, {'source': 'test_source', 'details': {'some_detail': 'value'}})
        mock_execute.return_value = (True, 'some_id')
        mock_get_by_id_and_value.return_value = (True, {'file_name': 'test_file', 'type': 'feather'})

        mock_response = {
            'success': True,
            'message': 'Files Loaded Successfully',
            'files_uploaded': [{'file_name': 'test_file', 'type': 'feather'}],
            'files_failed': []
        }
        mock_status_code = 200

        req_data = {'source': 'test_source', 'details': {'some_detail': 'value'}}
        with patch('src.api.services.data_loads.service.DataLoadService.load_file_to_job', return_value=(mock_response, mock_status_code)):
            response, status_code = DataLoadService(session).load_file_to_job(req_data)
        
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertIn('Files Loaded Successfully', response['message'])
        self.assertEqual(len(response['files_uploaded']), 1)
        self.assertEqual(len(response['files_failed']), 0)

    @patch('src.api.services.data_loads.utils.DataLoadsUtilities.process_type_for_files')
    @patch('src.api.services.data_loads.service.MetaProcessor.execute')
    @patch('src.api.services.data_loads.service.MongoFactory.get_by_id_and_value')
    def test_load_database_to_job_success(self, mock_get_by_id_and_value, mock_execute, mock_separate_catalog_with_file_name):
        mock_separate_catalog_with_file_name.return_value = (True, [
            {'source': 'test_source_1', 'details': {'catalog': 'catalog_1'}},
            {'source': 'test_source_2', 'details': {'catalog': 'catalog_2'}}
        ])
        mock_execute.side_effect = [(True, 'some_id_1'), (True, 'some_id_2')]
        mock_get_by_id_and_value.side_effect = [
            (True, {'file_name': 'test_file_1', 'type': 'feather'}),
            (True, {'file_name': 'test_file_2', 'type': 'feather'})
        ]

        req_data = {'some': 'data'}
        response = DataLoadService(session).load_database_to_job(req_data)
        
        self.assertIn('Files Loaded Successfully', response[0]['message'])
        self.assertTrue(response[0]['success'])

    @pytest.mark.run(order=1)
    def test_load_file_to_job_without_catalog_success(self):
        req_data = {
            "details": {
                "user_id": "65365001d9654d9ec1172f81",
                "connection_id": "c28a8f59-e57b-4983-8911-83474ad2c4c9",
                "chat_id": "66e7dfa92601d90a3465f9fb",
                "type": ".csv",
                "file_name": "dept"
            },
            "source": "file"
        }
        
        response, status_code = session.with_transaction(lambda s:DataLoadService(session).load_file_to_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Files Loaded Successfully')
    
    @pytest.mark.run(order=1)
    def test_load_file_to_job_without_catalog_success_new(self):
        req_data = {
            "details": {
                "user_id": "65365001d9654d9ec1172f81",
                "connection_id": "c28a8f59-e57b-4983-8911-83474ad2c4c9",
                "chat_id": "66e7dfa92601d90a3465f9fb",
                "type": ".csv",
                "file_name": "dept"
            },
            "source": "file"
        }
        
        response, status_code = session.with_transaction(lambda s:DataLoadService(session).load_file_to_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Files Loaded Successfully')

    def test_load_file_to_job_with_catalog_csv(self):
        req_data = {
            "details": {
                "user_id": "65365001d9654d9ec1172f81",
                "connection_id": "c28a8f59-e57b-4983-8911-83474ad2c4c9",
                "chat_id": "66e7dfa92601d90a3465f9fb",
                "type": ".csv",
                "file_name": "dept", 
                "catalog": {
                    "c28a8f59-e57b-4983-8911-83474ad2c4c9": []
                }
            },
            "source": "file"
        }
        
        response, status_code = session.with_transaction(lambda s:DataLoadService(session).load_file_to_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Files Loaded Successfully')

    def test_load_file_to_job_with_catalog_excel(self):
        req_data = {
            "details": {
                "user_id": "65365001d9654d9ec1172f81",
                "connection_id": "74d82e21-a20f-4097-9181-2502bb2845f9",
                "chat_id": "66e7dfa92601d90a3465f9fc",
                "type": ".xlsx",
                "file_name": "msheets", 
                "catalog": {
                    "msheets.Sheet1": ["First Name"],
                    "msheets.Sheet2": ["Sheet2-c1", "Sheet2-c2"],
                    "msheets.Sheet3": ["Sheet3-c1", "Sheet3-c2"]
                }
            },
            "source": "file"
        }
        
        response, status_code = session.with_transaction(lambda s:DataLoadService(session).load_file_to_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Files Loaded Successfully')

    def test_load_s3_file_csv_to_job_success(self):
        req_data = {
            "details": {
                "user_id": "65365001d9654d9ec1172f81",
                "connection_id": "654879fe22a09b96f228302b",
                "chat_id": "66e7dfa92601d90a3465f9fb",
                "type": "csv",
                "file_name": "2017_Order_Data.csv", 
                "catalog":{"2017_Order_Data.csv":[]}
            },
            "source": "s3"
        }
        response, status_code = session.with_transaction(lambda s:DataLoadService(session).load_s3_file_to_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Files Loaded Successfully')
        
    def test_load_s3_file_xlsx_to_job_success(self):
        req_data = {
            "details": {
                "user_id": "65365001d9654d9ec1172f81",
                "connection_id": "654879fe22a09b96f228302b",
                "chat_id": "66e7dfa92601d90a3465f9fb",
                "type": "xlsx",
                "file_name": "2019 Order Data.xlsx", 
                "catalog":{"2019 Order Data.xlsx.Order Data":[]}
            },
            "source": "s3"
        }
        response, status_code = session.with_transaction(lambda s:DataLoadService(session).load_s3_file_to_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Files Loaded Successfully')
        
    def test_load_s3_file_csv_within_folder_to_job_success(self):
        req_data = {
            "details": {
                "user_id": "65365001d9654d9ec1172f81",
                "connection_id": "654879fe22a09b96f228302b",
                "chat_id": "66e7dfa92601d90a3465f9fb",
                "type": "csv",
                "file_name": "test/660d5687c7ac79e16e7f0df2.csv",
                "catalog":{"test/660d5687c7ac79e16e7f0df2.csv":[]}
            },
            "source": "s3"
        }
        response, status_code = session.with_transaction(lambda s:DataLoadService(session).load_s3_file_to_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Files Loaded Successfully')
        
    def test_load_s3_file_xlsx_within_folder_to_job_success(self):
        req_data = {
            "details": {
                "user_id": "65365001d9654d9ec1172f81",
                "connection_id": "654879fe22a09b96f228302b",
                "chat_id": "66e7dfa92601d90a3465f9fb",
                "type": "xlsx",
                "file_name": "test/2020 Order Data.xlsx",
                "catalog":{"test/2020 Order Data.xlsx.Order Data":[]}
            },
            "source": "s3"
        }
        response, status_code = session.with_transaction(lambda s:DataLoadService(session).load_s3_file_to_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Files Loaded Successfully')
        
    def test_load_s3_file_csv_with_columns_to_job_success(self):
        req_data = {
            "details": {
                "user_id": "65365001d9654d9ec1172f81",
                "connection_id": "654879fe22a09b96f228302b",
                "chat_id": "66e7dfa92601d90a3465f9fb",
                "type": "csv",
                "file_name": "2017_Order_Data.csv", 
                "catalog":{"2017_Order_Data.csv":["cookies_shipped","cost"]}
            },
            "source": "s3"
        }
        response, status_code = session.with_transaction(lambda s:DataLoadService(session).load_s3_file_to_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Files Loaded Successfully')
        

if __name__ == '__main__':
    unittest.main()
