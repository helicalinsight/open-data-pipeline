import os
import unittest
import pytest

from src.exceptions.exception import *
from src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from src.etl.transfrom.manager import Manager
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()


class TestManager(unittest.TestCase):
    
    @pytest.mark.skip()
    def test_manage_transform_rename_column(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        intent_name = "rename_columns"
        # adding same name at old name and new name since everytime we run we might have to change the name in feather file also
        parameters = {"groups": [{"old_name": "name", "new_name": "new_name"}], "source":
            {"source_id": "6602a3a74475001648200351"}}
        status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(status)
        self.assertTrue(metadata_status)
        self.assertEqual(msg, 'Successfully renamed column(s) name with new_name.')

    def test_manage_transform_cast_as_boolean(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9f11"
        }
        intent_name = "typecast"
        # adding same name at old name and new name since everytime we run we might have to change the name in feather file also
        parameters = {"groups": [{"columns": ["bool_column"], "new_type": "boolean", "old_type":None}],
            "source_id": "662badd888e28e8af8679eb3"}
        status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(status)
        self.assertTrue(metadata_status)
        self.assertEqual(msg, "Updated data type of the given column(s) bool_column to 'boolean'.")

    def test_manage_transform_cast_as_bool(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9f11"
        }
        intent_name = "typecast"
        # adding same name at old name and new name since everytime we run we might have to change the name in feather file also
        parameters = {"groups": [{"columns": ["bool_column"], "new_type": "bool", "old_type":None}],
            "source_id": "662badd888e28e8af8679eb3"}
        status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(status)
        self.assertTrue(metadata_status)
        self.assertEqual(msg, "Updated data type of the given column(s) bool_column to 'boolean'.")

    def test_manage_transform_cast_as_integer(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9f11"
        }
        intent_name = "typecast"
        # adding same name at old name and new name since everytime we run we might have to change the name in feather file also
        parameters = {"groups": [{"columns": ["int_column"], "new_type": "float", "old_type":None}],
            "source_id": "662badd888e28e8af8679eb3"}
        status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(status)
        self.assertTrue(metadata_status)
        self.assertEqual(msg, "Updated data type of the given column(s) int_column to 'float'.")

    def test_manage_transform_add_columns(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        intent_name = "add_columns"
        parameters = {"groups": [{"columns": ["school"], "default": "MNS"}],
            "source_id": "6602a3a74475001648200351"}
        status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,) 
        self.assertTrue(status)
        self.assertTrue(metadata_status)
        self.assertEqual(msg, 'Successfully added column(s) school with default value MNS.')

    def test_manage_export(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        intent_name = "add_columns"
        parameters = {"groups": [{"columns": ["school"], "default": "MNS"}], "source":
            {"source_id": "6602a3a74475001648200351"}}
        result, id, export_name = session.with_transaction(lambda s:Manager(session).manage_export(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        

        self.assertEqual("6602a3a74475001648200351", id)
        self.assertEqual("6602a3a74475001648200351.csv", export_name)
        self.assertEqual(True, result)

    def test_manage_export_false(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        intent_name = "add_columns"
        parameters = {"groups": [{"columns": ["school"], "default": "MNS"}], "source":
            {"source_id": None}}
        with pytest.raises(ManagerException):
            result, id, export_name = session.with_transaction(lambda s:Manager(session).manage_export(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)

    @pytest.mark.skip()
    def test_preview(self):
        feather_id = "6602a3a74475001648200351"
        alias = "customer"
        preview_info = session.with_transaction(lambda s:Manager(session).preview(feather_id, alias),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_data = [{'_id': '6602a3a74475001648200351', 'alias': 'customer', 'total_records': 4, 'total_records_dataframe': 4, 'columns': [{'name': 'id', 'dataType': 'int64'
                        }, {'name': 'name', 'dataType': 'object'}, {'name': 'age', 'dataType': 'int64'}, {'name': 'join_date', 'dataType': 'datetime64[ns]'}], 'data': [{'id': 1,
                        'name': 'Alice', 'age': 25, 'join_date': '2022-01-01'}, {'id': 2, 'name': 'Bob', 'age': 30, 'join_date': '2022-02-15'}, {'id': 3, 'name': 'Charlie', 'age'
                        : 35, 'join_date': '2022-03-20'}, {'id': 4, 'name': 'David', 'age': 40, 'join_date': '2022-04-10'}]}]
        self.assertEqual(expected_data, preview_info)

    def test_get_step_number(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        success, step_number = session.with_transaction(lambda s:Manager(session).get_step_number(user_info),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(14, step_number)
        self.assertTrue(success)

    def test_get_step_number_with_non_existing_chat_id(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d2q"
        }
        with pytest.raises(UtilsException) as test_function:
            session.with_transaction(lambda s:Manager(session).get_step_number(user_info),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual("Failed to get step number.", str(test_function.value))

    def test_save_history_for_non_existing_chat_id(self):
        user_info = {
            "user_id": "65ce024b47ff1fc8d6ae2bb1",
            "chat_id": "j1"
        }
        history = {
                  "id": "eb0405bc-b99a-4cda-8802-12506c631ba7",
                  "step": 0,
                  "status": "PASS",
                  "function": "read_files",
                  "parameters": {
                    "file_id": "aa9ef98e-438c-48ed-9622-19f3a94b3106",
                    "file_name": "Dummy_Data (1)",
                    "source_id": "662bb3d788e28e8af8679eb7"
                  },
                  "output": None
                }
        with pytest.raises(UtilsException) as test_function:
            session.with_transaction(lambda s:Manager(session).save_history(user_info, history),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
            
        self.assertEqual("Failed to save history.", str(test_function.value))

    def test_save_history_existing(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        history = {
                  "id": "eb0405bc-b99a-4cda-8802-12506c631ba7",
                  "step": 0,
                  "status": "PASS",
                  "function": "read_files",
                  "parameters": {
                    "file_id": "aa9ef98e-438c-48ed-9622-19f3a94b3106",
                    "file_name": "Dummy_Data (1)",
                    "source_id": "662bb3d788e28e8af8679eb7"
                  },
                  "output": None
                }
        success = session.with_transaction(lambda s:Manager(session).save_history(user_info, history),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)

    def test_manage_transform_union(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        intent_name = "union"
        parameters = {"source_id": ["662bb3d788e28e8af8679eb7", "6602a3a74475001648200351"], "file_names": ["test_file1", "test_file2"],}
        status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(status)
        self.assertTrue(load['success'])
        self.assertIsInstance(load['files'][0]['source_id'], str)
        self.assertEqual(load['files'][0]['alias'], 'df_union_1')
        self.assertEqual(load['files'][0]['type'], 'csv') 
        self.assertTrue(metadata_status)
        self.assertEqual(msg, 'Union performed successfully for test_file1, test_file2.')
        self.assertEqual(details, {'exception': False, 'exception_name': None, 'exception_message': None})

    def test_manage_transform_join(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        intent_name = "joins"
        parameters = {"source_id": ["662bb3d788e28e8af8679eb7", "6602a3a74475001648200351"],
                      "groups": [{"join_type": "inner", "left_on": ["id"], "right_on": ["id"]}],
                      "file_names": ["Dummy_Data (1)", "customers-100"]}
        status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(status)
        self.assertTrue(load['success'])
        self.assertIsInstance(load['files'][0]['source_id'], str)
        self.assertEqual(load['files'][0]['alias'], 'df_joins_1')
        self.assertEqual(load['files'][0]['type'], 'csv') 
        self.assertTrue(metadata_status)
        expected_msg = "Successfully performed joins on files Dummy_Data (1), customers-100 on columns id and id with the type inner."
        self.assertEqual(expected_msg, msg)
        self.assertEqual(details, {'exception': False, 'exception_name': None, 'exception_message': None})

    def test_manage_transform_for_add_columns(self):
        user_info =  {
            "chat_id": "65cb43f2007a5f38718b9d6a",
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
            }
        intent_name = "add_columns"
        parameters = {"groups": [{
                "columns": ["adding"],
                "default": 19
            }],
            "source_id": "6602a3a74475001648200351"
        }
        
        status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(status)
        self.assertEqual(load, {'success': False, 'source_id': None})
        self.assertTrue(metadata_status)
        expected_msg = 'Successfully added column(s) adding with default value 19.'
        self.assertEqual(expected_msg, msg)
        self.assertEqual(details, {'exception': False, 'exception_name': None, 'exception_message': None})

    def test_manage_transform_for_add_columns_with_exception(self):
        user_info =  {
            "chat_id": "65cb43f2007a5f92018b9d6a",
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdDQuY29tIiwiX2lkIjoiNjYxOTE1NmFhNWY0YzVjMWIwMWU0ZDA3IiwiZXhwIjoxNzEyOTM3OTI1fQ.uKajZc4wYzDUPG5kiQrenQ4k5ba8xlm_b-kzmGPdMDQ"
            }
        intent_name = "add_columns"
        parameters = {"groups": [{
                "columns": ["adding"],
                "default": 19
            }]
        }
        with self.assertRaises(Exception):
            status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                        write_concern=wc_majority,
                        read_preference=ReadPreference.PRIMARY,)
            
    def test_manage_transform_for_pytool(self):
        parameters = {"code": """print('hello world !!')\na = 5\nb = 10\nprint(f"The sum of a and b is {a + b}")\nprint(DataframeInformation)""", "source_id": "6602a3a74475001648200351"}
        intent_name = "pytool"
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        
        status, metadata_status, load, msg, details = session.with_transaction(lambda s:Manager(session).manage_operation(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(status)
        self.assertEqual(load, {'success': False, 'source_id': None})
        self.assertEqual(msg, 'Executed the code successfully.')
        self.assertEqual(details, {'new_ids': []})
        

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="due to circular import error")
    def test_update_history(self):
        # Prepare test data
        step = 1
        status = "PASS"
        function = "joins"
        parameters = {"param1": "value1", "param2": "value2"}
        output = {"output1": "result1", "output2": "result2"}

        # Call the method
        success, result = session.with_transaction(lambda s:Manager(session).update_history(status, function, parameters, output=output),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        # Assert that the result is correct
        self.assertTrue(success)
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertEqual(result["step"], step)
        self.assertEqual(result["status"], status)
        self.assertEqual(result["function"], function)
        self.assertEqual(result["parameters"], parameters)
        self.assertEqual(result.get("output"), output)

        # Assert that the data is correctly inserted into the mock MongoDB collection
        # self.assertEqual(self.collection.count_documents({}), 1)
        # inserted_entry = self.collection.find_one()
        # self.assertEqual(inserted_entry["_id"], result["id"])
        # self.assertEqual(inserted_entry["step"], step)
        # self.assertEqual(inserted_entry["status"], status)
        # self.assertEqual(inserted_entry["function"], function)
        # self.assertEqual(inserted_entry["parameters"], parameters)
        # self.assertEqual(inserted_entry.get("output"), output)


if __name__ == '__main__':
    unittest.main()
