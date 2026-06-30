import unittest
from spark_server.pipeline.transformer import Filter
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import when, col
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerFilter(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestFilter").getOrCreate()
        cls.filter = Filter()

    def test_filter_equals_with_string_as_list(self):
        data = [
            Row(id=1, grade=10, name='Alice'),
            Row(id=2, grade=11, name='Bob'),
            Row(id=3, grade=9, name='Charlie')
                ]
        schema = ["id", "grade", "name"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["name"], "expr":"equals", "value":["Bob"]}]
        }
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=2, grade=11, name='Bob')
            ]
        expected_schema = ["id", "grade", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_equals_with_string(self):
        data = [
            Row(id=1, grade=10, name='Alice'),
            Row(id=2, grade=11, name='Bob'),
            Row(id=3, grade=9, name='Charlie')
                ]
        schema = ["id", "grade", "name"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["name"], "expr":"equals", "value":"Bob"}]
        }
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=2, grade=11, name='Bob')
            ]
        expected_schema = ["id", "grade", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_equals_with_list_of_string(self):
        data = [
            Row(id=1, grade=10, name='Alice'),
            Row(id=2, grade=11, name='Bob'),
            Row(id=3, grade=9, name='Charlie')
                ]
        schema = ["id", "grade", "name"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =  {"groups": [{"columns": ["name"], "expr": "equals", "value": ["Bob", "Alice"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=1, grade=10, name='Alice'),
                Row(id=2, grade=11, name='Bob')
            ]
        expected_schema = ["id", "grade", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_equals_with_list_of_integer(self):
        data = [
            Row(id=1, grade=1, name='Alice'),
            Row(id=2, grade=11, name='Bob'),
            Row(id=3, grade=9, name='David')
                ]
        schema = ["id", "grade", "name"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =  {"groups": [{"columns": ["id", "grade"], "expr": "equals", "value": [1,2]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
               Row(id=1, grade=1, name='Alice')
            ]
        expected_schema = ["id", "grade", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_equals_with_number_as_list(self):
        data = [
            Row(id=1, grade=10, name='Alice'),
            Row(id=2, grade=11, name='Bob'),
            Row(id=3, grade=10, name='David')
                ]
        schema = ["id", "grade", "name"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =  {"groups": [{"columns": ["grade"], "expr":"equals", "value":[10]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=10, name='Alice'),
            Row(id=3, grade=10, name='David')
            ]
        expected_schema = ["id", "grade", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_equals_with_number_as_integer(self):
        data = [
            Row(id=1, grade=10, name='Alice'),
            Row(id=2, grade=11, name='Bob'),
            Row(id=3, grade=10, name='David')
                ]
        schema = ["id", "grade", "name"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =  {"groups": [{"columns": ["grade"], "expr":"equals", "value":10}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=10, name='Alice'),
            Row(id=3, grade=10, name='David')
            ]
        expected_schema = ["id", "grade", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_equals_with_date(self):
        data = [
            Row(id=1, grade=10, name='Alice', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =  {"groups": [{"columns": ["date"], "expr":"equals", "value":["2024-03-08"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_not_equals_with_string(self):
        data = [
            Row(id=1, grade=10, name='Alice', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =   {"groups": [{"columns": ["name"], "expr":"not_equals", "value":["Alice"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_not_equals_with_number(self):
        data = [
            Row(id=1, grade=10, name='Alice', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =   {"groups": [{"columns": ["grade"], "expr":"not_equals", "value":[10]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, grade=11, name='Bob', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_not_equals_with_date(self):
        data = [
            Row(id=1, grade=10, name='Alice', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =   {"groups": [{"columns": ["date"], "expr":"not_equals", "value":['2024-03-08']}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=10, name='Alice', date='8/3/2024')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_contains_with_string(self):
        data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =  {"groups": [{"columns": ["name"], "expr":"contains", "value":["smith"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_does_not_contains_with_string(self):
        data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["name"], "expr":"not_contains", "value":["smith"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_startswith_string(self):
        data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["name"], "expr":"startswith", "value":["Alice"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_endswith_string(self):
        data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob_smith', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["name"], "expr":"endswith", "value":["smith"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob_smith', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_not_startswith_string(self):
        data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["name"], "expr":"not_startswith", "value":["Alice"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_not_endswith_string(self):
        data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob_smith', date='2024-03-08'),
            Row(id=3, grade=10, name='David', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["name"], "expr":"not_endswith", "value":["smith"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=3, grade=10, name='David', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_null(self):
        data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob_smith', date='2024-03-08'),
            Row(id=3, grade=10, name=None, date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["name"], "expr": "is_null", "value": [None]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=3, grade=10, name='null', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        df_filter = df_filter.withColumn("name", when(col("name").isNull(), "null").otherwise(col("name")))
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_not_null(self):
        data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob_smith', date='2024-03-08'),
            Row(id=3, grade=10, name=None, date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["name"], "expr": "is_not_null", "value": [None]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=10, name='Alice_smith', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob_smith', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_one_of_the_string(self):
        data = [
            Row(id=1, grade=10, name='Alice', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='doe', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["name"], "expr":"is_one_of_the", "value":['Bob', 'doe']}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='doe', date='2024-03-08')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_not_one_of_the_string(self):
        data = [
            Row(id=1, grade=10, name='Alice', date='8/3/2024'),
            Row(id=2, grade=11, name='Bob', date='2024-03-08'),
            Row(id=3, grade=10, name='doe', date='2024-03-08')
                ]
        schema = ["id", "grade", "name", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["name"], "expr":"is_not_one_of_the", "value":['Bob', 'doe']}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=10, name='Alice', date='8/3/2024')
            ]
        expected_schema = ["id", "grade", "name", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_in_range_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["date"], "expr":"in_range", "value":['2022-02-01', '2022-04-01']}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_in_range_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr":"in_range", "value":[20,40]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_not_in_range_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["date"], "expr":"not_in_range", "value":['2022-02-01', '2022-04-01']}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_not_in_range_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr":"not_in_range", "value":[20,40]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-01-01', value=10)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_in_between_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["date"], "expr":"in_between", "value":['2022-02-01', '2022-04-01']}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_in_between_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr":"in_between", "value":[20,40]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_not_in_between_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["date"], "expr":"not_in_between", "value":['2022-02-01', '2022-04-01']}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_not_in_between_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr":"not_in_between", "value":[20,40]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-01-01', value=10)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_one_of_the_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_one_of_the", "value":['2022-01-01', '2022-02-15', '2022-08-15']}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
           Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_not_one_of_the_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters ={"groups": [{"columns": ["date"], "expr":"is_not_one_of_the", "value":['2022-01-01', '2022-02-15', '2022-08-15']}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_one_of_the_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_one_of_the", "value":[10, 20]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
           Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_not_one_of_the_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters ={"groups": [{"columns": ["value"], "expr":"is_not_one_of_the", "value":[10, 20]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_null_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date=None, value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =  {"groups": [{"columns": ["date"], "expr": "is_null", "value": [None]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
           Row(date='null', value=20),
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        df_filter = df_filter.withColumn("date", when(col("date").isNull(), "null").otherwise(col("date")))
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_not_null_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date=None, value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters ={"groups": [{"columns": ["date"], "expr": "is_not_null", "value": [None]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_null_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=None),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters =  {"groups": [{"columns": ["value"], "expr": "is_null", "value": [None]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
           Row(date='2022-02-15', value='null')
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        df_filter = df_filter.withColumn("value", when(col("value").isNull(), "null").otherwise(col("value")))
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_not_null_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=None)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters ={"groups": [{"columns": ["value"], "expr": "is_not_null", "value": [None]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_greater_than_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_greater_than", "value":["2022-02-15"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_greater_than_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_greater_than", "value":[20]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_greater_than_or_equal_to_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_greater_than_or_equal_to", "value":["2022-02-15"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_greater_than_or_equal_to_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_greater_than_or_equal_to", "value":[20]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_lesser_than_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_lesser_than", "value":["2022-02-15"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-01-01', value=10)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_lesser_than_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters ={"groups": [{"columns": ["value"], "expr":"is_lesser_than", "value":[20]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
           Row(date='2022-01-01', value=10)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_lesser_than_or_equal_to_date(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_lesser_than_or_equal_to", "value":["2022-02-15"]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_lesser_than_or_equal_to_number(self):
        data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20),
            Row(date='2022-03-20', value=30),
            Row(date='2022-04-10', value=40)
                ]
        schema = ["date", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_lesser_than_or_equal_to", "value":[20]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(date='2022-01-01', value=10),
            Row(date='2022-02-15', value=20)
            ]
        expected_schema = ["date", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_true(self):
        data = [
            Row(grade='A', value=True),
            Row(grade='C', value=True),
            Row(grade='B', value=False),
            Row(grade='D', value=False)
                ]
        schema = ["grade", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr": "is_true", "value": [None]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(grade='A', value=True),
            Row(grade='C', value=True)
            ]
        expected_schema = ["grade", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])

    def test_filter_is_false(self):
        data = [
            Row(grade='A', value=True),
            Row(grade='C', value=True),
            Row(grade='B', value=False),
            Row(grade='D', value=False)
                ]
        schema = ["grade", "value"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"columns": ["value"], "expr": "is_false", "value": [None]}]}
        df_filter = self.filter.execute(df, parameters, self.spark)
        expected_data = [
            Row(grade='B', value=False),
            Row(grade='D', value=False)
            ]
        expected_schema = ["grade", "value"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_filter.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_filter.collect()], [row.asDict() for row in expected_df.collect()])


if __name__ == '__main__':
    unittest.main()
