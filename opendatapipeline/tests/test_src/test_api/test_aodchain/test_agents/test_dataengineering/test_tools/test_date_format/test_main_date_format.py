import unittest
from unittest.mock import Mock, patch

from opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.date_format.main import DateFormatAgent

from opendatapipeline.src.models.connector import MongoConnector
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
session = mongo_client._Database__client.start_session()

class TestDateFormatAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_aod = Mock()
        self.mock_toolkit = Mock()
        self.mock_initialize_agent = Mock(return_value=self.mock_llm)

        patches = [
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.date_format.main.get_chat_model', return_value=self.mock_llm),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.date_format.main.DateFormatToolkit', return_value=self.mock_toolkit),
            patch('opendatapipeline.src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.date_format.main.initialize_agent', return_value=self.mock_initialize_agent)
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        self.agent = DateFormatAgent(user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a', session=session)
        self.agent.agent = self.mock_llm

    def test_date_format_exam_date(self):
        natural_language_input = 'Format exam_date to MMM d, yyyy.'
        expected_json_output = {
            "columns": "exam_date",
            "format": "MMM d, yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the exam_date.")

    def test_date_format_birth_date(self):
        natural_language_input = 'Convert birth_date format to dd-mm-yyyy.'
        expected_json_output = {
            "columns": "birth_date",
            "format": "dd-mm-yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert the birth_date format.")

    def test_date_format_registration_date(self):
        natural_language_input = 'Format registration_date to yyyy-MM-dd.'
        expected_json_output = {
            "columns": "registration_date",
            "format": "yyyy-MM-dd"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the registration_date.")

    def test_date_format_start_date(self):
        natural_language_input = 'Format start_date to MMMM dd, yyyy.'
        expected_json_output = {
            "columns": "start_date",
            "format": "MMMM dd, yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the start_date.")

    def test_date_format_end_date(self):
        natural_language_input = 'Format end_date to MM/dd/yyyy.'
        expected_json_output = {
            "columns": "end_date",
            "format": "MM/dd/yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the end_date.")

    def test_date_format_created_at(self):
        natural_language_input = 'Format created_at to dd MMMM yyyy.'
        expected_json_output = {
            "columns": "created_at",
            "format": "dd MMMM yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the created_at.")

    def test_date_format_updated_at(self):
        natural_language_input = 'Format updated_at to yyyy/MM/dd HH:mm:ss.'
        expected_json_output = {
            "columns": "updated_at",
            "format": "yyyy/MM/dd HH:mm:ss"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the updated_at.")

    def test_date_format_exam_date(self):
        natural_language_input = 'Format exam_date to MMM d, yyyy.'
        expected_json_output = {
            "columns": "exam_date",
            "format": "MMM d, yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the exam_date.")

    def test_date_format_birth_date(self):
        natural_language_input = 'Convert birth_date format to dd-mm-yyyy.'
        expected_json_output = {
            "columns": "birth_date",
            "format": "dd-mm-yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly convert the birth_date format.")

    def test_date_format_registration_date(self):
        natural_language_input = 'Format registration_date to yyyy-MM-dd.'
        expected_json_output = {
            "columns": "registration_date",
            "format": "yyyy-MM-dd"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the registration_date.")

    def test_date_format_start_date(self):
        natural_language_input = 'Format start_date to MMMM dd, yyyy.'
        expected_json_output = {
            "columns": "start_date",
            "format": "MMMM dd, yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the start_date.")

    def test_date_format_end_date(self):
        natural_language_input = 'Format end_date to MM/dd/yyyy.'
        expected_json_output = {
            "columns": "end_date",
            "format": "MM/dd/yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the end_date.")

    def test_date_format_created_at(self):
        natural_language_input = 'Format created_at to dd MMMM yyyy.'
        expected_json_output = {
            "columns": "created_at",
            "format": "dd MMMM yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the created_at.")

    def test_date_format_updated_at(self):
        natural_language_input = 'Format updated_at to yyyy/MM/dd HH:mm:ss.'
        expected_json_output = {
            "columns": "updated_at",
            "format": "yyyy/MM/dd HH:mm:ss"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the updated_at.")

    def test_date_format_join_date(self):
        natural_language_input = 'Format join_date to MM-dd-yyyy.'
        expected_json_output = {
            "columns": "join_date",
            "format": "MM-dd-yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the join_date.")

    def test_date_format_leave_date(self):
        natural_language_input = 'Format leave_date to dd/MM/yyyy.'
        expected_json_output = {
            "columns": "leave_date",
            "format": "dd/MM/yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the leave_date.")

    def test_date_format_event_date(self):
        natural_language_input = 'Format event_date to MMMM d, yyyy.'
        expected_json_output = {
            "columns": "event_date",
            "format": "MMMM d, yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the event_date.")

    def test_date_format_appointment_date(self):
        natural_language_input = "Format appointment_date to EEE, MMM d, ''yy."
        expected_json_output = {
            "columns": "appointment_date",
            "format": "EEE, MMM d, ''yy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the appointment_date.")

    def test_date_format_payment_date(self):
        natural_language_input = 'Format payment_date to dd.MM.yyyy.'
        expected_json_output = {
            "columns": "payment_date",
            "format": "dd.MM.yyyy"
        }

        self.mock_llm.process.return_value = expected_json_output

        actual_json_command = self.agent.agent.process(natural_language_input)

        self.mock_llm.process.assert_called_with(natural_language_input)

        self.assertEqual(actual_json_command, expected_json_output,
                         "The agent did not correctly format the payment_date.")

if __name__ == '__main__':
    unittest.main()
