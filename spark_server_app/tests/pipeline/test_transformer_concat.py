import unittest
from spark_server.pipeline.transformer import Concat
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerConcat(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerConcat").getOrCreate()
        cls.concat = Concat()
    
    def test_concat(self):
        data = [
            Row(name="John", age=25, marks=40),
            Row(name="Alice", age=30, marks=39),
            Row(name="Bob", age=22, marks=19)
        ]
        schema = ["name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age", "marks"], "separator": "/", "destination_column": "code"}]
        }
        df = self.concat.execute(df, parameters, self.spark)
        expected_data = [
            Row(name="John", age=25, marks=40, code="25/40"),
            Row(name="Alice", age=30, marks=39, code="30/39"),
            Row(name="Bob", age=22, marks=19, code="22/19")
        ]
        expected_schema = ["name", "age", "marks", "code"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df.collect()], [row.asDict() for row in expected_df.collect()])

    def test_concat_without_destination_column(self):
        data = [
            Row(name="John", age=25, marks=40),
            Row(name="Alice", age=30, marks=39),
            Row(name="Bob", age=22, marks=19)
        ]
        schema = ["name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age", "marks"], "separator": "/", "destination_column":"age_marks_concat"}]
        }
        df = self.concat.execute(df, parameters, self.spark)
        expected_data = [
            Row(name="John", age=25, marks=40, age_marks_concat="25/40"),
            Row(name="Alice", age=30, marks=39, age_marks_concat="30/39"),
            Row(name="Bob", age=22, marks=19, age_marks_concat="22/19")
        ]
        expected_schema = ["name", "age", "marks", "age_marks_concat"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df.collect()], [row.asDict() for row in expected_df.collect()])

    def test_concat_without_separator(self):
        data = [
            Row(name="John", age=25, marks=40),
            Row(name="Alice", age=30, marks=39),
            Row(name="Bob", age=22, marks=19)
        ]
        schema = ["name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age", "marks"], "destination_column": "code", "separator":" "}]
        }
        df = self.concat.execute(df, parameters, self.spark)
        expected_data = [
            Row(name="John", age=25, marks=40, code="25 40"),
            Row(name="Alice", age=30, marks=39, code="30 39"),
            Row(name="Bob", age=22, marks=19, code="22 19")
        ]
        expected_schema = ["name", "age", "marks", "code"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df.collect()], [row.asDict() for row in expected_df.collect()])

    def test_concat_with_existing_destination_column(self):
        data = [
            Row(name="John", age=25, marks=40),
            Row(name="Alice", age=30, marks=39),
            Row(name="Bob", age=22, marks=19)
        ]
        schema = ["name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age", "marks"], "separator": "/", "destination_column": "marks_1"}]
        }
        df = self.concat.execute(df, parameters, self.spark)
        expected_data = [
            Row(name="John", age=25, marks=40, marks_1="25/40"),
            Row(name="Alice", age=30, marks=39, marks_1="30/39"),
            Row(name="Bob", age=22, marks=19, marks_1="22/19")
        ]
        expected_schema = ["name", "age", "marks", "marks_1"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df.collect()], [row.asDict() for row in expected_df.collect()])
