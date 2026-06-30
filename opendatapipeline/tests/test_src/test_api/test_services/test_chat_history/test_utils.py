import unittest
from src.api.services.chat_history.utils import ChatHistoryUtil
from src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestChatHistoryUtils(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_extract_user_event_text(self):
        event = {
            "event": "user",
            "parse_data": {
                "metadata": {
                    "value": "User event text"
                }
            }
        }
        expected_text = "User event text"
        extracted_text = session.with_transaction(lambda s:ChatHistoryUtil(session)._extract_event_text(event),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(extracted_text, expected_text)

    def test_extract_text_from_bot_event_custom_data_field(self):
        event = {
            "event": "bot",
            "data": {
                "custom": {
                    "data": {
                        "text": "Bot event custom data text"
                    }
                }
            }
        }
        expected_text = "Bot event custom data text"
        extracted_text = session.with_transaction(lambda s:ChatHistoryUtil(session)._extract_event_text(event),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertEqual(extracted_text, expected_text)

    def test_get_columns_list_with_valid_metadata(self):
        selected_files = [
            {"alias": "file1"},
            {"alias": "file2"}
        ]
        metadata = {
            "file1": [
                {"columns": ["col1", "col2"]}
            ],
            "file2": [
                {"columns": ["col3", "col4"]}
            ]
        }
        expected_columns = ["col1", "col2", "col3", "col4"]

        success, columns_list = session.with_transaction(
            lambda s: ChatHistoryUtil(session)._get_columns_list(selected_files, metadata),
            read_concern=ReadConcern("local"),
            write_concern=wc_majority,
            read_preference=ReadPreference.PRIMARY,
        )

        self.assertTrue(success)
        self.assertEqual(columns_list, expected_columns)

    def test_clear_chat_data_with_valid_input(self):
        langchain = {
            "chat_id": "662a0e02c684482642a80a5f",
            "messages": [
                {
                "message_id": "d6cf2c97-23df-45dc-8fd1-d772b0c5d5db",
                "message": "rename riverside to river ",
                "timestamp": {
                    "$date": "2024-04-25T08:03:48.666Z"
                },
                "stage": "initial",
                "details": {}
                }
            ]
        }
        
        result = session.with_transaction(
                lambda s: ChatHistoryUtil(session)._clear_chat_data(langchain),
                read_concern=ReadConcern("local"),
                write_concern=wc_majority,
                read_preference=ReadPreference.PRIMARY,
        )
        self.assertTrue(result)

    def test_clear_chat_history(self):
        chat = {
            "_id": "66729ec22ee1491c32b05b60",
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_name": "Job 20",
            "files": [
                {
                "source_id": "66729ece2ee1491c32b05b54",
                "alias": "customers-100",
                "type": "csv"
                }],
            "cwf": {
                "source_id": "66729ece2ee1491c32b05b54",
                "alias": "customers-100",
                "type": "csv"
            },
            "history": [],
            }

        result = session.with_transaction(
            lambda s: ChatHistoryUtil(session)._clear_chat_history(chat),
            read_concern=ReadConcern("local"),
            write_concern=wc_majority,
            read_preference=ReadPreference.PRIMARY,
        )
        self.assertTrue(result)



if __name__ == '__main__':
    unittest.main()
