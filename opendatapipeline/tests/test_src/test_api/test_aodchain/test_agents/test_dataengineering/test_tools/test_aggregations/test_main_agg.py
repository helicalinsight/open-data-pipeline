import unittest
from unittest.mock import Mock, patch
from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.aggregations.main import AggregationsAgent 

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestAggregationsAgent(unittest.TestCase):
    def setUp(self):
        self.mock_memory = Mock()
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm) 

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.aggregations.main.ConversationBufferMemory', return_value=self.mock_memory),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.aggregations.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.aggregations.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.aggregations.main.AggregationsToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.aggregations.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = AggregationsAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm  

    def test_sum_aggregation_with_group_by(self):
        natural_language_input = "Perform sum of value1, value2 group by category and subcategory and store it in sum_values"
        expected_json_output = {
            "columns": ["value1", "value2"],
            "destination_columns": ["sum_values"],
            "agg": ["sum"],
            "group_by": ["category", "subcategory"]
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

    def test_mean_aggregation_with_group_by_category_subcategory(self):

        natural_language_input = "Calculate mean of value1, value2 group by category and subcategory and store it in values_mean"
        expected_json_output = {
            "columns": ["value1", "value2"],
            "destination_columns": ["values_mean"],
            "agg": ["mean"],
            "group_by": ["category", "subcategory"]
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                        "The agent did not correctly convert the natural language command into a JSON command.")

    def test_sum_aggregation_without_group_by(self):
        natural_language_input = "Calculate mean of value1, value2"
        expected_json_output = {
            "columns": ["value1", "value2"],
            "destination_columns": None,
            "agg": ["mean"],
            "group_by": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert the natural language command into JSON command.")

if __name__ == '__main__':
    unittest.main()

