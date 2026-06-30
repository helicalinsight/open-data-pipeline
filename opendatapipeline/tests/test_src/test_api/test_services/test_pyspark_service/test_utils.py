import unittest
from unittest.mock import MagicMock
from src.api.services.pyspark_service.utils import Utils
from src.api.services.pyspark_service.prompt import Prompt
from langchain_classic.memory import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
import re


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.utils = Utils()
        
    def test_convert_from_mongo_history(self):
        mongo_history = [
            {"user": "User question 1", "ai": "AI response 1"},
            {"user": "User question 2", "ai": "AI response 2"}
        ]
        history = self.utils.convert_from_mongo_history(mongo_history)
        
        self.assertEqual(len(history.messages), 4)
        self.assertEqual(history.messages[0].content, "User question 1")
        self.assertEqual(history.messages[1].content, "AI response 1")

    def test_convert_from_mongo_history_empty(self):
        mongo_history = []
        history = self.utils.convert_from_mongo_history(mongo_history)
        self.assertEqual(len(history.messages), 0)

    def test_convert_from_mongo_history_missing_key(self):
        with self.assertRaises(KeyError):
            mongo_history = [{"user": "User question"}]  # Missing "ai" key
            history = self.utils.convert_from_mongo_history(mongo_history)
    
    def test_load_history_with_empty_history(self):
        mongo_history = []
        history = self.utils.load_history(Prompt().get_pyspark_code_generation_prompt("chat_id", "session_id"), mongo_history)
        self.assertEqual(len(history.messages), 2)

    def test_generate_mongo_history_valid(self):
        history = ChatMessageHistory()
        history.add_user_message("User question 1")
        history.add_ai_message("AI response 1")
        history.add_user_message("User question 2")
        history.add_ai_message("AI response 2")
        mongo_history = self.utils.generate_mongo_history(history)
        expected = [
            {"user": "User question 1", "ai": "AI response 1"},
            {"user": "User question 2", "ai": "AI response 2"}
        ]
        self.assertEqual(mongo_history, expected)
    
    def test_generate_mongo_history_unpaired(self):
        history = ChatMessageHistory()
        history.add_user_message("User question 1")
        history.add_ai_message("AI response 1")
        history.add_user_message("User question 2")  # No AI response
        mongo_history = self.utils.generate_mongo_history(history)
        expected = [{"user": "User question 1", "ai": "AI response 1"}]
        self.assertEqual(mongo_history, expected)
    
    def test_extract_code_with_code(self):
        response = "<code>print('Hello World')</code>"
        code = self.utils.extract_code(response)
        self.assertEqual(code, "print('Hello World')")
    
    def test_extract_code_without_code(self):
        response = "Some text without code tags"
        code = self.utils.extract_code(response)
        self.assertEqual(code, "No code found within <code> tags.")


if __name__ == "__main__":
    unittest.main()
