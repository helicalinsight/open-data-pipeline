import unittest
from spark_server.pipeline.transformer import Deduplicate
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerDeduplicate(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerDeduplicate").getOrCreate()
        cls.dedup = Deduplicate()

    def test_deduplicate(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22),
            Row(id=4, name="Bob", age=26)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["name"]}]
        }
        df_deduplicate = self.dedup.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_deduplicate.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_deduplicate.collect()], [row.asDict() for row in expected_df.collect()])

    def test_deduplicate_with_multiple_columns(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22),
            Row(id=4, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["name", "age"]}]
        }
        df_deduplicate = self.dedup.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_deduplicate.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_deduplicate.collect()], [row.asDict() for row in expected_df.collect()])
