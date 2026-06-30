import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.trim.main import TrimAgent


from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestTrimAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.trim.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.trim.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.trim.main.TrimToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.trim.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = TrimAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_trim_age_column_left(self):
        natural_language_input = 'Trim the "age" column from the left by 6 characters'
        expected_json_output = {"number_of_characters": 6, "location": "left", "columns": "age"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the trim operation on the 'age' column from the left.")
    
    def test_trim_name_column_right(self):
        natural_language_input = 'Trim the "name" column from the right by 3 characters'
        expected_json_output = {"number_of_characters": 3, "location": "right", "columns": "name"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the trim operation on the 'name' column from the right.")
    
    def test_trim_address_column_both(self):
        natural_language_input = 'Trim the "address" column from both ends by 2 characters'
        expected_json_output = {"number_of_characters": 2, "location": "both", "columns": "address"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the trim operation on the 'address' column from both ends.")
    
    def test_trim_email_column_left(self):
        natural_language_input = 'Trim the "email" column from the left by 4 characters'
        expected_json_output = {"number_of_characters": 4, "location": "left", "columns": "email"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the trim operation on the 'email' column from the left.")
    
    def test_trim_phone_number_column_right(self):
        natural_language_input = 'Trim the "phone_number" column from the right by 5 characters'
        expected_json_output = {"number_of_characters": 5, "location": "right", "columns": "phone_number"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the trim operation on the 'phone_number' column from the right.")
    
    def test_trim_department_column_both(self):
        natural_language_input = 'Trim the "department" column from both ends by 1 character'
        expected_json_output = {"number_of_characters": 1, "location": "both", "columns": "department"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the trim operation on the 'department' column from both ends.")

    def test_trim_identity_column_right(self):
        natural_language_input = 'Right trim the "identity" column by 3 characters'
        expected_json_output = {"number_of_characters": 3, "location": "right", "columns": "identity"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the right trim operation on the 'identity' column.")
    
    def test_trim_name_column_left(self):
        natural_language_input = 'Left trim the "name" column by 2 characters'
        expected_json_output = {"number_of_characters": 2, "location": "left", "columns": "name"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the left trim operation on the 'name' column.")
    
    def test_trim_description_column_right(self):
        natural_language_input = 'Trim the "description" column from the right by 5 characters'
        expected_json_output = {"number_of_characters": 5, "location": "right", "columns": "description"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the right trim operation on the 'description' column.")
    
    def test_trim_code_column_right(self):
        natural_language_input = 'Right trim the "code" column by 4 characters'
        expected_json_output = {"number_of_characters": 4, "location": "right", "columns": "code"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the right trim operation on the 'code' column.")
    
    def test_trim_address_column_left(self):
        natural_language_input = 'Left trim the "address" column by 3 characters'
        expected_json_output = {"number_of_characters": 3, "location": "left", "columns": "address"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the left trim operation on the 'address' column.")
    
    def test_trim_firstname_lastname_columns_left(self):
        natural_language_input = 'Trim the firstname by 3 and lastname by 5 characters from left'
        expected_json_output = [
            {"number_of_characters": 3, "location": "left", "columns": "firstname"},
            {"number_of_characters": 5, "location": "left", "columns": "lastname"}
        ]

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the left trim operation on the 'firstname' and 'lastname' columns.")

if __name__ == '__main__':
    unittest.main()
