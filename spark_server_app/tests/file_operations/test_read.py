import unittest
import pytest
from spark_server.file_operations.read import Read
from spark_server.exceptions.exceptions import *
import os
from pyspark.sql import SparkSession


class TestRead(unittest.TestCase):

    # creating the instance of the class Read
    
    @classmethod
    def setUpClass(cls):
        cls.read = Read()
        cls.base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        cls.spark = SparkSession.builder.appName("TestRead1").config("spark.jars.packages", "com.crealytics:spark-excel_2.12:3.3.3_0.20.3").getOrCreate()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_csv_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "flat_files", "file1.csv")
        result = self.read.csv(self.spark, path)
        self.assertEqual(result.count(), 3)

    def test_csv_with_columns_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "flat_files", "file1.csv")
        result = self.read.csv(self.spark, path, columns=["name"])
        self.assertEqual(result.columns, ["name"])

    def test_csv_with_config_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "flat_files", "file1_with_semicolon.csv")
        config = {'delimiter': ";"}
        result = self.read.csv(self.spark, path, config=config)
        self.assertEqual(result.count(), 3)

    def test_csv_with_config_columns_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "flat_files", "file1_with_semicolon.csv")
        config = {'delimiter': ";"}
        result = self.read.csv(self.spark, path, columns=["name"], config=config)
        self.assertEqual(result.count(), 3)
        self.assertEqual(result.columns, ["name"])

    def test_xlsx_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "flat_files", "file1.xlsx")
        result = self.read.xlsx(self.spark, path)
        self.assertEqual(result.count(), 3)
    
    def test_xlsx_with_columns_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "flat_files", "file1.xlsx")
        result = self.read.xlsx(self.spark, path, columns=["nme"])
        self.assertEqual(result.columns, ["nme"])

    def test_xlsx_with_config_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "flat_files", "file1.xlsx")
        config = {"dataAddress": "'Sheet1'!A1:B2"}
        result = self.read.xlsx(self.spark, path, config=config)
        self.assertEqual(result.count(), 1)

    def test_xlsx_with_config_columns_in_local(self):
        path = os.path.join(self.base_path, "hadoop_local", "flat_files", "file1.xlsx")
        config = {"dataAddress": "'Sheet1'!A1:B2"}
        result = self.read.xlsx(self.spark, path, columns=["nme"], config=config)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.columns, ["nme"])


if __name__ == '__main__':
    unittest.main()
