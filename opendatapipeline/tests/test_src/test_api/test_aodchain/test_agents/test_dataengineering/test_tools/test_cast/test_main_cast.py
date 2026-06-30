import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cast.main import CastAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestCastAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cast.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cast.main.DataEngineeringWrapper', return_value=self.mock_aod),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cast.main.CastToolkit.from_aod_api_wrapper', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cast.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = CastAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_cast_age_to_integer(self):
        natural_language_input = 'Cast the "age" column to integer'
        expected_json_output = {"columns": "age", "old_type": None, "new_type": "integer"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'age' column to integer.")
        
    
    def test_cast_salary_to_float(self):
        natural_language_input = 'Cast the "salary" column to float'
        expected_json_output = {"columns": "salary", "old_type": None, "new_type": "float"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'salary' column to float.")

    def test_cast_birthdate_to_date(self):
        natural_language_input = 'Cast the "birthdate" column to date'
        expected_json_output = {"columns": "birthdate", "old_type": None, "new_type": "date"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'birthdate' column to date.")

    def test_cast_is_active_to_boolean(self):
        natural_language_input = 'Cast the "is_active" column to boolean'
        expected_json_output = {"columns": "is_active", "old_type": None, "new_type": "boolean"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'is_active' column to boolean.")

    def test_cast_employee_id_to_string(self):
        natural_language_input = 'Cast the "employee_id" column to string'
        expected_json_output = {"columns": "employee_id", "old_type": None, "new_type": "string"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'employee_id' column to string.")

    def test_cast_score_to_double(self):
        natural_language_input = 'Cast the "score" column to double'
        expected_json_output = {"columns": "score", "old_type": None, "new_type": "double"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'score' column to double.")

    def test_cast_identity_to_string(self):
        natural_language_input = 'Cast the "identity" column to string'
        expected_json_output = {"columns": "identity", "old_type": None, "new_type": "string"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'identity' column to string.")

    def test_cast_identity_to_object(self):
        natural_language_input = 'Cast the "identity" column to object'
        expected_json_output = {"columns": "identity", "old_type": None, "new_type": "object"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'identity' column to object.")

    def test_cast_dob_unix_to_date(self):
        natural_language_input = 'Cast the "dob" column from Unix timestamp to date'
        expected_json_output = {"columns": "dob", "old_type": "unix", "new_type": "date"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'dob' column from Unix timestamp to date.")

    def test_cast_datelogsTesting_mmddyyyy_to_date(self):
        natural_language_input = 'Cast the "datelogsTesting" column from mmddyyyy format to date'
        expected_json_output = {"columns": "datelogsTesting", "old_type": "mmddyyyy", "new_type": "date"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'datelogsTesting' column from mmddyyyy format to date.")

    def test_cast_startdateTesting_mdy_to_date(self):
        natural_language_input = 'Change the "startdateTesting" column from mdy format to date'
        expected_json_output = {"columns": "startdateTesting", "old_type": "mdy", "new_type": "date"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'startdateTesting' column from mdy format to date.")

    def test_cast_end_dateTesting_ddmmyyyy_to_date(self):
        natural_language_input = 'Change the "end_dateTesting" column from ddmmyyyy format to date'
        expected_json_output = {"columns": "end_dateTesting", "old_type": "ddmmyyyy", "new_type": "date"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'end_dateTesting' column from ddmmyyyy format to date.")

    def test_cast_salary_float_to_integer(self):
        natural_language_input = 'Convert the "salary" column from float to integer'
        expected_json_output = {"columns": "salary", "old_type": "float", "new_type": "integer"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'salary' column from float to integer.")

    def test_cast_phone_number_string_to_integer(self):
        natural_language_input = 'Cast the "phone_number" column from string to integer'
        expected_json_output = {"columns": "phone_number", "old_type": "string", "new_type": "integer"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'phone_number' column from string to integer.")

    def test_cast_origin_etd_ddMMMYY_to_date(self):
        natural_language_input = 'Cast the "origin_etdTesting" column to date from dd-MMM-yy'
        expected_json_output = {"columns": "origin_etdTesting", "old_type": "dd-MMM-yy", "new_type": "date"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'origin_etdTesting' column to date from dd-MMM-yy.")

    def test_cast_dob_to_date(self):
        natural_language_input = 'Cast the "dob" column to date'
        expected_json_output = {"columns": "dob", "old_type": None, "new_type": "date"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'dob' column to date.")

    def test_cast_dob_mmddyyyy_to_date(self):
        natural_language_input = 'Cast the "dob" column to date using mm-dd-yyyy'
        expected_json_output = {"columns": "dob", "old_type": "mm-dd-yyyy", "new_type": "date"}

        self.mock_llm.process.return_value = expected_json_output
        actual_json_command = self.agent.agent.process(natural_language_input)
        self.mock_llm.process.assert_called_with(natural_language_input)
        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly process the casting of the 'dob' column to date using mm-dd-yyyy.")

if __name__ == '__main__':
    unittest.main()
