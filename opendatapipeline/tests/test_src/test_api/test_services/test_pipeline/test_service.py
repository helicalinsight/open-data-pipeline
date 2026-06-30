import unittest

from src.api.services.pipeline.service import PipelineHistoryService

from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestPipelineService(unittest.TestCase):
    def test_get_pipeline_history_with_invalid_chat_id(self):
        chat_id = "6757eef8de0e916ac22d4ad7"
        response, status_code = session.with_transaction(
            lambda s:PipelineHistoryService(session).get_pipeline_history(chat_id),
            read_concern=ReadConcern("local"),
            write_concern=wc_majority,
            read_preference=ReadPreference.PRIMARY
        )
        self.assertEqual(status_code, 204)
        
    def test_get_pipleline_history_with_existing_chat_id(self):
        chat_id = "6757ddf8de0e916ac22d4ad7"
        response, status_code = session.with_transaction(lambda s:PipelineHistoryService(session).get_pipeline_history(chat_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        """
        def test_get_pipleline_history(self):
            chat_id = "66729ec22ee1491c32b05b53"
            response, status_code = session.with_transaction(lambda s:PipelineHistoryService(session).get_pipeline_history(chat_id),read_concern=ReadConcern("local"),
                        write_concern=wc_majority,
                        read_preference=ReadPreference.PRIMARY,)
            expected_output = {'success': True, 'history': [{'function': 'read_files', 'parameters': [{'alias': 'customers-100', '_id': '74d82e21-a20f-4097-9181-2502bb2846f5'}], 'files': None, 'database_alias': 'flat_files'}, {'function': 'read_files', 'parameters': [{'alias': 'industry', '_id': 'be4f064b-8c0a-492f-8b75-a4f94532266a'}], 'files': None, 'database_alias': 'flat_files'}, {'function': 'rename_columns', 'parameters': [{'old_name': 'industry', 'new_name': 'indus'}], 'files': [{'alias': ['customers-100']}]}], 'next': []}
            self.assertEqual(response, expected_output)
            self.assertEqual(status_code, 200)

        def test_get_pipleline_history_with_non_existing_chat_id(self):
            chat_id = "6602a39d4475001648200351"
            response, status_code = session.with_transaction(lambda s:PipelineHistoryService(session).get_pipeline_history(chat_id),read_concern=ReadConcern("local"),
                        write_concern=wc_majority,
                        read_preference=ReadPreference.PRIMARY,)
            '''
            {'success': True, 'history': [{'id': '8ac63ea9-0cc1-4069-ac4c-5f6515c19136', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': [{'alias': 'customers-100'}], 'files': None}]}
            '''
            expected_output = {'success': False, 'msg': 'Failed to get data by id'}
            self.assertEqual(response, expected_output)
            self.assertEqual(status_code, 400)"""


if __name__ == '__main__':
    unittest.main()
