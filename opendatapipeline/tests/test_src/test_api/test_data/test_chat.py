import unittest
from unittest.mock import MagicMock
from bson import ObjectId
from src.models.mongo.mongo_factory import MongoFactory
from src.models.connector import MongoConnector
from src.api.data.chat import Chat

from src.models.connector import MongoConnector

mongo_client = MongoConnector()
mongo_client = mongo_client.client

from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestChat(unittest.TestCase):
    def setUp(self):
        self.mongo_connector_mock = MagicMock(spec=MongoConnector)
        self.mongo_factory_mock = MagicMock(spec=MongoFactory)
        self.chat = Chat(session=session)

    def test_create_success(self):
        data = {
            "chat_name": "Job 20",
            "cwf": {
                "source_id": "665480ea9b105cc5e3723a73",
                "alias": "union_wouyfrpI",
                "type": "csv"
            },
            "files": [
                {
                "source_id": "6602a3a74475001648200350",
                "alias": "bank_customers",
                "type": "xlsx"
                },
                {
                "source_id": "6602a3a74475001648200351",
                "alias": "customers-100",
                "type": "csv"
                },
                {
                "source_id": "6602a3a74475001648200352",
                "alias": "industry",
                "type": "csv"
                }
            ],
            "history": [
                {
                "id": "8d683e6e-ce2d-4f73-a3e4-82ddf19772b0",
                "step": 0,
                "status": "PASS",
                "function": "read_tables",
                "parameters": {
                    "connection_id": "654879fe42a09b96f228102c",
                    "file_id": "74d82e21-a20f-4097-9181-2502bb2846f5",
                    "table_name": "customers-100-table",
                },
                "output": {
                    "source_id": "6602a3a74475001648200351"
                }
                }
            ],
            "next": [],
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "isChatMode": False
        }

        success, result = self.chat.create(data)
        self.assertTrue(success)
        self.assertIsInstance(result, ObjectId)

    def test_get_success(self):
        _id = "66e7dfa92601d90a3468f9fc"

        success, result = self.chat.get(_id)

        self.assertTrue(success)

    def test_filter_success(self):
        query = {"_id": ObjectId("66e7dfa92601d90a3468f9fc")}

        success, result = self.chat.filter(query)

        self.assertTrue(success)
        self.assertEqual(len(result), 1)

    def test_filter_empty(self):
        query = {"source_id": "nonexistent_value"}
        success, result = self.chat.filter(query)

        self.assertFalse(success)
        self.assertEqual(result, [])

    def test_update_success(self):
        _id = "662a0e02c684482642a80a5f"
        key = "chat_name"
        data = "Updated chat-name"

        success, modified_count = self.chat.update(_id, key, data)

        self.assertTrue(success)
        self.assertEqual(modified_count, 1)

    def test_delete_success(self):
        _id = "66e7dfa92601d90a3464f9fc"

        success, deleted_count = self.chat.delete(_id)

        self.assertTrue(success)
        self.assertEqual(deleted_count, 1)

    def test_append_one_success(self):
        _id = "662a0e02c684482642a80a5f"
        key = "next"
        data = {
            "test-key": "test-value"
        }

        success, modified_count = self.chat.update(_id, key, data)
        self.assertTrue(success)
        self.assertEqual(modified_count, 1)

    @unittest.mock.patch('src.api.services.chat.service.MongoFactory')
    def test_chat_service_get_chats_with_filtering(self, mock_mongo_factory):
        from src.api.services.chat.service import ChatService
        
        # Setup mock chats
        mock_chats = [
            {"_id": ObjectId(), "chat_name": "Job 1", "service_mode": "DMS"},
            {"_id": ObjectId(), "chat_name": "Job 2", "service_mode": "dts"},
            {"_id": ObjectId(), "chat_name": "Job 3"}
        ]
        
        # Configure service mock
        service = ChatService(session=session)
        service.mongo_chats.get_all_by_user_id.return_value = (True, mock_chats)
        
        # Test default (dts) behavior: ignore_fields={"service_mode": "dms"}
        response, status = service.get_chats("dummy_user_id", ignore_fields={"service_mode": "DMS"})
        self.assertEqual(status, 200)
        self.assertTrue(response["success"])
        # Should return Job 2 and Job 3
        self.assertEqual(len(response["chats"]), 2)
        self.assertNotIn("Job 1", [c["chat_name"] for c in response["chats"]])
        
        # Test dms behavior: filter_fields={"service_mode": "dms"}
        response, status = service.get_chats("dummy_user_id", filter_fields={"service_mode": "DMS"})
        self.assertEqual(status, 200)
        self.assertTrue(response["success"])
        # Should only return Job 1
        self.assertEqual(len(response["chats"]), 1)
        self.assertEqual(response["chats"][0]["chat_name"], "Job 1")
