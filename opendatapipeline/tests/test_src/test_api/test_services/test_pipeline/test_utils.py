import json
import os
import unittest
import mongomock
from bson import ObjectId
import pytest

from src.api.services.pipeline.service import PipelineHistoryService
from src.api.services.pipeline.utils import PipelineHistoryUtils
from src.api import app
from src.models.mongo import mongo_factory
from src.api.validators.jwt_authentication import JWTAuthentication
from src.api.services.pipeline.utils import PipelineHistoryUtils

from src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

from src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()


class TestPipelineUtil(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.valid_token = JWTAuthentication().encode("shiv@gmail.com", "65365001d9654d9ec1172f87")

    '''def test_pipeline_history_for_joins_and_unions(self):
        response = self.app.get('/api/pipeline_history?chat_id=65d9e5f71dee0028fca0055c', headers={'Authorization': self.valid_token})
        actual_output = response.json
        print(actual_output)
        expected_output = True
        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_output['success'], expected_output)'''
    
    def test_format_history(self):
        chat_id = "66729ec22ee1491c32b05b53"
        history = [
                    {
                    "id": "8d683e6e-ce2d-4f73-a3e4-82ddf19772b0",
                    "step": 0,
                    "status": "PASS",
                    "function": "read_files",
                    "parameters": {
                        "file_id": "74d82e21-a20f-4097-9181-2502bb2846f5",
                        "file_name": "customers-100",
                    },
                    "output": {
                        "source_id": "6602a3a74475001648200351"
                    }
                    },
                    {
                    "id": "edf1e3d2-17a6-4bc0-ac04-ba62e78eac2a",
                    "step": 1,
                    "status": "PASS",
                    "function": "read_files",
                    "parameters": {
                        "file_id": "be4f064b-8c0a-492f-8b75-a4f94532266a",
                        "file_name": "industry",
                    },
                    "output": {
                        "source_id": "6602a3a74475001648200352"
                    }
                    },
                    {
                    "id": "cb8e679e-bc59-4447-86b9-59d736ad9761",
                    "step": 2,
                    "status": "PASS",
                    "function": "rename_columns",
                    "parameters": {
                        "groups": [
                        {
                            "old_name": "industry",
                            "new_name": "indus"
                        }
                        ],
                        "source_id": "6602a3a74475001648200352",
                    },
                    "output": None
                    },
                ]
        response = session.with_transaction(lambda s:PipelineHistoryUtils(session)._format_history(history, chat_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(response['success'])
    def test_format_parameters(self):
        item = {
                "id": "8d683e6e-ce2d-4f73-a3e4-82ddf19772b0",
                "step": 0,
                "status": "PASS",
                "function": "read_files",
                "parameters": {
                    "file_id": "74d82e21-a20f-4097-9181-2502bb2846f5",
                    "file_name": "customers-100",
                },
                "output": {
                    "source_id": "6602a3a74475001648200351"
                }
            }
        formatted_params, formatted_files, database_alias = session.with_transaction(lambda s:PipelineHistoryUtils(session)._format_parameters(
            item=item, cwf=None, files=None, chat_id="65cb43f2007a5f38718b9d6a", user_id="6619156aa5f4c5c1b01e4d07"
        ), read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_formatted_params = [{'alias': 'customers-100', '_id': '74d82e21-a20f-4097-9181-2502bb2846f5'}]
        expected_database_alias = 'flat_files'
        self.assertEqual(formatted_params, expected_formatted_params)
        self.assertEqual(database_alias, expected_database_alias)

    def test_format_parameters_with_read_fies(self):
        item = {
                "function": "read_files",
                "parameters": {
                    "file_id": "74d82e21-a20f-4097-9181-2502bb2846f5",
                    "file_name": "customers-100",
                },
                }
        cwf =  {}
        files = []
        formatted_params, formatted_files, database_alias = session.with_transaction(lambda s:PipelineHistoryUtils(session)._format_parameters(item, cwf, files, chat_id="65cb43f2007a5f38718b9d6a", user_id="6619156aa5f4c5c1b01e4d07"
        ), read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_formatted_params = [{'alias': 'customers-100', '_id': '74d82e21-a20f-4097-9181-2502bb2846f5'}]
        expected_formatted_files = None
        self.assertEqual(formatted_params, expected_formatted_params)
        self.assertEqual(formatted_files, expected_formatted_files)

    @pytest.mark.skip("Data is not present in db")
    def test_format_parameters_with_read_table(self):
        item = {
                "function": "read_tables",
                "parameters": {
                    "connection_id": "74d82e21-a20f-4097-9181-2502bb2846f5",
                    "table_name": "customers-100",
                },
                }
        cwf =  {}
        files = []
        formatted_params, formatted_files, database_alias = session.with_transaction(lambda s:PipelineHistoryUtils(session)._format_parameters(item, cwf, files, chat_id="65cb43f2007a5f38718b9d6a", user_id="6619156aa5f4c5c1b01e4d07"
        ),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_formatted_params = [{'catalog': 'customers-100', '_id': '74d82e21-a20f-4097-9181-2502bb2846f5'}]
        expected_formatted_files = None
        self.assertEqual(formatted_params, expected_formatted_params)
        self.assertEqual(formatted_files, expected_formatted_files)

    def test_format_parameters_with_read(self):
        item = {
                "function": "read",
                "parameters": {
                    "connection_id": "654879fe22a09b96f228302b",
                    "file_name": "2017_Order_Data.csv",
                    "source_type": "s3",
                    "type": ".csv"
                },
            }
        cwf =  {}
        files = []
        formatted_params, formatted_files, database_alias = session.with_transaction(lambda s:PipelineHistoryUtils(session)._format_parameters(item, cwf, files, chat_id="65cb43f2007a5f38718c9f77", user_id="65365001d9654d9ec1172f87"
        ),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_formatted_params = [{'catalog': '2017_Order_Data.csv', '_id': '654879fe22a09b96f228302b'}]
        expected_formatted_files = None
        self.assertEqual(formatted_params, expected_formatted_params)
        self.assertEqual(formatted_files, expected_formatted_files)

    def test_format_parameters_with_union(self):
        item = {
            "function": "union",
            "parameters": {
                "groups": [
                {
                    "columns": None
                }
                ],
                "file_names": [
                "industry",
                "customers-100"
                ],
            },
        }
        cwf =  {}
        files = []
        formatted_params, formatted_files, database_alias = session.with_transaction(lambda s:PipelineHistoryUtils(session)._format_parameters(item, cwf, files, chat_id="65cb43f2007a5f38718b9d6a", user_id="6619156aa5f4c5c1b01e4d07"
        ),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_formatted_params = [{'columns': None}]
        expected_formatted_files = [{'alias': ['industry', 'customers-100']}]
        self.assertEqual(formatted_params, expected_formatted_params)
        self.assertEqual(formatted_files, expected_formatted_files)

    def test_format_parameters_with_pytool(self):
        item = {
            "function": "pytool",
        }
        cwf =  {}
        files = []
        formatted_params, formatted_files, database_alias = session.with_transaction(lambda s:PipelineHistoryUtils(session)._format_parameters(item, cwf, files, chat_id="65cb43f2007a5f38718b9d6a", user_id="6619156aa5f4c5c1b01e4d07"
        ),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_formatted_params = [{'code': 'Check YML for Code.'}]
        expected_formatted_files = [{'alias': ['Not Available for PyTool']}]
        
        self.assertEqual(formatted_params, expected_formatted_params)
        self.assertEqual(formatted_files, expected_formatted_files)

    def test_format_parameters_for_else_with_source_id(self):
        item = {
            "function": "rename_columns",
            "parameters": {
                "groups": [
                {
                    "old_name": "indus",
                    "new_name": "industry"
                }
                ],
                "source_id": "6602a3a74475001648200352",
            },
        }
        cwf =  {}
        files = []
        formatted_params, formatted_files, database_alias = session.with_transaction(lambda s:PipelineHistoryUtils(session)._format_parameters(item, cwf, files, chat_id="65cb43f2007a5f38718b9d6a", user_id="6619156aa5f4c5c1b01e4d07"
        ),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_formatted_params = [{'old_name': 'indus', 'new_name': 'industry'}]
        expected_formatted_files = [{'alias': ['customers-100']}]
        self.assertEqual(formatted_params, expected_formatted_params)
        self.assertEqual(formatted_files, expected_formatted_files)

    def test_format_parameters_for_else_with_dataframe_alias(self):
        item = {
            "function": "rename_columns",
            "parameters": {
                "groups": [
                {
                    "old_name": "indus",
                    "new_name": "industry"
                }
                ],
                "dataframe_alias": "indus",
            },
        }
        cwf =  {}
        files = []
        formatted_params, formatted_files, database_alias = session.with_transaction(lambda s:PipelineHistoryUtils(session)._format_parameters(item, cwf, files, chat_id="65cb43f2007a5f38718b9d6a", user_id="6619156aa5f4c5c1b01e4d07"
        ),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_formatted_params = [{'old_name': 'indus', 'new_name': 'industry'}]
        expected_formatted_files = [{'alias': ['indus']}]
        self.assertEqual(formatted_params, expected_formatted_params)
        self.assertEqual(formatted_files, expected_formatted_files)
        

if __name__ == '__main__':
    unittest.main()
