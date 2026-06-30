import unittest

from src.api.services.data_sources.service import DatasourcesService
from ......src.models.connector import MongoConnector
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestDataSourcesService(unittest.TestCase):
    def test_data_service(self):
        response, status_code = session.with_transaction(lambda s:DatasourcesService(session).get_datasources(),read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual(response['success'], True)
        self.assertEqual(status_code, 200)


if __name__ == '__main__':
    unittest.main()
