import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.union.main import UnionAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestUnionAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.union.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.union.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.union.main.UnionToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.union.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = UnionAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_union_employees_files(self):
        natural_language_input = 'Union "Employees_2021" and "Employees_2022" files'
        expected_json_output = {"columns": None, "file_names": ["Employees_2021", "Employees_2022"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the union operation on the 'Employees_2021' and 'Employees_2022' files.")

    def test_union_sales_files(self):
        natural_language_input = 'Union "Sales_Q1" and "Sales_Q2" files'
        expected_json_output = {"columns": None, "file_names": ["Sales_Q1", "Sales_Q2"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the union operation on the 'Sales_Q1' and 'Sales_Q2' files.")

    def test_union_inventory_files(self):
        natural_language_input = 'Union "Inventory_Jan" and "Inventory_Feb" files'
        expected_json_output = {"columns": None, "file_names": ["Inventory_Jan", "Inventory_Feb"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the union operation on the 'Inventory_Jan' and 'Inventory_Feb' files.")

    def test_union_orders_files(self):
        natural_language_input = 'Union "Orders_2020" and "Orders_2021" files'
        expected_json_output = {"columns": None, "file_names": ["Orders_2020", "Orders_2021"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the union operation on the 'Orders_2020' and 'Orders_2021' files.")

    def test_union_products_files(self):
        natural_language_input = 'Union "Products_A" and "Products_B" files'
        expected_json_output = {"columns": None, "file_names": ["Products_A", "Products_B"]}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the union operation on the 'Products_A' and 'Products_B' files.")

if __name__ == '__main__':
    unittest.main()