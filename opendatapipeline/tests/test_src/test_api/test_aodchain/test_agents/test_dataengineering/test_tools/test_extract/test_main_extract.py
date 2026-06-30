import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.extract.main import ExtractAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestExtractAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.extract.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.extract.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.extract.main.ExtractToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.extract.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = ExtractAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_extract_operation(self):
        natural_language_input = 'Extract year component from joining_date column and store it in joining_year destination column'
        expected_json_output = {
            "column": "joining_date",
            "component": ["year"],
            "destination_column": "joining_year"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly extract the year component.")
        
    def test_extract_day_from_birth_date(self):
        natural_language_input = 'Extract day component from birth_date column and store it in bdate destination column'
        expected_json_output = {
            "column": "birth_date",
            "component": ["day"],
            "destination_column": "bdate"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly extract the day component from birth_date.")

    def test_extract_month_from_current_date(self):
        natural_language_input = 'Take month date part from current_date column.'
        expected_json_output = {
            "column": "current_date",
            "component": ["month"],
            "destination_column": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly extract the month component from current_date.")

    def test_extract_month_year_from_current_date(self):
        natural_language_input = 'Take month year date part from current_date column.'
        expected_json_output = {
            "column": "current_date",
            "component": ["month", "year"],
            "destination_column": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly extract the month and year components from current_date.")

    def test_extract_year_month_day_from_testing_column(self):
        natural_language_input = 'Extract the year, month and day column from the testing_column.'
        expected_json_output = {
            "column": "testing_column",
            "component": ["year", "month", "day"],
            "destination_column": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly extract the year, month, and day components from testing_column.")

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()
