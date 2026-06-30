import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.when_otherwise.main import WhenOtherwiseAgent
from opendatapipeline.src.models.connector import MongoConnector




mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestWhenOtherwiseAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.when_otherwise.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.when_otherwise.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.when_otherwise.main.WhenOtherwiseToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.when_otherwise.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = WhenOtherwiseAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_add_column_based_on_conditions(self):
        natural_language_input = 'Execute query to add a new column based on conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "\tWHEN marks > 39 THEN 'PASS'\n"
                     "\tWHEN marks < 20 THEN 'FAIL'\n"
                     "\tELSE 'MODERATE'\n"
                     "END AS __newcolumn__\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on conditions.")
    def test_add_column_based_on_age_conditions(self):
        natural_language_input = 'Execute query to add a new column based on age conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN age >= 18 THEN 'ADULT'\n"
                     "ELSE 'MINOR'\n"
                     "END AS __newcolumn__\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on age conditions.")

    def test_add_column_based_on_salary_conditions(self):
        natural_language_input = 'Execute query to add a new column based on salary conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN salary > 50000 THEN 'HIGH'\n"
                     "WHEN salary < 20000 THEN 'LOW'\n"
                     "ELSE 'MEDIUM'\n"
                     "END AS __newcolumn__\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on salary conditions.")

    def test_add_column_based_on_department_conditions(self):
        natural_language_input = 'Execute query to add a new column based on department conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN department = 'HR' THEN 'Human Resources'\n"
                     "WHEN department = 'ENG' THEN 'Engineering'\n"
                     "ELSE 'Other'\n"
                     "END AS __newcolumn__\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on department conditions.")

    def test_add_column_based_on_performance_conditions(self):
        natural_language_input = 'Execute query to add a new column based on performance conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN performance > 90 THEN 'EXCELLENT'\n"
                     "WHEN performance > 75 THEN 'GOOD'\n"
                     "WHEN performance > 50 THEN 'AVERAGE'\n"
                     "ELSE 'POOR'\n"
                     "END AS __newcolumn__\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on performance conditions.")

    def test_add_column_based_on_boolean_conditions(self):
        natural_language_input = 'Execute query to add a new column based on boolean conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN active = TRUE THEN 'ACTIVE'\n"
                     "ELSE 'INACTIVE'\n"
                     "END AS __newcolumn__\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on boolean conditions.")

    def test_add_final_res_column_based_on_conditions(self):
        natural_language_input = 'Run the query to add a new column named final_res based on conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "\tWHEN marks > 39 THEN 'PASS'\n"
                     "\tWHEN marks < 20 THEN 'FAIL'\n"
                     "\tELSE 'MODERATE'\n"
                     "END AS final_res\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column named final_res based on conditions.")

    def test_add_column_based_on_performance_conditions(self):
        natural_language_input = 'Execute query to add a new column based on performance conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN performance > 90 THEN 'EXCELLENT'\n"
                     "WHEN performance > 75 THEN 'GOOD'\n"
                     "WHEN performance > 50 THEN 'AVERAGE'\n"
                     "ELSE 'POOR'\n"
                     "END AS __newcolumn__\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on performance conditions.")

    def test_add_column_based_on_boolean_conditions(self):
        natural_language_input = 'Execute query to add a new column based on boolean conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN active = TRUE THEN 'ACTIVE'\n"
                     "ELSE 'INACTIVE'\n"
                     "END AS __newcolumn__\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on boolean conditions.")

    def test_add_final_res_column_based_on_conditions(self):
        natural_language_input = 'Run the query to add a new column named final_res based on conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "\tWHEN marks > 39 THEN 'PASS'\n"
                     "\tWHEN marks < 20 THEN 'FAIL'\n"
                     "\tELSE 'MODERATE'\n"
                     "END AS final_res\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column named final_res based on conditions.")

    def test_add_column_based_on_region_conditions(self):
        natural_language_input = 'Execute query to add a new column based on region conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN region = 'North' THEN 'Northern Region'\n"
                     "WHEN region = 'South' THEN 'Southern Region'\n"
                     "ELSE 'Other Region'\n"
                     "END AS region_description\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on region conditions.")

    def test_add_column_based_on_age_ranges(self):
        natural_language_input = 'Execute query to add a new column based on age ranges'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN age < 13 THEN 'Child'\n"
                     "WHEN age >= 13 AND age < 20 THEN 'Teen'\n"
                     "WHEN age >= 20 AND age < 60 THEN 'Adult'\n"
                     "ELSE 'Senior'\n"
                     "END AS age_group\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on age ranges.")

    def test_add_column_based_on_status_and_score_conditions(self):
        natural_language_input = 'Execute query to add a new column based on status and score conditions'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN status = 'Active' AND score > 80 THEN 'High Achiever'\n"
                     "WHEN status = 'Active' AND score <= 80 THEN 'Achiever'\n"
                     "WHEN status = 'Inactive' AND score > 50 THEN 'Moderate'\n"
                     "ELSE 'Low Performer'\n"
                     "END AS performance_category\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on status and score conditions.")

    def test_add_column_based_on_availability_and_type(self):
        natural_language_input = 'Execute query to add a new column based on availability and type'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN available = TRUE AND type = 'Premium' THEN 'Available Premium'\n"
                     "WHEN available = TRUE AND type = 'Standard' THEN 'Available Standard'\n"
                     "WHEN available = FALSE AND type = 'Premium' THEN 'Unavailable Premium'\n"
                     "ELSE 'Unavailable Standard'\n"
                     "END AS availability_status\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on availability and type.")

    def test_add_column_based_on_birthdate(self):
        natural_language_input = 'Execute query to add a new column based on birthdate'
        expected_json_output = {
            "query": "SELECT *, CASE\n"
                     "WHEN birthdate < '2000-01-01' THEN 'Born in 20th Century'\n"
                     "ELSE 'Born in 21st Century'\n"
                     "END AS century_born\n"
                     "FROM df;"
        }

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the query to add a new column based on birthdate.")

if __name__ == '__main__':
    unittest.main()

