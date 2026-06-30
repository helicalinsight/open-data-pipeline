import unittest
from spark_server.pipeline.transformer import RearrangeColumns
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerRearrangeColumns(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestRearrangeColumns").getOrCreate()
        cls.rearrange_columns = RearrangeColumns()
        cls.data = [
            Row(id=1, name="John", grade=25),
            Row(id=2, name="Alice", grade=30),
            Row(id=3, name="Bob", grade=22)
        ]
        cls.schema = ["id", "name", "grade"]
        cls.df = cls.spark.createDataFrame(cls.data, schema=cls.schema)

    def test_rearrange_columns_with_single_column_position(self):
        parameters = {"groups": [{"columns": [{"grade":1}]}]}
        df_rearrange_columns = self.rearrange_columns.execute(self.df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=25, name="John"),
            Row(id=2, grade=30, name="Alice"),
            Row(id=3, grade=22, name="Bob")
        ]
        expected_schema = ["id", "grade", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_rearrange_columns.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_rearrange_columns.collect()], [row.asDict() for row in expected_df.collect()])

    def test_rearrange_columns_with_single_column_position_to_negative_index(self):
        parameters = {"groups": [{"columns": [{"id":-1}]}]}
        df_rearrange_columns = self.rearrange_columns.execute(self.df, parameters, self.spark)
        expected_data = [
            Row(name="John", grade=25, id=1),
            Row(name="Alice", grade=30, id=2),
            Row(name="Bob", grade=22, id=3)
        ]
        expected_schema = ["name", "grade", "id"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_rearrange_columns.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_rearrange_columns.collect()], [row.asDict() for row in expected_df.collect()])

    def test_rearrange_columns_with_relative_columns_position_before(self):
        parameters = {"groups": [{"columns":[{"grade":1},{"id":2}]}]}
        df_rearrange_columns = self.rearrange_columns.execute(self.df, parameters, self.spark)
        expected_data = [
            Row(name="John", grade=25, id=1),
            Row(name="Alice", grade=30, id=2),
            Row(name="Bob", grade=22, id=3)
        ]
        expected_schema = ["name", "grade", "id"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_rearrange_columns.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_rearrange_columns.collect()], [row.asDict() for row in expected_df.collect()])

    def test_rearrange_columns_with_relative_columns_position_after(self):
        parameters = {"groups": [{"columns":[{"id":1},{"grade":2}]}]}
        df_rearrange_columns = self.rearrange_columns.execute(self.df, parameters, self.spark)
        expected_data = [
            Row(id=1, grade=25, name="John"),
            Row(id=2, grade=30, name="Alice"),
            Row(id=3, grade=22, name="Bob")
        ]
        expected_schema = ["id", "grade", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_rearrange_columns.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_rearrange_columns.collect()], [row.asDict() for row in expected_df.collect()])
