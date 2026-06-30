import unittest
from spark_server.pipeline.transformer import Extract
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import to_date, col, year, month, dayofmonth
from datetime import date
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerExtract(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestExtract").getOrCreate()
        cls.extract = Extract()

    def test_extract_year(self):
        data = [
            Row(id=1, joining_date=date(2024, 1, 1)),
            Row(id=2, joining_date=date(2024, 5, 20)),
            Row(id=3, joining_date=date(2024, 12, 31))
        ]
        schema = ["id", "joining_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"column": "joining_date", "component": ["year"], "destination_column": "joining_year"}]}
        df_extract = self.extract.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, joining_date=date(2024, 1, 1), joining_year=2024),
            Row(id=2, joining_date=date(2024, 5, 20), joining_year=2024),
            Row(id=3, joining_date=date(2024, 12, 31), joining_year=2024)
        ]
        expected_schema = ["id", "joining_date", "joining_year"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_extract.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_extract.collect()], [row.asDict() for row in expected_df.collect()])

    def test_extract_month(self):
        data = [
            Row(id=1, joining_date=date(2024, 1, 1)),
            Row(id=2, joining_date=date(2024, 5, 20)),
            Row(id=3, joining_date=date(2024, 12, 31))
        ]
        schema = ["id", "joining_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"column": "joining_date", "component": ["month"], "destination_column": "joining_month"}]}
        df_extract = self.extract.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, joining_date=date(2024, 1, 1), joining_month=1),
            Row(id=2, joining_date=date(2024, 5, 20), joining_month=5),
            Row(id=3, joining_date=date(2024, 12, 31), joining_month=12)
        ]
        expected_schema = ["id", "joining_date", "joining_month"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_extract.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_extract.collect()], [row.asDict() for row in expected_df.collect()])

    def test_extract_day(self):
        data = [
            Row(id=1, joining_date=date(2024, 1, 1)),
            Row(id=2, joining_date=date(2024, 5, 20)),
            Row(id=3, joining_date=date(2024, 12, 31))
        ]
        schema = ["id", "joining_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"column": "joining_date", "component": ["day"], "destination_column": "joining_day"}]}
        df_extract = self.extract.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, joining_date=date(2024, 1, 1), joining_day=1),
            Row(id=2, joining_date=date(2024, 5, 20), joining_day=20),
            Row(id=3, joining_date=date(2024, 12, 31), joining_day=31)
        ]
        expected_schema = ["id", "joining_date", "joining_day"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_extract.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_extract.collect()], [row.asDict() for row in expected_df.collect()])
