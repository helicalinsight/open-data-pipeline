import unittest
from unittest.mock import Mock, patch
from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.add_columns.main import AddColumnsAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestAddColumnsAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.add_columns.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.add_columns.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.add_columns.main.AddColumnToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.add_columns.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = AddColumnsAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_add_age_column(self):
        natural_language_input = 'Add "age" column to the data'
        expected_json_output = {
            "columns": "age",
            "default": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the age column.")

    def test_add_sampleIdentity_column(self):
        natural_language_input = 'Add a column named "sampleIdentity" to the data with default value as "sample data"'
        expected_json_output = {
            "columns": "sampleIdentity",
            "default": "sample data"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the sampleIdentity column.")

    def test_add_department_column(self):
        natural_language_input = 'Add "department" column with no default value'
        expected_json_output = {
            "columns": "department",
            "default": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the department column.")

    def test_add_email_column(self):
        natural_language_input = 'Add "email" column with default value as "N/A"'
        expected_json_output = {
            "columns": "email",
            "default": "N/A"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the email column.")

    def test_add_status_column(self):
        natural_language_input = 'Add "status" column with default value as "active"'
        expected_json_output = {
            "columns": "status",
            "default": "active"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the status column.")

    def test_add_phone_column(self):
        natural_language_input = 'Add "phone" column with no default value'
        expected_json_output = {
            "columns": "phone",
            "default": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the phone column.")

    def test_add_sampleIdentity_column(self):
        natural_language_input = 'Add a column named "sampleIdentity" to the data with default value as "sample data"'
        expected_json_output = {
            "columns": "sampleIdentity",
            "default": "sample data"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the sampleIdentity column.")

    def test_add_department_column(self):
        natural_language_input = 'Add "department" column with no default value'
        expected_json_output = {
            "columns": "department",
            "default": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the department column.")

    def test_add_email_column(self):
        natural_language_input = 'Add "email" column with default value as "N/A"'
        expected_json_output = {
            "columns": "email",
            "default": "N/A"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the email column.")

    def test_add_status_column(self):
        natural_language_input = 'Add "status" column with default value as "active"'
        expected_json_output = {
            "columns": "status",
            "default": "active"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the status column.")

    def test_add_phone_column(self):
        natural_language_input = 'Add "phone" column with no default value'
        expected_json_output = {
            "columns": "phone",
            "default": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the phone column.")

    def test_add_address_column(self):
        natural_language_input = 'Add "address" column with default value as "unknown"'
        expected_json_output = {
            "columns": "address",
            "default": "unknown"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the address column.")

    def test_add_salary_column(self):
        natural_language_input = 'Add "salary" column with default value as 0'
        expected_json_output = {
            "columns": "salary",
            "default": 0
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the salary column.")

    def test_add_join_date_column(self):
        natural_language_input = 'Add "join_date" column with default value as the current date'
        expected_json_output = {
            "columns": "join_date",
            "default": "current_date"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the join_date column.")

    def test_add_score_column(self):
        natural_language_input = 'Add "score" column with default value as 100'
        expected_json_output = {
            "columns": "score",
            "default": 100
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the score column.")

    def test_add_role_column(self):
        natural_language_input = 'Add "role" column with no default value'
        expected_json_output = {
            "columns": "role",
            "default": None
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the role column.")

    def test_add_grade_column(self):
        natural_language_input = 'Add "grade" column with default value as "A"'
        expected_json_output = {
            "columns": "grade",
            "default": "A"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the grade column.")

    def test_add_city_column(self):
        natural_language_input = 'Add "city" column with default value as "New York"'
        expected_json_output = {
            "columns": "city",
            "default": "New York"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the city column.")

    def test_add_country_column(self):
        natural_language_input = 'Add "country" column with default value as "USA"'
        expected_json_output = {
            "columns": "country",
            "default": "USA"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the country column.")

    def test_add_project_id_column(self):
        natural_language_input = 'Add "project_id" column with default value as 12345'
        expected_json_output = {
            "columns": "project_id",
            "default": 12345
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the project_id column.")

    def test_add_is_active_column(self):
        natural_language_input = 'Add "is_active" column with default value as true'
        expected_json_output = {
            "columns": "is_active",
            "default": True
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the is_active column.")

    def test_add_is_active_column(self):
        natural_language_input = 'Add "is_active" column with default value as true'
        expected_json_output = {
            "columns": "is_active",
            "default": True
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the is_active column.")

    def test_add_is_verified_column(self):
        natural_language_input = 'Add "is_verified" column with default value as false'
        expected_json_output = {
            "columns": "is_verified",
            "default": False
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the is_verified column.")

    def test_add_is_admin_column(self):
        natural_language_input = 'Add "is_admin" column with default value as true'
        expected_json_output = {
            "columns": "is_admin",
            "default": True
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the is_admin column.")

    def test_add_is_deleted_column(self):
        natural_language_input = 'Add "is_deleted" column with default value as false'
        expected_json_output = {
            "columns": "is_deleted",
            "default": False
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the is_deleted column.")

    def test_add_has_access_column(self):
        natural_language_input = 'Add "has_access" column with default value as true'
        expected_json_output = {
            "columns": "has_access",
            "default": True
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the has_access column.")

    def test_add_firstname_and_lastname_columns(self):
        natural_language_input = 'Add "firstname" column with default value as "abc" and "lastname" column'
        expected_json_output = [
            {"columns": "firstname", "default": "abc"},
            {"columns": "lastname", "default": None}
        ]

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the addition of the firstname and lastname columns.")

if __name__ == '__main__':
    unittest.main()