import unittest

from src.api.services.saved_connections.service import SavedConnectionsService

from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestSavedConnectionsService(unittest.TestCase):
    def test_saved_connections_with_existing_user_and_type(self):
        user_id = "65365001d9654d9ec1172f87"
        type = "redshift"
        response, status_code = session.with_transaction(lambda s:SavedConnectionsService(session).get_saved_connections(user_id, type),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_code = 200

        expected_output = {'success': True,
                           'databases': [{'_id': '65e4a71ec05be5064e004df6',
                                          'alias': 'Resshit',
                                          'type': 'redshift'}],
                           'msg': 'Fetched connections successfully.'}
        self.assertTrue(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)

    def test_saved_connections_with_existing_user_and_not_existing_type(self):
        user_id = "6544cb81d335bb2189b06e00"
        type = "s3"
        response, status_code = session.with_transaction(lambda s:SavedConnectionsService(session).get_saved_connections(user_id, type),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_code = 200
        print(response)
        expected_output = {'databases': [], 'msg': 'Fetched connections successfully.', 'success': True}
        self.assertTrue(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)

    def test_saved_connections_with_non_existing_user(self):
        # even though user doesnt exist it returns success as true but databases as empty list
        user_id = "6544cb81d335bb2189b06e21"
        type = "s3"
        response, status_code = session.with_transaction(lambda s:SavedConnectionsService(session).get_saved_connections(user_id, type),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_code = 200
        print(response)
        expected_output = {'databases': [], 'msg': 'Fetched connections successfully.', 'success': True}
        self.assertTrue(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)


if __name__ == '__main__':
    unittest.main()
