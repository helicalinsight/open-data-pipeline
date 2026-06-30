import unittest
from unittest.mock import patch, MagicMock
from src.api.services.pyspark_service.service import PySparkCodeGenerator

class TestPySparkCodeGenerator(unittest.TestCase):
    
    @patch('src.api.services.pyspark_service.service.Utils')  # Patch where Utils is used
    @patch('src.api.services.pyspark_service.service.MongoFactory')  # Patch where MongoFactory is used
    @patch('src.core.llm.factory.get_chat_model')  # Patch the single factory entry point
    @patch('src.api.services.pyspark_service.service.MongoConnector')  # Patch where MongoConnector is used
    @patch('src.api.services.pyspark_service.service.ConversationChain')  # Patch where ConversationChain is used
    @patch('src.api.services.pyspark_service.service.ConversationBufferMemory')
    def test_invoke_chain(self, mock_conversation_buffer_memory, mock_conversation_chain, mock_mongo_connector, mock_get_chat_model, mock_mongo_factory, mock_utils):
        # Mocking MongoConnector to return a mock MongoClient
        mock_mongo_connector_instance = MagicMock()
        mock_mongo_connector_instance.client = MagicMock()
        mock_mongo_connector.return_value = mock_mongo_connector_instance

        # Mocking MongoFactory to return mock chat data
        mock_mongo_langchain = MagicMock()
        mock_mongo_factory.return_value = mock_mongo_langchain
        
        # Ensure get_by_id returns a tuple with two values
        mock_mongo_langchain.get_by_id_and_value.return_value = (True, {"pyspark_bot_memory": "mock_memory"})

        # Mocking Utils methods
        mock_utils_instance = mock_utils.return_value
        mock_utils_instance.load_history.return_value = MagicMock()  # Mock as a valid ChatMessageHistory or similar
        mock_utils_instance.extract_code.return_value = "mock_extracted_code"
        mock_utils_instance.generate_mongo_history.return_value = "mock_generated_mongo_history"

        # Mocking get_chat_model to return a mock LLM
        mock_get_chat_model.return_value = MagicMock()

        # Mocking ConversationBufferMemory
        mock_conversation_buffer_memory_instance = MagicMock()
        mock_conversation_buffer_memory.return_value = mock_conversation_buffer_memory_instance

        # Mocking ConversationChain
        mock_chain_instance = MagicMock()
        mock_conversation_chain.return_value = mock_chain_instance
        mock_chain_instance.invoke.return_value = {"response": "Generated code here"}

        # Create an instance of PySparkCodeGenerator
        chat_id = "mock_chat_id"
        session = "mock_session"
        generator = PySparkCodeGenerator(chat_id, session)

        # Call invoke_chain method
        input_text = "Generate PySpark code"
        result, status_code = generator.invoke_chain(input_text)
        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["code"], "mock_extracted_code")
        self.assertEqual(result["message"], "Pyspark code generated successfully")

        # Verify the mocks were called with expected arguments
        mock_chain_instance.invoke.assert_called_once_with(input_text)
        mock_utils_instance.load_history.assert_called_once_with(generator.prompt, "mock_memory")
        mock_mongo_langchain.update_by_chat_id_value.assert_called_once_with(chat_id, "pyspark_bot_memory", "mock_generated_mongo_history")
        mock_utils_instance.extract_code.assert_called_once_with("Generated code here")
        mock_utils_instance.generate_mongo_history.assert_called_once()
    
    @patch('src.api.services.pyspark_service.service.MongoFactory')
    @patch('src.api.services.pyspark_service.service.MongoConnector')
    def test_initialization_failure_chat_not_found(self, mock_mongo_connector, mock_mongo_factory):
        mock_mongo_connector_instance = MagicMock()
        mock_mongo_connector_instance.client = MagicMock()
        mock_mongo_connector.return_value = mock_mongo_connector_instance
        
        mock_mongo_langchain = MagicMock()
        mock_mongo_factory.return_value = mock_mongo_langchain
        mock_mongo_langchain.get_by_id_and_value.return_value = (False, None)  # Chat not found
        
        with self.assertRaises(Exception) as context:
            PySparkCodeGenerator("invalid_chat_id", "session_id")
        
        self.assertIn("No chat found for chat_id", str(context.exception))


    @patch('src.api.services.pyspark_service.service.Utils')  # Patch where Utils is used
    @patch('src.api.services.pyspark_service.service.MongoFactory')  # Patch where MongoFactory is used
    @patch('src.core.llm.factory.get_chat_model')  # Patch the single factory entry point
    @patch('src.api.services.pyspark_service.service.MongoConnector')  # Patch where MongoConnector is used
    @patch('src.api.services.pyspark_service.service.ConversationChain')  # Patch where ConversationChain is used
    @patch('src.api.services.pyspark_service.service.ConversationBufferMemory')
    def test_reset_chain(self, mock_conversation_buffer_memory, mock_conversation_chain, mock_mongo_connector, mock_get_chat_model, mock_mongo_factory, mock_utils):
        # Mocking MongoConnector to return a mock MongoClient
        mock_mongo_connector_instance = MagicMock()
        mock_mongo_connector_instance.client = MagicMock()
        mock_mongo_connector.return_value = mock_mongo_connector_instance

        # Mocking MongoFactory to return mock langchain data
        mock_mongo_langchain = MagicMock()
        mock_mongo_factory.return_value = mock_mongo_langchain
        
        # Ensure get_by_id returns a tuple with two values
        mock_mongo_langchain.get_by_id_and_value.return_value = (True, {"pyspark_bot_memory": "mock_memory"})

        # Mocking Utils methods
        mock_utils_instance = mock_utils.return_value
        mock_utils_instance.load_history.return_value = MagicMock()  # Mock as a valid ChatMessageHistory or similar
        mock_utils_instance.extract_code.return_value = "mock_extracted_code"
        mock_utils_instance.generate_mongo_history.return_value = "mock_generated_mongo_history"

        # Mocking get_chat_model to return a mock LLM
        mock_get_chat_model.return_value = MagicMock()

        # Mocking ConversationBufferMemory
        mock_conversation_buffer_memory_instance = MagicMock()
        mock_conversation_buffer_memory.return_value = mock_conversation_buffer_memory_instance

        # Mocking ConversationChain
        mock_chain_instance = MagicMock()
        mock_conversation_chain.return_value = mock_chain_instance

        # Create an instance of PySparkCodeGenerator
        chat_id = "mock_chat_id"
        session = "mock_session"
        generator = PySparkCodeGenerator(chat_id, session)

        # Call invoke_chain method
        input_text = "Generate PySpark code"
        result, status_code = generator.reset_chain()
        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["message"], "Reset Successful")


if __name__ == '__main__':
    unittest.main()
