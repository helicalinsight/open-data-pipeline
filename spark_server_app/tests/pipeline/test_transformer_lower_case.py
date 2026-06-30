import unittest
from spark_server.pipeline.transformer import LowerCase
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerLowerCase(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestLowerCase").getOrCreate()
        cls.lower_case = LowerCase()

    def test_lower_case(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["name"]}]
        }
        df_lower_case = self.lower_case.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="john", age=25),
            Row(id=2, name="alice", age=30),
            Row(id=3, name="bob", age=22)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_lower_case.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_lower_case.collect()], [row.asDict() for row in expected_df.collect()])
