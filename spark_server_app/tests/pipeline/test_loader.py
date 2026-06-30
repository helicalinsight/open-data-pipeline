import unittest
import pytest
from unittest.mock import MagicMock
from spark_server.pipeline.loader import *
from spark_server.pipeline.extractor import ReadTables
from pyspark.sql import SparkSession
from spark_server.configurations.baseConfig.config import localDirectory


class TestLoader(unittest.TestCase):
    # creating the instance of the class Loader
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestLoader").config("spark.jars.packages", "org.postgresql:postgresql:42.7.1").getOrCreate()
        cls.load_file = Export()
        cls.load_table = ExportTables()
        cls.read_table = ReadTables()
        data = [("John", 25), ("Alice", 30), ("Bob", 35)]
        schema = ["Name", "Age"]
        cls.df = cls.spark.createDataFrame(data, schema)
        cls.dataframes = {"65dc3fb832b5b2a5665841fb": {"df": cls.df, "alias": "student"}}

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_export(self):
        #parameters = {"export_name": "output", "df_id": "65dc3fb832b5b2a5665841fb"}
        parameters = {"export_name": "output",  "df_id": "65dc3fb832b5b2a5665841fb", "user_id": "6641ad931a3ba5058c56af19", "chat_id": "665e937aaea87247ea567131"}
        connection_id = {}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        self.load_file.execute(self.dataframes, parameters, connection_id, self.spark, schedule_conf)
        base_path=localDirectory._path
        #'D:\\home\\ubuntu\\development\\opendatapipeline_application\\opendatapipeline\\hadoop_local\\65dc3fb832b5b2a5665841fb\\output\\123\\456'
        #expected_path = f"{base_path}/spark_server/SCHEDULED_OUTPUT/output"
        if os.getenv("APP_ENVIRONMENT") == "test":
            base_path = os.path.abspath(base_path)
            expected_path = os.path.join(base_path, "6641ad931a3ba5058c56af19", "output", "123", "456")
        else:
            expected_path = os.path.join(base_path, "6641ad931a3ba5058c56af19", "output", "123", "456")
        self.assertTrue(any(filename.startswith("part-") and filename.endswith(".csv") for filename in
                            os.listdir(expected_path)))

    #@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires vpn")
    def test_export_tables(self):
        parameters = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.test", "df_id": "65dc3fb832b5b2a5665841fb"}
        output = {"df_id": "65dc3fb832b5b2a5665841fb"}
        connection_id = {
            "654879fe42a09b96f228302c": {
                "type": "database",
                "details": {
                    "type": "postgres",
                    "sourceName": "Postgres Connector 2",
                    "host": "57.128.161.235",
                    "port": "5432",
                    "username": "airflow",
                    "password": "Helical@1234",
                    "database": "sakila"
                }
            }
        }
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        self.load_table.execute(self.dataframes, parameters, connection_id, self.spark, schedule_conf)
        dataframes = self.read_table.execute(parameters, connection_id, output, self.spark)
        self.assertEqual(3, dataframes["65dc3fb832b5b2a5665841fb"]["df"].count())


if __name__ == '__main__':
    unittest.main()
