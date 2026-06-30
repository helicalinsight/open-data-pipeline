import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.correlation.main import CorrelationAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestCorrelationAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.correlation.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.correlation.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.correlation.main.CorrelationToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.correlation.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = CorrelationAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_correlation_operation(self):
        natural_language_input = 'Calculate the correlation for age and marks and store it in age_marks_correlation'
        expected_json_output = {
            "columns": ["age", "marks"],
            "destination_column": "age_marks_correlation"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly calculate the correlation.")

    def test_correlation_operation_new_input(self):
        natural_language_input = 'Calculate the correlation for subject1_marks and subject2_marks.'
        expected_json_output = {
            "columns": ["subject1_marks", "subject2_marks"]
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly calculate the correlation for new input.")
    def test_correlation_height_weight(self):
        natural_language_input = 'Calculate the correlation for height and weight.'
        expected_json_output = {
            "columns": ["height", "weight"]
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly calculate the correlation for height and weight.")

    def test_correlation_income_expenses(self):
        natural_language_input = 'Calculate the correlation for income and expenses and store it in income_expenses_correlation'
        expected_json_output = {
            "columns": ["income", "expenses"],
            "destination_column": "income_expenses_correlation"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly calculate the correlation for income and expenses.")

    def test_correlation_study_hours_exam_score(self):
        natural_language_input = 'Calculate the correlation for study_hours and exam_score.'
        expected_json_output = {
            "columns": ["study_hours", "exam_score"]
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly calculate the correlation for study_hours and exam_score.")

    def test_correlation_temperature_humidity(self):
        natural_language_input = 'Calculate the correlation for temperature and humidity.'
        expected_json_output = {
            "columns": ["temperature", "humidity"]
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly calculate the correlation for temperature and humidity.")

    def test_correlation_years_experience_salary(self):
        natural_language_input = 'Calculate the correlation for years_experience and salary.'
        expected_json_output = {
            "columns": ["years_experience", "salary"]
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly calculate the correlation for years_experience and salary.")

if __name__ == '__main__':
    unittest.main()