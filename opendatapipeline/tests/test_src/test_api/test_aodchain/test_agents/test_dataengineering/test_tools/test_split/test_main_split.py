import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.split.main import SplitAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestSplitAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.split.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.split.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.split.main.SplitToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.split.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = SplitAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_split_dob_column(self):
        natural_language_input = 'Split "dob" column into "day", "month", and "year" using "-"'
        expected_json_output = {"column": "dob", "delimiter": "-", "destination_columns": ["day", "month", "year"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the splitting of the 'dob' column.")

    def test_split_salary_age_column(self):
        natural_language_input = 'Split "salary_age" column using ":"'
        expected_json_output = {"column": "salary_age", "delimiter": ":", "destination_columns": None}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the splitting of the 'salary_age' column.")

    def test_split_address_column(self):
        natural_language_input = 'Split "address" column into "street", "city", and "zip" using ","'
        expected_json_output = {"column": "address", "delimiter": ",", "destination_columns": ["street", "city", "zip"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the splitting of the 'address' column.")

    def test_split_name_column(self):
        natural_language_input = 'Split "name" column into "first_name" and "last_name" using space'
        expected_json_output = {"column": "name", "delimiter": " ", "destination_columns": ["first_name", "last_name"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the splitting of the 'name' column.")

    def test_split_phone_number_column(self):
        natural_language_input = 'Split "phone_number" column into "area_code" and "number" using "-"'
        expected_json_output = {"column": "phone_number", "delimiter": "-", "destination_columns": ["area_code", "number"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the splitting of the 'phone_number' column.")

    def test_split_email_column(self):
        natural_language_input = 'Split "email" column into "username" and "domain" using "@"'
        expected_json_output = {"column": "email", "delimiter": "@", "destination_columns": ["username", "domain"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the splitting of the 'email' column.")

if __name__ == '__main__':
    unittest.main()
