import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.filter.main import FilterAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestFilterAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.filter.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.filter.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.filter.main.FilterToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.filter.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = FilterAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',session=session)
        self.agent.agent = self.mock_llm

    def test_filter_nulls_operation(self):
        natural_language_input = 'Filter the nulls from "dob" column'
        expected_json_output = {
            "columns": "dob",
            "expr": "is_null",
            "value": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter nulls.")

    def test_filter_between_age_operation(self):
        natural_language_input = 'Filter the "age" column where age is between 10 and 20'
        expected_json_output = {
            "columns": "age",
            "expr": "in_between",
            "value": [10, 20]
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter age between 10 and 20.")

    def test_filter_contains_name_operation(self):
        natural_language_input = 'Filter the "name" column where name contains "John"'
        expected_json_output = {
            "columns": "name",
            "expr": "contains",
            "value": "John"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter name containing 'John'.")

    def test_filter_not_null_salary_operation(self):
        natural_language_input = 'Filter the "salary" column where salary is not null'
        expected_json_output = {
            "columns": "salary",
            "expr": "is_not_null",
            "value": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter salary where not null.")

    def test_filter_one_of_department_operation(self):
        natural_language_input = 'Filter the "department" column where department is one of ["HR", "Finance"]'
        expected_json_output = {
            "columns": "department",
            "expr": "is_one_of_the",
            "value": ["HR", "Finance"]
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter department where one of ['HR', 'Finance'].")
        
    def test_filter_not_endswith_email_operation(self):
        natural_language_input = 'Filter the "email" column where email does not end with ".com"'
        expected_json_output = {
            "columns": "email",
            "expr": "not_endswith",
            "value": ".com"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter email not ending with '.com'.")

    def test_filter_endswith_email_operation(self):
        natural_language_input = 'Filter the "email" column where email end with ".com"'
        expected_json_output = {
            "columns": "email",
            "expr": "endswith",
            "value": ".com"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter email ending with '.com'.")

    def test_filter_not_less_than_or_equal_age_operation(self):
        natural_language_input = 'Filter the data where age is not less than or equal to 30'
        expected_json_output = {
            "columns": "age",
            "expr": "is_greater_than_or_equal_to",
            "value": 30
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter age not less than or equal to 30.")

    def test_filter_lesser_than_or_equal_age_operation(self):
        natural_language_input = 'Filter the data where age is less than or equal to 30'
        expected_json_output = {
            "columns": "age",
            "expr": "is_lesser_than_or_equal_to",
            "value": 30
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter age less than or equal to 30.")

    def test_filter_not_one_of_name_operation(self):
        natural_language_input = 'Filter the data where name is not one of alice and ramesh'
        expected_json_output = {
            "columns": "name",
            "expr": "is_not_one_of_the",
            "value": ["alice", "ramesh"]
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter name not one of ['alice', 'ramesh'].")

    def test_filter_one_of_name_operation(self):
        natural_language_input = 'Filter the data where name is one of alice and ramesh'
        expected_json_output = {
            "columns": "name",
            "expr": "is_one_of_the",
            "value": ["alice", "ramesh"]
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter name one of ['alice', 'ramesh'].")

    def test_filter_is_false_success_column_operation(self):
        natural_language_input = 'Filter the data where success_column is not true'
        expected_json_output = {
            "columns": "success_column",
            "expr": "is_false",
            "value": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter success_column is not true.")

    def test_filter_is_true_success_column_operation(self):
        natural_language_input = 'Filter the data where success_column is true'
        expected_json_output = {
            "columns": "success_column",
            "expr": "is_true",
            "value": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly filter success_column is true.")

if __name__ == '__main__':
    unittest.main()

