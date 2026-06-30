import random
import string
import unittest
import uuid

from src.api.services.google_login.services import GoogleLoginService

from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestGoogleLoginService(unittest.TestCase):
    def test_google_login_service_with_existing_user(self):
        mock_request_data = {
            "id": "114550382253255756180",
            "email": "dighesurbhi88@gmail.com",
            "given_name": "Surbhi dighe"
        }

        class MockRequest:
            def get_json(self):
                return mock_request_data

        mock_request = MockRequest()
        response, status_code = session.with_transaction(lambda s:GoogleLoginService(session).google_login(mock_request),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        print(response)
        '''
        {'_id': ObjectId('6528ef73937ea4e403b98e27'), 'google_id': '114550382253255756180', 'email': 'dighesurbhi88@gmail.com', 'verified_email': True, 'name': 'Surbhi dighe', 'given_name': 'Surbhi dighe', 'family_name': None, 'picture': 'https://lh3.googleusercontent.com/a/ACg8ocICTw_h93PNcCCaNDloVGuvLCGUmcFIOw7C6mmU6Z6k3TI=s96-c', 'locale': 'en', 'external': None, 'password': None, 'jwt_auth_active': True, 'date_joined': datetime.datetime(2023, 10, 13, 7, 19, 15, 284000), 'role': 'free'}
        '''
        self.assertTrue(response['success'])
        self.assertEqual(status_code, 200)
        self.assertEqual(response['userid'], "6528ef73937ea4e403b98e27")
        self.assertIsNotNone(response['token'])

    def test_google_login_service_with_non_existing_user(self):
        # for existing user in response the userid is variable and for non existing user it is userID
        mock_request_data = {
            "id": "114550382253255756182",
            "email": "pooja@gmail.com",
            "given_name": "Pooja Shanmuk"
        }

        class MockRequest:
            def get_json(self):
                return mock_request_data

        mock_request = MockRequest()
        response, status_code = session.with_transaction(lambda s:GoogleLoginService(session).google_login(mock_request),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        '''
        {'success': True, 'userID': '660b9af28b64f6bb96f1dbef', 'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InBvb2phQGdtYWlsLmNvbSIsIl9pZCI6IjY2MGI5YWYyOGI2NGY2YmI5NmYxZGJlZiIsImV4cCI6MTcxMjA1NDU5NH0.8_zIkVk6tgCqBAxJ13s0h8iU65yA_3gz0sughgbrYvY', 'msg': 'Kindly await while we configure everything for you.'}
        '''
        self.assertTrue(response['success'])

    def test_google_login_service_with_non_existing_user_newuser_everytime(self):
        dynamic_id = str(uuid.uuid4())
        dynamic_email = f"user{random.randint(1000, 9999)}@gmail.com"
        dynamic_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        mock_request_data = {
            "id": dynamic_id,
            "email": dynamic_email,
            "given_name": dynamic_name
        }

        class MockRequest:
            def get_json(self):
                return mock_request_data

        mock_request = MockRequest()
        response, status_code = session.with_transaction(
            lambda s: GoogleLoginService(session).google_login(mock_request),
            read_concern=ReadConcern("local"),
            write_concern=wc_majority,
            read_preference=ReadPreference.PRIMARY,
        )

        self.assertTrue(response['success'])


if __name__ == '__main__':
    unittest.main()
