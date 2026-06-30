import mongomock
import unittest
import pytest

from src.models.mongo.mongo_files import MongoFiles
from src.exceptions.exception import *
from src.models.connector import MongoConnector

mongo_client = MongoConnector()
mongo_client = mongo_client.client

from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestMongoFiles(unittest.TestCase):

    def test_get_by_file_id(self):
        user_id = "65365001d9654d9ec1172f81"
        file_id = "c28a8f59-e57b-4983-8911-83474ad2c4c1"
        files = session.with_transaction(lambda s:MongoFiles(mongo_client, "files", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        success,actual_result = files.get_by_file_id(user_id, file_id)
        self.assertTrue(success)
        self.assertEqual("c28a8f59-e57b-4983-8911-83474ad2c4c1", actual_result.get("file_id"))

    def test_get_by_file_id_non_existing_user(self):
        user_id = "65365001d9654d9ec1172f84"
        file_id = "c28a8f59-e57b-4983-8911-83474ad2c4d9"
        files = session.with_transaction(lambda s:MongoFiles(mongo_client, "files", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        with pytest.raises(MongoException) as test_function:
          files.get_by_file_id(user_id, file_id)   
        self.assertEqual("Failed to get details by file id.", str(test_function.value))

    def test_get_by_non_existing_file_id(self):
        user_id = "65365001d9654d9ec1172f81"
        file_id = "c28a8f59-e57b-4983-8911-83474ad2c4c8"
        files = session.with_transaction(lambda s:MongoFiles(mongo_client, "files", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        files = session.with_transaction(lambda s:MongoFiles(mongo_client, "files", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        with pytest.raises(MongoException) as test_function:
          files.get_by_file_id(user_id, file_id)   
        self.assertEqual("Failed to get details by file id.", str(test_function.value))

    def test_update_by_file_id(self):
        user_id = "65365001d9654d9ec1172f81"
        file_id = "c28a8f59-e57b-4983-8911-83474ad2c4c1"
        file_info = {"metadata":  {"file_information": {
                                      "file_name": "departments.csv",
                                      "file_format": "csv",
                                      "file_size": 90
                                    }, "available":"True"}}
        files = session.with_transaction(lambda s:MongoFiles(mongo_client, "files", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success,actual_result = files.update_by_file_id(user_id, file_id, file_info)
        expected_result = 1
        self.assertEqual(actual_result, expected_result)

    def test_update_by_file_id_non_existing_user(self):
        user_id = "65365001d9654d9ec1172f82"
        file_id = "c28a8f59-e57b-4983-8911-83474ad2c4c1"
        file_info = {"metadata":  {"file_information": {
                                      "file_name": "departments.csv",
                                      "file_format": "csv",
                                      "file_size": 90
                                    }, "available":"True"}}
        files = session.with_transaction(lambda s:MongoFiles(mongo_client, "files", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = files.update_by_file_id(user_id, file_id, file_info)
        expected_result = 0
        self.assertEqual(actual_result, expected_result)

    def test_update_by_non_existing_file_id(self):
        user_id = "65365001d9654d9ec1172f82"
        file_id = "c28a8f59-e57b-4983-8911-83474ad2c4c9"
        file_info = {"metadata":  {"file_information": {
                                      "file_name": "departments.csv",
                                      "file_format": "csv",
                                      "file_size": 90
                                    }, "available":"True"}}
        files = session.with_transaction(lambda s:MongoFiles(mongo_client, "files", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success,actual_result = files.update_by_file_id(user_id, file_id, file_info)
        expected_result = 0
        self.assertEqual(actual_result, expected_result)



