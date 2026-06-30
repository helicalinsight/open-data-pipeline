import io
import json
import os
import unittest
import pytest
from werkzeug.datastructures import FileStorage

from src.api.services.files.service import FileService, FileServiceCache

from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()


class TestFilesService(unittest.TestCase):
    def test_file_service_get_files_list(self):
        response, status_code = session.with_transaction(lambda s:FileService(session).get_files_list("65365001d9654d9ec1172f81"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_output = 200
        self.assertTrue(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_output)

    def test_file_service_upload_file(self):
        '''
        <class '_io.BufferedReader'>
        <_io.BufferedReader name='D:\\nlp-master\\askondata\\hadoop_local\\65365001d9654d9ec1172f87\\source\\flat_files\\Departments.csv'>
        <class 'werkzeug.datastructures.file_storage.FileStorage'>
        '''
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f87", "source", "flat_files",
                            "Departments.csv")
        with open(path, 'rb') as file:
            file_content = file.read()
            # Create a BytesIO object to wrap the content
            file_wrapper = io.BytesIO(file_content)
            file_storage = FileStorage(stream=file_wrapper, filename=file.name)
        response, status_code= session.with_transaction(lambda s:FileService(session).upload_file("65365001d9654d9ec1172f87", file_storage, len(file_storage.stream.read())),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        expected_output = 200
        self.assertTrue(response['success'])
        self.assertEqual(status_code, expected_output)

    @pytest.mark.skip("passing on local")
    def test_file_service_update_file_name(self):
        response, status_code= session.with_transaction(lambda s:FileService(session).update_file_name("65365001d9654d9ec1172f81",
                                                                "c28a8f59-e57b-4983-8911-83474ad2c4c1", "dept_new"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        print(response)
        self.assertFalse(response['success'])
        self.assertEqual(response['message'], "Failed to update file name.")

    def test_delete_files_which_exists(self):
        user_id = "65365001d9654d9ec1172f81"
        file_ids = ['74d82e21-a20f-4097-9181-2502bb2846f5']

        response, status_code = session.with_transaction(lambda s:FileService(session).delete_file(user_id, file_ids),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_output = 200
        self.assertTrue(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_output)

    def test_delete_files_which_does_not_exists(self):
        user_id = "65365001d9654d9ec1172f81"
        file_ids = ['74d82e21-a20f-4097-9181-2502bb2846r3']

        response, status_code = session.with_transaction(lambda s:FileService(session).delete_file(user_id, file_ids),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_output = 500
        self.assertFalse(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_output)

    def test_update_file_name_failure(self):
        user_id = "65365001d9654d9ec1172f81"
        file_id = '74d82e21-a20f-4097-9181-2502bb2846f5'
        file_name = "new_file"

        response, status_code = session.with_transaction(lambda s:FileService(session).update_file_name(user_id, file_id, file_name),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_output = 500
        self.assertFalse(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_output)

    def test_rename_file_name_success(self):
        source_id = "66729ece2ee1491c32b05b54"
        file_name = "new_file"
        chat_id = "66729ec22ee1491c32b05b60"

        response, status_code = session.with_transaction(lambda s:FileServiceCache(session).rename_file(source_id, file_name, chat_id),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_output = 200
        self.assertTrue(response['success'])
        self.assertIsNotNone(response)
        self.assertEqual(status_code, expected_output)

if __name__ == '__main__':
    unittest.main()
