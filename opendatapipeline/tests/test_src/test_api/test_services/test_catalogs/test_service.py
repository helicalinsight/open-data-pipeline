import unittest
import pytest
import os

from src.api.services.catalogs.service import ListCatalogsService

from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestListCatalogsService(unittest.TestCase):
    def test_list_catalogs_service_without_valid_data_with_vpn(self):
        req_data = {}
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_catalogs(req_data),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_code= 500
        expected_output = {'success': False, 'msg': 'Invalid request data.', 'dataCatalog': None}
        self.assertFalse(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)

    def test_list_catalogs_service_with_missing_variables_with_vpn(self):
        req_data = {
            "db_type":"cassandra",
            "connection_id":"65cf47169536c580315b0d95"
        }
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_catalogs(req_data),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_code= 500
        expected_output = {'success': False, 'msg': 'Failed to get data by id', 'dataCatalog': None}
        self.assertFalse(response['success'])
        self.assertEqual(response, expected_output)
        self.assertEqual(status_code, expected_code)

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="not able to connect to postgres")
    def test_list_catalogs_service_with_correct_data(self):
        req_data = {
            "type": "postgres",
            "connection_id": "654879fe42a09b96f228302c",
            "database": "sakila"
        }
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_catalogs(req_data),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_code= 200
        self.assertTrue(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_code)

    def test_list_catalogs_service_exception_with_vpn(self):
        req_data = {
            "type": "postgresss",
            "connection_id": "654879fe42a09b96f228302c",
            "database": "pd"
        }
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_catalogs(req_data),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_code= 500
        self.assertFalse(response['success'])
        self.assertEqual(response, {'success': False, 'msg': 'Failed to connect to the database.', 'dataCatalog': None})
        self.assertEqual(status_code, expected_code)



class TestListColumns(unittest.TestCase):

    # def test_list_catalogs_service_for_cassandra(self):
    #     req_data = {
    #         "connection_id": "654879fe42a09b96f228102e",
    #         "catalog": "testkeyspace.dummy_table"
    #     }
        
    #     response, status_code = session.with_transaction(lambda s:ListColumns(session).list_columns(req_data),
    #                 write_concern=wc_majority,
    #                 read_preference=ReadPreference.PRIMARY,)
    #     print(response, status_code)
    #     self.assertTrue(response["success"])
    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_list_catalogs_service_for_firebird(self):
        req_data = {
            "type" : "database",
            "details" : {
            "connection_id": "66434293f1b35b98dcb35bc9",
            "catalog": "employee.employee"
        }}
        
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_columns(req_data),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response, [])
    
    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_list_catalogs_service_for_postgresql(self):
        req_data = {
            "type" : "database",
            "details" : {
            "connection_id": "654879fe42a09b96f228102c",
            "catalog": "public.dummy_table"
        }}
        
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_columns(req_data),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response["success"])
        self.assertEqual(response["columns"], ["id", "name"])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_list_catalogs_service_for_mysql(self):
        req_data = {
            "type" : "database",
            "details" : {
            "connection_id": "654879fe42a09b96f228303e",
            "catalog": "test"
        }}
        
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_columns(req_data),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response["success"])
        self.assertEqual(response["columns"], ["id", "name"])
    
    # def test_list_catalogs_service_for_astra(self):
    #     req_data = {
    #         "connection_id": "654879fe42a09b96f228302a",
    #         "catalog": "example_keyspace.users"
    #     }
        
    #     response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_columns(req_data),
    #                 write_concern=wc_majority,
    #                 read_preference=ReadPreference.PRIMARY,)
    #     print(response, status_code)
    #     self.assertTrue(response["success"])
    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_list_catalogs_service_for_redshift(self):
        req_data = {
            "type" : "database",
            "details" : {
            "connection_id": "654879fe42a09b96f228102c",
            "catalog": "public.dummy_table"
        }}
        
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_columns(req_data),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response["success"])
        self.assertEqual(response["columns"], ["id", "name"])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_list_catalogs_service_for_snowflake(self):
        req_data = {
            "type" : "database",
            "details" : {
            "connection_id": "654879fe42a09b96f228302e",
            "catalog": "FIREBIRD_COUNTRY.COUNTRY"
        }}
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_columns(req_data),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertTrue(response["success"])
        self.assertEqual(response["columns"], ['EMP_NO', 'FIRST_NAME', 'LAST_NAME', 'PHONE_EXT', 'HIRE_DATE', 'DEPT_NO', 'JOB_CODE', 'JOB_GRADE', 'JOB_COUNTRY', 'SALARY', 'FULL_NAME'])

    def test_list_catalogs_service_for_files(self):
        req_data = {
            "source" : "file",
            "connection_id": "74d82e21-a20f-4097-9181-2502bb2846f5",
        }
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_columns(req_data),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        print(response, status_code)
        self.assertTrue(response["success"])
        self.assertEqual(response["columns"], ['public_id', 'firstname', 'lastname', 'age', 'dob', 'zipcode', 'address'])


    def test_list_catalogs_service_for_files_with_catalog(self):
        req_data = {
            "source" : "file",
            "connection_id": "74d82e21-a20f-4097-9181-2502bb2845f9",
            "catalog": "msheets.Sheet3"
        }
        response, status_code = session.with_transaction(lambda s:ListCatalogsService(session).list_columns(req_data),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        print(response, status_code)
        
        self.assertTrue(response["success"])
        self.assertEqual(response["columns"], ['Sheet3-c1', 'Sheet3-c2', 'Sheet3-c3', 'Sheet3-c4'])
        self.assertEqual(response['msg'], 'Columns fetched successfully from file.')


if __name__ == '__main__':
    unittest.main()
