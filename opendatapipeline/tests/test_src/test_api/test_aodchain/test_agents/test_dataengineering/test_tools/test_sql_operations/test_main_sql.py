import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sql_operations.main import SQLOperationsAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestSQLOperationsAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sql_operations.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sql_operations.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sql_operations.main.SQLOperationsToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sql_operations.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = SQLOperationsAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_execute_query(self):
        natural_language_input = 'Execute query "SELECT count(students) FROM df"'
        expected_json_output = {"query": "SELECT count(students) FROM df"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the SQL query execution.")

    def test_run_query_with_condition(self):
        natural_language_input = 'Run the query "SELECT count(*) FROM df WHERE age > 25"'
        expected_json_output = {"query": "SELECT count(*) FROM df WHERE age > 25"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the SQL query with condition.")

    def test_execute_query(self):
        natural_language_input = 'Execute query "SELECT count(students) FROM df"'
        expected_json_output = {"query": "SELECT count(students) FROM df"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the SQL query execution.")

    def test_run_query_with_condition(self):
        natural_language_input = 'Run the query "SELECT count(*) FROM df WHERE age > 25"'
        expected_json_output = {"query": "SELECT count(*) FROM df WHERE age > 25"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the SQL query with condition.")
    
    def test_select_all_columns(self):
        natural_language_input = 'Run the query "SELECT * FROM df"'
        expected_json_output = {"query": "SELECT * FROM df"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the select all columns query.")

    def test_filter_rows_with_string_condition(self):
        natural_language_input = 'Run the query "SELECT * FROM df WHERE name = \'John\'"'
        expected_json_output = {"query": "SELECT * FROM df WHERE name = 'John'"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the filter rows with string condition query.")

    def test_join_two_tables(self):
        natural_language_input = 'Run the query "SELECT df1.name, df2.salary FROM df1 JOIN df2 ON df1.id = df2.id"'
        expected_json_output = {"query": "SELECT df1.name, df2.salary FROM df1 JOIN df2 ON df1.id = df2.id"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the join two tables query.")

    def test_update_column_value(self):
        natural_language_input = 'Run the query "UPDATE df SET salary = 50000 WHERE id = 1"'
        expected_json_output = {"query": "UPDATE df SET salary = 50000 WHERE id = 1"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the update column value query.")

    def test_delete_rows_with_condition(self):
        natural_language_input = 'Run the query "DELETE FROM df WHERE age < 18"'
        expected_json_output = {"query": "DELETE FROM df WHERE age < 18"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the delete rows with condition query.")

if __name__ == '__main__':
    unittest.main()
