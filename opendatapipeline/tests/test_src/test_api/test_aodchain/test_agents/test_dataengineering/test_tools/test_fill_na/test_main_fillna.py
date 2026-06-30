import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.fill_na.main import FillNaAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestFillNaAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.fill_na.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.fill_na.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.fill_na.main.FillNaToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.fill_na.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = FillNaAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_fillna_operation(self):
        natural_language_input = 'Fill null values with value 0.'
        expected_json_output = {
            "column": None,
            "value": 0,
            "method": None,
            "axis": None,
            "limit": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly fill null values.")

    def test_fillna_multiple_columns(self):
        natural_language_input = 'Fill all nulls of column helical with value 0 and column helicalB with value 10.'
        expected_json_output = {
            "column": None,
            "value": {'helical': 0, 'helicalB': 10},
            "method": None,
            "axis": None,
            "limit": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly fill null values for multiple columns.")

    def test_fillna_specific_column(self):
        natural_language_input = 'Update the null values in the column testing_column with 55.'
        expected_json_output = {
            "column": "testing_column",
            "value": 55,
            "method": None,
            "axis": None,
            "limit": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly update null values in the specific column.")

    def test_fillna_bfill_method(self):
        natural_language_input = 'Fill all the nulls using bfill method.'
        expected_json_output = {
            "column": None,
            "value": None,
            "method": "bfill",
            "axis": None,
            "limit": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly fill null values using bfill method.")

    def test_fillna_ffill_method(self):
        natural_language_input = 'Fill all the nulls using ffill method.'
        expected_json_output = {
            "column": None,
            "value": None,
            "method": "ffill",
            "axis": None,
            "limit": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly fill null values using ffill method.")

    def test_fillna_specific_value_string(self):
        natural_language_input = 'Fill null values of column city with value as "No City".'
        expected_json_output = {
            "column": "city",
            "value": "No City",
            "method": None,
            "axis": None,
            "limit": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly fill null values of the specified column with a string value.")

    def test_fillna_first_null_ffill(self):
        natural_language_input = 'Fill the first null value of column city using ffill method.'
        expected_json_output = {
            "column": "city",
            "value": None,
            "method": "ffill",
            "axis": None,
            "limit": 1
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly fill the first null value using ffill method.")

    def test_fillna_value_along_columns_axis(self):
        natural_language_input = 'Fill the "Full" value along columns axis.'
        expected_json_output = {
            "column": None,
            "value": "Full",
            "method": None,
            "axis": "columns",
            "limit": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly fill values along columns axis.")

    def test_fillna_value_along_index_axis(self):
        natural_language_input = 'Fill the "Empty" value along index axis.'
        expected_json_output = {
            "column": None,
            "value": "Empty",
            "method": None,
            "axis": 0,
            "limit": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly fill values along index axis.")

if __name__ == '__main__':
    unittest.main()
