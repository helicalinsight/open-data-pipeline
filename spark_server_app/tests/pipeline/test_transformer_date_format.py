import unittest
from spark_server.pipeline.transformer import DateFormat
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import to_date
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerDateFormat(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestDateFormat").getOrCreate()
        cls.date_format = DateFormat()

    def test_date_format(self):
        data = [
            Row(id=1, name="John", age=25, exam_date='12/22/2000'),
            Row(id=2, name="Alice", age=30, exam_date='11/24/2000'),
            Row(id=3, name="Bob", age=22, exam_date='12/28/2000')
        ]
        schema = ["id", "name", "age", "exam_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        df = df.withColumn("exam_date", to_date(df.exam_date, 'MM/dd/yyyy'))
        parameters = {
            "groups": [{"columns": ["exam_date"], "format": "YYYY.mm.DD"}]
        }
        df_date_format = self.date_format.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=1, name="John", age=25, exam_date='2000.12.22'),
                Row(id=2, name="Alice", age=30, exam_date='2000.11.24'),
                Row(id=3, name="Bob", age=22, exam_date='2000.12.28')
            ]
        expected_schema = ["id", "name", "age", "exam_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_date_format.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_date_format.collect()], [row.asDict() for row in expected_df.collect()])

    def test_date_format_1(self):
        data = [
            Row(id=1, name="John", age=25, exam_date='12/22/2000'),
            Row(id=2, name="Alice", age=30, exam_date='11/24/2000'),
            Row(id=3, name="Bob", age=22, exam_date='12/28/2000')
        ]
        schema = ["id", "name", "age", "exam_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        df = df.withColumn("exam_date", to_date(df.exam_date, 'MM/dd/yyyy'))
        parameters = {
            "groups": [{"columns": ["exam_date"], "format": "MMM d, yyyy"}]
        }
        df_date_format = self.date_format.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=1, name="John", age=25, exam_date='Dec 22, 2000'),
                Row(id=2, name="Alice", age=30, exam_date='Nov 24, 2000'),
                Row(id=3, name="Bob", age=22, exam_date='Dec 28, 2000')
            ]
        expected_schema = ["id", "name", "age", "exam_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_date_format.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_date_format.collect()], [row.asDict() for row in expected_df.collect()])

    def test_date_format_2(self):
        data = [
            Row(id=1, name="John", age=25, exam_date='12/22/2000'),
            Row(id=2, name="Alice", age=30, exam_date='11/24/2000'),
            Row(id=3, name="Bob", age=22, exam_date='12/28/2000')
        ]
        schema = ["id", "name", "age", "exam_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        df = df.withColumn("exam_date", to_date(df.exam_date, 'MM/dd/yyyy'))
        parameters = {
            "groups": [{"columns": ["exam_date"], "format": "dd-mm-yyyy"}]
        }
        df_date_format = self.date_format.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=1, name="John", age=25, exam_date='22-12-2000'),
                Row(id=2, name="Alice", age=30, exam_date='24-11-2000'),
                Row(id=3, name="Bob", age=22, exam_date='28-12-2000')
            ]
        expected_schema = ["id", "name", "age", "exam_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_date_format.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_date_format.collect()], [row.asDict() for row in expected_df.collect()])

    def test_date_format_3(self):
        data = [
            Row(id=1, name="John", age=25, exam_date='12/22/2000'),
            Row(id=2, name="Alice", age=30, exam_date='11/24/2000'),
            Row(id=3, name="Bob", age=22, exam_date='12/28/2000')
        ]
        schema = ["id", "name", "age", "exam_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        df = df.withColumn("exam_date", to_date(df.exam_date, 'MM/dd/yyyy'))
        parameters = {
            "groups": [{"columns": ["exam_date"], "format": "d MMMM yyyy"}]
        }
        df_date_format = self.date_format.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=1, name="John", age=25, exam_date='22 December 2000'),
                Row(id=2, name="Alice", age=30, exam_date='24 November 2000'),
                Row(id=3, name="Bob", age=22, exam_date='28 December 2000')
            ]
        expected_schema = ["id", "name", "age", "exam_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_date_format.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_date_format.collect()], [row.asDict() for row in expected_df.collect()])

    def test_date_format_4(self):
        data = [
            Row(id=1, name="John", age=25, exam_date='12/22/2000'),
            Row(id=2, name="Alice", age=30, exam_date='11/24/2000'),
            Row(id=3, name="Bob", age=22, exam_date='12/28/2000')
        ]
        schema = ["id", "name", "age", "exam_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        df = df.withColumn("exam_date", to_date(df.exam_date, 'MM/dd/yyyy'))
        parameters = {
            "groups": [{"columns": ["exam_date"], "format": "d mmmm"}]
        }
        df_date_format = self.date_format.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=1, name="John", age=25, exam_date='22 December'),
                Row(id=2, name="Alice", age=30, exam_date='24 November'),
                Row(id=3, name="Bob", age=22, exam_date='28 December')
            ]
        expected_schema = ["id", "name", "age", "exam_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_date_format.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_date_format.collect()], [row.asDict() for row in expected_df.collect()])

    def test_date_format_5(self):
        data = [
            Row(id=1, name="John", age=25, exam_date='12/22/2000'),
            Row(id=2, name="Alice", age=30, exam_date='11/24/2000'),
            Row(id=3, name="Bob", age=22, exam_date='12/28/2000')
        ]
        schema = ["id", "name", "age", "exam_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        df = df.withColumn("exam_date", to_date(df.exam_date, 'MM/dd/yyyy'))
        parameters = {
            "groups": [{"columns": ["exam_date"], "format": "d mmmm"}]
        }
        df_date_format = self.date_format.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=1, name="John", age=25, exam_date='22 December'),
                Row(id=2, name="Alice", age=30, exam_date='24 November'),
                Row(id=3, name="Bob", age=22, exam_date='28 December')
            ]
        expected_schema = ["id", "name", "age", "exam_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_date_format.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_date_format.collect()], [row.asDict() for row in expected_df.collect()])

    def test_date_format_6(self):
        data = [
            Row(id=1, name="John", age=25, exam_date='12/22/2000'),
            Row(id=2, name="Alice", age=30, exam_date='11/24/2000'),
            Row(id=3, name="Bob", age=22, exam_date='12/28/2000')
        ]
        schema = ["id", "name", "age", "exam_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        df = df.withColumn("exam_date", to_date(df.exam_date, 'MM/dd/yyyy'))
        parameters = {
            "groups": [{"columns": ["exam_date"], "format": "yymmdd"}]
        }
        df_date_format = self.date_format.execute(df, parameters, self.spark)
        expected_data = [
                Row(id=1, name="John", age=25, exam_date='20001222'),
                Row(id=2, name="Alice", age=30, exam_date='20001124'),
                Row(id=3, name="Bob", age=22, exam_date='20001228')
            ]
        expected_schema = ["id", "name", "age", "exam_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_date_format.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_date_format.collect()], [row.asDict() for row in expected_df.collect()])
