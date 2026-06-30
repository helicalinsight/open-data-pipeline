import unittest
from spark_server.pipeline.transformer import Split
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerSplitColumns(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerSplit").getOrCreate()
        cls.split_cols = Split()

    def test_split_columns_date(self):
        data = [
            Row(id=1, name="John_doe", age=25, date="5/9/2024"),
            Row(id=2, name="Alice_smith", age=30, date="5/9/2024"),
            Row(id=3, name="Bob_walker", age=22, date="5/9/2024")
        ]
        schema = ["id", "name", "age", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"destination_columns": ["month", "day", "year"], 
                                  "column": "date", 
                                  "delimiter": "/"}]}
        df_col_splitted = self.split_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John_doe", age=25, date="5/9/2024", month="5", day="9", year="2024"),
            Row(id=2, name="Alice_smith", age=30, date="5/9/2024", month="5", day="9", year="2024"),
            Row(id=3, name="Bob_walker", age=22, date="5/9/2024", month="5", day="9", year="2024")
        ]
        expected_schema = ["id", "name", "age", "date", "month", "day", "year"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_splitted.columns, ["id", "name", "age", "date", "month", "day", "year"])
        self.assertEqual([row.asDict() for row in df_col_splitted.collect()], [row.asDict() for row in expected_df.collect()])

    def test_split_columns_string(self):
        data = [
            Row(id=1, name="John_doe", age=25),
            Row(id=2, name="Alice_smith", age=30),
            Row(id=3, name="Bob_walker", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"destination_columns": ["first_name", "last_name"], 
                                  "column": "name", 
                                  "delimiter": "_"}]}
        df_col_splitted = self.split_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John_doe", age=25, first_name="John", last_name="doe"),
            Row(id=2, name="Alice_smith", age=30, first_name="Alice", last_name="smith"),
            Row(id=3, name="Bob_walker", age=22, first_name="Bob", last_name="walker")
        ]
        expected_schema = ["id", "name", "age", "first_name", "last_name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_splitted.columns, ["id", "name", "age", "first_name", "last_name"])
        self.assertEqual([row.asDict() for row in df_col_splitted.collect()], [row.asDict() for row in expected_df.collect()])

    def test_split_with_existing_destination_columns(self):
        data = [
            Row(id=1, name="John_doe", age=25),
            Row(id=2, name="Alice_smith", age=30),
            Row(id=3, name="Bob_walker", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"destination_columns": ["name_1", "last_name"], 
                                  "column": "name", 
                                  "delimiter": "_"}]}
        df_col_splitted = self.split_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John_doe", age=25, name_1="John", last_name="doe"),
            Row(id=2, name="Alice_smith", age=30, name_1="Alice", last_name="smith"),
            Row(id=3, name="Bob_walker", age=22, name_1="Bob", last_name="walker")
        ]
        expected_schema = ["id", "name", "age", "name_1", "last_name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_splitted.columns, ["id", "name", "age", "name_1", "last_name"])
        self.assertEqual([row.asDict() for row in df_col_splitted.collect()], [row.asDict() for row in expected_df.collect()])

    def test_split_without_destination_columns(self):
        data = [
            Row(id=1, name="John_doe", age=25),
            Row(id=2, name="Alice_smith", age=30),
            Row(id=3, name="Bob_walker", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"destination_columns": ["new_column_1", "new_column_2"],
                                  "column": "name", 
                                  "delimiter": "_"}]}
        df_col_splitted = self.split_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John_doe", age=25, new_column_1="John", new_column_2="doe"),
            Row(id=2, name="Alice_smith", age=30, new_column_1="Alice", new_column_2="smith"),
            Row(id=3, name="Bob_walker", age=22, new_column_1="Bob", new_column_2="walker")
        ]
        expected_schema = ["id", "name", "age", "new_column_1", "new_column_2"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_splitted.columns, ["id", "name", "age", "new_column_1", "new_column_2"])
        self.assertEqual([row.asDict() for row in df_col_splitted.collect()], [row.asDict() for row in expected_df.collect()])

    def test_split_columns_date_without_destination_columns(self):
        data = [
            Row(id=1, name="John_doe", age=25, date="5/9/2024"),
            Row(id=2, name="Alice_smith", age=30, date="5/9/2024"),
            Row(id=3, name="Bob_walker", age=22, date="5/9/2024")
        ]
        schema = ["id", "name", "age", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"destination_columns": ["new_column_1", "new_column_2", "new_column_3"],
                                  "column": "date", 
                                  "delimiter": "/"}]}
        df_col_splitted = self.split_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John_doe", age=25, date="5/9/2024", new_column_1="5", new_column_2="9", new_column_3="2024"),
            Row(id=2, name="Alice_smith", age=30, date="5/9/2024", new_column_1="5", new_column_2="9", new_column_3="2024"),
            Row(id=3, name="Bob_walker", age=22, date="5/9/2024", new_column_1="5", new_column_2="9", new_column_3="2024")
        ]
        expected_schema = ["id", "name", "age", "date", "new_column_1", "new_column_2", "new_column_3"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_splitted.columns, ["id", "name", "age", "date", "new_column_1", "new_column_2", "new_column_3"])
        self.assertEqual([row.asDict() for row in df_col_splitted.collect()], [row.asDict() for row in expected_df.collect()])

    def test_split_columns_string_1(self):
        data = [
            Row(id=1, name="John doe", age=25),
            Row(id=2, name="Alice smith", age=30),
            Row(id=3, name="Bob walker", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"destination_columns": ["first_name", "last_name"], 
                                  "column": "name", 
                                  "delimiter": " "}]}
        df_col_splitted = self.split_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John doe", age=25, first_name="John", last_name="doe"),
            Row(id=2, name="Alice smith", age=30, first_name="Alice", last_name="smith"),
            Row(id=3, name="Bob walker", age=22, first_name="Bob", last_name="walker")
        ]
        expected_schema = ["id", "name", "age", "first_name", "last_name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_splitted.columns, ["id", "name", "age", "first_name", "last_name"])
        self.assertEqual([row.asDict() for row in df_col_splitted.collect()], [row.asDict() for row in expected_df.collect()])


if __name__ == '__main__':
    unittest.main()
