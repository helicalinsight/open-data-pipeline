import unittest
import pytest
import os
from src.api.services.connections.service import ConnectionService

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestConnectionsService(unittest.TestCase):
    def test_connection_services_with_details_with_vpn(self):
        req_data = {
            "details": {
                        "username": "admin",
                        "password": "HelicalAdmin1$",
                        "host": "helical-test.982586453799.us-east-1.redshift-serverless.amazonaws.com",
                        "port": 5439,
                        "database": "dev"
                      },
            "connector": "redshift"
        }
        user_id = "65365001d9654d9ec1172f77"
        response, status_code = ConnectionService.test_connection(req_data, user_id)
        print(response, status_code)
        expected_code= 200
        expected_output = {'success': True, 'msg': 'Connection tested successfully'}
        self.assertTrue(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)

    def test_connection_services_with_connection_id_with_vpn(self):
        req_data = {
            "details":{"connection_id": "654879fe42a09b96f228302f"},
            "connector": "redshift"
        }
        user_id = "65365001d9654d9ec1172f77"
        response, status_code = ConnectionService.test_connection(req_data, user_id)
        print(response, status_code)
        expected_code= 200
        expected_output = {'success': True, 'msg': 'Connection tested successfully'}
        self.assertTrue(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)

    def test_connection_services_with_wrong_connection_id_with_vpn(self):
        req_data = {
            "details":{"connection_id": "654879fe42a09b96f228302a"},
            "connector": "redshift"
        }
        user_id = "65365001d9654d9ec1172f77"
        response, status_code = ConnectionService.test_connection(req_data, user_id)
        print(response, status_code)
        expected_code = 500
        expected_output = {'success': False, 'msg': 'An error occurred while testing the connection.'}
        self.assertFalse(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)


if __name__ == '__main__':
    unittest.main()
