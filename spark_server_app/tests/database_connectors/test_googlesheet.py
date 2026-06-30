import unittest
from unittest.mock import MagicMock
from spark_server.database_connectors.googlesheet import GoogleSheet
from spark_server.exceptions.exceptions import *
from pyspark.sql import SparkSession
import os
import pytest
from test_setup import TestSetup
import string
import random
 

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestGoogleSheet(unittest.TestCase):
    # creating the instance of the class GoogleSheet
    @classmethod
    def setUpClass(cls):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        cls.spark = TestSetup.set_up_spark()
        cls.googlesheet = GoogleSheet(cls.spark)
        
        # Load credentials dynamically to support git-ignored local credentials
        default_dir = os.path.join(base_path, "spark_server", "database_connectors", "connector_jars", "googlesheet")
        local_path = os.path.join(default_dir, "gsforaod-local.json")
        default_path = os.path.join(default_dir, "gsforaod-0f69e7a1a1a9.json")
        
        path = os.getenv("AOD_GOOGLE_SHEETS_CREDS_PATH")
        if not path:
            if os.path.exists(local_path):
                path = local_path
            else:
                path = default_path
        path = os.path.abspath(path).replace('\\','/')
        
        cls.connection_id = {
            "654879fe42a09b96f228301c": {
                "type": "database",
                "details": {
                    "type": "googlesheet",
                    "sourceName": "GoogleSheet Connector",
                    "credentials_object": {"file":path},
                    'sheet_id': '1-4agOzX1ZAIG4bgI-B02KZa9q1OK-uqhR9wg2Rf_ab0',
                    'database': None
                }
            }
        }
            

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_connect(self):
        config = self.googlesheet.connect(self.connection_id["654879fe42a09b96f228301c"])
        self.assertIsNotNone(config)

    def test_test_connection(self):
        connection = self.googlesheet.connect(self.connection_id["654879fe42a09b96f228301c"])
        config={'connection_id': '654879fe42a09b96f228301c',
                "df_id": "65dc3fb832b5b2a5665841fb"}
        test_result = self.googlesheet.test_connection(config, connection)
        self.assertEqual(test_result, True)

    def test_fetch_data(self):
        connection = self.googlesheet.connect(self.connection_id["654879fe42a09b96f228301c"])
        config = {'table_name': 'Sheet1', "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.googlesheet.fetch_data(config, connection)
        self.assertTrue("65dc3fb832b5b2a5665841fb" in result.keys())
    
    def test_fetch_data_with_columns(self):
        connection = self.googlesheet.connect(self.connection_id["654879fe42a09b96f228301c"])                                               
        config = {'table_name': 'Sheet1', "columns": ["id", "name"], "df_id": "65dc3fb832b5b2a5665841fb"}
        with pytest.raises(Exception):
            self.googlesheet.fetch_data(config, connection)
        # self.assertTrue("65dc3fb832b5b2a5665841fb" in result.keys())

    def test_fetch_data_with_custom_config_dbtable(self):
        connection = self.googlesheet.connect(self.connection_id["654879fe42a09b96f228301c"])
        config = {'table_name': 'Sheet1', "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config={'table_name':'Sheet2'}
        result = self.googlesheet.fetch_data(config, connection, custom_config)
        self.assertTrue("65dc3fb832b5b2a5665841fb" in result.keys())

    def test_fetch_data_from_empty_sheet(self):
        connection = self.googlesheet.connect(self.connection_id["654879fe42a09b96f228301c"])
        config = {'table_name': 'Sheet3', "df_id": "65dc3fb832b5b2a5665841fb"}
        with pytest.raises(DatabaseConnectionException) as test_function:
            self.googlesheet.fetch_data(config, connection)
        self.assertEqual("Failed to fetch data from Google sheet." , str(test_function.value))

    def test_write_data_without_custom_config(self):
        """
        Test writing data to googlesheet database table
        """
        connection = self.googlesheet.connect(self.connection_id["654879fe42a09b96f228301c"])
        config = {'table_name': 'Sheet4', "df_id": "65dc3fb832b5b2a5665841fb"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values)]
        schema = ["id", "name"]
        dataframe = self.spark.createDataFrame(data, schema)
        result = self.googlesheet.write_data(config, connection, dataframe)
        self.assertTrue(result)
        result = self.googlesheet.fetch_data(config, connection)
        self.assertTrue("65dc3fb832b5b2a5665841fb" in result.keys())

    def test_write_data_with_custom_config(self):
        """
        Test writing data to googlesheet database table
        """
        connection = self.googlesheet.connect(self.connection_id["654879fe42a09b96f228301c"])
        config = {'table_name': 'Sheet4', "df_id": "65dc3fb832b5b2a5665841fb"}
        random_values = ''.join(random.choices(string.ascii_letters, k=5))
        data = [(random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values), 
                (random.randint(1, 10), random_values)]
        schema = ["employee_id", "name"]
        custom_config={"mode": "append"}
        dataframe = self.spark.createDataFrame(data, schema)
        result = self.googlesheet.write_data(config, connection, dataframe, custom_config)
        self.assertTrue(result)
        result = self.googlesheet.fetch_data(config, connection, custom_config)
        self.assertTrue("65dc3fb832b5b2a5665841fb" in result.keys())


if __name__ == '__main__':
    unittest.main()
