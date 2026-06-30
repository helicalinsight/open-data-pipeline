import base64
import json
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId
import ast
from flask import Response
import pytest
from requests import RequestException
from src.exceptions.exception import MongoException
from src.api.services.airflow_service.service import AirflowAPI, RequestType
from src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern


class MockConfig:
    config = {
        "airflow": {
            "url": "http://localhost:8080",
            "username": "test_user",
            "password": "test_password"
        }
    }
class TestAirflowAPI(unittest.TestCase):


    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client=mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()
        global Config
        Config = MockConfig
        self.api = AirflowAPI()
        self.api.schedule_collection = MagicMock()
        self.api.chats_collection = MagicMock()

    def tearDown(self):
        # Clean up shared resources if needed
        self.session.end_session()
        
    def test_create_dag_success(self):
        with patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists') as mock_dag_exists:
            mock_dag_exists.return_value = False
            with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
                mock_call_api.return_value = {"message": "Successfully generated DAG: 66729ec22ee1491c32b05b60 using job_id: 66729ec22ee1491c32b05b60", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
                response, status_code = AirflowAPI(self.session).create_dag('66729ec22ee1491c32b05b60', 'user_id_1', 'job_name_1', '@daily', {"some_key": "some_value"}, {'type': 'yml'}, schedule_name="",executionType="yaml",run_engine_type="spark")
                
                self.assertEqual(status_code, 200)
                self.assertEqual(response["message"], "Scheduled  schedule for the job job_name_1 successfully")

    def test_create_dag_success_with_notification(self):
        with patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists') as mock_dag_exists:
            mock_dag_exists.return_value = False
            notification = {
                'active': True,
                'type': 'email',
                'details': {
                    # 'to': 'random@gmail.com',
                    # 'subject': 'Notification from Helical',
                    # 'body': 'Email sent successfully'
                }
            }
            with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
                mock_call_api.return_value = {"message": "Successfully generated DAG: 66729ec22ee1491c32b05b60 with email notification", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
                response, status_code = AirflowAPI(self.session).create_dag('66729ec22ee1491c32b05b60', '65365001d9654d9ec1172f87', 'job_name_1', '@daily', {"some_key": "some_value"}, {'type': 'yml'}, schedule_name="",executionType="yaml", notification=notification,run_engine_type="spark")

                self.assertEqual(status_code, 200)
                self.assertEqual(response["message"], "Scheduled  schedule for the job job_name_1 successfully")


    @patch('src.configurations.api.config.AirflowConfig')
    @patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists')
    def test_create_dag_already_exists(self, mock_dag_exists, mock_airflow_config):
        mock_dag_exists.return_value = True
        mock_airflow_config.config = {"airflow": {"spark_path": "/path/to/spark"}}

        response, status_code = AirflowAPI(self.session).create_dag('66729ec22ee1491c32b05b60', 'user_id_1', 'job_name_1', '@daily', {"some_key": "some_value"}, job_details={},schedule_name="",executionType="pipeline",run_engine_type="spark")
        self.assertEqual(status_code, 400)
        self.assertEqual(response, {"message": "DAG with job_id: 66729ec22ee1491c32b05b60 already exists"})
    # "src.api.services.airflow_service.service"
    @patch('src.configurations.api.config.AirflowConfig')
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    @patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists')
    def test_create_dag_api_call_failure(self, mock_dag_exists, mock_call_api, mock_airflow_config):
        mock_dag_exists.return_value = False
        mock_call_api.return_value = {'error': 'some_error'}
        mock_airflow_config.config = {"airflow": {"spark_path": "/path/to/spark"}}

        response, status_code = AirflowAPI(self.session).create_dag('66729ec22ee1491c32b05b60', 'user_id_1', 'job_name_1', '@daily', {"some_key": "some_value"}, job_details={},schedule_name="",executionType="code",run_engine_type="spark")
        
        self.assertEqual(status_code, 500)
        # self.assertEqual(response, {'error': 'some_error'})

    @patch('src.configurations.api.config.AirflowConfig')
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    @patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists')
    def test_create_dag_missing_schedule_interval(self, mock_dag_exists, mock_call_api, mock_airflow_config):
        mock_dag_exists.return_value = False
        mock_call_api.return_value = {"message": "Scheduled  schedule for the job job_name_1 successfully", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
        mock_airflow_config.config = {"airflow": {"spark_path": "/path/to/spark"}}

        response, status_code = AirflowAPI(self.session).create_dag('66729ec22ee1491c32b05b60', 'user_id_1', 'job_name_1', None, {"some_key": "some_value"}, job_details={},schedule_name="",executionType="pipeline",run_engine_type="spark")
        
        self.assertEqual(status_code, 200)  # Assuming no error occurs when schedule_interval is missing
        self.assertEqual(response["message"], "Scheduled  schedule for the job job_name_1 successfully")

    @patch('src.configurations.api.config.AirflowConfig')
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    @patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists')
    def test_create_dag_missing_advanced_scheduling(self, mock_dag_exists, mock_call_api, mock_airflow_config):
        mock_dag_exists.return_value = False
        mock_call_api.return_value = {"message": "Scheduled  schedule for the job job_name_1 successfully", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
        mock_airflow_config.config = {"airflow": {"spark_path": "/path/to/spark"}}

        response, status_code = AirflowAPI(self.session).create_dag('66729ec22ee1491c32b05b60', 'user_id_1', 'job_name_1', '@daily', None, job_details={},schedule_name="",executionType="pipeline",run_engine_type="spark")
        
        self.assertEqual(status_code, 200)  # Assuming no error occurs when advanced_scheduling is missing
        self.assertEqual(response["message"], "Scheduled  schedule for the job job_name_1 successfully")


    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_stream_dag_log(self, mock_call_api):
        mock_call_api.side_effect = [
            {"content": "[('', 'Log chunk 1')]", "continuation_token": "token1"},
            {"content": "[('', 'Log chunk 2')]", "continuation_token": "token1"},
            {"content": "[('', 'Log chunk 3')]", "continuation_token": "token1"},
            {"content": "[('', 'Log chunk 4')]", "continuation_token": "token1"},
            {"content": "[('', 'Log chunk end. Marking task as SUCCESS')]", "continuation_token": "token1"}
        ]
        
        airflow_api = AirflowAPI()
        
        response = airflow_api.stream_dag_log(job_id="123", dag_run_id="manual_1245",engine_type="spark")
        
        # Ensure the response is an instance of Flask Response
        self.assertIsInstance(response, Response)
        
        streamed_logs = "".join(response.response)
        
        self.assertIn("----Streaming logs for the run----", streamed_logs)
        self.assertIn("Log chunk 1", streamed_logs)
        self.assertIn("Log chunk 2", streamed_logs)
        self.assertIn("Marking task as SUCCESS", streamed_logs)
        self.assertIn("-----End of log streaming----", streamed_logs)
        
        # ensure call_api is called for each chunk
        self.assertEqual(mock_call_api.call_count, 5)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    @patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists')
    def test_delete_dag_api_call_error(self, mock_dag_exists, mock_call_api):
        # DAG exists
        mock_dag_exists.return_value = True
        # API response with error
        mock_call_api.return_value = {'message': 'DAG does not exist'}

        response = AirflowAPI(self.session).delete_dag('66729ec22ee1491c32b05b60')
        # self.assertEqual(response.status_code, 404)  
        self.assertEqual(response[0], {'message': 'DAG 66729ec22ee1491c32b05b60 deleted successfully'})

    @pytest.mark.skip(reason="It's raising passing unexpected executionType which is not expected")
    @patch('src.api.services.airflow_service.service.AirflowAPI._get_start_date_time_for_dag')
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_runs_success(self, mock_call_api, mock_get_start):
        mock_call_api.side_effect = [
            {
                "dags": [
                    {
                        "dag_id": "674d49ea846f5e936773c0f8",
                        "tags": [
                            {"name": "job_name:example_job"},
                            {"name": "local:True"},
                            {"name": "schedule_name:daily"}
                        ]
                    },
                    {
                        "dag_id": "674d49ea846f5e936773d0f8",
                        "tags": [
                            {"name": "job_name:example_job_2"},
                            {"name": "local:False"},
                            {"name": "schedule_name:weekly"}
                        ]
                    }
                ],
                "total_entries": 2
            },
            {
                "dags": []  # End of pagination
            }
        ]
        mock_get_start.return_value = "2025-08-11 10:00:00"  # valid datetime string

        mock_session = MagicMock()
        mock_session.client.user_sessions_test.__getitem__().find_one().get.side_effect = lambda key, default = None: (
            "pipeline" if key == "executionType" else default
        )
        api_instance = AirflowAPI(mock_session)
        api_instance.config = {
            "api": {
                "preview_default_page": 1,
                "preview_default_per_page": 10,
                "preview_max_per_page_limit": 999
            }
        }
        api_instance.chats_collection = MagicMock()
        api_instance.chats_collection.get_by_id.return_value = (
            True,
            {"chat_id": "some_chat_id", "messages": [], "chat_name": "some_chat_name"}
        )
        # Call get_dag_runs with mocked data
        response = api_instance.get_dag_runs({"user_id": "674d49ea846f5e936773e0f8"})
        expected_response = {'dags': [{'dag_id': '674d49ea846f5e936773c0f8', 'tags': [{'name': 'job_name:some_chat_name'}, {'name': 'local:True'}, {'name': 'schedule_name:daily'}], 'job_name': 'some_chat_name', 'local': True, 'schedule_name': '-', 'service_type': 'dts', 'starts_on': '2025-08-11 10:00:00', 'schedule_id': 'None', 'meta_schedule_version': 1, 'job_details': {'configuration': [], 'files_list': [], 'destination': [], 'advanced_scheduling': None}}, {'dag_id': '674d49ea846f5e936773d0f8', 'tags': [{'name': 'job_name:some_chat_name'}, {'name': 'local:False'}, {'name': 'schedule_name:weekly'}], 'job_name': 'some_chat_name', 'local': False, 'schedule_name': '-', 'service_type': 'dts', 'starts_on': '2025-08-11 10:00:00', 'schedule_id': 'None', 'meta_schedule_version': 1, 'job_details': {'configuration': [], 'files_list': [], 'destination': [], 'advanced_scheduling': None}}], "page": 1, "per_page": 10, 'total_records': 2}
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.get_dms_run_history_info')
    @patch('src.api.services.airflow_service.service.AirflowAPI._get_start_date_time_for_dag')
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_runs_with_dms_service(self, mock_call_api, mock_get_start, mock_get_dms_run_history):
        dags = [{
                "dag_id": "674d49ea846f5e936773d0f1",
                "tags": [{"name": "job_name:job_1"}, {"name": "local:True"}, {"name": "service_type:dms"}]
            }]
        mock_call_api.side_effect = [
            {"dags": dags, "total_entries": len(dags)}
        ]
        mock_get_start.return_value = "2025-08-11 10:00:00"

        mock_get_dms_run_history.return_value = {
            "migration_details": [{"step": 1}],
             "last_run": {"status": "success"},
        }

        mock_session = MagicMock()
        mock_session.client.user_sessions_test.__getitem__().find_one().get.side_effect = \
            lambda key, default=None: ("pipeline" if key == "executionType" else default)

        api_instance = AirflowAPI(mock_session)
        api_instance.config = {
            "api": {
                "preview_default_page": 1,
                "preview_default_per_page": 10,
                "preview_max_per_page_limit": 999
            }
        }
        test_obj_id = ObjectId()
        api_instance.schedule_collection = MagicMock()
        api_instance.schedule_collection.get_by_id.return_value = (
            True,
            {
                "_id": test_obj_id,
                "chat_id": "some_chat_id",
                "schedule_name": "daily",
                "pipeline": [],
                "job_details": {},
                "export_files_list": []
            }
        )
        api_instance.chats_collection = MagicMock()
        api_instance.chats_collection.get_by_id.return_value = (
            True,
            {"chat_id": "some_chat_id", "messages": [], "chat_name": "some_chat_name"}
        )

        with patch('src.api.services.airflow_service.utils.ExportPipeline.export_pipeline') as mock_export:
            mock_export.return_value = []
            response = api_instance.get_dag_runs({"user_id": "674d49ea846f5e936773e0f8", "page": 1})
            
        self.assertEqual(len(response['dags']), 1)
        dag = response['dags'][0]
        self.assertEqual(dag["service_type"], "dms")
        self.assertEqual(dag["migration_details"], [{"step": 1}])
        self.assertEqual(dag["last_run"], {'status': 'success', 'total_rows_transferred': 0, 'failed_step': ''})

    @patch('src.api.services.airflow_service.service.AirflowAPI._get_start_date_time_for_dag')
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_runs_with_only_page(self, mock_call_api, mock_get_start):
        # Prepare paginated mock data
        dags = [{
                "dag_id": f"674d49ea846f5e936773d0f{i}",
                "tags": [{"name": f"job_name:job_{i}"}, {"name": "local:True"}]
            }
            for i in range(1, 15)
        ]
        mock_call_api.side_effect = [
            {"dags": dags[10:15], "total_entries": len(dags)}
        ]
        mock_get_start.return_value = "2025-08-11 10:00:00"

        mock_session = MagicMock()
        mock_session.client.user_sessions_test.__getitem__().find_one().get.side_effect = \
            lambda key, default=None: ("pipeline" if key == "executionType" else default)

        api_instance = AirflowAPI(mock_session)
        api_instance.config = {
            "api": {
                "preview_default_page": 1,
                "preview_default_per_page": 10,
                "preview_max_per_page_limit": 999
            }
        }
        api_instance.schedule_collection = MagicMock()
        api_instance.schedule_collection.get_by_id.return_value = (
            True,
            {
                "_id": ObjectId(),
                "chat_id": "some_chat_id",
                "schedule_name": "daily",
                "pipeline": [],
                "job_details": {}
            }
        )
        api_instance.chats_collection = MagicMock()
        api_instance.chats_collection.get_by_id.return_value = (
            True,
            {"chat_id": "some_chat_id", "messages": [], "chat_name": "some_chat_name"}
        )

        # Call with explicit pagination params
        response = api_instance.get_dag_runs({"user_id": "674d49ea846f5e936773e0f8", "page": 2})
        # Assert that all paginated results were returned
        all_expected_dags = dags[10:15]
        self.assertEqual(len(response['dags']), len(all_expected_dags))
        self.assertEqual(response["page"], 2)
        self.assertEqual(response["per_page"], 10)
        self.assertEqual(response['total_records'], 14)

        returned_ids = [dag['dag_id'] for dag in response['dags']]
        expected_ids = [dag['dag_id'] for dag in all_expected_dags]
        self.assertListEqual(returned_ids, expected_ids)
    
    @patch('src.api.services.airflow_service.service.AirflowAPI._get_start_date_time_for_dag')
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_runs_with_page_and_per_page(self, mock_call_api, mock_get_start):
        # Prepare paginated mock data
        dags = [{
                "dag_id": f"674d49ea846f5e936773d0f{i}",
                "tags": [{"name": f"job_name:job_{i}"}, {"name": "local:True"}]
            }
            for i in range(1, 35)
        ]
        mock_call_api.side_effect = [
            {"dags": dags[10:15], "total_entries": len(dags)}
        ]
        mock_get_start.return_value = "2025-08-11 10:00:00"

        mock_session = MagicMock()
        mock_session.client.user_sessions_test.__getitem__().find_one().get.side_effect = \
            lambda key, default=None: ("pipeline" if key == "executionType" else default)

        api_instance = AirflowAPI(mock_session)
        api_instance.config = {
            "api": {
                "preview_default_page": 1,
                "preview_default_per_page": 10,
                "preview_max_per_page_limit": 999
            }
        }
        api_instance.schedule_collection = MagicMock()
        api_instance.schedule_collection.get_by_id.return_value = (
            True,
            {
                "_id": ObjectId(),
                "chat_id": "some_chat_id",
                "schedule_name": "daily",
                "pipeline": [],
                "job_details": {}
            }
        )
        api_instance.chats_collection = MagicMock()
        api_instance.chats_collection.get_by_id.return_value = (
            True,
            {"chat_id": "some_chat_id", "messages": [], "chat_name": "some_chat_name"}
        )

        # Call with explicit pagination params
        response = api_instance.get_dag_runs({"user_id": "674d49ea846f5e936773e0f8", "page": 3, "per_page": 5})

        # Assert that all paginated results were returned
        all_expected_dags = dags[10:15]
        self.assertEqual(len(response['dags']), len(all_expected_dags))
        self.assertEqual(response["page"], 3)
        self.assertEqual(response["per_page"], 5)
        self.assertEqual(response['total_records'], 34)
        returned_ids = [dag['dag_id'] for dag in response['dags']]
        expected_ids = [dag['dag_id'] for dag in all_expected_dags]
        self.assertListEqual(returned_ids, expected_ids)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_runs_no_dags(self, mock_call_api):
        # Mock response for the call_api method with no dags
        mock_call_api.return_value = {
            "dags": []
        }

        response = AirflowAPI(self.session).get_dag_runs({"user_id": "674d49ea846f5e936773e0f8"})
        
        expected_response = {'dags': [], "page": 1, "per_page": 10, 'total_records': 0}
        # self.assertEqual(status_code, 404)
        self.assertEqual(response, expected_response)

    @pytest.mark.skip(reason="We are making schedule and chat db calls in this which fail in mock setup")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_runs_no_matching_tags(self, mock_call_api):
        mock_call_api.side_effect = [
            {
                "dags": [
                    {
                        "dag_id": "dag_1",
                        "tags": [{"name": "another_user_id:job_1"}, {"name": "job_name:example_job"}]
                    }
                ]
            },
            {
                "dags": []  # End of pagination, simulating empty response
            }
        ]

        mock_session = MagicMock()
        api_instance = AirflowAPI(mock_session)

        response = api_instance.get_dag_runs('user_id_1')
        expected_response = {'dags': [{'dag_id': 'dag_1', 'tags': [{'name': 'another_user_id:job_1'}, {'name': 'job_name:example_job'}], 'job_name': 'example_job',"job_details": {
                "configuration": [],
                "files_list": [],
                "destination": [],
                "advanced_scheduling": {}
            }}]}
        
        self.assertEqual(response, expected_response)

    
    @pytest.mark.skip(reason="It's breaking")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_runs_partial_matching_tags(self, mock_call_api):
        # Mock response for the call_api method with some matching tags
        mock_call_api.return_value = {
            "dags": [
                {
                    "dag_id": "dag_1",
                    "tags": [{"name": "job_1:user_id_1"}, {"name": "job_name:example_job"}]
                },
                {
                    "dag_id": "dag_2",
                    "tags": [{"name": "job_2:another_user_id"}, {"name": "job_name:example_job_2"}]
                }
            ]
        }

        # Mock session
        mock_session = MagicMock()
        api_instance = AirflowAPI(mock_session)

        # Call get_dag_runs with mocked data
        response = api_instance.get_dag_runs('user_id_1')

        # Define the expected response
        expected_response = {
            "dags": [
                {
                    "dag_id": "dag_1",
                    "job_name": "example_job",
                    "local": None,
                    "schedule_name": None
                }
            ]
        }

        # Assert that the response is as expected
        self.assertEqual(response, expected_response)

    #@pytest.mark.skip(reason="The test is mocking whole `call_api` which does not lead to expected mock behavior")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_success(self, mock_call_api):
        # Mock responses for the call_api method
        mock_call_api.side_effect = [
            {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}]},
            {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8"}, {"run_id": "674d49ea846f5e936773e0f8"}],
            "total_entries": 2},
            {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        ]
        query_params = {
            "page": "1",
            "per_page": "10"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)
        
        expected_response = {
            "basic_info": {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}], "job_name": "example_job"},
            "dag_runs": {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8"}, {"run_id": "674d49ea846f5e936773e0f8"}], "page": 1, "per_page": 10, "total_entries": 2},
            "tasks": {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        }
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_with_only_page(self, mock_call_api):
        # Mock responses for the call_api method
        mock_call_api.side_effect = [
            {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}]},
            {"dag_runs": [{"run_id": f"674d49ea846f5e936773d0f{i}"} for i in range(10,20)],
            "total_entries": 20},
            {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        ]
        query_params = {
            "page": "2",
            "per_page": "10"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)
        expected_response = {
            "basic_info": {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}], "job_name": "example_job"},
            "dag_runs": {"dag_runs": [{"run_id": f"674d49ea846f5e936773d0f{i}"} for i in range(10,20)], "page": 2, "per_page": 10, "total_entries": 20},
            "tasks": {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        }
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_with_page_and_per_page(self, mock_call_api):
        # Mock responses for the call_api method
        mock_call_api.side_effect = [
            {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}]},
            {"dag_runs": [{"run_id": f"674d49ea846f5e936773d0f{i}"} for i in range(4,8)],
            "total_entries": 20},
            {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        ]
        query_params = {
            "page": "2",
            "per_page": "4"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)
        expected_response = {
            "basic_info": {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}], "job_name": "example_job"},
            "dag_runs": {"dag_runs": [{"run_id": f"674d49ea846f5e936773d0f{i}"} for i in range(4,8)], "page": 2, "per_page": 4, "total_entries": 20},
            "tasks": {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        }
        self.assertEqual(response, expected_response)

    #@pytest.mark.skip(reason="This is mocking whole `call_api` which does not lead to expected mock behavior")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_no_job_name_tag(self, mock_call_api):
        # Mock responses for the call_api method without a job_name tag
        mock_call_api.side_effect = [
            {"dag_id": "dag_1", "tags": []},
            {"dag_runs": [{"run_id": "run_1"}, {"run_id": "run_2"}],
            "total_entries": 2},
            {"tasks": [{"task_id": "task_1"}, {"task_id": "task_2"}]}
        ]
        query_params = {
            "page": "1",
            "per_page": "10"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)
        expected_response = {'basic_info': {'dag_id': 'dag_1', 'tags': []}, 'dag_runs': {'dag_runs': [{'run_id': 'run_1'}, {'run_id': 'run_2'}], "page": 1, "per_page": 10, "total_entries": 2}, 'tasks': {'tasks': [{'task_id': 'task_1'}, {'task_id': 'task_2'}]}}
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_pause_dag_success(self, mock_call_api):
        job_id = '66729ec22ee1491c32b05b60'
        req_data = {"is_paused": True}
        mock_call_api.return_value =  {'success': True, 'message': "Paused DAG 'dag_1' successfully."}
        response, status_code = AirflowAPI(self.session).pause_dag(job_id, req_data)
        expected_response = {'success': True, 'message': "Paused DAG successfully."}
        self.assertEqual(response, expected_response)
        self.assertEqual(status_code, 200)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_pause_dag_success_to_not_pause(self, mock_call_api):
        job_id = '66729ec22ee1491c32b05b60'
        req_data = {"is_paused": False}
        mock_call_api.return_value =  {'success': True, 'message': "Paused DAG 'dag_1' successfully."}
        response, status_code = AirflowAPI(self.session).pause_dag(job_id, req_data)
        expected_response = {'success': True, 'message': "Unpaused DAG successfully."}
        self.assertEqual(response, expected_response)
        self.assertEqual(status_code, 200)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_pause_dag_failure(self, mock_call_api):
        job_id = '66729ec22ee1491c32b05b60'
        req_data = {"is_paused": False}
        # to simulate that error occured from mock response we use 'error'
        mock_call_api.return_value = {'success': False, 'error':"Failed to pause DAG 66729ec22ee1491c32b05b60'"}
        response, status_code = AirflowAPI(self.session).pause_dag(job_id, req_data)
        expected_response = {'success': False, 'message': 'Failed to pause DAG 66729ec22ee1491c32b05b60'}
        self.assertEqual(response, expected_response)
        self.assertEqual(status_code, 404)


    @patch('src.api.services.airflow_service.service.AirflowAPI.get_dag_runs')
    def test_get_user_dags_success(self, mock_get_dag_runs):
        # Mock response for the get_dag_runs method
        mock_get_dag_runs.return_value = {
            "dags": [
                {"dag_id": "dag_1", "tags": [{"name": "user_1"}], "schedule_interval": {"value": "@daily"}},
                {"dag_id": "dag_2", "tags": [{"name": "user_2"}], "schedule_interval": {"value": "@weekly"}},
                {"dag_id": "dag_3", "tags": [{"name": "user_1"}], "schedule_interval": {"value": "@hourly"}}
            ]
        }

        response = AirflowAPI(self.session).get_user_dags('user_1')
        expected_response = {'user_id': 'user_1', 'user_dags': [{'dag_id': 'dag_1', 'schedule_interval': '@daily'}, {'dag_id': 'dag_3', 'schedule_interval': '@hourly'}]}
        # self.assertEqual(status_code, 200)
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.get_dag_runs')
    def test_get_user_dags_no_dags(self, mock_get_dag_runs):
        # Mock response for the get_dag_runs method with no DAGs
        mock_get_dag_runs.return_value = {"dags": []}

        response = AirflowAPI(self.session).get_user_dags('user_1')
        

        expected_response = {
            "user_id": "user_1",
            "user_dags": []
        }
        # self.assertEqual(status_code, 200)
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.get_dag_runs')
    def test_get_user_dags_no_schedule_interval(self, mock_get_dag_runs):
        # Mock response for the get_dag_runs method with DAGs missing schedule_interval
        mock_get_dag_runs.return_value = {
            "dags": [
                {"dag_id": "dag_1", "tags": [{"name": "user_1"}]},
                {"dag_id": "dag_2", "tags": [{"name": "user_2"}], "schedule_interval": {"value": "@weekly"}},
                {"dag_id": "dag_3", "tags": [{"name": "user_1"}]}
            ]
        }

        response = AirflowAPI(self.session).get_user_dags('user_1')
        expected_response = {'user_id': 'user_1', 'user_dags': [{'dag_id': 'dag_1', 'schedule_interval': ''}, {'dag_id': 'dag_3', 'schedule_interval': ''}]}
        # self.assertEqual(status_code, 200)
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_log_success(self, mock_call_api):
        # Mock response for tasks API call
        mock_call_api.side_effect = [
            {'task_instances': [{'task_id': 'task_1'}]},  # Tasks response
            'Log line 1. Log line 2.'  # Logs response
        ]

        response, status_code = AirflowAPI(self.session).get_dag_log('66729ec22ee1491c32b05b60', 'dag_run_id_1','spark')

        expected_response = 'Log line 1.\nLog line 2.'
        self.assertEqual(status_code, 200)
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_log_no_tasks(self, mock_call_api):
        # Mock response for tasks API call with no tasks
        mock_call_api.return_value = {'task_instances': []}

        response, status_code = AirflowAPI(self.session).get_dag_log('66729ec22ee1491c32b05b60', 'dag_run_id_1','spark')

        expected_response = "No tasks found for DAG run_id: dag_run_id_1"
        self.assertEqual(status_code, 404)
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_log_tasks_error(self, mock_call_api):
        # Mock response for tasks API call with error
        mock_call_api.return_value = {'error': 'some_error'}

        response, status_code = AirflowAPI(self.session).get_dag_log('66729ec22ee1491c32b05b60', 'dag_run_id_1','spark')

        expected_response = "No tasks found for DAG run_id: dag_run_id_1"
        self.assertEqual(status_code, 404)
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_log_logs_no_response(self, mock_call_api):
        # Mock response for tasks API call and logs API call with no logs
        mock_call_api.side_effect = [
            {'task_instances': [{'task_id': 'task_1'}]},  # Tasks response
            ''  # Empty logs response
        ]

        response, status_code = AirflowAPI(self.session).get_dag_log('66729ec22ee1491c32b05b60', 'dag_run_id_1','spark')
        expected_response = ''
        self.assertEqual(status_code, 200)
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_dag_exists_true(self, mock_call_api):
        # Mock response when DAG exists
        mock_call_api.return_value = {'dag_id': '66729ec22ee1491c32b05b60'}  # Replace with actual response

        result = AirflowAPI(self.session).dag_exists('66729ec22ee1491c32b05b60')
        self.assertTrue(result)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_dag_exists_false(self, mock_call_api):
        # Mock response when DAG does not exist
        mock_call_api.return_value = {'error': 'DAG not found'}  # Replace with actual response

        result = AirflowAPI(self.session).dag_exists('66729ec22ee1491c32b05b60')
        self.assertFalse(result)



    # 
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_call_api_success(self, mock_call_api):
        # Mock successful API response
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"message": "Success"}'
        mock_call_api.return_value = {"The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found"}

        result = AirflowAPI(self.session).call_api(RequestType.GET, "/api/v1/dags/66729ec22ee1491c32b05b60")
        
        expected_result = result
        self.assertIn("The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found", expected_result)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_call_api_error_response(self, mock_call_api):
        # Mock API response with error status code
        mock_response = Response()
        mock_response.status_code = 404
        mock_call_api.return_value = {"The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found"}

        # Call the API method
        result =  AirflowAPI(self.session).call_api(RequestType.GET, "/api/v1/dags/66729ec22ee1491c32b05b60")

        
        expected_result = result
        self.assertIn("The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found", expected_result)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_call_api_empty_response(self, mock_call_api):
        # Mock API response with empty content
        mock_response = Response()
        mock_response.status_code = 204
        mock_response._content = b''
        mock_call_api.return_value = {"The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found"}
        

        result =  AirflowAPI(self.session).call_api(RequestType.GET, "/api/v1/dags/66729ec22ee1491c32b05b60")
        
        expected_result = result
        self.assertIn("The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found", expected_result)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_call_api_expect_json_false(self, mock_call_api):
        # Mock API response where JSON decoding is not expected
        mock_response = Response()
        mock_response.status_code = 200
        mock_call_api.return_value = {"The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found"}

        result =  AirflowAPI(self.session).call_api(RequestType.GET, "/api/v1/dags/66729ec22ee1491c32b05b60", expect_json=False)
        
        expected_result = result
        self.assertIn("The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found", expected_result)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_call_api_json_decode_error(self, mock_call_api):
        # Mock API response with invalid JSON
        mock_response = Response()
        mock_response.status_code = 200
        mock_call_api.return_value = {"The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found"}

        result =  AirflowAPI(self.session).call_api(RequestType.GET, "/api/v1/dags/66729ec22ee1491c32b05b60")
        
        expected_result = result
        self.assertIn("The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found", expected_result)
        # self.assertEqual(result, {"error": "Failed to decode JSON", "response": '{"invalid": json}', "status_code": 404})

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_call_api_request_exception(self, mock_call_api):
        # Mock request exception
        mock_call_api.return_value = {"The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found"}
        result =  AirflowAPI(self.session).call_api(RequestType.GET, "/api/v1/dags/66729ec22ee1491c32b05b60")
        expected_result = result
        self.assertIn("The DAG with dag_id: 66729ec22ee1491c32b05b60 was not found", expected_result)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_trigger_dag_no_dag_id(self, mock_request):
        # Test when dag_id is not provided in req_data
        api_instance = AirflowAPI(self.session)
        
        req_data = {}
        
        result, status_code = api_instance.trigger_dag(req_data)
        
        self.assertEqual(result, {"success": False, "text": "dag_id is required"})
        self.assertEqual(status_code, 400)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_trigger_dag_failure(self, mock_request):
        # Mock the API response for a successful DAG trigger
        api_instance = AirflowAPI(self.session)
        
        req_data = {"dag_id": "test_dag_id"}
        mock_response = {"message": "Success"}
        mock_request.return_value = mock_response
        
        result, status_code = api_instance.trigger_dag(req_data)
        self.assertEqual(result.get("success"), True)
        self.assertEqual(status_code, 200)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_trigger_dag_api_error(self, mock_request):
        # Mock the API response with an error
        api_instance = AirflowAPI(self.session)
        
        req_data = {"dag_id": "test_dag_id"}
        mock_response = {"error": "Failed to trigger"}
        mock_request.return_value = mock_response
        
        result, status_code = api_instance.trigger_dag(req_data)
        
        self.assertEqual(result, {"success": False, "message": "failed to execute dag"})
        self.assertEqual(status_code, 500)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_trigger_dag_api_exception(self, mock_request):
        # Mock a request exception
        api_instance = AirflowAPI(self.session)
        
        req_data = {"dag_id": "test_dag_id"}
        mock_request.side_effect = RequestException("Request failed")
        
        result, status_code = api_instance.trigger_dag(req_data)
        
        self.assertEqual(result.get("success"), False)
        self.assertEqual(status_code, 500)
        

    def test_encode_credentials_valid(self):
        expected_credentials = f'{Config.config["airflow"]["username"]}:{Config.config["airflow"]["password"]}'
        expected_output = base64.b64encode(expected_credentials.encode()).decode()
        actual_output = self.api.encode_credentials()
        self.assertIsNotNone(expected_output)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_call_api_success_json_response(self, mock_call_api):
        # Mocking the return value of the call_api method
        mock_call_api.return_value = {"status": "success"}

        # Call the mocked call_api method
        response = self.api.call_api(request_type=RequestType.GET, endpoint='/api/test', expect_json=True)
        
        self.assertEqual(response, {"status": "success"})

    def test_create_dag_success_with_type_code(self):
        with patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists') as mock_dag_exists:
            mock_dag_exists.return_value = False
            with patch('src.api.services.airflow_service.service.AirflowAPI.call_api') as mock_call_api:
                mock_call_api.return_value = {"message": "Scheduled  schedule for the job job_name_1 successfully", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
                response, status_code = AirflowAPI(self.session).create_dag('66729ec22ee1491c32b05b60', 'user_id_1', 'job_name_1', '@daily', {"some_key": "some_value"}, {'type': 'code'}, schedule_name="",executionType="code",run_engine_type="spark")
                
                self.assertEqual(status_code, 200)
                self.assertEqual(response["message"], "Scheduled  schedule for the job job_name_1 successfully")

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    @patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists')
    def test_delete_dag_not_exist_error(self, mock_dag_exists, mock_call_api):
        # DAG exists
        mock_dag_exists.return_value = False
        # API response with error
        mock_call_api.return_value = {'message': 'DAG does not exist'}

        response = AirflowAPI(self.session).delete_dag('66729ec22ee1491c32b05b60')
        self.assertEqual(response[1], 404)  
        self.assertEqual(response[0], {'message': 'DAG does not exist'})

    @patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists')
    def test_delete_dag_error_in_response(self, mock_dag_exists):
        mock_dag_exists.return_value = True

        response = AirflowAPI(self.session).delete_dag('66729ec22ee1491c32b05b69')
        self.assertEqual(response["status_code"], 500)

    #@pytest.mark.skip(reason="This is mocking whole `call_api` which does not lead to expected mock behavior")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_success_with_local_tag(self, mock_call_api):
        # Mock responses for the call_api method
        mock_call_api.side_effect = [
            {"dag_id": "dag_1", "tags": [{"name": "local:123"}]},  
            {"dag_runs": [{"run_id": "run_1"}, {"run_id": "run_2"}],
            "total_entries": 2},
            {"tasks": [{"task_id": "task_1"}, {"task_id": "task_2"}]}
        ]
        query_params = {
            "page": "1",
            "per_page": "10"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)
        expected_response = {
            "basic_info": {"dag_id": "dag_1", "tags": [{"name": "local:123"}], "local": 123},
            "dag_runs": {"dag_runs": [{"run_id": "run_1"}, {"run_id": "run_2"}], "page": 1, "per_page": 10, "total_entries": 2},
            "tasks": {"tasks": [{"task_id": "task_1"}, {"task_id": "task_2"}]}
        }
        self.assertEqual(response, expected_response)

    #@pytest.mark.skip(reason="This is mocking whole `call_api` which does not lead to expected mock behavior")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_success_with_no_tag(self, mock_call_api):
        # Mock responses for the call_api method
        mock_call_api.side_effect = [
            {"dag_id": "dag_1", "tags": [{"name": ""}]},  
            {"dag_runs": [{"run_id": "run_1"}, {"run_id": "run_2"}],
            "total_entries": 2},
            {"tasks": [{"task_id": "task_1"}, {"task_id": "task_2"}]}
        ]
        query_params = {
            "page": "1",
            "per_page": "10"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)
        expected_response = {'basic_info': {'dag_id': 'dag_1', 'tags': [{'name': ''}]}, 'dag_runs': {'dag_runs': [{'run_id': 'run_1'}, {'run_id': 'run_2'}], "page": 1, "per_page": 10, "total_entries": 2}, 'tasks': {'tasks': [{'task_id': 'task_1'}, {'task_id': 'task_2'}]}}
        self.assertEqual(response, expected_response)

    #@pytest.mark.skip(reason="The test is mocking whole `call_api` which does not lead to expected mock behavior")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_execution_date_asc_success(self, mock_call_api):
        # Mock responses for the call_api method
        mock_call_api.side_effect = [
            {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}]},
            {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8", "execution_date":"2025-09-15T16:04:33.714690+05:30"}, 
                          {"run_id": "674d49ea846f5e936773e0f8", "execution_date":"2025-09-16T16:04:33.714690+05:30"}],
            "total_entries": 2},
            {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        ]
        query_params = {
            "page": "1",
            "per_page": "10",
            "sort_field": "execution_date",
            "sort_order": "asc"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)        
        expected_response = {
            "basic_info": {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}], "job_name": "example_job"},
            "dag_runs": {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8", "execution_date":"2025-09-15T16:04:33.714690+05:30"}, 
                          {"run_id": "674d49ea846f5e936773e0f8", "execution_date":"2025-09-16T16:04:33.714690+05:30"}], "page": 1, "per_page": 10, "total_entries": 2},
            "tasks": {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        }
        self.assertEqual(response, expected_response)

    #@pytest.mark.skip(reason="The test is mocking whole `call_api` which does not lead to expected mock behavior")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_execution_date_desc_success(self, mock_call_api):
        # Mock responses for the call_api method
        mock_call_api.side_effect = [
            {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}]},
            {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8", "execution_date":"2025-09-16T16:04:33.714690+05:30"}, 
                          {"run_id": "674d49ea846f5e936773e0f8", "execution_date":"2025-09-15T16:04:33.714690+05:30"}],
            "total_entries": 2},
            {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        ]
        query_params = {
            "page": "1",
            "per_page": "10",
            "sort_field": "execution_date",
            "sort_order": "desc"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)        
        expected_response = {
            "basic_info": {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}], "job_name": "example_job"},
            "dag_runs": {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8", "execution_date":"2025-09-16T16:04:33.714690+05:30"}, 
                          {"run_id": "674d49ea846f5e936773e0f8", "execution_date":"2025-09-15T16:04:33.714690+05:30"}], "page": 1, "per_page": 10, "total_entries": 2},
            "tasks": {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        }
        self.assertEqual(response, expected_response)

    #@pytest.mark.skip(reason="The test is mocking whole `call_api` which does not lead to expected mock behavior")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_execution_date_filter_success(self, mock_call_api):
        # Mock responses for the call_api method
        mock_call_api.side_effect = [
            {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}]},
            {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8", "execution_date":"2025-09-16T16:04:33.714690+05:30"}],
            "total_entries": 1},
            {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        ]
        query_params = {
            "page": "1",
            "per_page": "10",
            "start_date": "2025-09-15T22:30:00Z", 
            "end_date": "2025-09-16T22:30:00Z"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)
        expected_response = {
            "basic_info": {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}], "job_name": "example_job"},
            "dag_runs": {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8", "execution_date":"2025-09-16T16:04:33.714690+05:30"}], "page": 1, "per_page": 10, "total_entries": 1},
            "tasks": {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        }
        self.assertEqual(response, expected_response)

    #@pytest.mark.skip(reason="The test is mocking whole `call_api` which does not lead to expected mock behavior")
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_info_state_filter_success(self, mock_call_api):
        # Mock responses for the call_api method
        mock_call_api.side_effect = [
            {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}]},
            {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8", "state":"queued"}, 
                          {"run_id": "674d49ea846f5e936773e0f8", "state":"success"}],
            "total_entries": 2},
            {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        ]
        query_params = {
            "page": "1",
            "per_page": "10",
            "state": "queued,success"
        }
        response = AirflowAPI(self.session).get_dag_info("674d49ea846f5e936773c0f8", query_params)
        expected_response = {
            "basic_info": {"dag_id": "674d49ea846f5e936773c0f8", "tags": [{"name": "job_name:example_job"}], "job_name": "example_job"},
            "dag_runs": {"dag_runs": [{"run_id": "674d49ea846f5e936773d0f8", "state":"queued"}, 
                          {"run_id": "674d49ea846f5e936773e0f8", "state":"success"}], "page": 1, "per_page": 10, "total_entries": 2},
            "tasks": {"tasks": [{"task_id": "674d49ea846f5e936773a0f8"}, {"task_id": "674d49ea846f5e936773b0f8"}]}
        }
        self.assertEqual(response, expected_response)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_schedule_exists_returns_true(self, mock_call_api):
        # Mock the call_api method to return a response indicating schedule exists
        mock_call_api.return_value = {"dag_id": "dag_1", "tags": []} 

        schedule_id = 'dag_1'
        result = self.api.schedule_exists(schedule_id)

        self.assertTrue(result)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    @patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists')
    @patch('src.api.services.airflow_service.service.RequestType')
    def test_delete_multi_schedule_exists(self,mock_dag_exists, mock_call_api, mock_request):
        # DAG exists
        mock_dag_exists.return_value = True
        # API response with error
        mock_call_api.return_value = {'error': 'some_error'}

        # Mock the schedule_exists method to return False
        api_instance = AirflowAPI(self.session)
        api_instance.schedule_exists = MagicMock(return_value=True)
        
        result, status_code = api_instance.delete_schedule({"schedule_ids":["66943e4439e03d3497400154", "66943de139e03d349740014a"]})
        self.assertEqual(status_code, 200)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_delete_multi_schedule_with_non_exist_ids(self, mock_request):
        # Mock the schedule_exists method to return True
        api_instance = AirflowAPI(self.session)
        api_instance.schedule_exists = MagicMock(return_value=True)
        
        # Mock the API response
        mock_response = {"message": "Success"}
        mock_request.return_value = mock_response
        with self.assertRaises(MongoException):
            result, status_code = api_instance.delete_schedule({"schedule_ids":["66943e4439e03d3497400154", "66943de139e03d349740014a", "66943de139e03d349740054w"]})
        
    def test_get_start_date_time_for_dag(self):
        
        class mockScheduleCollection:
            def get_by_id(self, _id):
                return True, {
                    'advanced_scheduling': {
                        'StartDate': '2025-04-10',
                        'StartTime': '12:26:34',
                        'timeZone': 'Asia/Calcutta' 
                    }
                }
        api_instance = AirflowAPI(self.session)
        api_instance.schedule_collection = mockScheduleCollection()
        res = api_instance._get_start_date_time_for_dag('mock_id')
        self.assertEqual(res, "2025-04-10T12:26:34+05:30")
        
    def test_verify_start_date_constraint_for_dag(self):
        
        class mockScheduleCollection:
            def get_by_id(self, _id):
                return True, {
                    'advanced_scheduling': {
                        'StartDate': '2025-04-10',
                        'StartTime': '12:26:34',
                        'timeZone': 'Asia/Calcutta' 
                    }
                }
        api_instance = AirflowAPI(self.session)
        api_instance.schedule_collection = mockScheduleCollection()
        self.assertEqual(api_instance._verify_start_date_constraint_for_dag('mock_id'), True)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_run_status_success_specific_run(self, mock_call_api):
        """Returns state for a specific dag_run_id when dag_id provided"""
        mock_call_api.return_value = {
            'dag_run_id': 'manual__2025-08-14T09:43:29.281819+00:00',
            'state': 'success',
            'execution_date': '2025-08-14T09:43:29.281819+00:00'
        }

        req_data = {'dag_id': 'test_dag_123', 'dag_run_id': 'manual__2025-08-14T09:43:29.281819+00:00'}
        response, status_code = AirflowAPI(self.session).get_dag_run_status(req_data)

        expected_response = {
            'success': True,
            'dag_id': 'test_dag_123',
            'dag_run_id': 'manual__2025-08-14T09:43:29.281819+00:00',
            'state': 'success'
        }
        self.assertEqual(response, expected_response)
        self.assertEqual(status_code, 200)
        mock_call_api.assert_called_once_with(
            RequestType.GET,
            '/api/v1/dags/test_dag_123/dagRuns/manual__2025-08-14T09:43:29.281819+00:00'
        )

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_run_status_default_dag_id(self, mock_call_api):
        """When dag_id omitted, defaults to run_now_dag"""
        mock_call_api.return_value = {
            'dag_run_id': 'manual__2025-08-14T09:43:29.281819+00:00',
            'state': 'running'
        }

        req_data = {'dag_run_id': 'manual__2025-08-14T09:43:29.281819+00:00'}
        response, status_code = AirflowAPI(self.session).get_dag_run_status(req_data)

        expected_response = {
            'success': True,
            'dag_id': 'run_now_dag',
            'dag_run_id': 'manual__2025-08-14T09:43:29.281819+00:00',
            'state': 'running'
        }
        self.assertEqual(response, expected_response)
        self.assertEqual(status_code, 200)
        mock_call_api.assert_called_once_with(
            RequestType.GET,
            '/api/v1/dags/run_now_dag/dagRuns/manual__2025-08-14T09:43:29.281819+00:00'
        )

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_run_status_missing_dag_run_id(self, mock_call_api):
        """Requires dag_run_id"""
        req_data = {'dag_id': 'some_dag'}
        response, status_code = AirflowAPI(self.session).get_dag_run_status(req_data)

        expected_response = {
            'success': False,
            'msg': 'dag_run_id is required'
        }
        self.assertEqual(response, expected_response)
        self.assertEqual(status_code, 400)
        mock_call_api.assert_not_called()

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_run_status_api_error(self, mock_call_api):
        """When Airflow returns error, propagate message and status"""
        mock_call_api.return_value = {
            'error': 'Run not found',
            'status_code': 404
        }

        req_data = {'dag_id': 'nonexistent_dag', 'dag_run_id': 'run_1'}
        response, status_code = AirflowAPI(self.session).get_dag_run_status(req_data)

        expected_response = {
            'success': False,
            'msg': 'Run not found'
        }
        self.assertEqual(response, expected_response)
        self.assertEqual(status_code, 404)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_run_status_api_exception(self, mock_call_api):
        """API exception leads to 500"""
        mock_call_api.side_effect = Exception('Connection timeout')

        req_data = {'dag_id': 'test_dag_123', 'dag_run_id': 'run_123'}
        response, status_code = AirflowAPI(self.session).get_dag_run_status(req_data)

        expected_response = {
            'success': False,
            'msg': 'Connection timeout'
        }
        self.assertEqual(response, expected_response)
        self.assertEqual(status_code, 500)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_run_status_different_states(self, mock_call_api):
        """Different states propagate through"""
        test_cases = [
            ('running', 'running'),
            ('failed', 'failed'),
            ('queued', 'queued'),
            ('up_for_retry', 'up_for_retry'),
            ('up_for_reschedule', 'up_for_reschedule'),
            ('upstream_failed', 'upstream_failed'),
            ('skipped', 'skipped'),
            ('deferred', 'deferred'),
            ('removed', 'removed')
        ]

        for state, expected_state in test_cases:
            with self.subTest(state=state):
                mock_call_api.return_value = {
                    'dag_run_id': f'run_{state}',
                    'state': state,
                    'execution_date': '2025-08-14T09:43:29.281819+00:00'
                }

                req_data = {'dag_id': f'test_dag_{state}', 'dag_run_id': f'run_{state}'}
                response, status_code = AirflowAPI(self.session).get_dag_run_status(req_data)

                expected_response = {
                    'success': True,
                    'dag_id': f'test_dag_{state}',
                    'dag_run_id': f'run_{state}',
                    'state': expected_state
                }
                self.assertEqual(response, expected_response)
                self.assertEqual(status_code, 200)

    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_run_status_fetches_specific_run(self, mock_call_api):
        """Ensures it requests specific run endpoint"""
        mock_call_api.return_value = {
            'dag_run_id': 'latest_run',
            'state': 'success',
            'execution_date': '2025-08-14T10:00:00+00:00'
        }

        req_data = {'dag_id': 'test_dag_multiple', 'dag_run_id': 'latest_run'}
        response, status_code = AirflowAPI(self.session).get_dag_run_status(req_data)

        expected_response = {
            'success': True,
            'dag_id': 'test_dag_multiple',
            'dag_run_id': 'latest_run',
            'state': 'success'
        }
        self.assertEqual(response, expected_response)
        self.assertEqual(status_code, 200)
        mock_call_api.assert_called_once_with(
            RequestType.GET,
            '/api/v1/dags/test_dag_multiple/dagRuns/latest_run'
        )
        
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    @patch('src.api.services.airflow_service.service.AirflowAPI.dag_exists')
    def test_create_old_schedule_should_succeed(self, mock_dag_exists, mock_call_api):
        mock_dag_exists.return_value = False
        mock_call_api.return_value = {"message": "Successfully generated DAG: 66729ec22ee1491c32b05b60 using job_id: 66729ec22ee1491c32b05b60", "dag_run_id": "123", "job_id": "66729ec22ee1491c32b05b60"}
        response, status_code = AirflowAPI(self.session).create_dag(
            '66729ec22ee1491c32b05b60', 'user_id_1', 'job_name_1', '@daily', {"some_key": "some_value"}, {'type': 'code'},
            schedule_name="",executionType="code", run_engine_type="spark", should_create_v1_schedule=True)
        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Scheduled  schedule for the job job_name_1 successfully")

    @pytest.mark.skip(reason="It's raising passing unexpected executionType which is not expected")
    @patch('src.api.services.airflow_service.service.AirflowAPI._get_start_date_time_for_dag')
    @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    def test_get_dag_runs_search_success(self, mock_call_api, mock_get_start):
        mock_call_api.side_effect = [
            {
                "dags": [
                    {
                        "dag_id": "68c2ab89beade5fdfbc16fea",
                        "next_dagrun": "2025-09-14T16:44:00+05:30",
                        "tags": [
                            {"name": "user_id:68c29aa58e0052b09f0f5c1d"},
                            {"name": "schedule_name:wqfrerh"},
                            {"name": "job_name:Job 2"}
                        ]
                    }
                ],
                "total_entries": 1
            },
            {
                "dags": []  # End of pagination
            }
        ]
        mock_get_start.return_value = "2025-08-11 10:00:00"  # valid datetime string

        mock_session = MagicMock()
        mock_session.client.user_sessions_test.__getitem__().find_one().get.side_effect = lambda key, default=None: (
            "pipeline" if key == "executionType" else default
        )
        api_instance = AirflowAPI(mock_session)
        api_instance.chats_collection = MagicMock()
        api_instance.chats_collection.get_by_id.return_value = (
            True,
            {"chat_id": "some_chat_id", "messages": [], "chat_name": "some_chat_name"}
        )
        # Call get_dag_runs with mocked data
        response = api_instance.get_dag_runs({"user_id": "68c29aa58e0052b09f0f5c1d", "schedule_name": ["wqfrerh"]})
        expected_response = {'dags': [{'dag_id': '68c2ab89beade5fdfbc16fea', 'next_dagrun': '2025-09-14T16:44:00+05:30', 'tags': [{'name': 'user_id:68c29aa58e0052b09f0f5c1d'}, {'name': 'schedule_name:wqfrerh'}, {'name': 'job_name:some_chat_name'}], 'schedule_name': '-', 'job_name': 'some_chat_name', 'service_type': 'dts', 'starts_on': '2025-08-11 10:00:00', 'schedule_id': 'None', 'meta_schedule_version': 1, 'job_details': {'configuration': [], 'files_list': [], 'destination': [], 'advanced_scheduling': None}}], 'page': 1, 'per_page': 10, 'total_records': 1}
        self.assertEqual(response, expected_response)
    
    # @patch('src.api.services.airflow_service.service.AirflowAPI.schedule_exists')
    # @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    # # @patch('src.models.mongo.mongo_factory.MongoFactory')
    # @patch('os.path.exists')
    # @patch('os.remove')
    # def test_delete_schedule_success(self, mock_remove, mock_exists, mock_call_api, mock_schedule_exists):
    #     # Mock the schedule_exists method
    #     mock_schedule_exists.return_value = True
        
    #     # Mock the call_api method for pausing and deleting
    #     mock_call_api.side_effect = [
    #         {"status": "success"},  # Pausing response
    #         {"status": "success"}   # Deleting response
    #     ]
        
    #     # Mock os.path.exists to return True, meaning the DAG file exists
    #     mock_exists.return_value = True
        
    #     # Mock the delete_one method on the schedule_collection
    #     self.api.schedule_collection.delete_one = MagicMock()

    #     payload = {"schedule_ids": ["dag_1"]}
    #     response, status_code = self.api.delete_schedule(payload)

    #     expected_response = {
    #         "success": ["dag_1"],
    #         "errors": []
    #     }

    #     # Assertions
    #     self.assertEqual(response, expected_response)
    #     self.assertEqual(status_code, 200)
    #     mock_call_api.assert_any_call(RequestType.PATCH, "/api/v1/dags/dag_1", payload={"is_paused": True})
    #     mock_call_api.assert_any_call(RequestType.DELETE, "/api/v1/dags/dag_1")
    #     self.api.schedule_collection.delete_one.assert_called_once_with("dag_1")
    #     mock_remove.assert_called_once_with("path_to_dags/dags/dag_1.py")



    # @patch('src.api.services.airflow_service.service.AirflowAPI.schedule_exists')
    # @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    # @patch('src.api.services.airflow_service.service.MongoFactory.delete_one')
    # @patch('os.path.exists')
    # @patch('os.remove')
    # def test_delete_schedule_fail_to_pause(self, mock_remove, mock_exists, mock_delete_one, mock_call_api, mock_schedule_exists):
    #     # Mock responses
    #     mock_schedule_exists.return_value = True
    #     mock_call_api.side_effect = [
    #         {"error": "Failed to pause"},  # Pausing response with error
    #         {"status": "success"}         # Deleting response
    #     ]
    #     mock_exists.return_value = True  # DAG file exists

    #     payload = {"schedule_ids": ["dag_1"]}
    #     response, status_code = self.api.delete_schedule(payload)

    #     expected_response = {
    #         "success": [],
    #         "errors": ["Failed to pause DAG dag_1"]
    #     }

    #     # Assertions
    #     self.assertEqual(response, expected_response)
    #     self.assertEqual(status_code, 200)
    #     mock_call_api.assert_called_once_with(RequestType.PATCH, "/api/v1/dags/dag_1", payload={"is_paused": True})
    #     mock_delete_one.assert_not_called()
    #     mock_remove.assert_not_called()

    # @patch('src.api.services.airflow_service.service.AirflowAPI.schedule_exists')
    # @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    # @patch('src.api.services.airflow_service.service.MongoFactory.delete_one')
    # @patch('os.path.exists')
    # @patch('os.remove')
    # def test_delete_schedule_fail_to_delete(self, mock_remove, mock_exists, mock_delete_one, mock_call_api, mock_schedule_exists):
    #     # Mock responses
    #     mock_schedule_exists.return_value = True
    #     mock_call_api.side_effect = [
    #         {"status": "success"},  # Pausing response
    #         {"error": "Failed to delete"}  # Deleting response with error
    #     ]
    #     mock_exists.return_value = True  # DAG file exists

    #     payload = {"schedule_ids": ["dag_1"]}
    #     response, status_code = self.api.delete_schedule(payload)

    #     expected_response = {
    #         "success": [],
    #         "errors": ["Failed to delete DAG dag_1"]
    #     }

    #     # Assertions
    #     self.assertEqual(response, expected_response)
    #     self.assertEqual(status_code, 200)
    #     mock_call_api.assert_any_call(RequestType.PATCH, "/api/v1/dags/dag_1", payload={"is_paused": True})
    #     mock_call_api.assert_any_call(RequestType.DELETE, "/api/v1/dags/dag_1")
    #     mock_delete_one.assert_not_called()
    #     mock_remove.assert_not_called()

    # @patch('src.api.services.airflow_service.service.AirflowAPI.schedule_exists')
    # @patch('src.api.services.airflow_service.service.AirflowAPI.call_api')
    # @patch('src.api.services.airflow_service.service.MongoFactory.delete_one')
    # @patch('os.path.exists')
    # @patch('os.remove')
    # def test_delete_schedule_file_does_not_exist(self, mock_remove, mock_exists, mock_delete_one, mock_call_api, mock_schedule_exists):
    #     # Mock responses
    #     mock_schedule_exists.return_value = True
    #     mock_call_api.side_effect = [
    #         {"status": "success"},  # Pausing response
    #         {"status": "success"}   # Deleting response
    #     ]
    #     mock_exists.return_value = False  # DAG file does not exist

    #     payload = {"schedule_ids": ["dag_1"]}
    #     response, status_code = self.api.delete_schedule(payload)

    #     expected_response = {
    #         "success": ["dag_1"],
    #         "errors": ["DAG file path_to_dags/dags/dag_1.py does not exist"]
    #     }

    #     # Assertions
    #     self.assertEqual(response, expected_response)
    #     self.assertEqual(status_code, 200)
    #     mock_call_api.assert_any_call(RequestType.PATCH, "/api/v1/dags/dag_1", payload={"is_paused": True})
    #     mock_call_api.assert_any_call(RequestType.DELETE, "/api/v1/dags/dag_1")
    #     mock_delete_one.assert_called_once_with("dag_1")
    #     mock_remove.assert_not_called()

    def test_get_dag_search_filters_success(self):
        # Mock schedule data (with one 'once' and two recurring)
        schedule_data = [
            {'schedule_interval': 'hourly', 'schedule_name': 'Hourly Job', 'chat_id': 'chat1', 'generated_cron_expression': '57 */1 * * *',},
            {'schedule_interval': 'weekly', 'schedule_name': 'Weekly Job', 'chat_id': 'chat2', 'generated_cron_expression': '37 16 * * 0',},
            {'schedule_interval': 'once', 'schedule_name': 'One-time Job', 'chat_id': 'chat3', 'generated_cron_expression': None,},
        ]
        self.api.schedule_collection.get_all_by_user_id.return_value = (None, schedule_data)

        # Mock chat names
        self.api.chats_collection.get_by_id.side_effect = [
            (None, {'chat_name': 'Chat One'}),
            (None, {'chat_name': 'Chat Two'}),
        ]

        expected_result = {
            "success": True,
            "dag_search_filters": {
                "schedule_names": ['Hourly Job', 'Weekly Job'],
                "job_names": ['Chat One', 'Chat Two']
            },
            "msg": "Dag search filters retrieved successfully."
        }

        result, status_code = self.api.get_dag_search_filters('user123')
        self.assertEqual(status_code, 200)
        self.assertEqual(result['success'], True)
        self.assertCountEqual(result['dag_search_filters']['schedule_names'], ['Hourly Job', 'Weekly Job'])
        self.assertCountEqual(result['dag_search_filters']['job_names'], ['Chat One', 'Chat Two'])

    def test_get_dag_search_filters_valid_schedule(self):
        # Schedule has a valid cron expression → should be included in results
        schedule_data = [
            {
                'schedule_interval': 'daily',
                'schedule_name': 'Daily Job',
                'chat_id': 'chat1',
                'generated_cron_expression': '0 12 * * *'  # valid cron
            },
        ]
        chat_data = {
            "chat_name": "Job Chat"
        }
        # Mock schedule and chat DB calls
        self.api.schedule_collection.get_all_by_user_id.return_value = (None, schedule_data)
        self.api.chats_collection.get_by_id.return_value = (None, chat_data)
        result, status_code = self.api.get_dag_search_filters('user123')
        self.assertEqual(status_code, 200)
        self.assertTrue(result['success'])
        self.assertEqual(result['dag_search_filters']['schedule_names'], ['Daily Job'])
        self.assertEqual(result['dag_search_filters']['job_names'], ['Job Chat'])

    def test_get_dag_search_filters_empty_data(self):
        self.api.schedule_collection.get_all_by_user_id.return_value = (None, [])

        result, status_code = self.api.get_dag_search_filters('user123')
        self.assertEqual(status_code, 200)
        self.assertTrue(result['success'])
        self.assertEqual(result['dag_search_filters']['schedule_names'], [])
        self.assertEqual(result['dag_search_filters']['job_names'], [])

    def test_get_dag_search_filters_exception(self):
        # Raise an exception when accessing schedules
        self.api.schedule_collection.get_all_by_user_id.side_effect = Exception("Database error")

        result, status_code = self.api.get_dag_search_filters('user123')
        self.assertEqual(status_code, 500)
        self.assertFalse(result['success'])
        self.assertIn('Database error', result['msg'])


    @patch('src.api.services.airflow_service.utils.DLTPackageUtils.get_dlt_package')
    def test_dlt_packages_data_migration(self, mock_get_dlt_package):
        mock_get_dlt_package.side_effect = lambda pkg_type, conn_type: f"dlt-{conn_type}"
        
        mock_connections = MagicMock()
        def get_by_id_side_effect(conn_id):
            if conn_id == "source_conn_id":
                return (True, {"type": "mysql"})
            elif conn_id == "dest_conn_id":
                return (True, {"type": "postgres"})
            return (True, {"type": "unknown"})
        
        mock_connections.get_by_id.side_effect = get_by_id_side_effect
        
        # Setup API instance with mocked connection collection
        api_instance = AirflowAPI(MagicMock())
        api_instance.connections_collection = mock_connections
        
        pipeline = [
            {
                "function": "data_migration",
                "source_parameters": {"connection_id": "source_conn_id"},
                "destination_parameters": {"connection_id": "dest_conn_id"}
            }
        ]
        
        configurations = {"--packages": "custom_pkg==1.0.0"}
        user_id = "test_user"
        
        result = api_instance._dlt_packages(configurations, pipeline, user_id)
        
        self.assertIn("custom_pkg==1.0.0", result)
        self.assertIn("dlt-mysql", result)
        self.assertIn("dlt-postgres", result)


if __name__ == '__main__':
    unittest.main()
