import unittest
from uuid import UUID

from src.api.services.export_config.service import ExportConfigService
from ......src.models.mongo.mongo_factory import MongoFactory
from bson import ObjectId
from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

chats_collection = MongoFactory(MongoConnector().client, "chats", session=session)
class TestExportConfig(unittest.TestCase):

    def test_list_catalogs_service_without_valid_data(self):
        req_data = {}
        user_id = ""
        response, status_code = session.with_transaction(lambda s:ExportConfigService(session).export_config(req_data, user_id),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        print(response, status_code)
        expected_code= 400
        expected_output = {'success': False, 'msg': 'Failed to export configuration'}
        self.assertFalse(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)

   
    def test_export_config_update_history(self):
        # Setup initial chat document
        chat_id = "666bd9ed87c043982cd173d6"
        # Request data
        req_data = {
            "chat_id": chat_id,
            "details": {
                "type": "localstorage",
                "files_list": [{"source_id": "666bd9fc87c043982cd173d8"}]
            },
            "configurations": {"some_config_key": "some_config_value"}
        }
        user_id = "6619156aa5f4c5c1b01e4d07"
        wc_majority = WriteConcern("majority")

        # Call the export_config method within a transaction
        response, status_code = session.with_transaction(
            lambda s: ExportConfigService(session).export_config(req_data, user_id),
            write_concern=wc_majority,
            read_preference=ReadPreference.PRIMARY
        )
        # Check the updated document
        status , updated_chat_document = chats_collection.get_by_id(chat_id)
        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(response["success"], True)
        self.assertEqual(response["msg"], "Export configuration updated")
        self.assertEqual(len(updated_chat_document["history"]), 2)
        
        # Verify UUID is generated correctly
        # self.assertTrue(isinstance(UUID(updated_chat_document["history"][1]["id"], version=4), UUID))

if __name__ == '__main__':
    unittest.main()
