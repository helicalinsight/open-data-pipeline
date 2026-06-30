
import unittest

from src.models.connector import MongoConnector

class TestConnector(unittest.TestCase):

    def test_connect(self):
        mongo_connector = MongoConnector()
        actual_result = mongo_connector.client
        print('mongo_client', actual_result)
        self.assertIsNotNone(actual_result)
        collection = actual_result["chats"]
        cursor = collection.find({}).limit(1)
        self.assertIsNotNone(cursor)

if __name__ == '__main__':
    unittest.main()