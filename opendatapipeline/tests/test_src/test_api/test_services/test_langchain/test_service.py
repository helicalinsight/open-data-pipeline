from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch, MagicMock
import uuid
from src.api.services.langchain_service.service import LangchainService 
from src.models.connector import MongoConnector
from pymongo.write_concern import WriteConcern
from src.api.services.langchain_service.fallback_executor import FallBackExecutor

wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestLangchainService(unittest.TestCase):
    def setUp(self):
        self.config = {
            "configurable": {
                "user_id": "test_user",
                "chat_id": "test_chat"
            }
        }

    @patch('src.api.services.langchain_service.service.MongoFactory')
    @patch('src.core.llm.factory.get_chat_model')
    @patch('src.api.services.langchain_service.service.MongoConnector')
    @unittest.skip("Temporarily skipping this test case")
    def test_langchain_service_initialization(self, mock_mongo_connector, mock_get_chat_model, mock_mongo_factory):
        # Mocking MongoConnector and MongoFactory
        mock_mongo_connector.return_value.client = MagicMock()
        mock_mongo_factory.return_value = MagicMock()

        # Mocking get_chat_model to return a mock LLM
        mock_llm = MagicMock()
        mock_get_chat_model.return_value = mock_llm

        # Creating a mock session object
        mock_session = MagicMock()

        # Instantiating the LangchainService with the mock session
        service = LangchainService(mock_session)

        # Assertions to verify that the attributes are correctly set
        self.assertEqual(service.session, mock_session)
        self.assertEqual(service.chat_collection, mock_mongo_factory.return_value)
        self.assertEqual(service.llm, mock_llm)

        # Verifying that the MongoFactory was called with the correct parameters
        mock_mongo_factory.assert_called_once_with(mock_mongo_connector.return_value.client, "chats", mock_session)

        # Verifying that get_chat_model was called (once, with no args)
        mock_get_chat_model.assert_called_once()

    def test_json_serial_with_datetime(self):
        dt = datetime(2024, 8, 28, 12, 30, 45)
        result = LangchainService(session).json_serial(dt)
        expected_result = "2024-08-28T12:30:45"
        self.assertEqual(result, expected_result)

    def test_json_serial_with_date(self):
        d = date(2024, 8, 28)
        result = LangchainService(session).json_serial(d)
        expected_result = "2024-08-28"
        self.assertEqual(result, expected_result)

    @patch('builtins.print')
    def test_planner_agent_with_valid_input(self, mock_print):
        # Test with a valid input string
        input_1 = "Task 1||Task 2||Task 3"
        
        # Call the method
        result = LangchainService(session).plannerAgent(input_1)
        
        # Assertions
        self.assertEqual(result, input_1)

    @unittest.skip("Temporarily skipping this test case.This testcase needs llm connection.")
    @patch('src.api.services.langchain_service.utils.LangchainServiceUtils')
    @patch('src.api.services.langchain_service.service.DataEngineer.create_agent')
    @patch.object(FallBackExecutor, 'pytool_executor')
    def test_agent_identifier_successful_case(self, mock_pytool_executor, mock_create_agent, mock_langchain_utils):
        # Mock setup
        mock_langchain_utils_instance = MagicMock()
        mock_langchain_utils_instance.match_string.return_value = "sql_operations"
        mock_langchain_utils.return_value = mock_langchain_utils_instance
        
        mock_agent = MagicMock()

        mock_agent_instance = MagicMock()
        mock_agent_instance.agent = mock_agent
        mock_create_agent.return_value = lambda *args, **kwargs: mock_agent_instance

        mock_pytool_executor.return_value = ({}, None)
        
        instance = LangchainService(session)  

        config = {"configurable": {"user_id": "user123", "chat_id": "6823336a1707152fac937878"}}
        result, wrapper_result, agent_intent_logic = instance.agent_identifier("some_task", config)
        self.assertEqual(wrapper_result, None, None)



if __name__ == '__main__':
    unittest.main()
