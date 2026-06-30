import unittest
from spark_server.pipeline.extractor import *
from pyspark.sql import SparkSession


class TestExtractor(unittest.TestCase):
    # creating the instance of the class Extractor

    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestExtractor").config("spark.jars.packages", "org.postgresql:postgresql:42.7.1").getOrCreate()
        cls.read_file = ReadFiles()
        cls.read_table = ReadTables()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
        
    def test_read_files(self):
        absolute_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(absolute_path, "test_files", "file1.csv")
        file_path2 = os.path.join(absolute_path, "test_files", "file2.csv")
        parameters = {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'Students'}
        output = {'df_id': '6651805f1577224b6b08aa6d'}
        connection_id = {
            'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1': {
                'type': 'file',
                'details': {
                    'file_name': 'Students.csv',
                    'file_type': 'csv',
                    'file_path': file_path1
                }
            },
            'fd85ee69-46f5-438b-a1b0-1b4f9581f6f2': {
                'type': 'file',
                'details': {
                    'file_name': 'Students_1.csv',
                    'file_type': 'csv',
                    'file_path': file_path2
                }
            }
        }

        dfs = self.read_file.execute(parameters, connection_id, output, self.spark)
        self.assertEqual(4, dfs["6651805f1577224b6b08aa6d"]["df"].count())

    def test_read_files_with_columns(self):
        absolute_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(absolute_path, "test_files", "file1.csv")
        file_path2 = os.path.join(absolute_path, "test_files", "file2.csv")
        parameters = {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'Students'}
        output = {'df_id': '6651805f1577224b6b08aa6d'}
        connection_id = {
            'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1': {
                'type': 'file',
                'details': {
                    'file_name': 'Students.csv',
                    'file_type': 'csv',
                    'file_path': file_path1,
                    'columns': ["id", "name"]
                }
            },
            'fd85ee69-46f5-438b-a1b0-1b4f9581f6f2': {
                'type': 'file',
                'details': {
                    'file_name': 'Students_1.csv',
                    'file_type': 'csv',
                    'file_path': file_path2
                }
            }
        }
        dfs = self.read_file.execute(parameters, connection_id, output, self.spark)
        self.assertEqual(4, dfs["6651805f1577224b6b08aa6d"]["df"].count())
        self.assertEqual(dfs["6651805f1577224b6b08aa6d"]["df"].columns, ["id", "name"])

    def test_read_tables(self):
        parameters = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor"}
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
        dataframes = self.read_table.execute(parameters, connection_id, output, self.spark)
        self.assertEqual(200, dataframes["65dc3fb832b5b2a5665841fb"]["df"].count())

    def test_read_tables_with_columns(self):
        parameters = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor",
                    "columns": ["actor_id"]}
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
        dataframes = self.read_table.execute(parameters, connection_id, output, self.spark)
        self.assertEqual(200, dataframes["65dc3fb832b5b2a5665841fb"]["df"].count())
        self.assertEqual(dataframes["65dc3fb832b5b2a5665841fb"]["df"].columns, ["actor_id"])


if __name__ == '__main__':
    unittest.main()
