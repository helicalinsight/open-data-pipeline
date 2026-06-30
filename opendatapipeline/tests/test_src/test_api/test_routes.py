import json
import os
import unittest
from unittest.mock import patch, MagicMock

import pytest
from werkzeug.datastructures import FileStorage
import yaml
from ....src.api.data.chat import JobModes
from src.api import app
from src.api.validators.jwt_authentication import JWTAuthentication
from ....tests.create_data import setup_files
from src.models.connector import MongoConnector
from src.models.mongo.mongo_factory import MongoFactory

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()
cache_collection = MongoFactory(mongo_client, "cache", session=session)
chat_collection = MongoFactory(mongo_client, "chats", session=session)

class TestNewRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.valid_token = JWTAuthentication().encode("shiv@gmail.com", "65365001d9654d9ec1172f87")
    
    @pytest.mark.run(order=2)
    def test_rename_file_cache_success(self):
        request_data = {"source_id": "6602a3a74475001648200351", "new_file_name": "new_name.txt", "chat_id": "66729ec22ee1491c32b05b64"}
        response = self.app.post('/api/v1/rename_file_cache', headers={'Authorization': self.valid_token}, json=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"success": True, "message": "File renamed successfully."})
        success, cache_doc = cache_collection.get_by_fields("6602a3a74475001648200351", "65365001d9654d9ec1172f81", "66729ec22ee1491c32b05b64")
        self.assertEqual(cache_doc["dataframe_alias"], request_data["new_file_name"])
        success, chat_doc = chat_collection.get_by_id(cache_doc["chat_id"])
        for item in chat_doc["history"]:
            if item["function"] == "read_files":
                self.assertNotEqual(item["parameters"]["file_name"], request_data["new_file_name"])
                if item["parameters"]["file_name"] == "customers-100":
                    self.assertEqual(item["output"]["dataframe_alias"], request_data["new_file_name"])


    def test_rename_file_cache_missing_source_id(self):
        request_data = {"new_file_name": "new_name.txt"}
        response = self.app.post('/api/v1/rename_file_cache', headers={'Authorization': self.valid_token}, json=request_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], 'File not found.')

    def test_rename_file_cache_missing_new_file_name(self):
        request_data = {"source_id": "6602a3a74475001648200351"}
        response = self.app.post('/api/v1/rename_file_cache', headers={'Authorization': self.valid_token}, json=request_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'success': False, 'message': 'File not found.'})

    def test_rename_file_cache_file_not_found(self):
        request_data = {"source_id": "123", "new_file_name": "new_name.txt", "chat_id": "65365001d9654d9ec1172f81"}
        response = self.app.post('/api/v1/rename_file_cache', headers={'Authorization': self.valid_token}, json=request_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'success': False, 'message': 'File not found.'})

    def test_rename_file_cache_internal_server_error(self):
        request_data = {"source_id": "123", "new_file_name": "new_name.txt", "chat_id": "65365001d9654d9ec1172f81"}
        response = self.app.post('/api/v1/rename_file_cache', headers={'Authorization': self.valid_token}, json=request_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"success": False, "message": "File not found."})


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.valid_token = JWTAuthentication().encode("shiv@gmail.com", "65365001d9654d9ec1172f81")

    def test_list_runs_with_mismatching_userid_should_return_404(self):
        '''
        if we make reques to /api/v1/list/runs where "token" has different userid than the "payload",
        api should return a 404 response
        '''
        payload = {
            "user_id": "6619156aa5f4c5c1b01e4d07"
        }
        response = self.app.post(
            '/api/v1/list/runs', 
            headers = {'Authorization': self.valid_token},
            data = payload
        )
        response_json = response.json
        self.assertEqual(response_json['success'], False)
        self.assertEqual(response.status_code, 404)

    def test_get_files_with_valid_token(self):
        response = self.app.get('/api/v1/files', headers={'Authorization': self.valid_token})
        actual_output = response.json
        expected_output = True
        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_output['success'], expected_output)

    def test_get_files_without_token(self):
        response = self.app.get('/api/v1/files')
        actual_output = response.json
        expected_output = {'success': False, 'msg': 'Valid JWT token is missing'}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_get_files_with_invalid_token(self):
        invalid_token = '123'
        response = self.app.get('/api/v1/files', headers={'Authorization': invalid_token})
        actual_output = response.json
        expected_output = {"success": False, "msg": "Invalid token"}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_post_files(self):
        setup_files()
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../.."))
        path = os.path.join(absolute_path, "test_files", "data1.csv")
        with open(path, 'rb') as file:
            response = self.app.post('/api/v1/files',
                                     headers={'Authorization': self.valid_token},
                                     content_type='multipart/form-data',
                                     data={'file': (file, "data1.csv")}
                                     )
        actual_output = response.json
        self.assertEqual(actual_output['success'], True)
        self.assertEqual("data1", actual_output['filesUploaded']['alias'])
        self.assertEqual("File uploaded successfully", actual_output['message'])
        self.assertEqual(response.status_code, 200)

    @pytest.mark.run(order=1)
    def test_post_files_with_file_more_than_5_mb(self):
        setup_files()
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../.."))
        path = os.path.join(absolute_path, "test_files", "large_data.csv") #6000024
        with open(path, 'rb') as file:
            response = self.app.post('/api/v1/files',
                                     headers={'Authorization': self.valid_token},
                                     content_type='multipart/form-data',
                                     data={'file': (file, "large_file.csv")}
                                     )
        actual_output = response.json
        expected_output = {
            "success": False,
            "msg": "Failed to upload file! Please make sure the file size is within ""5120mb. "
        }
        self.assertEqual(expected_output, actual_output)
        self.assertEqual(response.status_code, 400)

    def test_post_files_with_invalid_token(self):
        setup_files()
        invalid_token = "asdfeer3fbsdfdgsdsfdgfbnjdfndkasbyrfbcjs3"
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../.."))
        path = os.path.join(absolute_path, "test_files", "data1.csv")
        with open(path, 'rb') as file:
            response = self.app.post('/api/v1/files',
                                     headers={'Authorization': invalid_token},
                                     content_type='multipart/form-data',
                                     data={'file': (file, "data1.csv")}
                                     )
        actual_output = response.json
        expected_output = {'success': False, 'msg': 'Invalid token'}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    '''def test_delete_files(self):
        file_ids = ["c28a8f59-e57b-4983-8911-83474ad2c4c9"]
        response = self.app.delete(f'/api/files', data=json.dumps({"ids": file_ids}),
                                   headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        print(actual_output)
        expected_output = {'success': True, 'message': 'File deleted successfully.','failed_file_ids': ['c28a8f59-e57b-4983-8911-83474ad2c4c9']}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 200)'''

    def test_delete_files_with_non_existing_file_id(self):
        file_ids = ["c28a8f59-e57b-4983-8911-83474ad2c4c3"]
        response = self.app.delete(f'/api/v1/files', data=json.dumps({"ids": file_ids}),
                                   headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        expected_output = {'success': False, 'message': 'Failed to get details by file id.',
                           'failed_file_ids': []}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 500)

    def test_delete_files_without_giving_file_id(self):
        file_ids = [None]
        response = self.app.delete(f'/api/v1/files', data=json.dumps({"ids": file_ids}),
                                   headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        expected_output = {'success': False, 'message': 'Failed to get details by file id.',
                           'failed_file_ids': []}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 500)

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="rename fails once already rename is done")
    def test_patch_files(self):
        file_id = "c28a8f59-e57b-4983-8911-83474ad2c4c9"  # Replace "your_file_id_here" with the actual file ID
        new_file_name = "Student_enrollements"  # Replace "new_file_name_here" with the desired new file name
        data = {
            "_id": file_id,
            "alias": new_file_name
        }
        response = self.app.patch('/api/v1/files', json=data, headers={'Authorization': self.valid_token})
        actual_output = response.json

    @pytest.mark.skip("Passing on local")
    def test_load_files(self):
        data = {
            "filesInfo": [
                {
                    "source": "file",
                    "details": {
                        "file_id": "c28a8f59-e57b-4983-8911-83474ad2c4c1",
                        "chat_id": "662a0e02c684482642a80a5f",
                        "type": ".csv",
                        "file_name": "dept"
                    }
                }
            ]
        }
        response = self.app.post('/api/v1/data_loads', data=json.dumps(data),
                                 headers={'Authorization': self.valid_token,
                                          'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertEqual(actual_output['success'], True)
        
    @pytest.mark.skip("Check File Path, Not sure if its present or not! - Utkarsh")
    def test_load_files_to_job_csv(self):
        data = {
            "filesInfo": [
                {
                    "source": "file",
                    "details": {
                        "user_id": "6619156aa5f4c5c1b01e4d07",
                        "connection_id": "74d82e21-a20f-4097-9181-2502bb2846f5",
                        "file_name": "industry",
                        "database_name": "flat_files",
                        "type": ".csv",
                        "chat_id": "66729ec22ee1491c32b05b54"
                    }
                }
            ]
        }
        response = self.app.post('/api/v1/data_loads', data=json.dumps(data),
                                 headers={'Authorization': self.valid_token,
                                          'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertEqual(actual_output['success'], True)
        self.assertEqual(actual_output['message'], 'All Files Loaded')

    @pytest.mark.skip("Failed because file is not present")
    def test_load_files_to_job_xlsx(self):
        data = {
            "filesInfo": [
                {
                    "source": "file",
                    "details": {
                        "user_id": "65365001d9654d9ec1172f81",
                        "file_id": "74d82e21-a20f-4097-9181-2502bb2845f4",
                        "file_name": "file1",
                        "type": ".xlsx",
                        "chat_id": "66729ec22ee1491c32b05b54",
                        "catalog" : {"file1.Sheet1" : ['id']}
                    }
                }
            ]
        }
        response = self.app.post('/api/v1/data_loads', data=json.dumps(data),
                                 headers={'Authorization': self.valid_token,
                                          'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertEqual(actual_output['success'], True)
        self.assertEqual(actual_output['message'], 'All Files Loaded')

    def test_rename_column_then_preview_updated_df(self):
        rename_data = {
            "type": "execute",
            "parameters": {
                "groups": [
                    {
                        "old_name": "name",
                        "new_name": "new_name"
                    }
                ]
            },
            "user_info": {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id" : "6619156aa5f4c5c1b01e4d07",
                "source_id": "665480ea9b105cc5e3723a73"
            },
            "intent_name": "rename_columns"
        }
        rename_response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(rename_data)
                                 )
        self.assertEqual(rename_response.status_code, 200)
        preview_data = {
            "type": "preview",
            "preview_info": [
                {
                    "alias": "csv file",
                    "source_id": "665480ea9b105cc5e3723a73"
                }
            ],
            "user_info": {
                "user_id" : "6619156aa5f4c5c1b01e4d07",
                "chat_id": "65cb43f2007a5f38718b9d6a"
            },
        }
        preview_response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(preview_data)
                                 )
        self.assertEqual(preview_response.json['preview'][0]["columns"][1]["name"], "new_name")

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_load_database_to_job(self):
        data = {
            "filesInfo": [
                {
                    "source": "database",
                    "details": {
                        "connection_id": "66445766377fefe5379a700d",
                        "chat_id": "66729ec22ee1491c32b05b53",
                        "file_name": "",
                        "user_id": "65365001d9654d9ec1172f81",
                        "database_name": "postgres",
                        "catalog": {"public.actor":['actor_id', 'first_name', 'last_name']},
                        "source_id": ""
                    }
                }
            ]
        }
        response = self.app.post('/api/v1/data_loads', data=json.dumps(data),
                                 headers={'Authorization': self.valid_token,
                                          'Content-Type': 'application/json'})
        self.assertEqual(response.json["files_uploaded"][0]["alias"], 'public_actor')

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_load_database_to_job_mysql(self):
        data = {
            "filesInfo": [
                {
                    "source": "database",
                    "details": {
                        "connection_id": "654879fe42a09b96f228303e",
                        "chat_id": "65cb43f2007a5f38718b9f77",
                        "file_name": "",
                        "user_id": "65365001d9654d9ec1172f87",
                        "database_name": "mysql",
                        "catalog": {"sakila.staff":['picture']},
                        "source_id": ""
                    }
                }
            ]
        }
        response = self.app.post('/api/v1/data_loads', data=json.dumps(data),
                                 headers={'Authorization': self.valid_token,
                                          'Content-Type': 'application/json'})
        self.assertTrue(response.json['success'])
        self.assertEqual(response.json['files_failed'], [])

    def test_api_chat_post_with_valid_token(self):
        data = {
            "chat_name": "chat_1"
        }
        response = self.app.post('/api/v1/chat',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        actual_output.pop("chat_id")
        expected_output = {'success': True, 'chat_name': 'chat_1'}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 200)
    
    def test_api_update_job_mode(self):
        data = {
            "job_mode": JobModes.ACE.value
        }
        response = self.app.patch('/api/v1/update_mode/6757ddf8de0e273ac22d4ad7',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        self.assertEqual(response.status_code, 204)
        success, chat_doc = chat_collection.get_by_id("6757ddf8de0e273ac22d4ad7")
        assert chat_doc.get("job_mode") == JobModes.ACE.value


    def test_api_chat_post_with_valid_token_without_chat_name(self):
        data = {
            "chat_name": None
        }
        response = self.app.post('/api/v1/chat',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        expected_output = {"success": False, "msg": "Session ID and chat name are required."}
        self.assertIn("Session ID and chat name are required", actual_output['msg'])
        self.assertFalse(actual_output['success'])
        self.assertEqual(response.status_code, 400)
    
    def test_get_data_api(self):
        response = self.app.get('/api/v1/get_data/66729ec22ee1491c32b05b53',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        assert response.status_code == 200
        assert response.json["chats"]["history"] != None

    def test_create_chat_data(self):
        value = '''
- function: read_tables
  id: ddfba15f-6f83-4924-a7bf-7d3f1f8d3371
  output:
    source_id: 668656e38b95219ad5b9400d
  parameters:
    columns:
    - actor_id
    - first_name
    connection_id: 668641a4f6111ba526e56b68
    table_name: public.actor
  status: PASS
  step: 0
- function: read_tables
  id: ddfba15f-6f83-4924-a7bf-7d3f1f8d3371
  output:
    source_id: 668656e38b95219ad5b9400d
  parameters:
    columns:
    - actor_id
    - first_name
    connection_id: 668641a4f6111ba526e56b68
    table_name: public.actor
  status: PASS
  step: 0
        '''
        response = self.app.post('/api/v1/get_data/66e7dfa92601d90a3465f9fc',data = json.dumps({"value":value, "mode":"yaml"}),
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        assert response.status_code == 201
        assert response.json["message"] == 'Updated chat data'

    def test_update_chat_data_read_tables(self):
        '''This testcase is testing the updating dataframe-alias case in the yml code in case of read-tables'''
        value = '''
- function: read_tables
  id: ddfba15f-6f83-4924-a7bf-7d3f1f8d3371
  output:
    dataframe_alias: public_cases0001
    source_id: 6602a3a74475001648200351
  parameters:
    columns: []
    connection_id: 654879fe42a09b96f228102c
    table_name: customers-100-table
  status: PASS
  step: 0
        '''
        response = self.app.post('/api/v1/get_data/66729ec22ee1491c32b05b54',data = json.dumps({"value":value, "mode":"yaml"}),
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        success, chat_doc = chat_collection.get_by_id("66729ec22ee1491c32b05b54")
        assert response.status_code == 201
        assert response.json["message"] == 'Updated chat data'
        assert chat_doc.get("job_mode") == JobModes.YAML.value

    def test_update_chat_data(self):
        value = '''
- function: read_files
  id: 1b2b678c-7c4b-4bb6-878e-ccfb9941b6b9
  output:
    dataframe_alias: msheets-new-0
    source_id: 66729ece2ee1491c32b05b54
  parameters:
    file_id: 74d82e21-a20f-4097-9181-2502bb2845f9
    file_name: msheets
  status: PASS
- function: read_files
  id: 1b2b678c-7c4b-4bb6-878e-ccfb9941b7b9
  output:
    dataframe_alias: dept-new-0
    source_id: 66729ece2ee1491c32b05b55
  parameters:
    file_id: c28a8f59-e57b-4983-8911-83474ad2c4c1
    file_name: dept
  status: PASS
- function: read_files
  id: 1b2b678c-7c4b-4bb6-878e-ccfb9941b8b9
  output:
    dataframe_alias: industry-new-0
    source_id: 66729ece2ee1491c32b05b56
  parameters:
    file_id: be4f064b-8c0a-492f-8b75-a4f94532256a
    file_name: industry
  status: PASS
'''

        response = self.app.post('/api/v1/get_data/66e7dfa92601d90a3465f9fc',data = json.dumps({"value":value, "mode":"yaml"}),
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        assert response.status_code == 201
        assert response.json["message"] == 'Updated chat data'

    def test_update_chat_data_pipeline_copy_case(self):
        '''
        Test to check that update works if pipeline is copied from one chat to another
        '''
        user_id = '670e60a261fa9d80ecb984b2'
        chat_id = '99910f9915753466362512d1'
        req_data = {
            "mode": "yaml",
            "value": '''
            -   function: read_files
                output:
                    dataframe_alias: test_alias
                    source_id: my_source_id
                parameters:
                    file_id: 7af4452a-502c-4230-9cbc-c1136ec08919
                    file_name: yield_copy111
            '''
        }
        
        response = self.app.post(
            f"/api/v1/get_data/{chat_id}",
            data = json.dumps(req_data),
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        
        assert response.status_code == 201
        assert response.json["message"] == "Updated chat data"

    @pytest.mark.skip()
    def test_get_information_api(self):
        response = self.app.get('/api/v1/get_information?chat_id=66729ec22ee1491c32b05b60',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        expected_output = {'success': True,
                           'chats': {'cwf': {
    "source_id": "66729ece2ee1491c32b05b54",
    "alias": "customers-100",
    "type": "csv"
  },
                                     'loaded_files': [
    {
      "source_id": "66729ece2ee1491c32b05b54",
      "alias": "customers-100",
      "type": "csv"
    }],
                                     'metadata': [
      "index",
      "customer_id",
      "first",
      "last_name",
      "company",
      "city",
      "country",
      "phone_1",
      "phone_2",
      "email",
      "subscription_date",
      "website"
    ],"configurations":{}},
                           'msg': 'Information retrieved successfully.'}

        self.assertEqual(expected_output, actual_output)
        self.assertEqual(response.status_code, 200)

    def test_get_information_api_for_old_users(self):
        response = self.app.get('/api/v1/get_information?chat_id=65cb43f2007a5f38718b9d6a',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        expected_output = {'success': True, 'chats': {'cwf': {'source_id': '6602a3a74475001648200352', 'type': 'csv'}, 'loaded_files': [{'alias': 'Dummy_Data (1)', 'type': 'csv', 'source_id': '662bb3d788e28e8af8679eb7'}, {'alias': 'new_name.txt', 'type': 'csv', 'source_id': '6602a3a74475001648200351'}], 'metadata': [], 'configurations': {}}, 'msg': 'Information retrieved successfully.'}
        actual_output['chats']['cwf'].pop('alias')
        # self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 200)
        
    def test_get_information_api_with_configuration(self):
        response = self.app.get('/api/v1/get_information?chat_id=66729ec22ee1491c32b05b59',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        expected_output = {'success': True,
                           'chats': {'cwf': {}, 'loaded_files': [],
                                     'metadata': [],"configurations":{"key":"value"}, "job_mode":"llm"},
                           'msg': 'Information retrieved successfully.'}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 200)

    def test_api_chat_post_with_invalid_token(self):
        invalid_token = "erew3efsdf5sdfsdffsfsdf"
        data = {
            "chat_name": "chat_1"
        }
        response = self.app.post('/api/v1/chat',
                                 headers={'Authorization': invalid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_api_chat_get_with_valid_token(self):
        response = self.app.get('/api/v1/chat', headers={'Authorization': self.valid_token})
        actual_output = response.json
        
        self.assertTrue(actual_output['success'])
        self.assertEqual(response.status_code, 200)

    def test_api_chat_get_with_invalid_token(self):
        invalid_token = "erew3efsdf5sdfsdffsfsdf"
        response = self.app.get('/api/v1/chat', headers={'Authorization': invalid_token})
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    @pytest.mark.run(order=1)
    def test_api_chat_patch_with_valid_token(self):
        data = {
            "chat_name": "Table read and export file New"
        }
        response = self.app.patch('/api/v1/chat/65cb43f2007a5f38718b9f77',
                                  headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                  data=json.dumps(data))
        actual_output = response.json
        expected_output = {'chat_id': '65cb43f2007a5f38718b9f77',
                           'chat_name': 'Table read and export file New',
                           'success': True,
                           'user_id': '65365001d9654d9ec1172f81'}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 200)

    def test_api_chat_patch_with_valid_token_without_chat_name(self):
        data = {
            "chat_name": None
        }
        response = self.app.patch('/api/v1/chat/65cb43f2007a5f38718b9d6a',
                                  headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                  data=json.dumps(data))
        actual_output = response.json
        self.assertIn("Chat name is required", actual_output['msg'])
        self.assertFalse(actual_output['success'])
        self.assertEqual(response.status_code, 400)

    def test_api_chat_patch_with_valid_token_invalid_chat_id(self):
        data = {
            "chat_name": "Table read and export file"
        }
        response = self.app.patch('/api/v1/chat/65cb43f2007a5f38718b9d6b',
                                  headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                  data=json.dumps(data))
        actual_output = response.json
        expected_output = {'msg': 'Chat not found.', 'success': False}
        self.assertIn('Chat not found', actual_output['msg'])
        self.assertFalse(actual_output['success'])
        self.assertEqual(response.status_code, 400)

    @pytest.mark.run(order=2)
    def test_api_chat_delete_with_valid_token(self):
        response = self.app.delete('/api/v1/chat/65cb43f2007a5f38718b9d6e',
                                   headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'}
                                   )
        actual_output = response.json
        expected_output = {"success": True, "msg": "Chat deleted successfully.", "chat_id": "65cb43f2007a5f38718b9d6e"}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 200)

    def test_api_chat_delete_with_valid_token_with_non_existing_chat_id(self):
        response = self.app.delete('/api/v1/chat/659bd21acfe7d466255b2a51',
                                   headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'}
                                   )
        actual_output = response.json
        expected_output = {'msg': 'Failed to get data by id', 'success': False}
        self.assertEqual(actual_output['success'], expected_output['success'])
        self.assertEqual(response.status_code, 500)

    def test_api_get_chat_history_with_existing_chat_id(self):
        response = self.app.get('/api/v1/chat_history/662a0e6434dab503d06fae2c',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        self.assertEqual(actual_output['chat_history'][0]['isUser'], False)

    def test_api_get_chat_history_with_existing_chat_id_and_invalid_token(self):
        invalid_token = "sddw3ssdasf3fafsfa3fafasf3"
        response = self.app.get('/api/v1/chat_history/65cb43f2007a5f38718b9d6a',
                                headers={'Authorization': invalid_token}
                                )
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_api_get_chat_history_with_non_existing_chat_id(self):
        response = self.app.get('/api/v1/chat_history/65cb43f2007a5f38718b9d62',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        expected_output = {'chat_history': [], 'has_more': False, 'messaage': 'Failed to get the data.'}
        self.assertEqual(actual_output['chat_history'], expected_output['chat_history'])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="working if we run single")
    def test_api_delete_chat_history_with_existing_chat_id(self):
        response = self.app.delete('/api/v1/chat_history/662a0e02c684482642a80a5f',
                                   headers={'Authorization': self.valid_token}
                                   )
        actual_output = response.json
        expected_output = {'status': True, 'chat_history': [], 'has_more': False, 'selected_files': [],
                           'loaded_files': [], 'columns': [], 'metadata': {},
                           'message': 'Chat history deleted successfully'}
        self.assertEqual(actual_output, expected_output)

    def test_api_delete_chat_history_if_history_is_None(self):
        response = self.app.delete('/api/v1/chat_history/66729ec22ee1491c32b05b60',
                                   headers={'Authorization': self.valid_token}
                                   )
        actual_output = response.json
        expected_output = {'status': True, 'chat_history': [], 'has_more': False, 'selected_files': [],
                           'loaded_files': [], 'columns': [], 'metadata': {},
                           'message': 'Chat history deleted successfully'}
        self.assertEqual(actual_output, expected_output)

    def test_api_delete_chat_history_with_existing_chat_id_and_invalid_token(self):
        invalid_token = "sddw3ssdasf3fafsfa3fafasf3"
        response = self.app.delete('/api/v1/chat_history/65cb43f2007a5f38718b9d6a',
                                   headers={'Authorization': invalid_token}
                                   )
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_get_api_datasources(self):
        response = self.app.get('/api/v1/datasources',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        self.assertIsNotNone(actual_output)
        self.assertTrue(actual_output['success'])

    def test_get_api_datasources_with_invalid_token(self):
        invalid_token = "sddw3ssdasf3fafsfa3fafasf3"
        response = self.app.get('/api/v1/datasources',
                                headers={'Authorization': invalid_token}
                                )
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_get_api_get_application(self):
        data = {"user_id": "65365001d9654d9ec1172f87"}
        response = self.app.get('/api/v1/get_application',
                                headers={'Authorization': self.valid_token},
                                data=data)
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output['msg'], 'Application Configurations and editor Configurations Fetched Successfully!')

    def test_get_api_get_application_with_invalid_token(self):
        invalid_token = "sddw3ssdasf3fafsfa3fafasf3"
        data = {"user_id": "65365001d9654d9ec1172f87"}
        response = self.app.get('/api/v1/get_application',
                                headers={'Authorization': invalid_token},
                                data=data)
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_get_api_saved_connections(self):
        response = self.app.get('/api/v1/Saved_connections?type=redshift',
                                headers={'Authorization': self.valid_token})
        actual_output = response.json
        expected_output = {'databases': [{'_id': '65e4a71ec05be1234e004df6',
                         'alias': 'Resshit',
                         'type': 'redshift'}],
          'msg': 'Fetched connections successfully.',
          'success': True}
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output, expected_output)

    def test_get_api_saved_connections_with_invalid_type(self):
        response = self.app.get('/api/v1/Saved_connections?type=redshiftt',
                                headers={'Authorization': self.valid_token})
        actual_output = response.json
        expected_output = {'success': True, 'databases': [], 'msg': 'Fetched connections successfully.'}
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output, expected_output)

    @pytest.mark.skip()
    def test_get_api_saved_connections_without_type(self):
        response = self.app.get('/api/v1/Saved_connections',
                                headers={'Authorization': self.valid_token})
        actual_output = response.json
        expected_output = {'success': True, 'databases': [], 'msg': 'Fetched connections successfully.'}
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output, expected_output)

    def test_get_api_saved_connections_with_invalid_token(self):
        invalid_token = "sddw3ssdasf3fafsfa3fafasf3"
        response = self.app.get('/api/v1/Saved_connections?type=redshift',
                                headers={'Authorization': invalid_token})
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    @pytest.mark.run(order=2)
    def test_get_api_data_connectors(self):
        response = self.app.get('/api/v1/Data_connectors?connection_id=65e4a71ec05be1234e004df6',
                                headers={'Authorization': self.valid_token})
        actual_output = response.json
        expected_output = {'success': True, 'connection_data': {'connection_id': '65e4a71ec05be1234e004df6',
                                                                'connection_details': {'username': 'redshift',
                                                                                       'password': 'cassendra',
                                                                                       'host': '57.128.161.235',
                                                                                       'port': '9042'}},
                           'msg': 'Connection details fetched successfully.'}
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output, expected_output)

    def test_get_api_data_connectors_with_non_existing_connection_id(self):
        response = self.app.get('/api/v1/Data_connectors?connection_id=65e4a71ec05be5064e112df6',
                                headers={'Authorization': self.valid_token})
        actual_output = response.json
        expected_output = {'success': False, 'connection_data': None, 'msg': 'No connection details found with connection_id: 65e4a71ec05be5064e112df6'}
        self.assertEqual(actual_output, expected_output)

    def test_get_api_data_connectors_with_invalid_token(self):
        invalid_token = "dsafgasde4gdgdfd9sdfnsudusdas"
        response = self.app.get('/api/v1/Data_connectors?connection_id=65e4a71ec05be5064e004df6',
                                headers={'Authorization': invalid_token})
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_get_api_data_connectors_without_connection_id(self):
        response = self.app.get('/api/v1/Data_connectors',
                                headers={'Authorization': self.valid_token},
                                data={"connection_id": "65e4a71ec05be5064e004df4"})
        actual_output = response.json
        expected_output = {'success': False, 'connection_data': None, 'msg': 'No connection details found with connection_id: None'}
        self.assertFalse(actual_output['success'])
        self.assertEqual(actual_output, expected_output)

    def test_post_api_data_connectors(self):
        data = {
            "connection_details": {
                "username": "admin",
                "password": "HelicalAdmin1$",
                "host": "helical-test.982586453799.us-east-1.redshift-serverless.amazonaws.com",
                "port": 5439,
                "database": "dev"
            },
            "connector": "redshift",
            "user_id": "65365001d9654d9ec1172f87"
        }
        response = self.app.post('/api/v1/Data_connectors',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output['message'], 'Connection saved successfully.')

    def test_post_api_data_connectors_with_invalid_token(self):
        invalid_token = "dsafgasde4gdgdfd9sdfnsudusdas"
        data = {
            "connection_details": {
                "username": "admin",
                "password": "HelicalAdmin1$",
                "host": "helical-test.982586453799.us-east-1.redshift-serverless.amazonaws.com",
                "port": 5439,
                "database": "dev"
            },
            "connector": "redshift",
            "user_id": "65365001d9654d9ec1172f87"
        }
        response = self.app.post('/api/v1/Data_connectors',
                                 headers={'Authorization': invalid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    @pytest.mark.skip()
    def test_patch_api_data_connectors(self):
        data = {"connection_id": "65e4a71ec05be5064e004df6",
                "connection_details": {
                    "username": "redshift",
                    "password": "cassandra",
                    "host": "57.128.161.235",
                    "port": "9042"
                },
                "user_id": "65365001d9654d9ec1172f87"
                }
        response = self.app.patch('/api/v1/Data_connectors',
                                  headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                  data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output['msg'], 'Connection details updated successfully.')

    def test_delete_api_data_connectors(self):
        data = {"_id": "65e4a71ec05be5064e004df6"
                }
        response = self.app.delete('/api/v1/Data_connectors',
                                   headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                   data=json.dumps(data))
        actual_output = response.json
        expected_output = {'success': True, 'msg': 'Connection deleted successfully.',
                           'connection_id': '65e4a71ec05be5064e004df6'}
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output, expected_output)

    def test_delete_api_data_connectors_with_non_existing_connection_id(self):
        data = {"_id": "65e4a71ec05be5064e112df6"
                }
        response = self.app.delete('/api/v1/Data_connectors',
                                   headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                   data=json.dumps(data))
        actual_output = response.json
        expected_output = {'success': False, 'msg': "Failed to get data by id",
                           'connection_id': None}
        self.assertFalse(actual_output['success'])

    def test_delete_api_data_connectors_with_invalid_token(self):
        invalid_token = "dsafgasde4gdgdfd9sdfnsudusdas"
        data = {"_id": "65e4a71ec05be5064e004df6"
                }
        response = self.app.delete('/api/v1/Data_connectors',
                                   headers={'Authorization': invalid_token, 'Content-Type': 'application/json'},
                                   data=json.dumps(data))
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    @pytest.mark.skip('needs correct postgres details')
    def test_post_api_connections(self):
        data = {
            "details": {
                "username": "admin",
                "password": "HelicalAdmin1$",
                "host": "helical-test.982586453799.us-east-1.redshift-serverless.amazonaws.com",
                "port": 5439,
                "database": "dev"
            },
            "connector": "redshift",
            "type": "test"
        }
        response = self.app.post('/api/v1/connections',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        expected_output = {'success': True, 'msg': 'Connection tested successfully'}
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output, expected_output)

    def test_post_api_connections_for_couchbase_db(self):
        data = {
            "details": {
                "username": "dbuser",
                "password": "dbpass",
                "host": "164.52.218.57",
                "port": 8091,
                "bucket": "test_bucket"
            },
            "connector": "couchbase",
            "type": "test"
        }
        response = self.app.post('/api/v1/connections',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        expected_output = {'success': True, 'msg': 'Connection tested successfully'}
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output, expected_output)

    def test_post_api_google_login_with_existing_user(self):
        data = {
            "id": "114550382253255756180",
            "email": "dighesurbhi88@gmail.com",
            "verified_email": True,
            "name": "Surbhi dighe",
            "given_name": "Surbhi dighe",
            "family_name": "None",
            "picture": "https://lh3.googleusercontent.com/a/ACg8ocICTw_h93PNcCCaNDloVGuvLCGUmcFIOw7C6mmU6Z6k3TI=s96-c",
            "locale": "en",
            "jwt_auth_active": True,
            "date_joined": {
                "$date": "2023-10-13T07:19:15.284Z"
            },
            "role": "free"
        }
        response = self.app.post('/api/v1/googleauth/login',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertIsNotNone(actual_output['userid'])
        self.assertIsNotNone(actual_output['token'])
        # self.assertEqual(actual_output['msg'], 'Welcome back Surbhi dighe! Getting your workspace ready.')

    def test_post_api_google_login_with_non_existing_user(self):
        data = {
            "id": "6528ef73937ea4e403b98e26",
            "email": "pooja1@gmail.com",
            "verified_email": True,
            "name": "Pooja shanmuk",
            "given_name": "Pooja shanmuk",
            "family_name": "shanmuk",
            "picture": "https://lh3.googleusercontent.com/a/ACg8ocICTw_h93PNcCCaNDloVGuvLCGUmcFIOw7C6mmU6Z6k3TI=s96-c",
            "locale": "en",
            "jwt_auth_active": True,
            "date_joined": {
                "$date": "2023-10-13T07:19:15.284Z"
            },
            "role": "free"
        }
        response = self.app.post('/api/v1/googleauth/login',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="vpn required")
    def test_post_api_list_catalogs_with_existing_connection_id(self):
        data = {
            "source": "postgres",
            "connection_id": "654879fe42a09b96f228302c",
            "database": "sakila"
        }
        response = self.app.post('/api/v1/List_catalogs',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output['msg'], 'Data catalog fetched successfully from sakila.')

    def test_post_api_list_catalogs_with_flat_files_csv(self):
        data = {
            "connection_id" : "74d82e21-a20f-4097-9181-2502bb2846f5",
            "source": "flat_files",
        }
        response = self.app.post('/api/v1/List_catalogs',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        
        expected_catalogs_list = [{'title': 'customers-100', 'value': 'customers-100', 'children': []}]
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output['dataCatalog'], expected_catalogs_list)

    def test_post_api_list_catalogs_with_flat_files_xlsx(self):
        data = {
            "connection_id" : "a4fb23d9-4f79-4ebd-a018-9ce8c1587963",
            "source": "flat_files",
        }
        response = self.app.post('/api/v1/List_catalogs',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        
        expected_catalogs_list = [{'title': 'bank_customers', 'value': 'bank_customers', 'children': [{'title': 'Sheet1', 'value': 'bank_customers.Sheet1'}]}]
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output['dataCatalog'], expected_catalogs_list)


    def test_post_api_list_catalogs_with_non_existing_connection_id(self):
        data = {
            "source": "database",
            "type": "postgres",
            "connection_id": "654879fe42a09b96f228102c",
            "database": "sakila"
        }
        response = self.app.post('/api/v1/List_catalogs',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertFalse(actual_output['success'])
        expected_output = {'success': False, 'msg': 'Failed to connect to the database.', 'dataCatalog': None}
        self.assertEqual(actual_output, expected_output)
    
    @patch("src.api.services.s3.service.S3Service.list_catalogs")
    def test_post_api_list_catalogs_with_s3(self, mock_list_catalogs):
        mock_list_catalogs.return_value = {
            "success": True,
            "msg": "Catalogs fetched successfully",
            "dataCatalog": [
                {'title': '2017_Order_Data.csv', 'value': '2017_Order_Data.csv', 'type': 'csv', 'children': None},
                {'title': '2019 Order Data.xlsx', 'value': '2019 Order Data.xlsx', 'type': 'xlsx', 'children': [
                    {'title': 'Order Data', 'value': '2019 Order Data.xlsx.Order Data', 'type': 'sheet'}
                ]},
                {'title': 'test/', 'value': 'test/', 'type': 'folder', 'children': [
                    {'title': '2020 Order Data.xlsx', 'value': 'test/2020 Order Data.xlsx', 'type': 'xlsx', 'children': [
                        {'title': 'Order Data', 'value': 'test/2020 Order Data.xlsx.Order Data', 'type': 'sheet'}
                    ]},
                    {'title': '660d5687c7ac79e16e7f0df2.csv', 'value': 'test/660d5687c7ac79e16e7f0df2.csv', 'type': 'csv', 'children': None}
                ]}
            ]
        }
        data = {
            "connection_id": "654879fe22a09b96f228302b",
            "source": "s3",
        }
        response = self.app.post(
            '/api/v1/List_catalogs',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output, mock_list_catalogs.return_value)

    def test_post_api_upload_config_with_file(self):
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../.."))
        path = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f87", "source", "flat_files",
                            "Departments.csv")
        with open(path, 'rb') as file:
            response = self.app.post('/api/v1/upload_config',
                                     headers={'Authorization': self.valid_token},
                                     content_type='multipart/form-data',
                                     buffered=True,
                                     data={'file': file, 'db_name': 'new_db'}
                                     )
        actual_output = response.json
        self.assertEqual(actual_output['success'], True)
        expected_output = {'success': True,
                           'user_id': '65365001d9654d9ec1172f81',
                           'details': {'file': path}}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 200)

    def test_post_api_upload_config_without_file(self):
        response = self.app.post('/api/v1/upload_config',
                                 headers={'Authorization': self.valid_token},
                                 content_type='multipart/form-data',
                                 buffered=True,
                                 data={'file': None, 'db_name': 'new_db'}
                                 )
        actual_output = response.json
        self.assertEqual(actual_output['success'], False)
        expected_output = {'success': False, 'msg': 'Unable to Upload.'}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 500)

    def test_api_get_pipeline_history_with_existing_chat_id(self):
        response = self.app.get('/api/v1/pipeline_history?chat_id=6757ddf8de0e916ac22d4ad7',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        self.assertTrue(actual_output['success'])
    
    def test_api_get_pipeline_history_with_existing_chat_id_for_delete_file_operation(self):
        response = self.app.get('/api/v1/pipeline_history?chat_id=67c1afe95c53f9f8424d0b08',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        last_history_entry = actual_output.get("history")[-1]
        expected_output = {'function': 'delete_files', 'parameters': [{'source_id': '800cd78c-140c-44c2-8877-e94761a443b3'}], 'files': []}
        self.assertEqual(last_history_entry, expected_output)


    def test_fix_for_pipeline_history_getting_extra_info(self):
        response = self.app.get('/api/v1/pipeline_history?chat_id=6721e1dc3cfa19546ff0b833',
                                headers={'Authorization': self.valid_token}
                                )
        self.assertFalse('extra_info' in str(response.json))

    def test_api_get_pipeline_history_with_existing_chat_id_and_connection_id(self):
        response = self.app.get('/api/v1/pipeline_history?chat_id=66729ec22ee1491c32b05b54',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        expected_output = [{'function': 'read_files', 'parameters': [{'alias': 'customers-100', '_id': '74d82e21-a20f-4097-9181-2502bb2846f5'}], 'files': None, 'database_alias': 'flat_files'}, {'function': 'read_files', 'parameters': [{'alias': 'industry', '_id': 'be4f064b-8c0a-492f-8b75-a4f94532266a'}], 'files': None, 'database_alias': 'flat_files'}, {'function': 'rename_columns', 'parameters': [{'new_name': 'indus', 'old_name': 'industry'}], 'files': [{'alias': ['na']}]}]
        self.assertTrue(actual_output['success'])
        self.assertEqual(actual_output['history'], expected_output)

    def test_api_get_pipeline_history_with_existing_chat_id_and_invalid_token(self):
        invalid_token = "sdfsd6fnsdfhbsjf8dfnbhdfbd4"
        response = self.app.get('/api/v1/pipeline_history?chat_id=65d9e5f71dee0028fca0055c',
                                headers={'Authorization': invalid_token}
                                )
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_api_get_pipeline_history_with_non_existing_chat_id(self):
        response = self.app.get('/api/v1/pipeline_history?chat_id=65d9e5f71dee0028fca0055d',
                                headers={'Authorization': self.valid_token}
                                )
        self.assertTrue(response.status_code, 204)

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="working if we run single")
    def test_post_api_preview_with_existing_feather_id(self):
        data = {
            "type": "preview",
            "preview_info": [
                {
                    "alias": "csv file",
                    "source_id": "6602a3a74475001648200351"
                }
            ],
            "user_info": {
                "chat_id": "66191e6fa5f4c5c1d01e4d0d"
            }
        }
        response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        actual_output = response.json
        self.assertEqual(actual_output['success'], True)
        self.assertIsNotNone(actual_output['preview'])

    def test_post_api_preview_with_not_existing_feather_id(self):
        data = {
            "type": "preview",
            "preview_info": [
                {
                    "alias": "csv file",
                    "source_id": "6602a3a74475001648200350"
                }
            ]
        }
        response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        actual_output = response.json
        expected_output = {'success': False, 'text': 'Failed to preview'}
        self.assertEqual(actual_output['success'], False)
        self.assertIsNotNone(actual_output, expected_output)

    # need to change the request data and test
    def test_post_api_preview_with_existing_feather_id_and_type_as_execute(self):
        data = {
            "type": "execute",
            "preview_info": [
                {
                    "alias": "csv file",
                    "source_id": "660d3f62605778fcc79c3dc9"
                }
            ]
        }
        response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        actual_output = response.json
        self.assertEqual(actual_output['success'], False)

        # self.assertIsNotNone(actual_output['preview'])

    def test_api_download_with_non_existing_feather_id(self):
        response = self.app.get('/api/v1/download/662badd888e28e8af8679eb3',
                                headers={'Authorization': self.valid_token}
                                )
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.get_data)

    def test_api_download_with_non_existing_feather_id(self):
        response = self.app.get('/api/v1/download/6602a3a74475001648200331',
                                headers={'Authorization': self.valid_token}
                                )
        expected_output = {'success': False, 'text': 'The file not found'}
        self.assertEqual(response.json, expected_output)
        self.assertEqual(response.status_code, 404)

    def test_api_download_with_non_existing_feather_id_and_invalid_token(self):
        invalid_token = "dfbsudfsfudh7ebvdshudasdhvuewbdsd4"
        response = self.app.get('/api/v1/download/6602a3a74475001648200331',
                                headers={'Authorization': invalid_token}
                                )
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_api_cwf(self):
        data = {
            "source_id": "6602a3a74475001648200352",
            "chat_id": "65cb43f2007a5f38718b9d6a",
            "user_id": "6619156aa5f4c5c1b01e4d07"
        }
        response = self.app.post('/api/v1/cwf',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        actual_output = response.json
        expected_output = {'success': True, 'msg': 'customers-100 is the current working file.'}
        self.assertEqual(actual_output, expected_output)

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
    def test_api_get_columns(self):
        data = {
            "connection_id": "66445766377fefe5379a700d",
            "catalog": "public.actor"
             
        }
        response = self.app.post('/api/v1/get_columns',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        self.assertEqual(response.json["columns"], ['actor_id', 'first_name', 'last_name', 'last_update'])

    @pytest.mark.skip("Passing on local")
    def test_api_re_run_pipeline_with_dataframe_alias(self):
            
            data =  [
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
                        "old_name": "name",
                        "new_name": "indus"
                    }
                    ],
                    "source_id": "6602a3a74475001648200352",
                },
                "output": None
                },
            ]
            data_yaml =yaml.dump(data)
            req_data = {
                "mode": "yaml",
                "details": {"value" : data_yaml},
                "chat_id" : "66729ec22ee1491c32b05b53",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))
            assert response.json is not None
            self.assertEqual(response.status_code, 200)

    @pytest.mark.skip("Requires db connection")
    def test_api_re_run_pipeline_in_read_tables(self):
            
            data =  [
                {
                    "function": "read_tables",
                    "id": "b2c8fdb8-6e70-49d1-9ad8-3aa741c6b542",
                    "output":{
                        "dataframe_alias": "public_cases01",
                        "source_id": "674d37e2bedbac8590ea113b",},
                    "parameters":{
                        "columns": [],
                        "connection_id": "6746b7307a00fa554ac4b0a5",
                        "table_name": "public.cases1",
                    "status": "PASS"
                }
                }
            ]
            data_yaml =yaml.dump(data)
            req_data = {
                "mode": "yaml",
                "details": {"value" : data_yaml},
                "chat_id" : "66729ec22ee1491c32b05b54",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))
            assert response.json is not None
            self.assertEqual(response.status_code, 200)

    
    @pytest.mark.skip("Requires db connection")
    def test_api_re_run_pipeline_without_loading_table(self):
            
            data =  [
                {
                    "function": "read_tables",
                    "id": "b2c8fdb8-6e70-49d1-9ad8-3aa741c6b542",
                    "output":{
                        "dataframe_alias": "public_cases01",
                        "source_id": "674d37e2bedbac8590ea114b",},
                    "parameters":{
                        "columns": [],
                        "connection_id": "6746b7307a00fa554ac4b0a5",
                        "table_name": "public.cases1",
                    "status": "PASS"
                }
                }
            ]
            data_yaml =yaml.dump(data)
            req_data = {
                "mode": "yaml",
                "details": {"value" : data_yaml},
                "chat_id" : "66729ec22ee1491c32b05b54",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))

            expected_message = 'First load tables to perform operation'
            assert response.json is not None
            self.assertFalse(response.json['success'])
            self.assertEqual(response.json['message'], expected_message)
    
    def test_api_re_run_pipeline_with_filter_value(self):
        data = [
            {
                "id": "8d683e6e-ce2d-4f73-a3e4-82ddf1977999",
                "step": 0,
                "status": "PASS",
                "function": "read_files",
                "parameters": {
                    "file_id": "be4f064b-8c0a-492f-8b75-a4f94532266a",
                    "file_name": "data2",
                },
                "output": {
                    "dataframe_alias": "step1_out",
                    "source_id": "6602a3a74475001648200999"
                }
            },
            {
                "id": "fd97d793-a5ba-4521-bef7-1ad64c8d6cce",
                "step": 1,
                "function": "filter_value",
                "output": {
                    "dataframe_alias": "step2_out",
                    "source_id": "6602a3a74475001648209999"
                },
                "parameters": {
                    "dataframe_alias": "step1_out",
                    "source_id": "6602a3a74475001648200999",
                    "groups": [{
                        "columns": [
                            "name"
                        ],
                        "expr": "not_equals",
                        "value": "\"nan\""
                    }]
                }
            },
            {
                "id": "fd97d793-a5ba-4521-bef7-1ad64c8d6cce",
                "step": 2,
                "function": "filter_value",
                "parameters": {
                    "dataframe_alias": "step2_out",
                    "source_id": "6602a3a74475001648209999",
                    "groups": [{
                        "columns": [
                            "name"
                        ],
                        "expr": "not_startswith",
                        "value": ["\"XX\""]
                    }]
                }
            }
        ]
        data_yaml =yaml.dump(data)
        req_data = {
            "mode": "yaml",
            "details": {"value" : data_yaml},
            "chat_id" : "66e7dfa92601d90e0000c0a0",
            "dry_run" : True
        }
        response = self.app.post(
            '/api/v1/run_pipeline', 
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'}, 
            data=json.dumps(req_data))
        
        assert response.json is not None
        self.assertEqual(response.status_code, 200)

    def test_api_re_run_pipeline_with_pytool(self):
            
            data =  [
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
                        "old_name": "name",
                        "new_name": "indus"
                    }
                    ],
                    "source_id": "6602a3a74475001648200352",
                },
                "output": None
                },
                {
                "id": "cb8e679e-bc59-4447-86b9-59d736ad9761",
                "step": 3,
                "status": "PASS",
                "function": "pytool",
                "parameters": {
                    "code": 'import pandas as pd\ndf_conf = DataframeInformation.get(id="6602a3a74475001648200352")\ndf = df_conf["6602a3a74475001648200352"]["df"]\ndf["new"] = 0\nDataframeInformation.update(df, id="6602a3a74475001648200352")',
                    "source_id": "6602a3a74475001648200352",
                },
                "output": None
                },
            ]
            req_data = {
                "mode": "yaml",
                "details": {"value" : data},
                "chat_id" : "66729ec22ee1491c32b05b53",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))
            assert response.json is not None
            self.assertEqual(response.status_code, 404)

    def test_api_re_run_pipeline_with_pytool_create(self):
            
            data =  [
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
                        "old_name": "name",
                        "new_name": "indus"
                    }
                    ],
                    "source_id": "6602a3a74475001648200352",
                },
                "output": None
                },
                {
                "id": "cb8e679e-bc59-4447-86b9-59d736ad9761",
                "step": 3,
                "status": "PASS",
                "function": "pytool",
                "parameters": {
                    "code": 'import pandas as pd\ndf_conf = DataframeInformation.get(id="6602a3a74475001648200352")\ndf = df_conf["6602a3a74475001648200352"]["df"]\ndf["new"] = 0\nDataframeInformation.create("6602a3a74475001648200358", "my_test", df)',
                    "source_id": "6602a3a74475001648200352",
                },
                "output": [{"source_id":"6602a3a74475001648200358", "dataframe_alias":"my_test"}]
                },
            ]
            req_data = {
                "mode": "yaml",
                "details": {"value" : data},
                "chat_id" : "66729ec22ee1491c32b05b53",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))
            assert response.json is not None
            self.assertEqual(response.status_code, 404)

    def test_api_re_run_pipeline_with_data_new(self):
            data =  [
                {
                "id": "edf1e3d2-17a6-4bc0-ac04-ba62e78eac2a",
                "function": "read_files",
                "parameters": {
                    "file_id": "be4f064b-8c0a-492f-8b75-a4f94532266a",
                    "file_name": "data2",
                },
                "output": {
                    "source_id": "data2",
                    "dataframe_alias": "data2"
                }
                },

            ]
            data_yaml =yaml.dump(data)
            req_data = {
                "mode": "yaml",
                "details": {"value" : data_yaml},
                "chat_id" : "66e7dfa92601d90e0000c0a0",
                "dry_run" : True
            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))
            assert response.json is not None
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['message'], 'Successfully Ran Pipeline')
            # self.assertEqual(response.json['data'], expected_data)
    
    def test_api_re_run_pipeline_with_data_new_with_rename(self):
            data =  [
                {
                "id": "edf1e3d2-17a6-4bc0-ac04-ba62e78eac2a",
                "function": "read_files",
                "parameters": {
                    "file_id": "be4f064b-8c0a-492f-8b75-a4f94532266a",
                    "file_name": "data2",
                },
                "output": {
                    "source_id": "data2",
                    "dataframe_alias": "data2"
                }
                },
                {
                "id": "edf1e3d2-17a6-4bc0-ac04-ba62e78eac2e",
                "function": "rename_columns",
                "parameters": {
                    "groups": [
                    {
                        "old_name": "name",
                        "new_name": "indus"
                    }
                    ],
                    "source_id": "data2",
                },
                "output": None
                },
            ]
            data_yaml =yaml.dump(data)
            req_data = {
                "mode": "yaml",
                "details": {"value" : data_yaml},
                "chat_id" : "66e7dfa92601d90e0000c0a0",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))

            assert response.json is not None
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['message'], 'Successfully Ran Pipeline')
            # self.assertEqual(response.json['data'], expected_data)
    
    def test_api_re_run_pipeline_with_data_new_with_filter(self):
        data =  [
            {
            "id": "edf1e3d2-17a6-4bc0-ac04-ba62e78eac2a",
            "function": "read_files",
            "parameters": {
                "file_id": "be4f064b-8c0a-492f-8b75-a4f94532266a",
                "file_name": "data2",
            },
            "output": {
                "source_id": "data2",
                "dataframe_alias": "data2"
            }
            },
            {
                "id": "edf1e3d2-17b6-4bc0-ac04-ba62e78eac2e",
                "function": "filter_value",
                "parameters": {
                    "dataframe_alias": "data2",
                    "groups": [
                        {
                            "columns": [
                                "order_id"
                            ],
                            "expr": "startswith",
                            "value": [
                                "XXX"
                            ]
                        }
                    ],
                    "source_id": "data2",
                },
                "output": {
                    "dataframe_alias": "filter_1",
                    "source_id": "filter_1"
                }
            },
        ]
        data_yaml =yaml.dump(data)
        req_data = {
            "mode": "yaml",
            "details": {"value" : data_yaml},
            "chat_id" : "66e7dfa92601d90e0000c0a0",
            "dry_run" : False

        }
        response = self.app.post('/api/v1/run_pipeline',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                data=json.dumps(req_data))

        # expected_data =  [{'_id': 'data2', 'alias': 'data2', 'total_records': 3, 'total_records_dataframe': 3, 'columns': [{'name': 'id', 'dataType': 'int64'}, {'name': 'indus', 'dataType': 'object'}, {'name': 'age', 'dataType': 'int64'}], 'data': [{'id': 4, 'indus': 'Sarah', 'age': 28}, {'id': 5, 'indus': 'Michael', 'age': 40}, {'id': 6, 'indus': 'Emily', 'age': 22}]}]
        assert response.json is not None
        print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully Ran Pipeline')
        # self.assertEqual(response.json['data'][0]["alias"], "data2")
        # self.assertEqual(response.json['data'], expected_data)

    @pytest.mark.run(order=1)
    def test_api_re_run_pipeline_with_data_new_with_pytool(self):
        data =  [
            {
            "id": "edf1e3d2-17a6-4bc0-ac04-ba62e78eac2a",
            "function": "read_files",
            "parameters": {
                "file_id": "be4f064b-8c0a-492f-8b75-a4f94532266a",
                "file_name": "data2",
            },
            "output": {
                "source_id": "data2",
                "dataframe_alias": "data2"
            }
            },
            {
            "id": "cb8e679e-bc59-4447-86b9-59d736ad9761",
            "function": "pytool",
            "parameters": {
                'spark_code' : "",
                "code": 'df = DataframeInformation.get(alias="data2")\ndf=df.drop("age", axis=1)\nDataframeInformation.create(id="my_test",alias="my_test", dataframe=df)',
            },
            "output": [{"source_id":"my_test", "dataframe_alias":"my_test"}]
            },
        ]
        data_yaml =yaml.dump(data)
        req_data = {
            "mode": "yaml",
            "details": {"value" : data_yaml},
            "chat_id" : "66e7dfa92601d90e0000c0a0",
            "dry_run" : True

        }
        response = self.app.post('/api/v1/run_pipeline',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                data=json.dumps(req_data))

        assert response.json is not None
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully Ran Pipeline')

    
    def test_api_re_run_pipeline_with_response_200(self):
            req_data = {
                "mode": "yaml",
                "chat_id" : "66e7dfa92601d90a3464f9fc",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))

            assert response.json is not None
            self.assertTrue(response.json['success'])  

    def test_api_re_run_pipeline_with_empty_data(self):
            req_data = {
                "mode": "yaml",
                "chat_id" : "66e7dfa92601d90a3468f9fc",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))

            assert response.json is not None
            self.assertTrue(response.json['success'])

    @pytest.mark.skip
    def test_api_run_pipeline_with_loading_two_files_one_after_another(self):
            data =  [
                {
                "id": "edf1e3d2-17a6-4bc0-ac04-ba62e78eac2a",
                "step": 1,
                "status": "PASS",
                "function": "read_files",
                "parameters": {
                    "file_id": "ca269158-a6bc-42f1-a918-c38b317ff82f",
                    "file_name": "enrollments",
                },
                "output": {
                    "dataframe_alias": "enrollments",
                    "source_id": "675ac1f823cceabc00088ea1"
                }
                },
                {
                "id": "cb8e679e-bc59-4447-86b9-59d736ad9761",
                "step": 2,
                "status": "PASS",
                "function": "read_files",
                "parameters": {
                    "file_id": "275fae15-66c5-4f53-a0b4-fb77aa3d644e",
                    "file_name": "film",
                },
                "output": {
                    "dataframe_alias": "film",
                    "source_id": "675ac1f823cceabc00088ea2"
                },
                }
            ]
            data_yaml =yaml.dump(data)
            req_data = {
                "mode": "yaml",
                "details": {"value" : data_yaml},
                "chat_id" : "675ac1ea23cceabc00088ea0",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))
            assert response.json is not None
            self.assertFalse(response.json['success'])
            self.assertEqual(response.json['message'], "Unable to execute Error: Failed to preview.")
    
    '''CASE-1: After creating a new job, if I copy and paste YAML code into the YAML editor from other job 
    and run it without loading a file, it should display an error.'''
    @pytest.mark.skip
    def test_api_run_pipeline_for_case_1_failure(self):
            data =  [
                {
                "id": "b1b3e165-f2e9-44d2-977e-4438ce98872e",
                "step": 1,
                "status": "PASS",
                "function": "read_files",
                "parameters": {
                    "file_id": "8d7828ab-3eef-469a-8b82-b75e5443d853",
                    "file_name": "enrollments",
                },
                "output": {
                    "source_id": "675fbb603cbc100b6eccc4cb",
                    "dataframe_alias": "enrollments"
                }
                }
            ]
            data_yaml =yaml.dump(data)
            req_data = {
                "mode": "yaml",
                "details": {"value" : data_yaml},
                "chat_id" : "675fbb963cbc100b6eccc4cc",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))

            expected_data =  []
            assert response.json is not None
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json['success'])
            self.assertEqual(response.json['message'], "First load file to perform operation")
            self.assertEqual(response.json['data'], expected_data)
    
    @pytest.mark.skip
    def test_api_run_pipeline_for_case_1_success(self):
            data =  [
                {
                "id": "5a49659b-7d2f-495e-b261-e15f095de739",
                "step": 1,
                "status": "PASS",
                "function": "read_files",
                "parameters": {
                    "file_id": "8d7828ab-3eef-469a-8b82-b75e5443d853",
                    "file_name": "enrollments",
                },
                "output": {
                    "source_id": "67610fbacd7129e678bc4f43",
                    "dataframe_alias": "enrollments"
                }
                }
            ]
            data_yaml =yaml.dump(data)
            req_data = {
                "mode": "yaml",
                "details": {"value" : data_yaml},
                "chat_id" : "67610f9915753466362512d1",
                "dry_run" : True

            }
            response = self.app.post('/api/v1/run_pipeline',
                                    headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                    data=json.dumps(req_data))

            expected_data =  [{'_id': '67610fbacd7129e678bc4f43', 'alias': 'enrollments', 'total_records': 4, 'total_records_dataframe': 4, 'columns': [{'name': 'bool_column', 'dataType': 'object'}, {'name': 'int_column', 'dataType': 'int64'}], 'data': [{'bool_column': 'true', 'int_column': 12}, {'bool_column': 'false', 'int_column': 34}, {'bool_column': '1', 'int_column': 45}, {'bool_column': 'False', 'int_column': 56}]}]
            assert response.json is not None
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json['success'])
            self.assertEqual(response.json['message'], "Successfully Ran Pipeline")
            self.assertEqual(response.json['data'], expected_data)
    
    # def test_api_run_pipeline_without_dry_run(self):
    #         req_data = {
    #             "mode": "yaml",
    #             "details": {"value" : []},
    #             "chat_id" : "66729ec22ee1491c32b05b28",
    #             "dry_run" : False

    #         }
    #         response = self.app.post('/api/run_pipeline',
    #                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
    #                                 data=json.dumps(req_data))

    #         assert response.json is not None
    #         self.assertEqual(response.status_code, 200)
    #         self.assertTrue(response.json['success'])
    #         self.assertEqual(response.json['message'], "Successfully Ran Pipeline")
    

    @patch('src.api.v1_routes.PySparkCodeGenerator')
    def test_pyspark(self, mock_PySparkCodeGenerator):
            req_data = {
                "user_text": "hi",
                "chat_id" : "662a0e02c684485642a10a1a"
            }
            mock_generator_instance = MagicMock()
            mock_generator_instance.invoke_chain.return_value = {"success": True}
            mock_PySparkCodeGenerator.return_value = mock_generator_instance
            response = self.app.post('/api/v1/pyspark/generate', headers={'Authorization': self.valid_token}, json=req_data)
            self.assertEqual(response.status_code, 200)

    @patch('src.api.v1_routes.PySparkCodeGenerator')
    def test_pyspark_with_exception(self, mock_PySparkCodeGenerator):
            req_data = {
                "chat_id" : "662a0e02c684485642a10a1a"
            }
            mock_generator_instance = MagicMock()
            mock_generator_instance.invoke_chain.side_effect = Exception("Test Exception")
            mock_PySparkCodeGenerator.return_value = mock_generator_instance
            response = self.app.post('/api/v1/pyspark/generate', headers={'Authorization': self.valid_token}, json=req_data)
            self.assertEqual(response.status_code, 500)
    
    @patch('src.api.v1_routes.PySparkCodeGenerator')
    def test_pyspark_reset(self, mock_PySparkCodeGenerator):
            req_data = {
                "chat_id" : "662a0e02c684485642a10a1a"
            }
            mock_generator_instance = MagicMock()
            mock_generator_instance.reset_chain.return_value = {"success": True}
            mock_PySparkCodeGenerator.return_value = mock_generator_instance
            response = self.app.post('/api/v1/pyspark/reset', headers={'Authorization': self.valid_token}, json=req_data)
            self.assertEqual(response.status_code, 200)
   
    @patch('src.api.v1_routes.PySparkCodeGenerator')
    def test_pyspark_reset_with_exception(self, mock_PySparkCodeGenerator):
            req_data = {
                "chat_id" : "662a0e02c684485642a10a1a"
            }
            mock_generator_instance = MagicMock()
            mock_generator_instance.reset_chain.side_effect = Exception("Test Exception")
            mock_PySparkCodeGenerator.return_value = mock_generator_instance
            response = self.app.post('/api/v1/pyspark/generate', headers={'Authorization': self.valid_token}, json=req_data)
            self.assertEqual(response.status_code, 500)

    @pytest.mark.run(order=2)
    @pytest.mark.skip()
    def test_audit_usage_api(self):
        
        response = self.app.get('/api/v1/audit/billing/explore?chat_id=66729ec22ee1491c32b05b54&schedule_id=&run_id=&mode=pipeline&start_time=2024-10-10T16:44&end_time=2024-10-21T11:20',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'}
                                 )
        actual_output = response.json
        self.assertEqual(len(actual_output["Audits"]), 1)
        self.assertEqual(actual_output, {'Audits': [{'Chat_id': '66729ec22ee1491c32b05b54', 'Schedule_id': '12345abc', 'Run_id': 'run_101', 'mode': 'pipeline', 'Total_run_cost': 50, 'run_start_time': '2024-10-10T16:50:00', 'run_end_time': '2024-10-21T11:00:00'}]})

    def test_get_billing_summary_api_daily(self):
        response = self.app.get('/api/v1/audit/billing/summary?summary_type=daily&target_date=2024-09-27',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        expected_output = {'_id': '6701b5a4e6cbe8da73ff33ec', 'user_id': '65365001d9654d9ec1172f81', 'summary_type': 'daily', 'start_date': '2024-09-27T00:00:00', 'end_date': '2024-09-28T00:00:00', 'total_audit_cost': 0}
        self.assertEqual(actual_output['user_id'], expected_output['user_id'])
        self.assertEqual(actual_output['total_audit_cost'], expected_output['total_audit_cost'])

    def test_get_billing_summary_api_weekly(self):
        response = self.app.get('/api/v1/audit/billing/summary?summary_type=weekly&target_date=2024-09-27',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        expected_output = {'user_id': '65365001d9654d9ec1172f81', 'summary_type': 'weekly', 'start_date': '2024-09-23 00:00:00', 'end_date': '2024-09-30 00:00:00', 'total_audit_cost': 0}
        self.assertEqual(actual_output['user_id'], expected_output['user_id'])
        self.assertEqual(actual_output['total_audit_cost'], expected_output['total_audit_cost'])

    def test_get_billing_summary_api_monthly(self):
        response = self.app.get('/api/v1/audit/billing/summary?summary_type=monthly&target_date=2024-09-27',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        expected_output = {'user_id': '65365001d9654d9ec1172f81', 'summary_type': 'monthly', 'start_date': '2024-09-23 00:00:00', 'end_date': '2024-09-30 00:00:00', 'total_audit_cost': 0}
        self.assertEqual(actual_output['user_id'], expected_output['user_id'])
        self.assertEqual(actual_output['total_audit_cost'], expected_output['total_audit_cost'])

    @pytest.mark.skip("Working on local due to data issue in mongodb failing at pipeline")
    def test_get_billing_summary_api_yearly(self):
        response = self.app.get('/api/v1/audit/billing/summary?summary_type=yearly&target_date=2024-09-27',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        expected_output = {
                           'user_id': '65365001d9654d9ec1172f81', 'summary_type': 'yearly', 'start_date': '2024-01-01 00:00:00', 'end_date': '2025-01-01 00:00:00', 
                           'total_audit_cost': 120, 
                           'daily_details': [{'month': 10, 'audit_cost': 120, 'detail_link': '/audit/billing/explore?start_time=2024-10-01T00:00&end_time=2024-10-31T23:59'}], 
                           '_id': "(True, ObjectId('671b75c95db82b27c5b8d366'))"
                        }
        self.assertEqual(actual_output['daily_details'], expected_output['daily_details'])
        self.assertEqual(actual_output['total_audit_cost'], expected_output['total_audit_cost'])
    
    def test_api_get_pipeline_history_when_only_one_step(self):
        response = self.app.get('/api/v1/pipeline_history?chat_id=678a7611682cea02f988e466',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(len(actual_output['next']), 2)
    


    def test_post_api_preview_with_pagination_params(self):
        data = {
            "type": "preview",
            "preview_info": [
                {
                    "alias": "csv file",
                    "source_id": "d89d837c-78e6-4303-9732-6a163e44df71"
                }
            ],
            "page": 1,
            "per_page": 3,
            "user_info":{
                "user_id":"65365001d9654d9ec1172f81",
                "chat_id":"65cb43f2007a5f38718b9d6a"
            }
        }
        response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        actual_output = response.json
        self.assertEqual(actual_output['success'], True)
        self.assertEqual(actual_output["per_page"], 3)
        self.assertEqual(actual_output["page"], 1)
        self.assertEqual(actual_output["total_records"], 4)
    
    def test_post_api_preview_with_pagination_params_page_two(self):
        data = {
            "type": "preview",
            "preview_info": [
                {
                    "alias": "csv file",
                    "source_id": "d89d837c-78e6-4303-9732-6a163e44df71"
                }
            ],
            "page":2,
            "per_page":3,
            "user_info":{
                "user_id":"65365001d9654d9ec1172f81",
                "chat_id":"65cb43f2007a5f38718b9d6a"
            }
        }   
        response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        actual_output = response.json
        self.assertEqual(actual_output["total_records"], 4)
        self.assertEqual(len(response.json["preview"][0]["data"]), 1)

    def test_post_api_preview_with_wrong_pagination_params_gives_blank_data(self):
        data = {
            "type": "preview",
            "preview_info": [
                {
                    "alias": "csv file",
                    "source_id": "d89d837c-78e6-4303-9732-6a163e44df71"
                }
            ],
            "page":2,
            "per_page":4,
            "user_info":{
                "user_id":"65365001d9654d9ec1172f81",
                "chat_id":"65cb43f2007a5f38718b9d6a"
            }
        }   
        response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        self.assertEqual(response.json["preview"][0]["data"], [])

     
    def test_create_dag_without_job_details_for_read_files(self):
        data = {
            "job_id": "6757ddf8de0e521ac22d4ad7",
            "job_name": "Job 22",
            "user_id": "666bc978d5c791c6fbc6752c",
            "schedule_interval": "once",
            "schedule_name": "test2",
            "executionType": "yaml",
            "replace_connections": {
                "61d440a2-c524-439d-81a6-add049028d95": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"},
                "d5f030e0-ca36-4f3a-bf90-7938aa0ca47a": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"}
            },
            "job_details":{
                 "type":"yaml"
            },
            "notification": {
                "active": False,
                "type": "email",
                "details": {
                    "to": None,
                    "subject": None,
                    "body": None
                }
            }
        }
        with patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists') as mock_dag_exists:
            mock_dag_exists.return_value = False
            with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
                mock_call_api.return_value = {"message": "Successfully generated DAG: 66729ec22ee1491c32b05b60 using job_id: 66729ec22ee1491c32b05b60", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
                response = self.app.post('/api/v1/dag', data=json.dumps(data),
                                        headers={'Authorization': self.valid_token,
                                                'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_output['message'], "Scheduled test2 schedule for the job Job 22 successfully")
        
    def test_create_dag_without_job_details_for_read_files_pipeline_mode(self):
        data = {
            "job_id": "6757ddf8de0e521ac22d4ad7",
            "job_name": "Job 22",
            "user_id": "666bc978d5c791c6fbc6752c",
            "schedule_interval": "once",
            "schedule_name": "test2",
            "executionType": "pipeline",
            "replace_connections": {
                "61d440a2-c524-439d-81a6-add049028d95": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"},
                "d5f030e0-ca36-4f3a-bf90-7938aa0ca47a": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"}
            },
            "notification": {
                "active": False,
                "type": "email",
                "details": {
                    "to": None,
                    "subject": None,
                    "body": None
                }
            }
        }
        with patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists') as mock_dag_exists:
            mock_dag_exists.return_value = False
            with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
                mock_call_api.return_value = {"message": "Successfully generated DAG: 66729ec22ee1491c32b05b60 using job_id: 66729ec22ee1491c32b05b60", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
                response = self.app.post('/api/v1/dag', data=json.dumps(data),
                                        headers={'Authorization': self.valid_token,
                                                'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_output['message'], "Scheduled test2 schedule for the job Job 22 successfully")
    
    @patch('src.api.services.airflow_service.service.AirflowAPI.create_dms_dag')
    def test_post_dms_creates_schedule(self, mock_create_dms_dag):
        mock_create_dms_dag.return_value = {
            "message": "Created DMS DAG successfully",
            "schedule_id": "schedule_123"
        }

        payload = {
            "mode": "replace",
            "user_id": "65365001d9654d9ec1172f81",
            "schedule_name": "Nightly migration",
            "schedule_interval": "daily",
            "notification": {"active": False},
            "advanced_scheduling": {},
            "migration_details": {
                "mode": "replace",
                "source_parameters": {
                    "connection_id": "source-conn",
                    "table_name": "public.source_table"
                },
                "destination_parameters": {
                    "connection_id": "dest-conn",
                    "table_name": "public.dest_table"
                },
                "primary_key": "id",
                "migration_type": "table-to-table"
            }
        }

        response = self.app.post(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Created DMS DAG successfully", "schedule_id": "schedule_123"})
    
    @patch('src.api.services.airflow_service.service.AirflowAPI.create_dms_dag')
    def test_dms_primary_key_default_only_for_merge_mode(self, mock_create_dms_dag):
        """Test that primary_key defaults to 'id' only for merge mode, not for append or replace"""
        mock_create_dms_dag.return_value = {
            "message": "Created DMS DAG successfully",
            "schedule_id": "schedule_123"
        }

        base_payload = {
            "user_id": "65365001d9654d9ec1172f81",
            "schedule_name": "Test migration",
            "schedule_interval": "daily",
            "notification": {"active": False},
            "advanced_scheduling": {},
            "migration_details": {
                "source_parameters": {
                    "connection_id": "source-conn",
                    "table_name": "public.source_table"
                },
                "destination_parameters": {
                    "connection_id": "dest-conn",
                    "table_name": "public.dest_table"
                },
                "migration_type": "table-to-table",
                # Note: primary_key is intentionally not provided
            }
        }

        # Test merge mode - should set primary_key to "id" when not provided
        merge_payload = base_payload.copy()
        merge_payload["migration_details"]["mode"] = "merge"
        
        response = self.app.post(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(merge_payload)
        )
        
        self.assertEqual(response.status_code, 200)
        # Check that create_dms_dag was called with primary_key set to "id"
        call_args = mock_create_dms_dag.call_args
        migration_details = call_args[1]['migration_details']  # keyword argument
        self.assertEqual(migration_details.get("primary_key"), "id")
        self.assertEqual(migration_details.get("mode"), "merge")
        
        # Reset mock for next test
        mock_create_dms_dag.reset_mock()

        # Test append mode - should NOT set primary_key to "id" when not provided
        append_payload = base_payload.copy()
        append_payload["migration_details"]["mode"] = "append"
        
        response = self.app.post(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(append_payload)
        )
        
        self.assertEqual(response.status_code, 200)
        # Check that create_dms_dag was called with primary_key as None (not set to "id")
        call_args = mock_create_dms_dag.call_args
        migration_details = call_args[1]['migration_details']
        self.assertIsNone(migration_details.get("primary_key"))
        self.assertEqual(migration_details.get("mode"), "append")
        
        # Reset mock for next test
        mock_create_dms_dag.reset_mock()

        # Test replace mode - should NOT set primary_key to "id" when not provided
        replace_payload = base_payload.copy()
        replace_payload["migration_details"]["mode"] = "replace"
        
        response = self.app.post(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(replace_payload)
        )
        
        self.assertEqual(response.status_code, 200)
        # Check that create_dms_dag was called with primary_key as None (not set to "id")
        call_args = mock_create_dms_dag.call_args
        migration_details = call_args[1]['migration_details']
        self.assertIsNone(migration_details.get("primary_key"))
        self.assertEqual(migration_details.get("mode"), "replace")
    @patch('src.api.services.airflow_service.service.AirflowAPI.get_dms_schedule_info')
    def test_get_dms_schedule_info(self, mock_get_dms_schedule_info):
        mock_get_dms_schedule_info.return_value = {
            "success": True,
            "schedules": [
                {
                    "schedule_id": "schedule_123",
                    "schedule_name": "Nightly migration",
                    "user_id": "65365001d9654d9ec1172f81",
                    "migration_details": {
                        "mode": "replace",
                        "source_parameters": {
                            "connection_id": "source-conn",
                            "table_name": "public.source_table"
                        }
                    }
                }
            ]
        }
        
        response = self.app.get(
            '/api/v1/dms?user_id=65365001d9654d9ec1172f81',
            headers={'Authorization': self.valid_token}
        )
        actual_output = response.json
        self.assertEqual(response.status_code, 200)
        self.assertTrue(actual_output['success'])
        mock_get_dms_schedule_info.assert_called_once_with(
            user_id="65365001d9654d9ec1172f81",
            schedule_id=None
        )
    
    @patch('src.api.services.airflow_service.service.AirflowAPI.get_dms_schedule_info')
    def test_get_dms_schedule_info_with_schedule_id(self, mock_get_dms_schedule_info):
        mock_get_dms_schedule_info.return_value = {
            "success": True,
            "schedule": {
                "schedule_id": "schedule_123",
                "schedule_name": "Nightly migration",
                "user_id": "65365001d9654d9ec1172f81"
            }
        }
        
        response = self.app.get('/api/v1/dms?user_id=65365001d9654d9ec1172f81&schedule_id=schedule_123',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        self.assertEqual(response.status_code, 200)
        self.assertTrue(actual_output['success'])
        mock_get_dms_schedule_info.assert_called_once_with(
            user_id="65365001d9654d9ec1172f81",
            schedule_id="schedule_123"
        )
    
    @patch('src.api.services.airflow_service.service.AirflowAPI.get_dms_schedule_info')
    def test_get_dms_schedule_info_with_exception(self, mock_get_dms_schedule_info):
        mock_get_dms_schedule_info.side_effect = Exception("Schedule not found")
        
        response = self.app.get('/api/v1/dms?user_id=65365001d9654d9ec1172f81',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        self.assertEqual(response.status_code, 500)
        self.assertFalse(actual_output['success'])
        self.assertEqual(actual_output['error'], "Schedule not found")
    
    def test_get_dms_schedule_info_with_invalid_token(self):
        invalid_token = "sddw3ssdasf3fafsfa3fafasf3"
        response = self.app.get('/api/v1/dms?user_id=65365001d9654d9ec1172f81',
                                headers={'Authorization': invalid_token}
                                )
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_get_dms_schedule_info_missing_user_id(self):
        response = self.app.get(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token}
        )
        actual_output = response.json
        self.assertEqual(response.status_code, 400)
        self.assertFalse(actual_output['success'])
        self.assertEqual(actual_output['message'], 'user_id is required')
        
    @patch('src.api.services.airflow_service.service.AirflowAPI.delete_dms_dag')
    def test_delete_dms_schedule(self, mock_delete_dms_schedule):
        mock_delete_dms_schedule.return_value = {
            "message": "schedule_123"
        }
        
        payload = {
            "user_id": "65365001d9654d9ec1172f81",
            "schedule_id": "schedule_123"
        }
        
        response = self.app.delete(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        actual_output = response.json
        self.assertEqual(response.status_code, 200)
        mock_delete_dms_schedule.assert_called_once()

    def test_delete_dms_schedule_with_invalid_token(self):
        invalid_token = "sddw3ssdasf3fafsfa3fafasf3"
        payload = {
            "user_id": "65365001d9654d9ec1172f81",
            "schedule_id": "schedule_123"
        }
        
        response = self.app.delete(
            '/api/v1/dms',
            headers={'Authorization': invalid_token, 'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        actual_output = response.json
        expected_output = {'msg': 'Invalid token', 'success': False}
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 400)

    def test_delete_dms_schedule_with_mismatched_user_id(self):
        payload = {
            "user_id": "different_user_id",
            "schedule_id": "schedule_123"
        }
        
        response = self.app.delete(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        actual_output = response.json
        self.assertEqual(response.status_code, 400)

    def test_delete_dms_schedule_missing_user_id(self):
        payload = {
            "schedule_id": "schedule_123"
        }
        
        response = self.app.delete(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        actual_output = response.json
        self.assertEqual(response.status_code, 400)

    def test_delete_dms_schedule_missing_schedule_ids(self):
        payload = {
            "user_id": "65365001d9654d9ec1172f81"
        }
        
        response = self.app.delete(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        actual_output = response.json
        self.assertEqual(response.status_code, 400)

    @patch('src.api.services.airflow_service.service.AirflowAPI.delete_dms_dag')
    def test_delete_dms_schedule_with_exception(self, mock_delete_dms_schedule):
        mock_delete_dms_schedule.side_effect = Exception("Failed to delete schedule")
        
        payload = {
            "user_id": "65365001d9654d9ec1172f81",
            "schedule_id": "schedule_123"
        }
        
        response = self.app.delete(
            '/api/v1/dms',
            headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        actual_output = response.json
        self.assertEqual(response.status_code, 500)
        
    def test_edit_schedule(self):
        
        data = {
            "schedule_id": "99995001d9654d9ec1172f87",
            "notification": {
                "active": False,
                "type": "email",
                "details": {
                    "to": None,
                    "subject": None,
                    "body": None
                }
            }
        }
        
        with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
            mock_call_api.return_value = {"message": "success", "dag_run_id": "abs", "job_id": "abc", "engine_type": "code"}
            response = self.app.patch(
                '/api/v1/schedule', 
                data=json.dumps(data),
                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'}
            )
            
        self.assertEqual(response.json["success"], True)
        
    def test_edit_schedule_should_not_succeed_with_invalid_execution_type(self):
        
        data = {
            "schedule_id": "99995001d9654d9ec1172f87",
            "notification": {
                "active": False,
                "type": "email",
                "details": {
                    "to": None,
                    "subject": None,
                    "body": None
                }
            },
            "execution_type": "random"
        }
        
        with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
            mock_call_api.return_value = {"message": "success", "dag_run_id": "abs", "job_id": "abc"}
            response = self.app.patch(
                '/api/v1/schedule', 
                data=json.dumps(data),
                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'}
            )
            
        self.assertEqual(response.json["success"], False)

    def test_create_dag_without_job_details_for_read_tables(self):
        
        data = {
            "job_id": "6757ddf8de0e763ac22d4ad7",
            "job_name": "Job 22",
            "user_id": "666bc978d5c791c6fbc6752c",
            "schedule_interval": "once",
            "schedule_name": "test2",
            "executionType": "yaml",
            "replace_connections": {
                "61d440a2-c524-439d-81a6-add049028d95": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"},
                "d5f030e0-ca36-4f3a-bf90-7938aa0ca47a": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"}
            },
            "job_details":{
                 "type":"yaml"
            },
            "notification": {
                "active": False,
                "type": "email",
                "details": {
                    "to": None,
                    "subject": None,
                    "body": None
                }
            }
        }
        with patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists') as mock_dag_exists:
            mock_dag_exists.return_value = False
            with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
                mock_call_api.return_value = {"message": "Successfully generated DAG: 66729ec22ee1491c32b05b60 using job_id: 66729ec22ee1491c32b05b60", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
                response = self.app.post('/api/v1/dag', data=json.dumps(data),
                                        headers={'Authorization': self.valid_token,
                                                'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Scheduled test2 schedule for the job Job 22 successfully")

    def test_create_dag_without_export(self):
        data = {
            "job_id": "6757ddf8de0e916ac22d4ad7",
            "job_name": "Job 22",
            "user_id": "666bc978d5c791c6fbc6752c",
            "schedule_interval": "once",
            "schedule_name": "test2",
            "executionType": "yaml",
            "replace_connections": {
                "61d440a2-c524-439d-81a6-add049028d95": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"},
                "d5f030e0-ca36-4f3a-bf90-7938aa0ca47a": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"}
            },
            "job_details":{
                 "type":"yaml"
            },
            "notification": {
                "active": False,
                "type": "email",
                "details": {
                    "to": None,
                    "subject": None,
                    "body": None
                }
            }
        }
        with patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists') as mock_dag_exists:
            mock_dag_exists.return_value = False
            with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
                mock_call_api.return_value = {"message": "Successfully generated DAG: 66729ec22ee1491c32b05b60 using job_id: 66729ec22ee1491c32b05b60", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
                response = self.app.post('/api/v1/dag', data=json.dumps(data),
                                        headers={'Authorization': self.valid_token,
                                                'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Scheduled test2 schedule for the job Job 22 successfully")
    
    def test_stream_dag_log(self):
        data = {
            "job_id": "123",
            "dag_run_id": "manual_456"
        }
        
        with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
            mock_call_api.side_effect = [
                {"content": "[('', 'Log chunk 1')]", "continuation_token": "token1"},
                {"content": "[('', 'Log chunk 2')]", "continuation_token": "token1"},
                {"content": "[('', 'Log chunk 3')]", "continuation_token": "token1"},
                {"content": "[('', 'Log chunk 4')]", "continuation_token": "token1"},
                {"content": "[('', 'Log chunk end. Marking task as SUCCESS')]", "continuation_token": "token1"}
            ]
            
            response = self.app.post(
                '/api/v1/airflow/stream_log',
                data=json.dumps(data),
                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'}
            )
            
            self.assertEqual(response.status_code, 200)
            
            streamed_logs = b"".join(response.response).decode("utf-8")
        
            self.assertIn("----Streaming logs for the run----", streamed_logs)
            self.assertIn("Log chunk 1", streamed_logs)
            self.assertIn("Log chunk 2", streamed_logs)
            self.assertIn("Marking task as SUCCESS", streamed_logs)
            self.assertIn("-----End of log streaming----", streamed_logs)
            
            # ensure call_api is called for each chunk
            self.assertEqual(mock_call_api.call_count, 5)
    
    def test_create_dag_with_read_as_last_step(self):
        data = {
            "job_id": "6757ddf8de0e273ac22d4ad7",
            "job_name": "Job 22",
            "user_id": "666bc978d5c791c6fbc6752c",
            "schedule_interval": "once",
            "schedule_name": "test2",
            "executionType": "yaml",
            "replace_connections": {
                "61d440a2-c524-439d-81a6-add049028d95": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"},
                "d5f030e0-ca36-4f3a-bf90-7938aa0ca47a": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"}
            },
            "job_details":{
                 "type":"yaml"
            },
            "notification": {
                "active": False,
                "type": "email",
                "details": {
                    "to": None,
                    "subject": None,
                    "body": None
                }
            }
        }
        with patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists') as mock_dag_exists:
            mock_dag_exists.return_value = False
            with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
                mock_call_api.return_value = {"message": "Successfully generated DAG: 66729ec22ee1491c32b05b60 using job_id: 66729ec22ee1491c32b05b60", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
                response = self.app.post('/api/v1/dag', data=json.dumps(data),
                                        headers={'Authorization': self.valid_token,
                                                'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Scheduled test2 schedule for the job Job 22 successfully")
    
    def test_create_dag_with_filter_value_as_last_step(self):
        data = {
            "job_id": "6757ddf8de0e283ac22d4ad7",
            "job_name": "Job 22",
            "user_id": "666bc978d5c791c6fbc6752c",
            "schedule_interval": "once",
            "schedule_name": "test2",
            "executionType": "yaml",
            "replace_connections": {
                "61d440a2-c524-439d-81a6-add049028d95": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"},
                "d5f030e0-ca36-4f3a-bf90-7938aa0ca47a": {"connectionId":"69142c9374cdef6ef932d2b4","connectionName":"new","connectionType":"postgres"}
            },
            "job_details":{
                 "type":"yaml"
            },
            "notification": {
                "active": False,
                "type": "email",
                "details": {
                    "to": None,
                    "subject": None,
                    "body": None
                }
            }
        }
        with patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists') as mock_dag_exists:
            mock_dag_exists.return_value = False
            with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
                mock_call_api.return_value = {"message": "Successfully generated DAG: 66729ec22ee1491c32b05b60 using job_id: 66729ec22ee1491c32b05b60", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
                response = self.app.post('/api/v1/dag', data=json.dumps(data),
                                        headers={'Authorization': self.valid_token,
                                                'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Scheduled test2 schedule for the job Job 22 successfully")
    
    @pytest.mark.skip("get_data is not expected to have side effect in mongodb now, so skipping the test")
    def test_get_preview_after_dry_run_in_execute_preview_api(self):
        data =  [
            {
            "id": "edf1e3d2-17a6-4bc0-ac04-ba62e78eac2a",
            "function": "read_files",
            "parameters": {
                "file_id": "be4f064b-8c0a-492f-8b75-a4f94532266a",
                "file_name": "data2",
            },
            "output": {
                "source_id": "data2",
                "dataframe_alias": "data2"
            }
            },
            {
                "id": "edf1e3d2-17b6-4bc0-ac04-ba62e78eac2e",
                "function": "filter_value",
                "parameters": {
                    "dataframe_alias": "data2",
                    "groups": [
                        {
                            "columns": [
                                "name"
                            ],
                            "expr": "equals",
                            "value": [
                                22
                            ]
                        }
                    ],
                    "source_id": "data2",
                },
                "output": {
                    "dataframe_alias": "filter_1",
                    "source_id": "filter_1"
                }
            },
        ]
        data_yaml =yaml.dump(data)
        req_data = {
            "mode": "yaml",
            "value" : data_yaml,

        }
        response = self.app.post('/api/v1/get_data/65cb43f2007a5f12718b9d6e',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                data=json.dumps(req_data))
        self.assertEqual(response.status_code, 201)

        get_info_expected_data = {'success': True, 'chats': {'cwf': {'source_id': 'filter_1', 'alias': 'filter_1'}, 
                            'loaded_files': [
                                {'alias': 'data2', 'source_id': 'data2'}, 
                                {'alias': 'filter_1', 'source_id': 'filter_1'}
                            ], 'metadata': [], 'configurations': {}, 'job_mode': 'yaml'}, 
                            'msg': 'Information retrieved successfully.'}
        get_info_response = self.app.get('/api/v1/get_information?chat_id=65cb43f2007a5f12718b9d6e',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        self.assertEqual(get_info_response.status_code, 200)
        self.assertEqual(get_info_expected_data, get_info_response.json)

        preview_data = {
            "type": "preview",
            "preview_info": [
                {
                    "alias": "filter_1",
                    "source_id": "filter_1"
                }
            ],
            "mode": "yaml",
            "user_info":{
                "user_id":"65365001d9654d9ec1172f81",
                "chat_id":"65cb43f2007a5f12718b9d6e"
            }
        }
        preview_response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(preview_data)
                                 )
        self.assertEqual(preview_response.status_code, 200)
        self.assertEqual(preview_response.json['preview'][0]["total_records"], 0)

    def test_remove_files_from_job(self):
        response = self.app.delete('/api/v1/remove_file',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                data=json.dumps({"source_id":"666bd9fc87c043982cd173d8", "chat_id":"6757ddf8de0e916ac22d4ad7"}))
        assert response.status_code == 200
        assert response.json == {'success': True, 'message': 'File Deleted Successfully'}
        succ, chat_doc = chat_collection.get_by_id("6757ddf8de0e916ac22d4ad7")
        assert "666bd9fc87c043982cd173d8" not in chat_doc.get("files")
        last_step = chat_doc.get("history")[-1]
        assert last_step.get("function") == "delete_files"
    
    def test_rerun_pipeline_with_delete_files(self):
        history = [{'function': 'read_files', 'id': 'c28a8f59-e57b-4983-8911-83474ad2c4c9', 'output': {'source_id': '666bd9f987c043982cd173d7'}, 'parameters': {'file_id': 'c28a8f59-e57b-4983-8911-83474ad2c4c9', 'file_name': 'customers-100'}, 'status': 'PASS', 'step': 0}, {'id': 'b8278709-b19e-433c-9e31-46519ef66c48', 'status': 'PASS', 'function': 'delete_files', 'parameters': {'source_id': '666bd9f987c043982cd173d7'}, 'output': None}]
        data_yaml =yaml.dump(history)
        req_data = {
            "mode": "yaml",
            "details": {"value" : data_yaml},
            "chat_id" : "6757ddf8de0e916ac27d4ad7",
            "dry_run" : True

        }
        response = self.app.post('/api/v1/run_pipeline',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                data=json.dumps(req_data))
        assert response.status_code == 200
    
    def test_rerun_with_export_file(self):
        data =  [
            {
            "id": "edf1e3d2-17a6-4bc0-ac04-ba62e78eac2a",
            "function": "read_files",
            "parameters": {
                "file_id": "c28a8f59-e57b-4983-8911-83474ad2c4c9",
                "file_name": "data2",
            },
            "output": {
                "source_id": "data2",
                "dataframe_alias": "data2"
            }
            },
            {
                "id": "edf1e3d2-17b6-4bc0-ac04-ba62e78eac2e",
                "function": "export",
                "parameters": {
                    "source_id": "data2",
                    "export_name":"data2"
                },
                "output": None
            },
        ]
        data_yaml =yaml.dump(data)
        req_data = {
            "mode": "yaml",
            "details": {"value" : data_yaml},
            "chat_id" : "66729ec22ee1491c32b05b64",
            "dry_run" : True

        }
        response = self.app.post('/api/v1/run_pipeline',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                data=json.dumps(req_data))
        self.assertEqual(response.status_code, 200)
    

    def test_export_and_preview_yaml(self):
        rename_data = {
            "type": "execute",
            "parameters": {
                "source": 
                    {
                        "source_id": "66729ece2ee1492c32b05b54"
                    },
                "export_name": "data2"

            },
            "user_info": {
                "chat_id" : "66729ec22ee1491c32b05b64",
                "user_id" : "65365001d9654d9ec1172f81",
            },
            "intent_name": "export"
        }
        response = self.app.post('/api/v1/execute',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(rename_data)
                                 )
        self.assertEqual(response.status_code, 200)

        get_data_response = self.app.get('/api/v1/get_data/66729ec22ee1491c32b05b64',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(rename_data)
                                 )
        assert get_data_response.status_code == 200
        data = yaml.load(get_data_response.json["chats"]["history"], Loader=yaml.SafeLoader)
        assert data[-1]["function"] == "export"

    
    def test_get_information_api_for_old_chat_with_code(self):
        response = self.app.get('/api/v1/get_information?chat_id=6757ddf8de0e273ac22d4ad7',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        assert response.json["chats"]["job_mode"] == JobModes.ACE.value
        # self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 200)
    
    def test_get_information_api_for_old_chat_with_no_code(self):
        response = self.app.get('/api/v1/get_information?chat_id=6757ddf8de0e283ac22d4ad7',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        assert response.json["chats"]["job_mode"] == JobModes.LLM.value
        # self.assertEqual(actual_output, expected_output)
        self.assertEqual(response.status_code, 200)

    def test_api_get_pipeline_history_with_existing_chat_id_for_aggregate_operation(self):
        response = self.app.get('/api/v1/pipeline_history?chat_id=67c57ad921f57b7a40ad1006',
                                headers={'Authorization': self.valid_token}
                                )
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        last_history_entry = actual_output.get("history")[-1]
        self.assertIsNotNone(last_history_entry.get("parameters")[0].get("destination_columns"))

    @unittest.skip("Temporarily skipping this test case.This testcase needs llm connection.")
    def test_mongodb_update(self):
        data = {
        "input_text": "calculate sum of id column",
        "chat_id": "65cb43f2007a5f38718b9d6a",
        "user_id": "680a2d804c83f84f2211b148"
        #user_id": "6619156aa5f4c5c1b01e4d07",
        }
        response = self.app.post('/api/v1/completion',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        actual_output = response.json
        self.assertTrue(actual_output['success'])

    def test_api_get_pipeline_history_with_no_history(self):
        response = self.app.get('/api/v1/pipeline_history?chat_id=67e6a27e99c63c42a69d36ea',
                                headers={'Authorization': self.valid_token}
                                )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("connections" in response.json)

    def test_jwt_token_generation_with_expiry_date(self):
        data = {
            "email": "reshmab2511@gmail.com",
            "token_name": "jwt_token",
            "expiry_date": '2027-08-07'
        }
        response = self.app.post('/api/v1/generate_api_key',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])

    def test_jwt_token_generation_without_expiry_date(self):
        data = {
            "email": "reshmab2511@gmail.com",
            "token_name": "jwt_token",
        }
        response = self.app.post('/api/v1/generate_api_key',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])
    
    def test_jwt_token_generation_with_invalid_user_email(self):
        data = {
            "email": "resh@gmail.com",
            "token_name": "jwt_token",
            "expiry_date": '2027-04-17'
        }
        response = self.app.post('/api/v1/generate_api_key',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"success": False, "msg": "Invalid user credentials"})

    def test_jwt_token_generation_with_expiry_date_in_invalid_format(self):
        data = {
            "email": "reshmab2511@gmail.com",
            "token_name": "jwt_token",
            "expiry_date": '2027-22-04'
        }
        response = self.app.post('/api/v1/generate_api_key',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"success": False, "msg": "Invalid expiry_date format. Expected YYYY-MM-DD."})
    
    def test_get_data_api_with_valid_api_key(self):
        api_key = JWTAuthentication().encode("reshmab2511@gmail.com", "67ea863595ba00fa2ba16f7a",14400)
        response = self.app.get('/api/v1/get_data/66729ec22ee1491c32b05b53',
                                headers={'Authorization':api_key , 'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        assert response.json["chats"]["history"] != None
    
    def test_get_api_key(self):
        response = self.app.get('/api/v1/generate_api_key?user_id=67ea863595ba00fa2ba16f7b',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(response.status_code, 200)
    
    def test_generate_api_key_returns_success_when_no_existing_api_data(self):
        response = self.app.get('/api/v1/generate_api_key?user_id=67ea863595ba00fa2ba16f7a',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(response.status_code, 200)

    def test_get_api_key_with_invalid_user_id(self):
        response = self.app.get('/api/v1/generate_api_key?user_id=67ea8635rt6a00fa2ba16f7b',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertFalse(actual_output['success'])
        self.assertEqual(response.status_code, 400)
   
    def test_delete_api_key_with_invalid_user_id(self):
        response = self.app.delete('/api/v1/generate_api_key?user_id=67ea866a00fa2ba16f7b',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertFalse(actual_output['success'])
        self.assertEqual(response.status_code, 400)

    def test_delete_api_key(self):
        response = self.app.delete('/api/v1/generate_api_key?user_id=67ea863595ba00fa2ba16f7b',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(response.status_code, 200)
    
    
    def test_post_api_login_with_existing_user(self):
        data = {"email": "reshmab2511@gmail.com", "password": "Akku@2599"}
        response = self.app.post('/api/v1/login',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertIsNotNone(actual_output['userid'])
        self.assertIsNotNone(actual_output['token'])

    @unittest.skip("Temporarily skipping this test case")
    def test_new_user_registration(self):
        data = {"name": "User_name","family_name":"family_name","email": "user@gmail.com","password": "password","confirm": "password"}
        response = self.app.post('/api/v1/register',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])
    
    def test_post_api_login_with_existing_user_with_api_key(self):
        data = {"email": "aparna2511@gmail.com", "password": "Akku@2599"}
        response = self.app.post('/api/v1/login',
                                 headers={'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertIsNotNone(actual_output['userid'])
        self.assertIsNotNone(actual_output['token'])

    def test_api_integration_testing(self):
        data = {"email": "reshmab2511@gmail.com", "password": "Akku@2599"}
        response = self.app.post('/api/v1/login',
                                 headers={'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        token = actual_output['token']

        data = {
            "email": "reshmab2511@gmail.com",
            "token_name": "jwt_token",
            "expiry_date": '2027-05-02'
        }
        response = self.app.post('/api/v1/generate_api_key',
                                 headers={'Authorization': token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])

        data = {"email": "reshmab2511@gmail.com", "password": "Akku@2599"}
        response = self.app.post('/api/v1/login',
                                 headers={'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        actual_output = response.json
        self.assertTrue(actual_output['success'])

        response = self.app.get('/api/v1/generate_api_key?user_id=67ea863595ba00fa2ba16f7a',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(response.status_code, 200)

        response = self.app.delete('/api/v1/generate_api_key?user_id=67ea863595ba00fa2ba16f7a',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        actual_output = response.json
        self.assertTrue(actual_output['success'])
        self.assertEqual(response.status_code, 200)
    
    @unittest.skip("Temporarily skipping this test case")
    def test_llama_api_server(self):
        data = {
        "input_text": "calculate sum of id column",
        "chat_id": "65cb43f2007a5f38718b9d6a",
        "user_id": "680a2d804c83f84f2211b148"
        #user_id": "6619156aa5f4c5c1b01e4d07",
        }
        response = self.app.post('/api/v1/completion',
                                 headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'},
                                 data=json.dumps(data)
                                 )
        actual_output = response.json
        self.assertTrue(actual_output['success'])
    
    def test_get_information_api_returns_loaded_files_with_connection_ids(self):
        response = self.app.get('/api/v1/get_information?chat_id=6823336a1707152fac937878',
                                headers={'Authorization': self.valid_token, 'Content-Type': 'application/json'})
        loaded_files = response.json["chats"]["loaded_files"]
        id = any('_id' in file for file in loaded_files)

        self.assertTrue(id, "No '_id' found in any loaded_files entry")
        self.assertEqual(response.status_code, 200)
        
    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_data_loads_api_for_connection_id_update_in_cache_collection(self):
        data = {
            "filesInfo": [
                {
                    "source": "database",
                    "details": {
                        "connection_id": "682334a52d5cf8468ae56058",
                        "chat_id": "6823336a1707152fac937878",
                        "file_name": "",
                        "database_name": "postgres",
                        "catalog": {
                            "information_schema.sql_features": []
                        },
                        "source_id": ""
                    }
                }
            ]
        }

        response = self.app.post(
            '/api/v1/data_loads',
            data=json.dumps(data),
            headers={
                'Authorization': self.valid_token,
                'Content-Type': 'application/json'
            }
        )

        actual_output = response.json
        self.assertEqual(actual_output['success'], True)


if __name__ == '__main__':
    unittest.main()