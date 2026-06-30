import unittest
from spark_server.pipeline.transformer import Sort
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerSort(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerSort").getOrCreate()
        cls.sort = Sort()

    def test_sort(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age"], "ascending": True}]
        }
        df_sort = self.sort.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=3, name="Bob", age=22),
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sort.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sort.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sort_descending(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age"], "ascending": False}]
        }
        df_sort = self.sort.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, name="Alice", age=30),
            Row(id=1, name="John", age=25),
            Row(id=3, name="Bob", age=22)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sort.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sort.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sort_multiple_columns(self):
        data = [
            Row(id=1, name="John", age=10, marks=40),
            Row(id=2, name="Alice", age=11, marks=39),
            Row(id=3, name="Bob", age=12, marks=45)
        ]
        schema = ["id", "name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age"], "ascending": True},
                        {"columns": ["marks"], "ascending": True}] 
        }
        df_sort = self.sort.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, name="Alice", age=11, marks=39),
            Row(id=1, name="John", age=10, marks=40),
            Row(id=3, name="Bob", age=12, marks=45)
        ]
        expected_schema = ["id", "name", "age", "marks"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sort.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sort.collect()], [row.asDict() for row in expected_df.collect()])
    
    def test_sort_numeric_columns(self):
        data = [
            Row(number=1, decimal=45.67, fraction=1/4, scientific=1.23E+04, special=12345, negative_int=-30, negative_decimal=-50.6, phone_number=7012642205),
            Row(number=2, decimal=67.94, fraction=1/3, scientific=4.56E+05, special=34567, negative_int=-20, negative_decimal=-35.3, phone_number=8008543211),
            Row(number=3, decimal=98.05, fraction=1/2, scientific=7.89E+06, special=56789, negative_int=-10, negative_decimal=-11.1, phone_number=9934565324)
        ]
        schema = ["number", "decimal", "fraction", "scientific", "special", "negative_int", "negative_decimal", "phone_number"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["number", "decimal", "fraction", "scientific", "special", "negative_int", "negative_decimal", "phone_number"], "ascending": True}]
        }
        df_sort = self.sort.execute(df, parameters, self.spark)
        expected_data = data
        expected_schema = schema
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sort.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sort.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sort_numeric_columns_descending(self):
        data = [
            Row(number=3, decimal=98.05, fraction=1/2, scientific=7.89E+06, special=56789, negative_int=-10, negative_decimal=-11.1, phone_number=9934565324),
            Row(number=2, decimal=67.94, fraction=1/3, scientific=4.56E+05, special=34567, negative_int=-20, negative_decimal=-35.3, phone_number=8008543211),
            Row(number=1, decimal=45.67, fraction=1/4, scientific=1.23E+04, special=12345, negative_int=-30, negative_decimal=-50.6, phone_number=7012642205)
        ]
        schema = ["number", "decimal", "fraction", "scientific", "special", "negative_int", "negative_decimal", "phone_number"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["number", "decimal", "fraction", "scientific", "special", "negative_int", "negative_decimal", "phone_number"], "ascending": False}]
        }
        df_sort = self.sort.execute(df, parameters, self.spark)
        expected_data = data
        expected_schema = schema
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sort.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sort.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sort_string_columns(self):
        data = [
            Row(short_text="Alex", long_text="A story began long long ago......", number="01234", date="1999-01-01", boolean="False", percentage="50%"),
            Row(short_text="Zen", long_text="This is a story of......", number="987654321", date="2024-01-01", boolean="True", percentage="90%"),
        ]
        schema = ["short_text", "long_text", "number", "date", "boolean", "percentage"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["short_text", "long_text", "number", "date", "boolean", "percentage"], "ascending": True}]
        }
        df_sort = self.sort.execute(df, parameters, self.spark)
        expected_data = data
        expected_schema = schema
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sort.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sort.collect()], [row.asDict() for row in expected_df.collect()])
    
    def test_sort_string_columns_descending(self):
        data = [
            Row(short_text="Zen", long_text="This is a story of......", number="987654321", date="2024-01-01", boolean="True", percentage="90%"),
            Row(short_text="Alex", long_text="A story began long long ago......", number="01234", date="1999-01-01", boolean="False", percentage="50%")
        ]
        schema = ["short_text", "long_text", "number", "date", "boolean", "percentage"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["short_text", "long_text", "number", "date", "boolean", "percentage"], "ascending": False}]
        }
        df_sort = self.sort.execute(df, parameters, self.spark)
        expected_data = data
        expected_schema = schema
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sort.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sort.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sort_boolean(self):
        data = [
            Row(boolean=True),
            Row(boolean=False)
        ]
        schema = ["boolean"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["boolean"], "ascending": True}]
        }
        df_sort = self.sort.execute(df, parameters, self.spark)
        expected_data = [
            Row(boolean=False),
            Row(boolean=True)
        ]
        expected_schema = schema
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sort.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sort.collect()], [row.asDict() for row in expected_df.collect()])