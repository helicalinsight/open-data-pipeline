from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch, MagicMock
import uuid
from src.api.services.langchain_service.utils import LangchainServiceUtils 
from src.models.connector import MongoConnector
from pymongo.write_concern import WriteConcern

wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestLangchainServiceUtils(unittest.TestCase):
    def setUp(self):
        # Mock session and llm
        self.mock_session = MagicMock()
        self.mock_llm = MagicMock()
        self.service_utils = LangchainServiceUtils(session=self.mock_session, llm=self.mock_llm)

    def test_initialization(self):
        # Mock the session and llm objects
        mock_session = MagicMock()
        mock_llm = MagicMock()

        # Create an instance of LangchainServiceUtils
        service_utils = LangchainServiceUtils(session=mock_session, llm=mock_llm)

        # Assertions to verify that instance variables are set correctly
        self.assertEqual(service_utils.session, mock_session)
        self.assertEqual(service_utils.llm, mock_llm)

    def test_json_serial_datetime(self):
        dt = datetime(2024, 8, 28, 15, 30, 0)
        result = self.service_utils.json_serial(dt)
        self.assertEqual(result, dt.isoformat())

    def test_json_serial_date(self):
        d = date(2024, 8, 28)
        result = self.service_utils.json_serial(d)
        self.assertEqual(result, d.isoformat())

    @patch('src.api.services.langchain_service.utils.difflib.get_close_matches')
    def test_match_string_found(self, mock_get_close_matches):
        # Mocking the intent_list and get_close_matches
        mock_get_close_matches.return_value = ['intent1']
        input_string = 'input'
        result = self.service_utils.match_string(input_string)
        self.assertEqual(result, 'intent1')

    @patch('src.api.services.langchain_service.utils.difflib.get_close_matches')
    def test_match_string_not_found(self, mock_get_close_matches):
        # Mocking the intent_list and get_close_matches
        mock_get_close_matches.return_value = []
        input_string = 'input'
        result = self.service_utils.match_string(input_string)
        self.assertEqual(result, 'analysis')

    @patch('src.api.services.langchain_service.utils.QueryGenerator')
    def test_sql_generator(self, MockQueryGenerator):
        # Mock QueryGenerator
        mock_query_generator = MagicMock()
        MockQueryGenerator.return_value = mock_query_generator
        mock_query_generator.generate_expected_output.return_value = 'SELECT * FROM table'

        # Mock llm invoke
        mock_llm_response = MagicMock()
        mock_llm_response.content = 'SELECT * FROM table'
        self.mock_llm.invoke.return_value = mock_llm_response

        input_prompt = 'prompt'
        chat_id = 'chat1'
        result = self.service_utils.sql_generator(input_prompt, chat_id)

        self.assertEqual(result, 'SELECT * FROM table')
        self.mock_llm.invoke.assert_called_once_with('SELECT * FROM table')
        MockQueryGenerator.assert_called_once_with(self.mock_session)
        mock_query_generator.generate_expected_output.assert_called_once_with(input_prompt, chat_id)

    def test_regex_matcher_sql_block(self):
        response = 'Here is the SQL query:\n```sql\nSELECT * FROM table;\n```'
        result = self.service_utils.regex_matcher(response)
        self.assertEqual(result, 'SELECT * FROM table;')

    def test_regex_matcher_sql_inline(self):
        response = 'Here is the query: SELECT * FROM table; and more text.'
        result = self.service_utils.regex_matcher(response)
        self.assertEqual(result, 'SELECT * FROM table;')

    def test_regex_matcher_no_sql(self):
        response = 'This is a text without SQL query.'
        result = self.service_utils.regex_matcher(response)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
