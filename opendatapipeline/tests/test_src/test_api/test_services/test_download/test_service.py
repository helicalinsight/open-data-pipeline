import unittest
import pytest
from src.api import app
from src.api.validators.jwt_authentication import JWTAuthentication


class TestDownloadService(unittest.TestCase):
    # this requires active http request to download file to test send file of flask
    def setUp(self):
        self.app = app.test_client()
        self.valid_token = JWTAuthentication().encode("shiv@gmail.com", "65365001d9654d9ec1172f87")

    @pytest.mark.skip("File not present")
    def test_download_with_existing_feather_id(self):
        response = self.app.get('/api/v1/download/6602a3a74475001648200351?chat_id=66729ec22ee1491c32b05b64',
                                   headers={'Authorization': self.valid_token}
                                   )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.get_data)

    def test_download_with_non_existing_feather_id(self):
        response = self.app.get('/api/v1/download/6602a3a74475001648200331?chat_id=66729ec22ee1491c32b05b64',
                                   headers={'Authorization': self.valid_token}
                                   )
        expected_output = {'success': False, 'text': 'The file not found'}
        self.assertEqual(response.json, expected_output)
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
