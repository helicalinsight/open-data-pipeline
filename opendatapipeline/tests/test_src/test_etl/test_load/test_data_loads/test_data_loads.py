import os
import unittest
import uuid
import pytest
import pandas
from src.etl.load.data_loads.data_loads import DataLoads
from src.exceptions.exception import *
from src.models.connector import MongoConnector
from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()


class TestDataLoads(unittest.TestCase):
    # creating the instance of the class Manager

    def test_export_manager_without_export_name(self):
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"user_id": "65ce024b47ff1fc8d6ae2bb1", "job_id": "j1"}], "source":
            {"source_id": "6602a3a74475001648200351"}}
        user_info = {
            "user_id": "65ce024b47ff1fc8d6ae2bb1",
            "chat_id": "j1"
        }
        success, _id, filename = session.with_transaction(lambda s:DataLoads(session).export(user_info, dataframe, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(success)

    @pytest.mark.skip('file not found issue')
    def test_csv_quoting_for_export(self):
        data = {'col1': [1, 2], 'col2': ['a', 'b']}
        dataframe = pandas.DataFrame(data)
        parameters = {
            "groups": [{"user_id": "65ce024b47ff1fc8d6ae2bb1", "job_id": "j1"}], 
            "source": {"source_id": "6602a3a74475001648200351"}
        }
        user_info = {
            "user_id": "65ce024b47ff1fc8d6ae2bb1",
            "chat_id": "j1"
        }
        success, _id, export_name = session.with_transaction(lambda s:DataLoads(session).export(user_info, dataframe, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        export_path = os.path.join(absolute_path, "hadoop_local", "65ce024b47ff1fc8d6ae2bb1", ".cache", "j1", "export", export_name).replace('\\','/')
        with open(export_path, 'r') as file:
            csv_content = file.read()
        expected_csv_content = '"name","age","marks"\n"pooja","10","40"\n"kavya","11","39"\n"bhavya","12","45"\n'
        self.assertEqual(csv_content, expected_csv_content)

    def test_export(self):
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"user_id": "65ce024b47ff1fc8d6ae2bb1", "job_id": "j1"}], "source":
            {"source_id": "6602a3a74475001648200351"}, "export_name": "file1.csv"}
        user_info = {
            "user_id": "65ce024b47ff1fc8d6ae2bb1",
            "chat_id": "j1"
        }
        success, _id, filename = session.with_transaction(lambda s:DataLoads(session).export(user_info, dataframe, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(success, True)
        self.assertEqual(_id, "6602a3a74475001648200351")
        self.assertEqual(filename, 'file1.csv')

    def test_export_else(self):
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"user_id": None, "job_id": "j1"}], "source":
            {"source_id": "6602a3a74475001648200351"}, "export_name": "file1.csv"}
        user_info = {
            "user_id": None,
            "chat_id": "j1"
        }
        with pytest.raises(UtilsException) as test_function:
            session.with_transaction(lambda s:DataLoads(session).export(user_info, dataframe, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual("Failed to export the file.", str(test_function.value))

    def test_generate_export_path(self):
        user_id = "6602a3a74475001648200351"
        job_id = "j1"
        export_name = "file"
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        export_path = os.path.join("/hadoop_local", user_id, ".cache", job_id, "export", export_name).replace('\\','/')
        success, path = session.with_transaction(lambda s:DataLoads(session).generate_export_path(user_id, job_id, export_name),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(export_path, path)
        self.assertTrue(success)

    def test_generate_export_path_non_existing(self):
        user_id = "6602a3a74475001648200351"
        job_id = str(uuid.uuid4())
        export_name = "file"
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        # export_path = os.path.join(absolute_path, "hadoop_local", user_id, ".cache", job_id, "export", export_name).replace('\\','/')
        export_path = os.path.join("/hadoop_local", user_id, ".cache", job_id, "export", export_name).replace('\\','/')
        success, path = session.with_transaction(lambda s:DataLoads(session).generate_export_path(user_id, job_id, export_name),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(export_path, path)
        self.assertTrue(success)

    def test_generate_export_path_exception(self):
        user_id = None
        job_id = str(uuid.uuid4())
        export_name = "file"
        with pytest.raises(UtilsException) as test_function:
            session.with_transaction(lambda s:DataLoads(session).generate_export_path(user_id, job_id, export_name),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
            
        self.assertEqual("Failed to generate export path.", str(test_function.value))

    def test_update_history(self):
        step = 1
        status = True
        function = "add_columns"
        parameters = {"columns": ["name"], "default": "amit"}
        success, history_entry = session.with_transaction(lambda s:DataLoads(session).update_history(step, status, function, parameters),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        history_entry.pop('id')
        expected_output = {'step': 1, 'status': 'PASS', 'function': 'add_columns',
                           'parameters': {'columns': ['name'], 'default': 'amit'}, 'output': None}
        self.assertEqual(expected_output, history_entry)
        self.assertTrue(success)

    def test_save_history_not_existing(self):
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
            session.with_transaction(lambda s:DataLoads(session).save_history(user_info, history),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
            
        self.assertEqual("Failed to save the history.", str(test_function.value))

    @pytest.mark.run(order=1)
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
        success = session.with_transaction(lambda s:DataLoads(session).save_history(user_info, history),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(success)

    @pytest.mark.run(order=1)
    def test_get_step_number(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d6a"
        }
        success, step_number = session.with_transaction(lambda s: DataLoads(session).get_step_number(user_info),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
       
        self.assertEqual(14, step_number)
        self.assertTrue(success)

    def test_get_step_number_with_non_existing_chat_id(self):
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "65cb43f2007a5f38718b9d20"
        }
        with pytest.raises(UtilsException) as test_function:
            session.with_transaction(lambda s: DataLoads(session).get_step_number(user_info),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
            
        self.assertEqual("Failed to get step number.", str(test_function.value))

if __name__ == '__main__':
    unittest.main()