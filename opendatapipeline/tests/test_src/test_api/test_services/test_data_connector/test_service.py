import unittest

import pytest

from src.api.services.data_connector.service import DataConnectorsService

from ......src.models.connector import MongoConnector
from ......src.models.mongo.mongo_factory import MongoFactory
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)

mongo_client = MongoConnector().client
session = mongo_client._Database__client.start_session()
mongo_connections = MongoFactory(mongo_client, "connections", session=session)
class TestDataConnectorService(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_get_data_connector(self):
        connection_id = "65e4a71ec05be1234e004df6"
        response, status_code = session.with_transaction(lambda s:DataConnectorsService(session).get_data_connector(connection_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_output = {'success': True,
                           'connection_data':
                               {'connection_id': '65e4a71ec05be1234e004df6',
                                'connection_details': {'username': 'redshift',
                                                       'password': 'cassendra',
                                                       'host': '57.128.161.235',
                                                       'port': '9042'}},
                           'msg': 'Connection details fetched successfully.'}

        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, 200)

    def test_create_data_connector(self):
        user_id = "65365001d9654d9ec1172f87"
        req_data = {
            "connection_details": {
                "username": "admin",
                "password": "HelicalAdmin1$",
                "host": "helical-test.982586453799.us-east-1.redshift-serverless.amazonaws.com",
                "port": 5439,
                "database": "dev"
            },
            "connector": "redshift",
            "user_id": "65365001d9654d9ec1172f87"
        }
        response, status_code = session.with_transaction(lambda s:DataConnectorsService(session).create_data_connector(req_data, user_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response['success'])
        self.assertEqual(response['message'], 'Connection saved successfully.')
        self.assertEqual(status_code, 200)

    @pytest.mark.run(order=2)
    def test_update_data_connector(self):
        req_data = {"connection_id": "65e4a71ec05be5064e004df9",
                    "connection_details": {
                        "username": "cassandra_connect",
                        "password": "cassandra_connect",
                        "host": "57.128.161.235",
                        "port": "9042"
                    },
                    "user_id": "65365001d9654d9ec1172f89"
                    }
        response, status_code = session.with_transaction(lambda s: DataConnectorsService(session).update_data_connector(req_data),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response['success'])
        self.assertEqual(response['updated_data']['connection_details']['password'], "cassandra_connect")
        self.assertEqual(response['msg'], 'Connection details updated successfully.')
        self.assertEqual(status_code, 200)

    @pytest.mark.run(order=3)
    def test_delete_data_connector(self):
        req_data = {"_id": "65e4a71ec05be5064e004df6"
                    }
        response, status_code = session.with_transaction(lambda s: DataConnectorsService(session).delete_data_connector(req_data),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_output = {'success': True, 'msg': 'Connection deleted successfully.', 'connection_id': '65e4a71ec05be5064e004df6'}
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, 200)


    def test_create_data_connector_without_pool_connection(self):
        user_id = "65365001d9654d9ec1172f87"
        req_data = {
            "connection_details": {
                "username": "admin",
                "password": "HelicalAdmin1$",
                "host": "helical-test.982586453799.us-east-1.redshift-serverless.amazonaws.com",
                "port": 5439,
                "database": "dev"
            },
            "type": "postgres",
            "connector": "redshift",
            "user_id": "65365001d9654d9ec1172f87"
        }
        response, status_code = session.with_transaction(lambda s:DataConnectorsService(session).create_data_connector(req_data, user_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        self.assertTrue(response['success'])
        self.assertEqual(response['message'], 'Connection saved successfully.')
        self.assertEqual(status_code, 200)

    def test_create_data_connector_wit_pool_connection(self):
        user_id = "65365001d9654d9ec1172f87"
        req_data = {
            "connection_details": {
                "username": "admin",
                "password": "HelicalAdmin1$",
                "host": "helical-test.982586453799.us-east-1.redshift-serverless.amazonaws.com",
                "port": 5439,
                "database": "dev",
                "type": "mysql",
                "connection_pool" : {
                        "pool_name":"mysql",
                        "pool_size": 5
                    }  
            },
            "type": "postgres",
            "connector": "redshift",
            "user_id": "65365001d9654d9ec1172f87"
        }
        response, status_code = session.with_transaction(lambda s:DataConnectorsService(session).create_data_connector(req_data, user_id),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        connection_id = response['connection_id']
        connection_pool = mongo_connections.get_by_id(connection_id)[1]['connection_details']['connection_pool']
        self.assertEqual(connection_pool, req_data['connection_details']['connection_pool'])
        self.assertTrue(response['success'])
        self.assertEqual(response['message'], 'Connection saved successfully.')
        self.assertEqual(status_code, 200)




if __name__ == '__main__':
    unittest.main()
