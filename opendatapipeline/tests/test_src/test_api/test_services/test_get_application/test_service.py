import unittest

from src.api.services.get_application.service import ApplicationService

from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestApplicationService(unittest.TestCase):
    def test_application_service_with_non_existing_user_id(self):
        user_id = "65365001d9654d9ec1172f85"
        response, status_code = session.with_transaction(lambda s:ApplicationService(session).get_appservice(user_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_code = 500
        expected_output = {'success': False, 'configuration': None, 'job_help_info': None, 'editor_configuration': None, 'schedule_configuration': None, 'version': None, 'msg': 'Error fetching Application.'}
        self.assertFalse(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)

    def test_application_service_with_existing_user_id(self):
        user_id = "65365001d9654d9ec1172f87"
        response, status_code = session.with_transaction(lambda s:ApplicationService(session).get_appservice(user_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_code = 200
        expected_configuration= {'role': 'admin', 'chat': ['jobs', 'create', 'schedule'], 'job': ['history', 'datapreview', 'reset', 'load', 'trigger', 'undo', 'yaml', 'ace'], 'datasources': ['flat_files', 'redshift', 'mysql', 'snowflake', 'postgres', 'astra', 'cassandra', 'firebird', 'oracle', 'ms_sql_server', 'google_sheets', 's3','couchbase', 'databricks']}
        #expected_output = {'success': True, 'configuration': {'role': 'admin', 'chat': ['jobs', 'create', 'schedule'], 'job': ['histroy', 'dataPreview', 'reset', 'load', 'trigger', 'undo', 'redo'], 'datasources': ['flat_files', 'redshift', 'mysql', 'snowflake', 'postgres', 'astra', 'cassandra', 'firebird', 'oracle', 'ms_sql_server']}, 'msg': 'Application Configurations Fetched Successfully!'}
        self.assertTrue(response['success'])
        self.assertEqual(response['configuration'], expected_configuration)
        self.assertEqual(response['editor_configuration']['yaml'][0]['label'], 'read_files')
        self.assertEqual(status_code, expected_code)

    def test_application_service_schedule_state(self):
        user_id = "65365001d9654d9ec1172f87"
        response, status_code = session.with_transaction(lambda s:ApplicationService(session).get_appservice(user_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        states = response['schedule_configuration']['state']
        expected_code = 200
        self.assertEqual(status_code, expected_code)
        self.assertTrue(response['success'])
        self.assertIsInstance(response['schedule_configuration']['state'], dict)
        expected_states = ['queued', 'running', 'success', 'failed']
        for state in expected_states:
            assert state in states, f"Expected state '{state}' not found in schedule.state"


if __name__ == '__main__':
    unittest.main()
