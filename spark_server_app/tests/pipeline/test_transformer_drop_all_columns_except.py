import unittest
from spark_server.pipeline.transformer import DropAllColumnsExcept
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerDropAllColumnsExcept(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerDropAllColumnsExcept").getOrCreate()
        cls.drop_all_cols_except = DropAllColumnsExcept()
    
    def test_drop_all_columns_except(self):
        data = [
            Row(name="John", age=25, marks=40),
            Row(name="Alice", age=30, marks=39),
            Row(name="Bob", age=22, marks=19)
        ]
        schema = ["name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age", "marks"]}]
        }
        df = self.drop_all_cols_except.execute(df, parameters, self.spark)
        expected_data = [
            Row(age=25, marks=40),
            Row(age=30, marks=39),
            Row(age=22, marks=19)
        ]
        expected_schema = ["age", "marks"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df.collect()], [row.asDict() for row in expected_df.collect()])

    def test_drop_all_columns_except_with_non_existing_column(self):
        data = [
            Row(name="John", age=25, marks=40),
            Row(name="Alice", age=30, marks=39),
            Row(name="Bob", age=22, marks=19)
        ]
        schema = ["name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age1", "marks1"]}]
        }
        df = self.drop_all_cols_except.execute(df, parameters, self.spark)
        expected_data = [{}, {}, {}]
        expected_schema = []
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df.collect()], [row.asDict() for row in expected_df.collect()])
