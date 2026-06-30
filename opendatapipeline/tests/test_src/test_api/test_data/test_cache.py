import unittest
from unittest.mock import MagicMock
from bson import ObjectId
from src.models.mongo.mongo_factory import MongoFactory
from src.models.connector import MongoConnector
from src.exceptions.exception import MongoException
from src.api.data.cache import Cache

from src.models.connector import MongoConnector

mongo_client = MongoConnector()
mongo_client = mongo_client.client

from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestCache(unittest.TestCase):
    def setUp(self):
        self.mongo_connector_mock = MagicMock(spec=MongoConnector)
        self.mongo_factory_mock = MagicMock(spec=MongoFactory)
        self.cache = Cache(session=session)
        # self.cache._cache_collection = self.mongo_factory_mock

    def test_create_success(self):
        data = {
        "chat_id": "65cb43f2007a5f38718b9d6a",
        "dataframe_alias": "customers-100",
        "export_name": "exported_file.csv",
        "export_path": "hadoop_local/export/65365001d9654d9ec1172f87/dept.csv",
        "feather_file_path": "hadoop_local/65365001d9654d9ec1172f87/.cache/65cb43f2007a5f38718b9d6f/be687a30-1329-4639-a606-16f083afa6e6.feather",
        "file_name": "customers-100",
        "source_id": "6602a3a74475001648200351",
        "type": "csv",
        "user_id": "6619156aa5f4c5c1b01e4d07",
        "metadata": {
            "file_information": {},
            "column_information": {
            "column_names": [
                "id",
                "name",
                "age",
                "join_date",
                "school"
            ],
            "datatypes": {
                "id": "int64",
                "name": "object",
                "age": "int64",
                "join_date": "datetime64[ns]",
                "school": "object"
            },
            "num_of_columns": 5,
            "num_of_rows": 4
            },
            "statistics": {},
            "data_classification": {}
        }
        }

        success, result = self.cache.create(data)
        self.assertTrue(success)
        self.assertIsInstance(result, ObjectId)

    def test_get_success(self):
        _id = "6602a3a74475001648280351"

        success, result = self.cache.get(_id)

        self.assertTrue(success)


    def test_get_by_fields_success(self):
        _id = "665480ea9b105cc5e3723a73"
        user_id = "6619156aa5f4c5c1b01e4d07"
        chat_id = "65cb43f2007a5f38718b9d6a"
        
        success, result = self.cache.get_by_fields(_id, user_id, chat_id)

        self.assertTrue(success)
        self.assertEqual(result.get("source_id"), "665480ea9b105cc5e3723a73")

    def test_filter_success(self):
        query = {"_id": ObjectId("6602a3a74475001648280351")}

        success, result = self.cache.filter(query)

        self.assertTrue(success)
        self.assertEqual(len(result), 1)

    def test_filter_empty(self):
        query = {"source_id": "nonexistent_value"}
        success, result = self.cache.filter(query)

        self.assertFalse(success)
        self.assertEqual(result, [])

    def test_update_success(self):
        _id = "6602a3a74475001648280351"
        key = "dataframe_alias"
        data = "new_value"

        success, modified_count = self.cache.update(_id, key, data)

        self.assertTrue(success)
        self.assertEqual(modified_count, 1)

    def test_delete_success(self):
        _id = "662bb3d788e28e8af8639eb8"
        
        success, inserted_id = self.cache.create({"_id": ObjectId(_id)})

        success, deleted_count = self.cache.delete(inserted_id)

        self.assertTrue(success)
        self.assertEqual(deleted_count, 1)
