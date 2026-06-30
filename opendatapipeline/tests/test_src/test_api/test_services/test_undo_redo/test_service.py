import unittest
import mongomock
import pytest

from src.api import app
from src.models.mongo import mongo_factory
from src.api.validators.jwt_authentication import JWTAuthentication
from src.api.services.undo_redo.service import UndoRedoService
from src.models.connector import MongoConnector
from src.models.mongo.mongo_factory import MongoFactory
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
chat_collection = MongoFactory(mongo_client, "chats", session=session)


class TestUndoRedo(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.valid_token = JWTAuthentication().encode("shiv@gmail.com", "65365001d9654d9ec1172f77")

    def test_undo_feature_without_token(self):
        response = self.app.post('/api/v1/undo', json={
            "chat_id":"665480a59b105cc5e3723a70",
        })
        self.assertEqual(response.status_code, 400)

    @pytest.mark.skip
    def test_undo_feature_for_multiple_steps(self):
        user_id = "670e60a261fa9d80ecb984b2"
        chat_id = "675ac1ea23cceabc00088ea0"
        response, status_code = session.with_transaction(lambda s:UndoRedoService(session).undo(user_id, chat_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response["msg"], "Undo Successful")
        
    def test_undo_single_step(self):
        user_id = "670e60a261fa9d80ecb984b2"
        chat_id = "99910f9915753466362512d1"
        
        response, status_code = session.with_transaction(lambda s:UndoRedoService(session).undo(user_id, chat_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY)
        
        self.assertEqual(response["msg"], "Undo Successful")
        
        # get mongo chat to check history got empty
        status, chat = chat_collection.get_by_id(chat_id)
        self.assertEqual(chat["history"], [])
        self.assertEqual(chat["next"][0]["function"], "read_files")
        
    def test_undo_for_invalid_chat_id(self):
        user_id = "670e60a261fa9d80ecb984b2"
        chat_id = "999999999999999999999990"
        
        response, status_code = session.with_transaction(
            lambda s:UndoRedoService(session).undo(user_id, chat_id),
            read_concern=ReadConcern("local"),
            write_concern=wc_majority,
            read_preference=ReadPreference.PRIMARY)
        
        self.assertEqual(response["msg"], "No step to undo")

    def test_undo_feature_for_empty_history(self):
        user_id = "6619156aa5f4c5c1b01e4d07"
        chat_id = "66729ec22ee1491c32b05b60"
        response, status_code = session.with_transaction(lambda s:UndoRedoService(session).undo(user_id, chat_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response["msg"], 'Undo Successful')
    
    def test_undo_feature_for_union(self):
        response = self.app.post('/api/v1/undo', json={
            "chat_id":"66729ec22ee1491c32b05b54",
        }, headers={'Authorization': self.valid_token})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["msg"], "Undo Failed")
    
    @pytest.mark.run(order=1)
    def test_undo_feature_for_add_column(self):
        user_id = "65365001d9654d9ec1172f77"
        chat_id = "66729ec22ee1491c32b05b28"
        response, status_code = session.with_transaction(lambda s:UndoRedoService(session).undo(user_id, chat_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertIn("Undo", response['msg'])

    @pytest.mark.run(order=1)
    def test_undo_feature_for_rename_column(self):
        user_id = "65365001d9654d9ec1172f77"
        chat_id = "66729ec22ee1491c32b05b53"
        response, status_code = session.with_transaction(lambda s:UndoRedoService(session).undo(user_id, chat_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertIn(response["msg"], ["Undo Successful", "Undo Failed"]) 
        
        # with MongoConnector().client._Database__client.start_session() as session:
        #     with session.start_transaction():
        #         cache_collection = MongoFactory(MongoConnector().client, "cache",session=session)
        #         succ,cache = cache_collection.get_by_id_and_value("source_id", "66729ece2ee1491c32b05b54")
        #         column_names = cache.get("metadata").get("column_information").get("column_names")
        #         self.assertIn("first", column_names)
  
    def test_redo_feature_when_redo_is_not_available(self):
        response = self.app.post('/api/v1/redo', json={
            "chat_id":"65cb43f2007a5f38718b9d6e",
        }, headers={'Authorization': self.valid_token})
        self.assertEqual(response.status_code, 500)

    def test_undo_feature_for_edgecase(self):
        user_id = "65365001d9654d9ec1172f77"
        chat_id = "666abcb55232d65bb2791199"
        response, status_code = session.with_transaction(lambda s:UndoRedoService(session).undo(user_id, chat_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertIn(response["msg"], ["Undo Successful", "Undo Failed"])

    def test_undo_for_read_file(self):
        response = self.app.post('/api/v1/undo', json={
            "chat_id":"65cb43f2007a5f38818b9d6f",
        }, headers={'Authorization': self.valid_token})
        succ, chat_doc = chat_collection.get_by_id('65cb43f2007a5f38818b9d6f')
        self.assertEqual(len(chat_doc.get('next')), 1)
        self.assertEqual(response.status_code, 200)
        
    def test_undo_with_three_read_two_delete(self):
        valid_token = JWTAuthentication().encode("shiv@gmail.com", "6619156aa5f4c5c1b01e4d07")
        response = self.app.post('/api/v1/undo', json={"chat_id": "66729ec22ee1491c32b05b11"}, headers={'Authorization': valid_token})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()