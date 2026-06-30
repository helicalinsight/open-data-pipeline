import unittest
from spark_server.pipeline.transformer import DropNa
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerDropNa(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestDropNa").getOrCreate()
        cls.drop_na = DropNa()

    def test_drop_na(self):
        data = [
            Row(id=None, name="John", age=None),
            Row(id=2, name="Alice", age=30),
            Row(id=None, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = None
        df_drop_na = self.drop_na.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, name="Alice", age=30)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_drop_na.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_drop_na.collect()], [row.asDict() for row in expected_df.collect()])

    def test_drop_na_with_subset(self):
        data = [
            Row(id=None, name="John", age=None),
            Row(id=2, name="Alice", age=30),
            Row(id=None, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"subset":['name', 'age']}]
        }
        df_drop_na = self.drop_na.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2 ,name="Alice", age=30),
            Row(id=None, name="Bob", age=22)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_drop_na.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_drop_na.collect()], [row.asDict() for row in expected_df.collect()])
