import unittest
import pytest
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase


from src.api.services.execute.service import ExecuteService
from ......src.models.connector import MongoConnector
from ......src.models.mongo.mongo_factory import MongoFactory
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

mongo = MongoConnector()
mongo_client = mongo.client
cache: CacheBase = get_cache(session=session)

class TestExecuteService(unittest.TestCase):
    def test_execute_service_for_union(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "union",
            "parameters": {
                "source_id": ["6602a3a74475001648200351", "662bb3d788e28e8af8679eb7"],
                "file_names": ["test_file1", "test_file2"],
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        source_id = response['load']['files'][0]['source_id']
        user_id = req_data['user_info']['user_id']
        chat_id = req_data['user_info']['chat_id']
        cache_item = cache.get_item(source_id, user_id, chat_id)
        
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], 'Union performed successfully for test_file1, test_file2.')
        self.assertEqual(status_code, 200)
        self.assertIsNotNone(cache_item)

    def test_execute_service_for_arithmetic(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "expression",
            "parameters": {"groups": [{'query': 'age + 5', 'destination_column': 'Increased_age'}], "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)

        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Arithmetic operation performed on the given query 'age + 5' and stored to 'Increased_age'.")
        self.assertEqual(status_code, 200)

    def test_execute_service_for_aggregation(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "aggregate",
            "parameters": {"groups": [{'columns': ['age'], 'destination_columns': ['new_age'],
            'agg': ['sum'], 'group_by': ['id']}], "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Successfully performed aggregations on 'age' grouped by 'id'.")
        self.assertEqual(status_code, 200)

    def test_execute_service_for_correlation(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "correlation",
            "parameters": {"groups": [{'columns': ['id', 'id'], 'destination_column':
            'correlation_column'}], "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Successfully calculated correlation for the column(s) id, id to correlation_column.")
        self.assertEqual(status_code, 200)

    def test_execute_service_for_date_format(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "date_format",
            "parameters": {"groups": [{'columns': ['join_date'], 'format': 'yyyy/mm/dd'}], "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Successfully updated the format of the date for the column(s) join_date to 'yyyy/mm/dd'.")
        self.assertEqual(status_code, 200)

    @pytest.mark.run(order=1)
    def test_execute_service_for_drop_null(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "drop_na",
            "parameters": {"groups": [{'subset': ['name']}], "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Dropped NaN values for ['name'] columns")
        self.assertEqual(status_code, 200)

    @pytest.mark.run(order=1)
    def test_execute_service_for_extract(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "extract",
            "parameters": {"groups": [{'column': 'join_date', 'component': 'year',
            'destination_column': 'joining_year'}], "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)

        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Extracted 'year' from 'join_date' column")
        self.assertEqual(status_code, 200)

    def test_execute_service_for_fill_na(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "fill_na",
            "parameters": {"groups": [{'value': 'Fail'}], "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)

        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Filled NaN values with 'Fail' value")
        self.assertEqual(status_code, 200)
    
    @pytest.mark.run(order=1)
    def test_execute_service_for_trim(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "trim",
            "parameters": {"groups": [
                {
                    "number_of_characters": 1,
                    "location": "left",
                    "columns": ["name"]
                }
            ],
            "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Successfully trimmed column(s) name to '1' character(s) to its left.")
        self.assertEqual(status_code, 200)

    def test_execute_service_for_add_columns(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "add_columns",
            "parameters": {"groups": [
                {
                    "columns": ["adding"],
                    "default": 19
                }],
                "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)

        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], 'Successfully added column(s) adding with default value 19.')
        self.assertEqual(status_code, 200)
    
    def test_execute_service_for_drop_all_columns_except(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "drop_all_columns_except",
            "parameters": {"groups": 
                           [{
                                "columns": ["name"]
                            }],
                            "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], 'Successfully dropped all column(s) except name.')
        self.assertEqual(status_code, 200)
    
    def test_execute_service_for_cast(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "typecast",
            "parameters": {"groups": 
                [{
                    "columns": ["name"],
                    "new_type": "object",
                    "old_type": "string",
                }],
                "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Updated data type of the given column(s) name to 'object'.")
        self.assertEqual(status_code, 200)
    
    def test_execute_service_for_concat(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "concat",
            "parameters": {"groups": [
                {
                    "columns": ["id", "name"],    
                    "separator": "-",
                    "destination_column": "dest_col",
                }],
                "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Successfully concatenated column(s) id, name with '-' to the column 'dest_col'.")
        self.assertEqual(status_code, 200)
    
    def test_execute_service_for_deduplicate(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "deduplicate",
            "parameters": {"groups": [
                {
                    "columns": ["name"],
                }],
                "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], 'Successfully deduplicated column(s) name.')
        self.assertEqual(status_code, 200)
    
    @pytest.mark.run(order=1)
    def test_execute_service_for_filter_value(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "filter_value",
            "parameters": {"groups": [
                {
                    'columns': ['age'], 'expr': 'in_between', 'value': [25, 40]
                }],
                "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], "Successfully filtered column(s) 'age' based on the given criteria.")
        self.assertEqual(status_code, 200)
    
    @pytest.mark.run(order=1)
    def test_execute_service_for_sort(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "sort",
            "parameters": {"groups": [
                {
                    'columns': ['age'], 'ascending': True
                }],
                "source_id": "6602a3a74475001648200351"
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], 'Successfully sorted column(s)  age.')
        self.assertEqual(status_code, 200)

    def test_execute_service_for_export_success(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "export",
            "parameters": {
                "groups": [{'export_name': 'test.csv'}],
                "source":{"source_id": "6602a3a74475001648200351"}
            }
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(response['success'], True)
        self.assertEqual(response['text'], 'File Ready To Download')
        self.assertTrue(response['export_name'].endswith('.csv')) 
        self.assertEqual(status_code, 200)

    # test execute service other then export
    def test_execute_service_for_drop_columns(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "drop_columns",
            "parameters": {"groups": [{"columns": ["name"]}], "source_id": "6602a3a74475001648200351"}
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(response['success'], True)
        self.assertTrue(response['metadata_status'])
        self.assertEqual(response['text'], "Successfully dropped column(s) name.")
        self.assertEqual(response['load'], {'success': False, 'source_id': None})  # we don't create new_df in case of drop column, that's why getting default value for 'load'
        self.assertEqual(status_code, 200)

    def test_execute_service_for_drop_columns_with_exception(self):
        req_data = {
            "user_info" : {
                "chat_id": "65cb43f2007a5f38718b9d6a",
                "user_id": "6619156aa5f4c5c1b01e4d07",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
                },
            "intent_name": "drop_columns",
            "parameters": {"groups": [{"columns": ["next_col"]}], "source_id": "6602a3a74475001648200351"}
        }
        response, status_code = session.with_transaction(lambda s:ExecuteService(session).execute(req_data),
        read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['text'], 'Function failed: Failed to drop columns."[\'next_col\'] not found in axis"')
        self.assertEqual(status_code, 500)

if __name__ == '__main__':
    unittest.main()
