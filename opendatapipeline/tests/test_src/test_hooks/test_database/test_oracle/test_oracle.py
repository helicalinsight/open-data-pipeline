import unittest
import json
import os

import pandas
import pytest

# from src.hooks.database.sql.postgres import Postgres
from src.exceptions.exception import *
from core.datasource.implementations.sql_alchemy import SqlAlchemy


json_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations",
                              "test_hooks", "oracle_creds.json")

with open(json_file_path, "r") as json_file:
    connection_details = json.load(json_file) #update the oracle_creds.json for testing

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestPostgres(unittest.TestCase):
    def test_connect_with_vpn(self):
        actual_result = SqlAlchemy().connect(connection_details, "oracle")
        self.assertIsNotNone(actual_result)


if __name__ == '__main__':
    unittest.main()
