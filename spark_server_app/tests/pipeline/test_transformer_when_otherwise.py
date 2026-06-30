import unittest
from spark_server.pipeline.transformer import WhenOtherwise
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerWhenOtherwise(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestWhenOtherwise").getOrCreate()
        cls.when_otherwise = WhenOtherwise()

    def test_when_otherwise_without_new_column_name(self):
        data = [
            Row(id=1, name="John", age=25, marks=40),
            Row(id=2, name="Alice", age=30, marks=39),
            Row(id=3, name="Bob", age=22, marks=19)
        ]
        schema = ["id", "name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups":[{"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS new_column_1\nFROM df;"}]}

        df_when_otherwise = self.when_otherwise.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, marks=40, new_column_1="PASS"),
            Row(id=2, name="Alice", age=30, marks=39, new_column_1="MODERATE"),
            Row(id=3, name="Bob", age=22, marks=19, new_column_1="FAIL")
        ]
        expected_schema = ["id", "name", "age", "marks", "new_column_1"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_when_otherwise.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_when_otherwise.collect()], [row.asDict() for row in expected_df.collect()])

    def test_when_otherwise_with_new_column_name(self):
        data = [
            Row(id=1, name="John", age=25, marks=40),
            Row(id=2, name="Alice", age=30, marks=39),
            Row(id=3, name="Bob", age=22, marks=19)
        ]
        schema = ["id", "name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups":[{"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS final_res\nFROM df;"}]}

        df_when_otherwise = self.when_otherwise.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, marks=40, final_res="PASS"),
            Row(id=2, name="Alice", age=30, marks=39, final_res="MODERATE"),
            Row(id=3, name="Bob", age=22, marks=19, final_res="FAIL")
        ]
        expected_schema = ["id", "name", "age", "marks", "final_res"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_when_otherwise.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_when_otherwise.collect()], [row.asDict() for row in expected_df.collect()])

    def test_when_otherwise_with_existing_new_column_name(self):
        data = [
            Row(id=1, name="John", age=25, marks=40),
            Row(id=2, name="Alice", age=30, marks=39),
            Row(id=3, name="Bob", age=22, marks=19)
        ]
        schema = ["id", "name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups":[{"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS marks_1\nFROM df;"}]}

        df_when_otherwise = self.when_otherwise.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, marks=40, marks_1="PASS"),
            Row(id=2, name="Alice", age=30, marks=39, marks_1="MODERATE"),
            Row(id=3, name="Bob", age=22, marks=19, marks_1="FAIL")
        ]
        expected_schema = ["id", "name", "age", "marks", "marks_1"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_when_otherwise.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_when_otherwise.collect()], [row.asDict() for row in expected_df.collect()])

if __name__ == '__main__':
    unittest.main()
