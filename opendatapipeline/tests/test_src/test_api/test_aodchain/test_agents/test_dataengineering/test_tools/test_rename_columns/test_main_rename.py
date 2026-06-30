import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.rename_columns.main import RenameColumnsAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestRenameColumnsAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.rename_columns.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.rename_columns.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.rename_columns.main.RenameColumnsToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.rename_columns.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = RenameColumnsAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_rename_age_column(self):
        natural_language_input = 'Rename age column to age_2'
        expected_json_output = {"old_name": "age", "new_name": "age_2"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly rename the columns.")

    def test_rename_identity_column(self):
        natural_language_input = 'Rename "identity" column to "studentIdentity"'
        expected_json_output = {"old_name": "identity", "new_name": "studentIdentity"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly rename the columns.")

    def test_rename_salary_column(self):
        natural_language_input = 'Rename salary column to monthlySalary'
        expected_json_output = {"old_name": "salary", "new_name": "monthlySalary"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly rename the columns.")

    def test_rename_address_column(self):
        natural_language_input = 'I like to rename address column to fullAddress'
        expected_json_output = {"old_name": "address", "new_name": "fullAddress"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly rename the columns.")

    def test_rename_phone_column(self):
        natural_language_input = 'Please Rename phone to contactNumber'
        expected_json_output = {"old_name": "phone", "new_name": "contactNumber"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly rename the columns.")

    def test_rename_department_column(self):
        natural_language_input = 'Rename department to dept'
        expected_json_output = {"old_name": "department", "new_name": "dept"}

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly rename the columns.")

if __name__ == '__main__':
    unittest.main()
