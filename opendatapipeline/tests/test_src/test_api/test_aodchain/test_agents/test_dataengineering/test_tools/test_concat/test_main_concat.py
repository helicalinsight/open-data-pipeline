import unittest
from unittest.mock import Mock, patch
from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.concat.main import ConcatAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestConcatAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.concat.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.concat.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.concat.main.ConcatToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.concat.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = ConcatAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_concatenate_operation(self):
        natural_language_input = 'Concatenate "day", "month", and "year" into "dob" using \'-\''
        expected_json_output = {
            "columns": ["day", "month", "year"],
            "separator": "-",
            "destination_column": "dob"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert the natural language command into a JSON command.")

    def test_concatenate_operation_no_destination_column(self):
        natural_language_input = 'Concatenate "salary" and "age" using \':\' (no destination_column specified)'
        expected_json_output = {
            "columns": ["salary", "age"],
            "separator": ":",
            "destination_column": None
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

    def test_concatenate_operation_with_destination_column(self):
        natural_language_input = 'Concatenate "first_name" and "last_name" using space (\' \') into "full_name"'
        expected_json_output = {
            "columns": ["first_name", "last_name"],
            "separator": " ",
            "destination_column": "full_name"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

    def test_concatenate_operation_no_destination_column_multiple_columns(self):
        natural_language_input = 'Concatenate "street", "city", and "zip" using \',\''
        expected_json_output = {
            "columns": ["street", "city", "zip"],
            "separator": ",",
            "destination_column": None
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

    
    def test_concatenate_operation_with_destination_column_custom_separator(self):
        natural_language_input = 'Concatenate "username" and "domain" using \'@\' into "email_address"'
        expected_json_output = {
            "columns": ["username", "domain"],
            "separator": "@",
            "destination_column": "email_address"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

    def test_concatenate_operation_with_destination_column_and_custom_separator(self):
        natural_language_input = 'Concatenate "prefix" and "phone_number" using \'-\' into "full_phone_number"'
        expected_json_output = {
            "columns": ["prefix", "phone_number"],
            "separator": "-",
            "destination_column": "full_phone_number"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

if __name__ == '__main__':
    unittest.main()
