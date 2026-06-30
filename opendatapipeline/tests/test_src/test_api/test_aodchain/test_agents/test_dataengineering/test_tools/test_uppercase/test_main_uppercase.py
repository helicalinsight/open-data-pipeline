import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.uppercase.main import UpperCaseAgent
from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestUpperCaseAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.uppercase.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.uppercase.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.uppercase.main.UpperCaseToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.uppercase.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = UpperCaseAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_convert_day_hour_to_uppercase(self):
        natural_language_input = 'Convert "day" and "hour" columns to uppercase'
        expected_json_output = {"columns": ["day", "hour"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of 'day' and 'hour' columns to uppercase.")

    def test_convert_name_address_to_uppercase(self):
        natural_language_input = 'Convert "name" and "address" columns to uppercase'
        expected_json_output = {"columns": ["name", "address"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of 'name' and 'address' columns to uppercase.")

    def test_convert_email_username_to_uppercase(self):
        natural_language_input = 'Convert "email" and "username" columns to uppercase'
        expected_json_output = {"columns": ["email", "username"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of 'email' and 'username' columns to uppercase.")

    def test_convert_department_role_to_uppercase(self):
        natural_language_input = 'Convert "department" and "role" columns to uppercase'
        expected_json_output = {"columns": ["department", "role"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of 'department' and 'role' columns to uppercase.")

    def test_convert_city_country_to_uppercase(self):
        natural_language_input = 'Convert "city" and "country" columns to uppercase'
        expected_json_output = {"columns": ["city", "country"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of 'city' and 'country' columns to uppercase.")

    def test_convert_description_comments_to_uppercase(self):
        natural_language_input = 'Convert "description" and "comments" columns to uppercase'
        expected_json_output = {"columns": ["description", "comments"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of 'description' and 'comments' columns to uppercase.")

    def test_convert_day_hour_to_uppercase(self):
        natural_language_input = 'Convert "day" and "hour" columns to uppercase'
        expected_json_output = {"columns": ["day", "hour"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of 'day' and 'hour' columns to uppercase.")

    def test_convert_age_hour_limit_helical_to_uppercase(self):
        natural_language_input = 'Convert "age", "hour", "limit", and "helical" columns to uppercase'
        expected_json_output = {"columns": ["age", "hour", "limit", "helical"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of 'age', 'hour', 'limit', and 'helical' columns to uppercase.")

    def test_convert_name_to_uppercase(self):
        natural_language_input = 'Convert "name" column to uppercase'
        expected_json_output = {"columns": ["name"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of the 'name' column to uppercase.")

    def test_convert_email_to_uppercase(self):
        natural_language_input = 'Convert "email" column to uppercase'
        expected_json_output = {"columns": ["email"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of the 'email' column to uppercase.")

    def test_convert_department_to_uppercase(self):
        natural_language_input = 'Convert "department" column to uppercase'
        expected_json_output = {"columns": ["department"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the conversion of the 'department' column to uppercase.")

if __name__ == '__main__':
    unittest.main()
