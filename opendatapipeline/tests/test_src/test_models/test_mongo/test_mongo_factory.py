import mongomock
import unittest
from bson import ObjectId
import pytest

from src.models.mongo.mongo_factory import MongoFactory
from src.exceptions.exception import *
from src.models.connector import MongoConnector

mongo_client = MongoConnector()
mongo_client = mongo_client.client

from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

@pytest.mark.skip()
class TestMongoCollections(unittest.TestCase):
    def test_get_by_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.get_by_id("665480a59b105cc5e3723a70")
        expected_user_id = "6619156aa5f4c5c1b01e4d07"
        self.assertTrue(success)
        self.assertEqual(expected_user_id, actual_result.get("user_id"))

    def test_get_by_id_non_existing(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        with pytest.raises(MongoException) as test_function:
            chats.get_by_id("65c4f60439598679e7f4c352")
        self.assertEqual("Failed to get data by id", str(test_function.value))

    def test_get_by_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.get_by_user_id("6619156aa5f4c5c1b01e4d07")
        self.assertEqual("6619156aa5f4c5c1b01e4d07", actual_result.get("user_id"))
        self.assertTrue(success)

    def test_get_by_user_id_non_existing(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        with pytest.raises(MongoException) as test_function:
            chats.get_by_user_id("12342")
        self.assertEqual("Failed to get the data by user id.", str(test_function.value))

    def test_insert_one(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, result = chats.insert_one("info", {"name": "anil", "user_id": "6529162a1c40270b6e18ca98"})
        self.assertTrue(success)
        self.assertIsInstance(result, ObjectId)

    def test_update_one_with_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.update_one("665480a59b105cc5e3723a70","toys_3", {"toy1":"doll", "toy2":"car"},"6619156aa5f4c5c1b01e4d07")
        expected_result = 1
        self.assertTrue(success)
        self.assertEqual(actual_result, expected_result)

    def test_update_one_with_non_existing_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, modified_count = chats.update_one("65c4f60439598679e7f4c353","toys_3", {"toy1":"doll", "toy2":"car"},"1234")
        self.assertTrue(success)
        self.assertEqual(0, modified_count)

    def test_update_one_without_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.update_one("665480a59b105cc5e3723a70", "toys", {"toy1":"doll", "toy2":"car"})
        expected_result = 1
        self.assertTrue(success)
        self.assertEqual(actual_result, expected_result)

    def test_update_all_with_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.update_all("665480a59b105cc5e3723a70",
                                                     {"toy1": "doll", "toy2": "car"}, "6619156aa5f4c5c1b01e4d07")
        expected_result = 1
        self.assertTrue(success)
        self.assertEqual(actual_result, expected_result)

    def test_update_all_with_non_existing_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.update_all("665480a59b105cc5e3723a70",
                                                     {"toy1": "doll", "toy2": "car"}, "6609156aa5f4c5c1b01e4d07")
        expected_result = 0
        self.assertTrue(success)
        self.assertEqual(actual_result, expected_result)

    def test_update_all_without_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.update_all("665480a59b105cc5e3723a70",
                                                     {"toy1": "doll", "toy2": "car"})
        expected_result = 1
        self.assertTrue(success)
        self.assertEqual(actual_result, expected_result)

    def test_delete_one_with_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.delete_one("665480a59b105cc5e3723a70", user_id="6619156aa5f4c5c1b01e4d07")
        expected_result = 1
        self.assertTrue(success)
        self.assertEqual(actual_result, expected_result)

    def test_delete_one_with_user_id_and_key(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.delete_one("665480a59b105cc5e3723a70", key="history", user_id="6619156aa5f4c5c1b01e4d07")
        expected_result = 1
        self.assertTrue(success)
        self.assertEqual(actual_result, expected_result)

    def test_delete_one_without_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.delete_one("665480a59b105cc5e3723a70")
        expected_result = 1
        self.assertTrue(success)
        self.assertEqual(actual_result, expected_result)

    def test_delete_one_with_non_existing_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, deleted_count = chats.delete_one("665480a59b105cc5e3723a70", "321")
        self.assertTrue(success)
        self.assertEqual(0, deleted_count)

    def test_delete_all_with_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.delete_all("665480a59b105cc5e3723a70", "6619156aa5f4c5c1b01e4d07")
        expected_result = 1
        self.assertEqual(actual_result, expected_result)

    def test_delete_all_without_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, actual_result = chats.delete_all("665480a59b105cc5e3723a70")
        expected_result = 1
        self.assertEqual(actual_result, expected_result)

    def test_delete_all_with_non_existing_user_id(self):
        chats = session.with_transaction(lambda s:MongoFactory(mongo_client, "chats", session=session),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        success, deleted_count = chats.delete_all("665480a59b105cc5e3723a71", "2345")
        self.assertTrue(success)
        self.assertEqual(0, deleted_count)

if __name__ == '__main__':
    unittest.main()



