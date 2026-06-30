
import unittest
from unittest.mock import patch

from src.api.services.chat.service import ChatService
from ......src.models.connector import MongoConnector
from ......src.models.mongo.mongo_factory import MongoFactory
from ......src.api.data.chat import JobModes
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

mongo = MongoConnector()
mongo_client = mongo.client
chat_collection = MongoFactory(mongo_client, "chats", session=session)

class TestChatService(unittest.TestCase):
    def test_chat_service_create_chat(self):
        response, status_code = session.with_transaction(lambda s:ChatService(session).create_chat("65365001d9654d9ec1172f87", "new_chat"),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_output = 200
        success, chat_doc = chat_collection.get_by_id(response["chat_id"])
        self.assertTrue(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_output)
        self.assertEqual(chat_doc.get("job_mode"), JobModes.LLM.value)

    def test_chat_service_update_chat(self):
        response, status_code = session.with_transaction(lambda s: ChatService(session).update_chat("65365001d9654d9ec1172f87", "65cb43f2007a5f38718b9d6a",
                                                        "new_chat"),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_output = 200
        self.assertTrue(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_output)

    def test_chat_service_get_chats(self):
        response, status_code = session.with_transaction(lambda s: ChatService(session).get_chats("65365001d9654d9ec1172f87"),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_output = 200
        self.assertTrue(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_output)

    def test_chat_service_delete_chat(self):
        response, status_code = session.with_transaction(lambda s: ChatService(session).delete_chat("65365001d9654d9ec1172f87", "65365001d9654d9ec1172f87"),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_output = 500
        self.assertFalse(response['success'])
        self.assertEqual(status_code, expected_output)

    def test_chat_service_get_information(self):
        response, status_code = session.with_transaction(lambda s: ChatService(session).get_information("65cb43f2007a5f38718b9d6a"),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        

        self.assertEqual(200, status_code)
    
    def test_get_information_with_invalid_chat_id(self):
        response, status_code = session.with_transaction(
            lambda s: ChatService(session).get_information("65cb43f2117a5f38718b9d6a"),
            read_concern=ReadConcern("local"),
            write_concern=wc_majority,
            read_preference=ReadPreference.PRIMARY
        )
        self.assertEqual(204, status_code)

    def test_chat_service_delete_chat_with_job(self):
        with patch('src.api.services.airflow_service.service.AirflowAPI.delete_dag', return_value={'success': True}):
            response, status_code = session.with_transaction(
                lambda s: ChatService(session).delete_chat(
                    "65365001d9654d9ec1172f81", 
                    "66e7dfa92601d90a3465f9fc"
                ),
                read_concern=ReadConcern("local"),
                write_concern=wc_majority,
                read_preference=ReadPreference.PRIMARY,
            )
        
            expected_output = 200
            self.assertTrue(response['success'])
            self.assertEqual(status_code, expected_output)
        
    def test_chat_service_update_chat_mode(self):
        response, status_code = session.with_transaction(lambda s:ChatService(session).create_or_update_data("6757ddf8de0e916ac22d4ad7", {"mode":JobModes.ACE.value}),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)

        success, chat_doc = chat_collection.get_by_id("6757ddf8de0e916ac22d4ad7")
        self.assertEqual(status_code, 201)
        self.assertEqual(chat_doc.get("job_mode"), JobModes.ACE.value)
        
    @patch('src.api.services.chat.service.ChatService._rebuild_cache_with_history_for_chat')
    @patch('src.api.services.chat.service.ChatService._invalidate_cache_for_chat')
    def test_chat_service_update_chat_mode_from_llm_to_yaml(self, mock_invalidate_cache_for_chat, mock_rebuild_cache):
        mock_invalidate_cache_for_chat.return_value = True
        mock_rebuild_cache.return_value = True
        
        response, status_code = session.with_transaction(
            lambda s:ChatService(session).update_mode("6757ddf8de0e916ac22d4ad7", "llm"),
            write_concern=wc_majority,
            read_preference=ReadPreference.PRIMARY)
        
        assert status_code == 204
        
        response, status_code = session.with_transaction(
            lambda s:ChatService(session).update_mode("6757ddf8de0e916ac22d4ad7", "yaml"),
            write_concern=wc_majority,
            read_preference=ReadPreference.PRIMARY)
        
        assert status_code == 204
        
    def test_chat_service_update_dms_progress(self):
        resp, _ = session.with_transaction(lambda s:ChatService(session).create_chat("65365001d9654d9ec1172f87", "dms_test_chat", "DMS"), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        chat_id = resp["chat_id"]
        
        payload = {
            "dms_migration_mode": "offline",
            "source_details": {"type": "postgres"},
            "destination_details": {"type": "mysql"}
        }
        response, status_code = session.with_transaction(lambda s:ChatService(session).update_dms_progress("65365001d9654d9ec1172f87", chat_id, payload), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        
        self.assertEqual(status_code, 200)
        self.assertTrue(response['success'])
        
        success, chat_doc = chat_collection.get_by_id(chat_id)
        self.assertEqual(chat_doc.get("dms_migration_mode"), "offline")
        self.assertEqual(chat_doc.get("source_details"), {"type": "postgres"})

    def test_chat_service_update_dms_progress_invalid_mode(self):
        resp, _ = session.with_transaction(lambda s:ChatService(session).create_chat("65365001d9654d9ec1172f87", "dts_test_chat", "DTS"), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        chat_id = resp["chat_id"]
        
        payload = {"dms_migration_mode": "offline"}
        response, status_code = session.with_transaction(lambda s:ChatService(session).update_dms_progress("65365001d9654d9ec1172f87", chat_id, payload), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        
        self.assertEqual(status_code, 400)
        self.assertFalse(response['success'])
        
    def test_chat_service_update_dms_progress_invalid_chat(self):
        payload = {"dms_migration_mode": "offline"}
        response, status_code = session.with_transaction(lambda s:ChatService(session).update_dms_progress("65365001d9654d9ec1172f87", "invalid_id_123", payload), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        
        self.assertEqual(status_code, 400)
        self.assertFalse(response['success'])

    def test_chat_service_get_dms_progress(self):
        resp, _ = session.with_transaction(lambda s:ChatService(session).create_chat("65365001d9654d9ec1172f87", "dms_get_test_chat", "DMS"), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        chat_id = resp["chat_id"]
        
        payload = {
            "dms_migration_mode": "offline",
            "source_details": {"type": "postgres"},
            "destination_details": {"type": "mysql"}
        }
        session.with_transaction(lambda s:ChatService(session).update_dms_progress("65365001d9654d9ec1172f87", chat_id, payload), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        
        response, status_code = session.with_transaction(lambda s:ChatService(session).get_dms_progress("65365001d9654d9ec1172f87", chat_id), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        
        self.assertEqual(status_code, 200)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['dms_migration_mode'], "offline")
        self.assertEqual(response['data']['service_mode'], "DMS")
        self.assertEqual(response['data']['chat_id'], chat_id)

    def test_chat_service_get_dms_progress_invalid_mode(self):
        resp, _ = session.with_transaction(lambda s:ChatService(session).create_chat("65365001d9654d9ec1172f87", "dts_get_test_chat", "DTS"), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        chat_id = resp["chat_id"]
        
        response, status_code = session.with_transaction(lambda s:ChatService(session).get_dms_progress("65365001d9654d9ec1172f87", chat_id), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        
        self.assertEqual(status_code, 400)
        self.assertFalse(response['success'])

    def test_chat_service_get_dms_progress_invalid_chat(self):
        response, status_code = session.with_transaction(lambda s:ChatService(session).get_dms_progress("65365001d9654d9ec1172f87", "invalid_id_get_123"), read_concern=ReadConcern("local"), write_concern=wc_majority, read_preference=ReadPreference.PRIMARY)
        
        self.assertEqual(status_code, 400)
        self.assertFalse(response['success'])



if __name__ == '__main__':
    unittest.main()
