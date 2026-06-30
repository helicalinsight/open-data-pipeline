import unittest
from spark_server.configurations.replace_connections import ReplaceConnections
from spark_server.exceptions.exceptions import *

class TestReplaceConnections(unittest.TestCase):
    
    def test_get_replace_connections_without_replace_connections(self):
        result = ReplaceConnections().get_replace_connections('65cb43f2007a5f38718b9d6c')
        self.assertEqual({}, result)

    def test_get_replace_connections(self):
        result = ReplaceConnections().get_replace_connections('65cb43f2007a5f38718b6111')
        self.assertIsNotNone(result)

    def test_process(self):
        connection_id_dict = {'6659a8f3aea87247ea56711c': {'type': 'database', 'details': {'host': '', 'port': 5432, 'username': '', 'password': '', 'database': '', 'type': 'postgres'}}}
        result = ReplaceConnections().process(connection_id_dict, "65cb43f2007a5f38718b6111", "6641ad931a3ba5058c56af19")
        self.assertIsNotNone(result)

    def test_process_without_replace_connections(self):
        connection_id_dict = {'6659a8f3aea87247ea56711c': {'type': 'database', 'details': {'host': '', 'port': 5432, 'username': '', 'password': '', 'database': '', 'type': 'postgres'}}}
        result = ReplaceConnections().process(connection_id_dict, "65cb43f2007a5f38718b9d6c", "6641ad931a3ba5058c56af19")
        self.assertEqual(connection_id_dict, result)
    
    def test_process_with_replace_connections_without_existing_connection(self):
        connection_id_dict = {'6659a8f3aea87247ea56711c': {'type': 'database', 'details': {'host': '', 'port': 5432, 'username': '', 'password': '', 'database': '', 'type': 'postgres'}}}
        result = ReplaceConnections().process(connection_id_dict, "65cb43f2007a5f38718b6112", "6641ad931a3ba5058c56af19")
        self.assertEqual(connection_id_dict, result)
