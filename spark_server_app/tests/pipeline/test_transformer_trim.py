import unittest
from spark_server.pipeline.transformer import Trim
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerTrim(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTrim").getOrCreate()
        cls.trim = Trim()

    def test_trim(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["name"], "location": "left", "number_of_characters": 1}]
        }
        df_trim = self.trim.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="ohn", age=25),
            Row(id=2, name="lice", age=30),
            Row(id=3, name="ob", age=22)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_trim.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_trim.collect()], [row.asDict() for row in expected_df.collect()])
