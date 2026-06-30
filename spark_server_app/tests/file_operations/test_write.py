import unittest
import pytest
from spark_server.file_operations.write import Write
from spark_server.exceptions.exceptions import *
from pyspark.sql import SparkSession, Row
import os


class TestWrite(unittest.TestCase):
    # creating the instance of the class Write
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestWrite").config("spark.jars.packages", "com.crealytics:spark-excel_2.12:3.3.3_0.20.3").getOrCreate()
        cls.write = Write()
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        cls.df = cls.spark.createDataFrame(data, schema=schema)
        cls.base_path = os.path.abspath(os.path.join(__file__, "../../.."))
    
    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_csv_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "output", "file1.csv")
        self.write.csv(self.df, path)
        self.assertEqual(os.path.exists(path), True)

    def test_csv_with_config_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "output", "file1_with_semicolon.csv")
        config = {'mode': 'append', 'delimiter': ";"}
        self.write.csv(self.df, path, config)
        self.assertEqual(os.path.exists(path), True)

    def test_csv_with_config_without_mode_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "output", "file1_with_semicolon.csv")
        config = {'delimiter': ";"}
        self.write.csv(self.df, path, config)
        self.assertEqual(os.path.exists(path), True)

    def test_xlsx_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "output", "file2.xlsx")
        self.write.xlsx(self.df, path)
        self.assertEqual(os.path.exists(path), True)

    def test_xlsx_with_config_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "output", "file3.xlsx")
        config = {'mode': 'append', "dataAddress": "'Sheet1'!B2:D5"}
        self.write.xlsx(self.df, path, config)
        self.assertEqual(os.path.exists(path), True)

    def test_xlsx_with_config_without_mode_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "output", "file4.xlsx")
        config = {'header': False}
        self.write.xlsx(self.df, path, config)
        self.assertEqual(os.path.exists(path), True)


if __name__ == '__main__':
    unittest.main()
