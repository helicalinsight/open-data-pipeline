import os
import unittest
import pytest
import pandas

from src.etl.transfrom.process.processor import Processor
from src.exceptions.exception import *
from src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestProcessor(unittest.TestCase):

    def test_execute_operations_with_existing_feather_id(self):
        intent_name = "add_columns"
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        parameters = {"groups": [{"columns": ["customer_id"], "default": 1}], "source":
            {"source_id": "6602a3a74475001648200351"}, "export_name": "file1.csv"}
        status, metadata_status, df, msg, new_df, details = session.with_transaction(lambda s:Processor(session).execute_operations(intent_name, parameters, user_info=user_info),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(status)
        self.assertTrue(metadata_status)
        self.assertEqual(msg, 'Successfully added column(s) customer_id with default value 1.')
        self.assertIsNotNone(df)
        self.assertFalse(new_df)

    def test_execute_operations_with_existing_feather_id(self):
        intent_name = "rename_columns"
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        parameters = {"groups": [{"old_name": "name", "new_name": "first_name"}], "source_id":
            "6602a3a74475001648200351", "dataframe_alias": "file1"}
        status, metadata_status, df, msg, new_df, details = session.with_transaction(lambda s:Processor(session).execute_operations(intent_name, parameters, user_info=user_info),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(status)
        self.assertTrue(metadata_status)
        self.assertEqual(msg, 'Successfully renamed column(s) name with first_name.')
        self.assertIsNotNone(df)
        self.assertFalse(new_df)
    
    def test_execute_operations_with_existing_feather_id_new(self):
        intent_name = "rename_columns"
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        parameters = {"groups": [{"old_name": "name", "new_name": "first_name"}], "source_id":
        "d89d837c-78e6-4303-9732-6a163e44df71", "dataframe_alias": "file1"}
        status, metadata_status, df, msg, new_df, details = session.with_transaction(lambda s:Processor(session).execute_operations(intent_name, parameters, user_info=user_info),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(status)
        self.assertTrue(metadata_status)
        self.assertEqual(msg, 'Successfully renamed column(s) name with first_name.')
        self.assertIsNotNone(df)
        self.assertFalse(new_df)

    @pytest.mark.skip("This case is not happening so skipping it.")
    def test_execute_operations_with_non_existing_feather_id(self):
        intent_name = "add_columns"
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        parameters = {"groups": [{"columns": ["customer_id"], "default": 1}], "source":
            {"source_id": "6602a3a74475001648202351"}, "output": None}
        # if the source_id given here is not present in db still it executes since feather path is picked from cwf in processor
        status, metadata_status, df, msg, new_df, details = session.with_transaction(lambda s:Processor(session).execute_operations(intent_name, parameters, user_info=user_info),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(status)
        self.assertTrue(metadata_status)
        self.assertEqual(msg, 'Successfully added column(s) customer_id with default value 1.')
        self.assertIsNotNone(df)
        self.assertFalse(new_df)
    
    def test_execute_operations_for_pytool(self):
        parameters = {"code": """print('hello world !!')\na = 5\nb = 10\nprint(f"The sum of a and b is {a + b}")\nprint(DataframeInformation)"""}
        intent_name = "pytool"
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "66729ec22ee1491c32b05b53"
        }
        status, metadata_status, df, msg, new_df, details = session.with_transaction(lambda s:Processor(session).execute_operations(intent_name, parameters, user_info=user_info, dataframe_configuration={}),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(status)       

    # @pytest.mark.skip("will fix")
    def test_execute_operations_for_pytool_with_import_statements_in_code(self):
        parameters = {"code": """\nimport pandas as pd\ndef sample(a):\n    df=pd.DataFrame()\n    print("empty Dataframe",df)	\n    print("sampleWord",a)\nsample("utkarsh")"""}
        intent_name = "pytool"
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "66729ec22ee1491c32b05b53"
        }
        status, metadata_status, df, msg, new_df, details = session.with_transaction(lambda s:Processor(session).execute_operations(intent_name, parameters, user_info=user_info, dataframe_configuration={}),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(status)     

    def test_execute_operations_with_non_existing_chat_id(self):
        intent_name = "add_columns"
        user_info = {
            "user_id": "65ce024b47ff1fc8d6ae2bb1",
            "chat_id": "65cb43f2127a5f38718b9d6f"
        }
        parameters = {"groups": [{"columns": ["customer_id"], "default": 1}], "source":
            {"source_id": "6602a3a74475001648202351"}, "export_name": "file1.csv"}
        with pytest.raises(Exception) as test_func:
            resp =  session.with_transaction(lambda s:Processor(session).execute_operations(intent_name,parameters,user_info=user_info),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)

    def test_prepare_file_path(self):
        test_file_path = "test_file.txt"
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        expected_file_path = os.path.join(absolute_path, "src", "etl", "transfrom", "hadoop", test_file_path)
        success, result_file_path = session.with_transaction(lambda s:Processor(session).prepare_file_path(test_file_path),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(expected_file_path, result_file_path)
        self.assertTrue(success)

    def test_preview(self):
        feather_id = "6602a3a74475001648200351"
        alias = "customer"
        success, preview_info = session.with_transaction(lambda s:Processor(session).preview(feather_id, alias),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_result = [{'_id': '6602a3a74475001648200351', 'alias': 'customer', 'total_records': 4, 'total_records_dataframe': 4, 'columns': [{'name': 'id', 'dataType': 'int64'
                        }, {'name': 'name', 'dataType': 'object'}, {'name': 'age', 'dataType': 'int64'}, {'name': 'join_date', 'dataType': 'datetime64[ns]'}], 'data': [{'id': 1,
                        'name': 'Alice', 'age': 25, 'join_date': '2022-01-01'}, {'id': 2, 'name': 'Bob', 'age': 30, 'join_date': '2022-02-15'}, {'id': 3, 'name': 'Charlie', 'age'
                        : 35, 'join_date': '2022-03-20'}, {'id': 4, 'name': 'David', 'age': 40, 'join_date': '2022-04-10'}]}]
        self.assertEqual(expected_result, preview_info)
        self.assertTrue(success)

    def test_preview_with_non_existing_feather_id(self):
        feather_id = "6602a3a72275001648200351"
        alias = "customer"
        success, preview_info = session.with_transaction(lambda s:Processor(session).preview(feather_id, alias),
                write_concern=wc_majority,
                read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(preview_info, [])
        
    def test_execute_export(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        intent_name = "add_columns"
        parameters = {"groups": [{"columns": ["school"], "default": "MNS"}], "source":
            {"source_id": "6602a3a74475001648200351"}}
        result, id, export_name = session.with_transaction(lambda s:Processor(session).execute_export(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        

        self.assertEqual("6602a3a74475001648200351", id)
        self.assertEqual("6602a3a74475001648200351.csv", export_name)
        self.assertEqual(True, result)

    def test_execute_export_false(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        intent_name = "add_columns"
        parameters = {"groups": [{"columns": ["school"], "default": "MNS"}], "source":
            {"source_id": None}}
        with pytest.raises(ExecuteException) as test_function:
            session.with_transaction(lambda s:Processor(session).execute_export(user_info, intent_name, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual("Failed to execute the operation ' execute_export'.", str(test_function.value))


if __name__ == '__main__':
    unittest.main()
