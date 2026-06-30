import unittest
from spark_server.pipeline.manager import *
from pyspark.sql import SparkSession
import os
from spark_server.configurations.baseConfig.config import localDirectory

class TestManager(unittest.TestCase):
    # creating the instance of the class Manager
    @classmethod
    def setUpClass(cls):
        cls.base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(cls.base_path, "test_files", "file1.csv")
        file_path2 = os.path.join(cls.base_path, "test_files", "file2.csv")
        cls.spark = SparkSession.builder.appName("TestManager").getOrCreate()
        cls.pipeline = [
                    {'function': 'read_files', 
                    'parameters': 
                        {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 
                        'output': {'df_id': '6651805f1577224b6b08aa6d'}}, 
                        
                    {'function': 'read_files', 
                    'parameters': 
                    {'file_id': 'e8ea0c4d-28c5-4f00-9d69-54a1aee43ffb', 'file_name': 'file2'}, 
                    'output': {'df_id': '6651805f1577224b6b08aa6e'}}, 
                    
                    {'function': 'union', 
                    'parameters': 
                    {'groups': [{'columns': None}], 
                    'df_id': ['6651805f1577224b6b08aa6d', '6651805f1577224b6b08aa6e'], 
                    'file_names': ['file1', 'file2'], 'file_id': None}, 
                    'output': {'df_id': '6651809b1577224b6b08aa6f'}}, 
                    
                    {'function': 'rename_columns', 
                    'parameters': {'groups': [{'old_name': 'name', 'new_name': 'full_name'}], 
                    'df_id': '6651809b1577224b6b08aa6f'}}, 
                    
                    {'function': 'export', 
                    'parameters': 
                    {"export_name": "output", "df_id": "6651809b1577224b6b08aa6f", "user_id": "6641ad931a3ba5058c56af19", "chat_id": "665e937aaea87247ea567131"}}]
        cls.connection_id = {
            'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1': {
                'type': 'file',
                'details': {
                    'file_name': 'file1.csv',
                    'file_type': 'csv',
                    'file_path': file_path1
                }
            },
            'e8ea0c4d-28c5-4f00-9d69-54a1aee43ffb': {
                'type': 'file',
                'details': {
                    'file_name': 'file2.csv',
                    'file_type': 'csv',
                    'file_path': file_path2
                }
            }
        }
        cls.config = {}
        cls.schedule_conf = {"schedule_id":"123", "run_id": "456"}
        cls.manager = Manager(cls.pipeline, cls.connection_id, cls.config, cls.spark, cls.schedule_conf)
        cls.unsorted_pipeline = [{'function': 'union', 'parameters': {'groups': [{'columns': None}], 'df_id': ['6651805f1577224b6b08aa6d', '6651805f1577224b6b08aa6e'], 'file_names': ['file1', 'file2'], 'file_id': None}, 'output': {'df_id': '6651809b1577224b6b08aa6f'}}, {'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}}, {'function': 'rename_columns', 'parameters': {'groups': [{'old_name': 'name', 'new_name': 'full_name'}], 'df_id': '6651809b1577224b6b08aa6f'}}, {'function': 'read_files', 'parameters': {'file_id': 'e8ea0c4d-28c5-4f00-9d69-54a1aee43ffb', 'file_name': 'file2'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}}, {'function': 'export', 'parameters': {"export_name": "output", "user_id": "6641ad931a3ba5058c56af19", "chat_id": "665e937aaea87247ea567131", "df_id": "6651809b1577224b6b08aa6f"}}]

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_manage(self):
        self.manager.manage()
        base_path=localDirectory._path
        expected_path = os.path.join(base_path, "65dc3fb832b5b2a5665841fb", "output", "output")
        #expected_path = f"{self.base_path}/spark_server/SCHEDULED_OUTPUT/output"
        self.assertTrue(any(filename.startswith("part-") and filename.endswith(".csv") for filename in
                            os.listdir(expected_path)))

    def test_sort_pipeline(self):
        sorted_pipeline = self.manager.sort_pipeline(self.unsorted_pipeline)
        self.assertEqual(self.pipeline, sorted_pipeline)


if __name__ == '__main__':
    unittest.main()
