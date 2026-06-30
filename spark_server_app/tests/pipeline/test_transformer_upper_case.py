import unittest
from spark_server.pipeline.transformer import UpperCase
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerUpperCase(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestUpperCase").getOrCreate()
        cls.upper_case = UpperCase()

    def test_upper_case(self):
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
        df_upper_case = self.upper_case.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="JOHN", age=25),
            Row(id=2, name="ALICE", age=30),
            Row(id=3, name="BOB", age=22)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_upper_case.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_upper_case.collect()], [row.asDict() for row in expected_df.collect()])
