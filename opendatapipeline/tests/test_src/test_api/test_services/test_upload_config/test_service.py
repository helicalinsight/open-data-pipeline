import os
import io
import unittest
from werkzeug.datastructures import FileStorage

from src.api.services.upload_config.service import UploadConfigService
from ......tests.create_data import setup_files

from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestUploadConfig(unittest.TestCase):
    def test_upload_config(self):
        setup_files()
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data1.csv")
        with open(path, 'rb') as file:
            file_content = file.read()
            # Create a BytesIO object to wrap the content
            file_wrapper = io.BytesIO(file_content)
            file_storage = FileStorage(stream=file_wrapper, filename=file.name)
        actual_output, status_code = session.with_transaction(lambda s:UploadConfigService(session).upload_config(file_storage, "new_db", "65365001d9654d9ec1172f87"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_output = {'success': True,
                           'user_id': '65365001d9654d9ec1172f87',
                           'details': {'file': path}}

        self.assertEqual(status_code, 200)
        self.assertEqual(actual_output, expected_output)

    def test_upload_config_with_no_file(self):
        setup_files()
        actual_output, status_code = session.with_transaction(lambda s:UploadConfigService(session).upload_config(None, "new_db", "65365001d9654d9ec1172f87"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        
        expected_output = {'success': False, 'msg': 'Please make sure you selected the files to upload.'}
        self.assertEqual(actual_output, expected_output)


if __name__ == '__main__':
    unittest.main()
