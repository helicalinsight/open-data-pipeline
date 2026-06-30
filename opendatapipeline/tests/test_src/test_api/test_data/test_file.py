import unittest
from unittest.mock import MagicMock
import uuid
from bson import ObjectId
from src.models.mongo.mongo_factory import MongoFactory
from src.models.connector import MongoConnector
from src.exceptions.exception import MongoException
from src.api.data.file import File

from src.models.connector import MongoConnector

mongo_client = MongoConnector()
mongo_client = mongo_client.client

from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestFile(unittest.TestCase):
    def setUp(self):
        self.mongo_connector_mock = MagicMock(spec=MongoConnector)
        self.mongo_factory_mock = MagicMock(spec=MongoFactory)
        self.file = File(session=session)

    def test_create_success(self):
        data = {
            "files": [
                {
                "file_id": "fc1a8abf-29e9-4df0-b793-ef2ddfc938d6",
                "file_name": "Dummy_Data1",
                "file_type": ".csv",
                "file_path": "/home/ubuntu/development/askondata_application/opendatapipeline/hadoop_local/66191b15269b28de01885c4a/sources/flat_files/Dummy_Data.csv",
                "full_name": "Dummy_Data1.csv",
                "metadata": None,
                "json_path": None,
                "available": False
                }
            ],
            "user_id": "6619156aa5f4c5c1b01e4d07"
        }

        success, result = self.file.create(data)
        self.assertTrue(success)
        self.assertIsInstance(result, ObjectId)

    def test_get_success(self):
        _id = "66192b15269b28de01885c4c"

        success, result = self.file.get(_id)

        self.assertTrue(success)

    def test_filter_success(self):
        query = {"_id": ObjectId("661923ef269b28de01885c41")}

        success, result = self.file.filter(query)

        self.assertTrue(success)
        self.assertEqual(len(result), 1)

    def test_filter_empty(self):
        query = {"source_id": "nonexistent_value"}
        success, result = self.file.filter(query)

        self.assertFalse(success)
        self.assertEqual(result, [])

    def test_update_success(self):
        _id = "66192b17369b18de01885c4c"
        key = "user_id"
        data = str(uuid.uuid4())

        success, modified_count = self.file.update(_id, key, data)

        self.assertTrue(success)
        self.assertEqual(modified_count, 1)

    def test_delete_success(self):
        _id = "66192b15269b18de01885c4c"

        success, deleted_count = self.file.delete(_id)

        self.assertTrue(success)
        self.assertEqual(deleted_count, 1)

