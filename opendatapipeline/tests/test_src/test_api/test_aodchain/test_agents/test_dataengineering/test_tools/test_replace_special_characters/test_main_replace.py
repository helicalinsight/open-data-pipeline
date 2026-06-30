import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.replace_special_characters.main import ReplaceSpecialCharactersAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestReplaceSpecialCharactersAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.replace_special_characters.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.replace_special_characters.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.replace_special_characters.main.ReplaceSpecialCharactersToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.replace_special_characters.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = ReplaceSpecialCharactersAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_replace_special_characters(self):
        natural_language_input = 'Replace - from "age" column with _'
        expected_json_output = {"columns": "age", "target_character": "-", "replacement_character": "_"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the replacement of special characters.")

    def test_replace_special_characters_dateidentity(self):
        natural_language_input = 'Replace all occurrences of "$" with space from "dateidentity" column'
        expected_json_output = {"columns": "dateidentity", "target_character": "$", "replacement_character": " "}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the replacement of special characters for 'dateidentity' column.")

    def test_replace_special_characters_description(self):
        natural_language_input = 'Replace "&" from "description" column with "#"'
        expected_json_output = {"columns": "description", "target_character": "&", "replacement_character": "#"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the replacement of special characters for 'description' column.")

    def test_replace_special_characters_phone_number(self):
        natural_language_input = 'Replace "#" from "phone_number" column with "-"'
        expected_json_output = {"columns": "phone_number", "target_character": "#", "replacement_character": "-"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the replacement of special characters for 'phone_number' column.")

    def test_replace_special_characters_email(self):
        natural_language_input = 'Replace "*" from "email" column with "@"'
        expected_json_output = {"columns": "email", "target_character": "*", "replacement_character": "@"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the replacement of special characters for 'email' column.")

    def test_replace_special_characters_address_plus(self):
        natural_language_input = 'Replace "%" from "address" column with "+"'
        expected_json_output = {"columns": "address", "target_character": "%", "replacement_character": "+"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the replacement of special characters for 'address' column with '+'.")

    def test_replace_special_characters_address_empty(self):
        natural_language_input = 'Replace "%" from address'
        expected_json_output = {"columns": "address", "target_character": "%", "replacement_character": ""}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the replacement of special characters for 'address' column with an empty string.")

if __name__ == '__main__':
    unittest.main()
