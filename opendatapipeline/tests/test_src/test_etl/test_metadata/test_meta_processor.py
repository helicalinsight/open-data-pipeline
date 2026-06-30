import os.path
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.etl.metadata.meta_processor import MetaProcessor
from src.exceptions.exception import *
from .....tests.create_data import setup_files
from src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()


class TestProcessor(unittest.TestCase):      
    def setUp(self):
        setup_files()
        self.client = MongoConnector().client
        self.session = self.client._Database__client.start_session()

    def test_execute_file(self):
        source = "file"
        args = {"user_id": "65365001d9654d9ec1172f81", "chat_id": "65cb43f2007a5f38718b9f11", "type": "csv",
                "file_id": "c28a8f59-e57b-4983-8911-83474ad2c4a2", "file_name": "data1"}
        success, inserted_id = session.with_transaction(lambda s:MetaProcessor(session).execute(source, **args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        self.assertIsNotNone(inserted_id)

    def test_execute_file1(self):
        source = "file"
        args = {"user_id": "65365001d9654d9ec1172f81", "chat_id": "65cb43f2007a5f38718b9f11", "type": "csv",
                "file_id": "c28a8f59-e57b-4911-8911-83474ad2c4a2", "file_name": "data2"}
        success, inserted_id = session.with_transaction(lambda s:MetaProcessor(session).execute(source, **args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        self.assertIsNotNone(inserted_id)

    def test_execute_file2(self):
        source = "file"
        args = {"user_id": "65365001d9654d9ec1172f81", "chat_id": "65cb43f2007a5f38718b9f11", "type": "csv",
                "file_id": "c28a8f59-e57b-4983-8923-83474ad2c4a2", "file_name": "data3"}
        success, inserted_id = session.with_transaction(lambda s:MetaProcessor(session).execute(source, **args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        self.assertIsNotNone(inserted_id)

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_execute_database(self):
        source = "database"
        args = {"user_id": "65365001d9654d9ec1172f87", "chat_id": "65cb43f2007a5f38718b9f77", "type": "table",
                "connection_id": "654879fe42a09b96f228302a", "database_name": "astra",
                "catalog": "helical.test_sample3", "file_name": "test_sample3"
                }
        success, inserted_id = session.with_transaction(lambda s:MetaProcessor(session).execute(source, **args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        self.assertIsNotNone(inserted_id)

    def test_prepare_file_path(self):
        test_file_path = "test_file.txt"
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../.."))
        expected_file_path = os.path.join(absolute_path, "hadoop_local", test_file_path).replace("\\", '/')
        success, result_file_path = session.with_transaction(lambda s:MetaProcessor(session).prepare_file_path(test_file_path),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(success)
        self.assertEqual(expected_file_path, result_file_path)

    def test_extract_file(self):
        source = "file"
        args = {"user_id": "65365001d9654d9ec1172f81", "chat_id": "65cb43f2007a5f38718b9f11", "type": "csv",
                "file_id": "c28a8f59-e57b-4983-8911-83474ad2c4c1", "file_name": "dept"}
        success, df = session.with_transaction(lambda s:MetaProcessor(session).extract(source, **args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        self.assertEqual(['public_id', 'firstname', 'lastname', 'age', 'dob', 'zipcode', 'address']
                         , df.columns.tolist())

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_extract_postgres_database_with_vpn(self):
        source = "database"
        args = {"user_id": "65365001d9654d9ec1172f87", "chat_id": "65cb43f2007a5f38718b9f77", "type": "table",
                "connection_id": "654879fe42a09b96f228302c", "database_name": "postgres",
                "catalog": "employee", "file_name": "order_info"
                }
        success, df =session.with_transaction(lambda s:MetaProcessor(session).extract(source, **args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        self.assertEqual(['first_name', 'last_name', 'age', 'sex', 'income'], df.columns.tolist())

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_extract_astra_database_with_vpn(self):
        source = "database"
        args = {"user_id": "65365001d9654d9ec1172f87", "chat_id": "65cb43f2007a5f38718b9f77", "type": "table",
                "connection_id": "654879fe42a09b96f228302a", "database_name": "astra",
                "catalog": "helical.test_sample3", "file_name": "test_sample3"
                }
        success, df =session.with_transaction(lambda s:MetaProcessor(session).extract(source, **args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        self.assertEqual(['state', 'address_2', 'latitude', 'location', 'longitude'], df.columns.tolist())

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_read_table_with_vpn(self):
        args = {"user_id": "65365001d9654d9ec1172f87", "chat_id": "65cb43f2007a5f38718b9f77", "type": "table",
                "connection_id": "654879fe42a09b96f228302c", "database_name": "postgres",
                "catalog": "employee", "file_name": "order_info"
                }
        success, df = session.with_transaction(lambda s:MetaProcessor(session).read_table(**args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(success)
        self.assertEqual(['first_name', 'last_name', 'age', 'sex', 'income'], df.columns.tolist())

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_read_table_mysql(self):
        args = {"user_id": "65365001d9654d9ec1172f87", "chat_id": "65cb43f2007a5f38718b9f77", "type": "table",
                "connection_id": "654879fe42a09b96f228303e", "database_name": "mysql",
                "catalog": "staff", "columns": []
                }
        success, df = session.with_transaction(lambda s:MetaProcessor(session).read_table(**args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(success)
        self.assertEqual(['staff_id', 'first_name', 'last_name', 'address_id', 'picture', 'email', 'store_id', 'active', 'username', 'password', 'last_update'], df.columns.tolist())

    def test_read_file(self):
        args = {"user_id": "65365001d9654d9ec1172f81", "chat_id": "65cb43f2007a5f38718b9f71", "type": "csv",
                "file_id": "c28a8f59-e57b-4983-8911-83474ad2c4c1", "file_name": "dept"}
        success, df = session.with_transaction(lambda s:MetaProcessor(session).read_file(**args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        self.assertEqual(['public_id', 'firstname', 'lastname', 'age', 'dob', 'zipcode', 'address'], df.columns.tolist())

    def test_read_file_for_settings(self):
        args = {"user_id": "65365001d9654d9ec1172f81", "chat_id": "65cb43f2007a5f38718b9f71", "type": "csv",
                "file_id": "c28a8f59-e57b-4983-8911-83474ad2c4c1", "file_name": "dept"}
        success, df = session.with_transaction(lambda s:MetaProcessor(session).read_file(**args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)
        self.assertEqual(len(df), 12)
        self.assertEqual(['public_id', 'firstname', 'lastname', 'age', 'dob', 'zipcode', 'address'], df.columns.tolist())

    def test_generate_metadata(self):
        args = {"user_id": "65365001d9654d9ec1172f81", "chat_id": "65cb43f2007a5f38718b9f71", "type": "csv",
                "file_id": "c28a8f59-e57b-4983-8911-83474ad2c4c1", "file_name": "dept"}
        read_success, df = session.with_transaction(lambda s:MetaProcessor(session).read_file(**args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(read_success)
        success, metadata = MetaProcessor(self.session).generate_metadata(df)
        self.assertTrue(success)
        self.assertEqual(metadata['column_information']['column_names'],
                         ['public_id', 'firstname', 'lastname', 'age', 'dob', 'zipcode', 'address'])
        self.assertEqual(metadata['column_information']['datatypes'],
                         {'public_id': 'int64', 'firstname': 'object', 'lastname': 'object', 'age': 'int64', 'dob': 'object', 'zipcode': 'int64', 'address': 'object'})

    def test_generate_data_profile(self):
        args = {"user_id": "65365001d9654d9ec1172f81", "chat_id": "65cb43f2007a5f38718b9f71", "type": "csv",
                "file_id": "c28a8f59-e57b-4983-8911-83474ad2c4c1", "file_name": "dept"}
        read_success, df = session.with_transaction(lambda s:MetaProcessor(session).read_file(**args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, data_profile = MetaProcessor(self.session).generate_data_profile(df)
        self.assertTrue(success)
        self.assertTrue(read_success)
        expected_data_profile ={'columns': ['public_id', 'firstname', 'lastname', 'age', 'dob', 'zipcode', 'address'],
                                'concat': [], 'date_format': [{'dob': {'format': '%Y-%m-%d'}}],
                                'deduplicate': [], 'drop_all_columns_except': [], 'drop_columns': [],
                                'filter': [], 'rename_columns': [], 'replace_special_characters': [],
                                'sort': [], 'split': []}

        self.assertEqual(expected_data_profile, data_profile)

    def test_upload_feather(self):
        args= {"user_id": "65365001d9654d9ec1172f81", "chat_id": "65cb43f2007a5f38718b9f71", "type": "csv",
                "file_id": "c28a8f59-e57b-4983-8911-83474ad2c4c1", "file_name": "dept"}
        success, df = session.with_transaction(lambda s:MetaProcessor(session).read_file(**args),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../.."))
        file_path = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f81", ".cache", "65cb43f2007a5f38718b9f71",
                                 "c60ea0f2-c5e3-4ff4-8a66-18d835f4f841.feather")
        success = MetaProcessor(self.session).upload_feather(file_path, df)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(file_path))

    def test_save_history_existing(self):
        chat_id= "65cb43f2007a5f38718b9d6a"
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
        success = session.with_transaction(lambda s:MetaProcessor(session).save_history(chat_id, history),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(success)

    @patch("src.etl.metadata.meta_processor.MetaProcessor.execute")
    def test_execute_s3(self, mock_execute):
        mock_execute.return_value = (True, "dummy_id")
        source = "s3"
        args = {
            "user_id": "65365001d9654d9ec1172f87",
            "chat_id": "65cb43f3007a5f38718b9f77",
            "type": ".csv",
            "connection_id": "654879fe22a09b96f228302b",
            "database_name": "s3",
            "catalog": "2017_Order_Data.csv",
            "file_name": "2017_Order_Data"
        }
        mock_execute.return_value = (True, "mock_inserted_id")
        success, inserted_id = session.with_transaction(
            lambda s: MetaProcessor(s).execute(source, **args),
            write_concern=WriteConcern("majority"),
            read_preference=ReadPreference.PRIMARY,
        )
        self.assertTrue(success)
        self.assertEqual(inserted_id, "mock_inserted_id")
        mock_execute.assert_called_once_with(source, **args)
        

if __name__ == '__main__':
    unittest.main()