import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sort.main import SortAgent


from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestSortAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sort.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sort.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sort.main.SortToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sort.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = SortAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_sort_dob_ascending(self):
        natural_language_input = 'Sort the "dob" column in ascending order'
        expected_json_output = {"columns": "dob", "ascending": True}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the sorting of the 'dob' column in ascending order.")

    def test_sort_age_descending(self):
        natural_language_input = 'Sort the "age" column in descending order'
        expected_json_output = {"columns": "age", "ascending": False}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the sorting of the 'age' column in descending order.")

    def test_sort_name_ascending(self):
        natural_language_input = 'Sort the "name" column in ascending order'
        expected_json_output = {"columns": "name", "ascending": True}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the sorting of the 'name' column in ascending order.")

    def test_sort_salary_descending(self):
        natural_language_input = 'Sort the "salary" column in descending order'
        expected_json_output = {"columns": "salary", "ascending": False}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the sorting of the 'salary' column in descending order.")

    def test_sort_email_ascending(self):
        natural_language_input = 'Sort the "email" column in ascending order'
        expected_json_output = {"columns": "email", "ascending": True}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the sorting of the 'email' column in ascending order.")

    def test_sort_department_descending(self):
        natural_language_input = 'Sort the "department" column in descending order'
        expected_json_output = {"columns": "department", "ascending": False}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the sorting of the 'department' column in descending order.")

if __name__ == '__main__':
    unittest.main()
