import unittest
from unittest.mock import patch, MagicMock
from src.api.services.langchain_service.odpgraph.odpchain.query_generator import QueryGenerator
from src.models.connector import MongoConnector
from src.models.mongo.mongo_factory import MongoFactory
from pymongo.write_concern import WriteConcern

wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

mongo = MongoConnector()

mongo_client = mongo.client

cache_collection = MongoFactory(mongo_client, "cache", session=session)

class TestQueryGenerator(unittest.TestCase):

    def test_map_datatype(self):
        self.assertEqual(QueryGenerator(session).map_datatype('int64'), 'INTEGER')
        self.assertEqual(QueryGenerator(session).map_datatype('object'), 'VARCHAR')
        self.assertEqual(QueryGenerator(session).map_datatype('float64'), 'FLOAT')
        self.assertEqual(QueryGenerator(session).map_datatype('bool'), 'boolean')
        self.assertEqual(QueryGenerator(session).map_datatype('date'), 'DATE')
        self.assertEqual(QueryGenerator(session).map_datatype('datetime64[ns]'), 'DATE')
        self.assertEqual(QueryGenerator(session).map_datatype('unknown'), 'others')

    def test_generate_create_table_statement(self):
        datatypes = {
            "id": "int64",
            "name": "object",
            "age": "int64",
            "salary": "float64"
        }
        expected_query = ' Schema: (\n    id INTEGER,\n    name VARCHAR,\n    age INTEGER,\n    salary FLOAT\n)'
        result = QueryGenerator(session).generate_create_table_statement("df", datatypes)
        self.assertEqual(result, expected_query)

    def test_extract_column_datatypes_from_mongodb(self):
        file_name, datatypes = QueryGenerator(session).extract_column_datatypes_from_mongodb("66729ece2ee1491c32b05b54", "66729ec22ee1491c32b05b60")
        expected_dtypes = {'index': 'int64', 'customer_id': 'object', 'first': 'object', 'last_name': 'object', 'company': 'object', 'city': 'object', 'country': 'object', 'phone_1': 'object', 'phone_2': 'object', 'email': 'object', 'subscription_date': 'object', 'website': 'object'}
        self.assertEqual(file_name, 'customers-100')
        self.assertEqual(datatypes, expected_dtypes)

    def test_generate_expected_output(self):
        
        result = QueryGenerator(session).generate_expected_output("", "66729ec22ee1491c32b05b60")
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()