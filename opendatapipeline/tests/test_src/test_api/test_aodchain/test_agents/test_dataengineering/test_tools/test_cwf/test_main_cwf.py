import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cwf.main import CurrentWorkingFileAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestCurrentWorkingFileAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cwf.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cwf.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cwf.main.CurrentWorkingFileToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cwf.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = CurrentWorkingFileAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_current_working_file_operation(self):
        natural_language_input = "Choose 'student' file as the current working file"
        expected_json_output = {
            "file": "student"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly choose the current working file.")
        
    def test_select_grades_file_operation(self):
        natural_language_input = "Select 'grades' as the current file"
        expected_json_output = {
            "file": "grades"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly select the 'grades' file.")   
        
        
    def test_set_sales_data_file_operation(self):
        natural_language_input = "Set 'sales_data' as the current working file"
        expected_json_output = {
            "file": "sales_data"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly set the 'sales_data' file.")

    def test_make_inventory_file_operation(self):
        natural_language_input = "Make 'inventory' the current file"
        expected_json_output = {
            "file": "inventory"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly make 'inventory' the current file.")

    def test_choose_expenses_file_operation(self):
        natural_language_input = "Choose 'expenses' file as the current working file"
        expected_json_output = {
            "file": "expenses"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly choose 'expenses' as the current working file.") 

if __name__ == '__main__':
    unittest.main()
