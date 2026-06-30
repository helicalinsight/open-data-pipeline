import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.joins.main import JoinsAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestJoinsAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.joins.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.joins.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.joins.main.JoinsToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.joins.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = JoinsAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm
        
    def test_join_operation(self):
        natural_language_input = 'Join "Enrollments" and "Students" files using "identity" from Enrollments and "id" from Students by left join'
        expected_json_output = {
            "file_names": ["Enrollments", "Students"],
            "left_on": "identity",
            "right_on": "id",
            "join_type": "left"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly perform the join operation.")

    def test_join_helical_aod_inner(self):
        natural_language_input = 'Join "helical" and "aod" files by "id" and "aod_id" with inner join'
        expected_json_output = {
            "file_names": ["helical", "aod"],
            "left_on": ["id", "dept"],
            "right_on": ["aod_id", "aod_dept"],
            "join_type": "inner"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly perform the inner join.")

    def test_join_orders_customers_outer(self):
        natural_language_input = 'Join "orders" and "customers" files using "order_id" from orders and "customer_id" from customers by outer join'
        expected_json_output = {
            "file_names": ["orders", "customers"],
            "left_on": "order_id",
            "right_on": "customer_id",
            "join_type": "outer"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly perform the outer join.")

    def test_join_products_categories_right(self):
        natural_language_input = 'Join "products" and "categories" files by "product_id" and "category_id" with right join'
        expected_json_output = {
            "file_names": ["products", "categories"],
            "left_on": "product_id",
            "right_on": "category_id",
            "join_type": "right"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly perform the right join.")

    def test_join_sales_regions_inner(self):
        natural_language_input = 'Join "sales" and "regions" files using "sales_rep" from sales and "region_code" from regions by inner join'
        expected_json_output = {
            "file_names": ["sales", "regions"],
            "left_on": "sales_rep",
            "right_on": "region_code",
            "join_type": "inner"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly perform the inner join.")

if __name__ == '__main__':
    unittest.main()
