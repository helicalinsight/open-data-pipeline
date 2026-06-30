import unittest
from bson import ObjectId
import pytest

from src.models.mongo.mongo_messages import MongoMessages
from src.exceptions.exception import *
from src.models.connector import MongoConnector

mongo_client = MongoConnector()
mongo_client = mongo_client.client

from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestMongoCollections(unittest.TestCase):
    def setUp(self) -> None:
        self.client = MongoConnector().client
        self.session = self.client._Database__client.start_session()

    def test_update_one_by_chat_id(self):
        messages =  session.with_transaction(lambda s:MongoMessages(mongo_client, "langchain", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        chat_id = "662a0e02c684482642a80a5f"
        key = "active_loop"
        value = {"name": "Tom"}
        success, actual_result = messages.update_one_by_chat_id(chat_id, key, value)
        self.assertTrue(success)

    def test_update_one_by_non_existing_chat_id(self):
        messages =  session.with_transaction(lambda s:MongoMessages(mongo_client, "langchain", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        chat_id = "65c4f60439598679e7f4c352"
        key = "test_data"
        value = {"name": "Tom"}
        success, updated_count = messages.update_one_by_chat_id(chat_id, key, value)
        self.assertTrue(success)
        self.assertEqual(0, updated_count)

if __name__ == '__main__':
    unittest.main()
