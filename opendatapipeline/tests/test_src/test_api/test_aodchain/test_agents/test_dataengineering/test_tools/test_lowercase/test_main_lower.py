import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.lowercase.main import LowerCaseAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestLowerCaseAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.lowercase.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.lowercase.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.lowercase.main.LowerCaseToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.lowercase.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = LowerCaseAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',session=session)
        self.agent.agent = self.mock_llm

    def test_lower_case_operation(self):
        natural_language_input = 'Convert "day" and "hour" columns to lowercase'
        expected_json_output = {"columns": ["day", "hour"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert columns to lowercase.")
        
    def test_lower_case_age_hour_limit_helical(self):
        natural_language_input = 'Convert "age", "hour", "limit", and "helical" columns to lowercase'
        expected_json_output = {"columns": ["age", "hour", "limit", "helical"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert 'age', 'hour', 'limit', and 'helical' columns to lowercase.")

    def test_lower_case_name(self):
        natural_language_input = 'Convert "name" column to lowercase'
        expected_json_output = {"columns": ["name"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert 'name' column to lowercase.")

    def test_lower_case_email(self):
        natural_language_input = 'Convert "email" column to lowercase'
        expected_json_output = {"columns": ["email"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert 'email' column to lowercase.")

    def test_lower_case_department(self):
        natural_language_input = 'Convert "department" column to lowercase'
        expected_json_output = {"columns": ["department"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert 'department' column to lowercase.")

if __name__ == '__main__':
    unittest.main()

