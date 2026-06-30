from src.models.connector import MongoConnector
from src.api import app
from src.models.mongo import mongo_factory
import unittest
from src.api.validators.jwt_authentication import JWTAuthentication



class TestSettings(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.valid_token = JWTAuthentication().encode(
            "dighesurbhi88@gmail.com", "6528ef73937ea4e403b98e27"
        )

    def test_get_settings_without_token(self):
        response = self.app.get("/api/v1/user_preferences")
        self.assertEqual(response.status_code, 400)

    def test_get_settings_response_200_ok(self):
        response = self.app.get(
            "/api/v1/user_preferences", headers={"Authorization": self.valid_token}
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn(response.json, [{'files': {'file_size': '5MB'}},{'files': {'num_records': 100, 'file_size': 5}}])

    def test_create_settings_response_201(self):
        response = self.app.post(
            "/api/v1/user_preferences",
            headers={
                "Authorization": self.valid_token,
                "Content-Type": "application/json",
            },
            json={"files": {"file_size": "5MB"}, "font": "40px"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'files': {'num_records': 100, 'file_size': "5MB"}})

    def test_create_settings_if_size_is_0MB(self):
        response = self.app.post(
            "/api/v1/user_preferences",
            headers={
                "Authorization": self.valid_token,
                "Content-Type": "application/json",
            },
            json={"files": {"file_size": "0MB"}, "font": "40px"},
        )
        self.assertEqual(response.status_code, 201)


    def test_create_settings_if_size_is_0(self):
        response = self.app.post(
            "/api/v1/user_preferences",
            headers={
                "Authorization": self.valid_token,
                "Content-Type": "application/json",
            },
            json={"files": {"file_size": "0"}, "font": "40px"},
        )
        self.assertEqual(response.status_code, 201)

    def test_create_settings_with_null_values(self):
        payload = {
            "files": {
                "file_size": None,
                "num_records": None
            }
        }

        response = self.app.post(
            "/api/v1/user_preferences",
            headers={
                "Authorization": self.valid_token,
                "Content-Type": "application/json",
            },
            json=payload,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'files': {'num_records': 100, 'file_size': 5}})

    def test_create_settings_with_file_size_null(self):
        payload = {
            "files": {
                "file_size": None,
                "num_records": 50
            }
        }

        response = self.app.post(
            "/api/v1/user_preferences",
            headers={
                "Authorization": self.valid_token,
                "Content-Type": "application/json",
            },
            json=payload,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'files': {'num_records': 50, 'file_size': 5}})

    def test_create_settings_with_num_records_null(self):
        payload = {
            "files": {
                "file_size": 3,
                "num_records": None
            }
        }

        response = self.app.post(
            "/api/v1/user_preferences",
            headers={
                "Authorization": self.valid_token,
                "Content-Type": "application/json",
            },
            json=payload,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'files': {'num_records': 100, 'file_size': 3}})

    def test_create_settings_with_values(self):
        payload = {
            "files": {
                "file_size": 7,
                "num_records": 120
            }
        }

        response = self.app.post(
            "/api/v1/user_preferences",
            headers={
                "Authorization": self.valid_token,
                "Content-Type": "application/json",
            },
            json=payload,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'files': {'num_records': 120, 'file_size': 7}})

        