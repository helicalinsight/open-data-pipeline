import unittest
from spark_server.pipeline.transformer import Arithmetic
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import to_date
from datetime import date, timedelta
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerArithmetic(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestArithmetic").getOrCreate()
        cls.arithmetic = Arithmetic()

    def test_arithmetic_operations_for_addition(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold+5", "destination_column": "units_total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, units_total=105),
            Row(product=2, units_sold=200, units_total=205)
        ]
        expected_schema = ["product", "units_sold", "units_total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])

    def test_arithmetic_operations_for_addition_if_new_column_is_none(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold+5", "destination_column": "new_column_1"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, new_column_1=105),
            Row(product=2, units_sold=200, new_column_1=205)
        ]
        expected_schema = ["product", "units_sold", "new_column_1"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])

    def test_arithmetic_operations_for_subtraction(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold-5", "destination_column": "units_total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, units_total=95),
            Row(product=2, units_sold=200, units_total=195)
        ]
        expected_schema = ["product", "units_sold", "units_total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])


    def test_arithmetic_operations_for_subtraction_for_two_columns(self):
        data = [
            Row(product=1, units_sold=100, unit_price=10),
            Row(product=2, units_sold=200, unit_price=20)
        ]
        schema = ["product", "units_sold", "unit_price"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold-unit_price", "destination_column": "units_total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, unit_price=10, units_total=90),
            Row(product=2, units_sold=200, unit_price=20, units_total=180)
        ]
        expected_schema = ["product", "units_sold", "unit_price", "units_total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])


    def test_arithmetic_operations_for_multiplication_for_two_columns(self):
        data = [
            Row(product=1, units_sold=10, unit_price=10),
            Row(product=2, units_sold=20, unit_price=20)
        ]
        schema = ["product", "units_sold", "unit_price"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold*unit_price", "destination_column": "units_total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=10, unit_price=10, units_total=100),
            Row(product=2, units_sold=20, unit_price=20, units_total=400)
        ]
        expected_schema = ["product", "units_sold", "unit_price", "units_total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])

    def test_arithmetic_operations_for_division(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold/2", "destination_column": "units_total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, units_total=50),
            Row(product=2, units_sold=200, units_total=100)
        ]
        expected_schema = ["product", "units_sold", "units_total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])


    def test_arithmetic_operations_for_power(self):
        data = [
            Row(product=1, units_sold=10),
            Row(product=2, units_sold=20)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold**3", "destination_column": "units_total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=10, units_total=1000),
            Row(product=2, units_sold=20, units_total=8000)
        ]
        expected_schema = ["product", "units_sold", "units_total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])

    def test_arithmetic_operations_multiple_operations(self):
        data = [
            Row(product=1, units_sold=10),
            Row(product=2, units_sold=20)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold+3", "destination_column": "new_column_1"},
                                 {"query": "units_sold+2", "destination_column": "new_column_2"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=10, new_column_1=13, new_column_2=12),
            Row(product=2, units_sold=20, new_column_1=23, new_column_2=22)
        ]
        expected_schema = ["product", "units_sold", "new_column_1", "new_column_2"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])

    def test_arithmetic_operations_multiple_operations_with_existing_column_as_new_column(self):
        data = [
            Row(product=1, units_sold=10),
            Row(product=2, units_sold=20)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold+3", "destination_column": "units_sold"},
                                 {"query": "units_sold+6", "destination_column": "units_sold"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=19),
            Row(product=2, units_sold=29)
        ]
        expected_schema = ["product", "units_sold"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])

    def test_arithmetic_operations_for_modulo(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold%2", "destination_column": "total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, total=0),
            Row(product=2, units_sold=200, total=0)
        ]
        expected_schema = ["product", "units_sold", "total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])


    def test_arithmetic_operations_for_floor_division(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "units_sold//2", "destination_column": "total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, total=50),
            Row(product=2, units_sold=200, total=100)
        ]
        expected_schema = ["product", "units_sold", "total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])


    def test_arithmetic_operations_abs(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "abs(units_sold)", "destination_column": "total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, total=100),
            Row(product=2, units_sold=200, total=200)
        ]
        expected_schema = ["product", "units_sold", "total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])


    def test_arithmetic_operations_log(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "log(units_sold)", "destination_column": "total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, total=4.605170185988092),
            Row(product=2, units_sold=200, total=5.298317366548036)
        ]
        expected_schema = ["product", "units_sold", "total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])


    def test_arithmetic_operations_expr1(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "(units_sold + 100) / (2 * 3)", "destination_column": "total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, total=33.333333333333336),
            Row(product=2, units_sold=200, total=50.0)
        ]
        expected_schema = ["product", "units_sold", "total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])

    def test_arithmetic_operations_expr2(self):
        data = [
            Row(product=1, units_sold=100),
            Row(product=2, units_sold=200)
        ]
        schema = ["product", "units_sold"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {"groups": [{"query": "(units_sold + 100) / (2 * 3)", "destination_column": "total"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(product=1, units_sold=100, total=33.333333333333336),
            Row(product=2, units_sold=200, total=50.0)
        ]
        expected_schema = ["product", "units_sold", "total"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])


    def test_arithmetic_operations_date_columns_1_subtract(self):
        data = [
            Row(date_1="2024-03-20", date_2="2024-03-21"),
            Row(date_1="2024-03-10", date_2="2024-03-10")
        ]
        schema = ["date_1", "date_2"]
        df = self.spark.createDataFrame(data, schema=schema)
        df = df.withColumn("date_1", to_date("date_1", "yyyy-MM-dd"))
        df = df.withColumn("date_2", to_date("date_2", "yyyy-MM-dd"))
        parameters = {"groups": [{"query": "date_1-date_2", "destination_column": "date_difference"}]}
        df_arithmetic = self.arithmetic.execute(df, parameters, self.spark)
        expected_data = [
            Row(date_1=date(2024, 3, 20), date_2=date(2024, 3, 21), date_difference=timedelta(days=-1)),
            Row(date_1=date(2024, 3, 10), date_2=date(2024, 3, 10), date_difference=timedelta(days=0))
        ]
        # add date diff value in pandas we get 10 days and 11 days
        expected_schema = ["date_1", "date_2", "date_difference"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_arithmetic.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_arithmetic.collect()], [row.asDict() for row in expected_df.collect()])
