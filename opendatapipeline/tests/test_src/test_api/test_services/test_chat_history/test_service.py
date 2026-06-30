import unittest

from src.api.services.chat_history.service import ChatHistoryService


class TestChatHistoryService(unittest.TestCase):
    '''def test_chat_history_with_existing_chat_id(self):
        # chat history doesnt return success status code 200 it returns only error is there
        chat_id = "65cb43f2007a5f38718b9d6a"
        user_id = "65365001d9654d9ec1172f87"
        response = ChatHistoryService.get_chat_history(user_id, chat_id, 1, 1)
        self.assertIsNotNone(response['columns'])

    def test_chat_history_with_non_existing_chat_id(self):
        # chat history doesnt return success status code 200 it returns only error is there
        chat_id = "6602a39d4475001648200351"
        user_id = "65ce024b47ff1fc8d6ae2bb1"
        response, status_code = ChatHistoryService.get_chat_history(user_id, chat_id, 1, 1)
        print(response, status_code)
        expected_output = {'status': False, 'message': 'Chat ID not found for the user'}
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, 404)'''


if __name__ == '__main__':
    unittest.main()
