import unittest
from spark_server.pipeline.transformer import Correlation
from pyspark.sql import SparkSession, Row
from datetime import date
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerCorrelation(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestCorrelation").getOrCreate()
        cls.correlation = Correlation()

    def test_correlation(self):
        data = [
            Row(name="Alex", age=10, marks=40),
            Row(name="Bob", age=11, marks=39),
            Row(name="Emily", age=12, marks=45)
        ]
        schema = ["name", "age", "marks"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [ {"columns": ["age", "marks"],  "destination_column":"age_marks_correlation"}]
        }
        df_correlation = self.correlation.execute(df, parameters, self.spark)
        expected_data = [
            Row(name="Alex", age=10, marks=40, age_marks_correlation=0.7777137710478189),
            Row(name="Bob", age=11, marks=39, age_marks_correlation=0.7777137710478189),
            Row(name="Emily", age=12, marks=45, age_marks_correlation=0.7777137710478189)
        ]
        expected_schema = ["name", "age", "marks", "age_marks_correlation"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_correlation.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_correlation.collect()], [row.asDict() for row in expected_df.collect()])
