import unittest
from spark_server.pipeline.transformer import FillNa
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerFillNa(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestFillNa").getOrCreate()
        cls.fill_na = FillNa()

    def test_fill_na_with_value(self):
        data = [
            Row(id=None, name="John", age=None),
            Row(id=2, name="Alice", age=30),
            Row(id=None, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"value": 0}]
        }
        df_fill_na = self.fill_na.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=0, name="John", age=0),
            Row(id=2, name="Alice", age=30),
            Row(id=0, name="Bob", age=22)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_fill_na.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_fill_na.collect()], [row.asDict() for row in expected_df.collect()])

    def test_fill_na_with_dictionary(self):
        data = [
            Row(A=1, B=None),
            Row(A=2, B=5),
            Row(A=None, B=6)
        ]
        schema = ["A", "B"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"value": {'A': 0, 'B': 10}}]
        }
        df_fill_na = self.fill_na.execute(df, parameters, self.spark)
        expected_data = [
            Row(A=1, B=10),
            Row(A=2, B=5),
            Row(A=0, B=6)
        ]
        expected_schema = ["A", "B"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_fill_na.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_fill_na.collect()], [row.asDict() for row in expected_df.collect()])

    def test_fill_na_with_value_axis(self):
        data = [
            Row(name="John", age=25, city="New York"),
            Row(name="Jane", age=30, city=None),
            Row(name="Jade", age=35, city="Paris"),
            Row(name="Jan", age=40, city=None)
        ]
        schema = ["name", "age", "city"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"value": "Unknown", "axis": "columns"}]
        }
        df_fill_na = self.fill_na.execute(df, parameters, self.spark)
        expected_data = [
            Row(name="John", age=25, city="New York"),
            Row(name="Jane", age=30, city="Unknown"),
            Row(name="Jade", age=35, city="Paris"),
            Row(name="Jan", age=40, city="Unknown")
        ]
        expected_schema = ["name", "age", "city"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_fill_na.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_fill_na.collect()], [row.asDict() for row in expected_df.collect()])

    def test_fill_na_with_value_column(self):
        data = [
            Row(name="John", age=25, city=None),
            Row(name="Jane", age=30, city="London"),
            Row(name="Jade", age=35, city="Paris"),
            Row(name="Jan", age=40, city=None)
        ]
        schema = ["name", "age", "city"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"column": "city", "value": "No City"}]
        }
        df_fill_na = self.fill_na.execute(df, parameters, self.spark)
        expected_data = [
            Row(name="John", age=25, city="No City"),
            Row(name="Jane", age=30, city="London"),
            Row(name="Jade", age=35, city="Paris"),
            Row(name="Jan", age=40, city="No City")
        ]
        expected_schema = ["name", "age", "city"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_fill_na.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_fill_na.collect()], [row.asDict() for row in expected_df.collect()])
"""
    def test_fill_na_with_ffill(self):
        data = [
            Row(A=1, B=None),
            Row(A=None, B=5),
            Row(A=3, B=None),
            Row(A=None, B=7)
        ]
        schema = ["A", "B"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"method": "ffill"}]
        }
        df_fill_na = self.fill_na.execute(df, parameters, self.spark)
        expected_data = [
            Row(A=1, B=None),
            Row(A=1, B=5),
            Row(A=3, B=5),
            Row(A=3, B=7)
        ]
        expected_schema = ["A", "B"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_fill_na.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_fill_na.collect()], [row.asDict() for row in expected_df.collect()])

    def test_fill_na_with_bfill(self):
        data = [
            Row(A=1, B=None),
            Row(A=None, B=5),
            Row(A=3, B=None),
            Row(A=None, B=7)
        ]
        schema = ["A", "B"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"method": "bfill"}]
        }
        df_fill_na = self.fill_na.execute(df, parameters, self.spark)
        expected_data = [
            Row(A=1, B=5),
            Row(A=3, B=5),
            Row(A=3, B=7),
            Row(A=None, B=7)
        ]
        expected_schema = ["A", "B"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_fill_na.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_fill_na.collect()], [row.asDict() for row in expected_df.collect()])
"""