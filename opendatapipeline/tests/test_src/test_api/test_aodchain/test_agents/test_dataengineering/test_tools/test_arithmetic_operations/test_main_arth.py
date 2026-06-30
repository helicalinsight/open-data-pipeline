import unittest
from unittest.mock import Mock, patch
from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.arithmetic_operations.main import ArithmeticOperationsAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestArithmeticOperationsAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.arithmetic_operations.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.arithmetic_operations.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.arithmetic_operations.main.ArithmeticOperationsToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.arithmetic_operations.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = ArithmeticOperationsAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_arithmetic_operation_with_storage(self):
        natural_language_input = "Calculate units_sold + 5 and store it in units_total."
        expected_json_output = {
            "query": "units_sold + 5",
            "destination_column": "units_total"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert the natural language command into a JSON command.")

    def test_arithmetic_operation_subtraction_add_to_column(self):
        natural_language_input = "Perform units_sold - unit_price and add in units_lost."

        expected_json_output = {
            "query": "units_sold - unit_price",
            "destination_column": "units_lost"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

    def test_arithmetic_operation_power(self):
        natural_language_input = "Do unit_price ** 3."

        expected_json_output = {
            "query": "unit_price ** 3",
            "destination_column": None  
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

    def test_mixed_arithmetic_operations(self):

        natural_language_input = "calculate 1+20-3/10"

        expected_json_output = {
            "query": "1+20-3/10",
            "destination_column": None 
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

    def test_arithmetic_operation_multiplication_with_no_storage(self):
        natural_language_input = "calculate 2 multiply 5"

        expected_json_output = {
            "query": "2*5",
            "destination_column": None  
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

if __name__ == '__main__':
    unittest.main()
