import unittest
from spark_server.pipeline.transformer import SQLOperations
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerSQLOperations(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestSQLOperations").getOrCreate()
        cls.sql_operations = SQLOperations()

    def test_sql_operations(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"query": "SELECT * FROM df where age >= 25 order by name"}]
        }
        df_sql_operations = self.sql_operations.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=2, name="Alice", age=30),
            Row(id=1, name="John", age=25)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sql_operations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sql_operations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sql_operations_1(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"query": "SELECT * FROM df"}]
        }
        df_sql_operations = self.sql_operations.execute(df, parameters, self.spark)
        expected_data =  [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sql_operations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sql_operations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sql_operations_2(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"query": "SELECT age FROM df"}]
        }
        df_sql_operations = self.sql_operations.execute(df, parameters, self.spark)
        expected_data =  [
            Row(age=25),
            Row(age=30),
            Row(age=22)
        ]
        expected_schema = ["age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sql_operations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sql_operations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sql_operations_3(self):
        data = [
            Row(customer='Alice', order_amount=100),
            Row(customer='Bob', order_amount=150),
            Row(customer='Alice', order_amount=200),
            Row(customer='David', order_amount=120),
        ]
        schema = ["customer", "order_amount"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"query": "SELECT customer, SUM(order_amount) AS total_sales FROM df GROUP BY customer"}]
        }
        df_sql_operations = self.sql_operations.execute(df, parameters, self.spark)
        expected_data =  [
            Row(customer='Alice', total_sales=300),
            Row(customer='Bob', total_sales=150),
            Row(customer='David', total_sales=120)
        ]
        expected_schema = ['customer', 'total_sales']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sql_operations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sql_operations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sql_operations_4(self):
        data = [
            Row(product='A', sales=800, region='North'),
            Row(product='B', sales=1200, region='North'),
            Row(product='C', sales=950, region='North'),
            Row(product='D', sales=1400, region='West'),
        ]
        schema = ["product", "sales", "region"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"query": "SELECT * FROM df WHERE sales > 1000 AND region = 'North'"}]
        }
        df_sql_operations = self.sql_operations.execute(df, parameters, self.spark)
        expected_data =  [
            Row(product='B', sales=1200, region='North')
        ]
        expected_schema = ["product", "sales", "region"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sql_operations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sql_operations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sql_operations_5(self):
        data = [
            Row(product='A', sales=800, region='North'),
            Row(product='B', sales=1200, region='North'),
            Row(product='C', sales=950, region='North'),
            Row(product='D', sales=1400, region='West'),
        ]
        schema = ["product", "sales", "region"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"query": "SELECT * FROM df limit 2"}]
        }
        df_sql_operations = self.sql_operations.execute(df, parameters, self.spark)
        expected_data =  [
            Row(product='A', sales=800, region='North'),
            Row(product='B', sales=1200, region='North')
        ]
        expected_schema = ["product", "sales", "region"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sql_operations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sql_operations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sql_operations_6(self):
        data = [
            Row(product='A', sales=800, region='North', date='2024-03-15'),
            Row(product='B', sales=1200, region='North', date='2024-03-15'),
            Row(product='C', sales=950, region='North', date='2024-01-15'),
            Row(product='D', sales=1400, region='West', date='2024-01-15'),
        ]
        schema = ["product", "sales", "region", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"query": "SELECT * FROM df WHERE MONTH(CAST(date AS DATE)) = 1"}]
        }
        df_sql_operations = self.sql_operations.execute(df, parameters, self.spark)
        expected_data =  [
            Row(product='C', sales=950, region='North', date='2024-01-15'),
            Row(product='D', sales=1400, region='West', date='2024-01-15')
        ]
        expected_schema = ["product", "sales", "region", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sql_operations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sql_operations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sql_operations_7(self):
        data = [
            Row(product='A', sales=800, region='North', date='2024-03-15'),
            Row(product='B', sales=1200, region='North', date='2024-03-15'),
            Row(product='C', sales=950, region='North', date='2024-01-15'),
            Row(product='D', sales=1400, region='West', date='2024-01-15'),
        ]
        schema = ["product", "sales", "region", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"query": "SELECT * FROM df WHERE date = '2024-01-15'"}]
        }
        df_sql_operations = self.sql_operations.execute(df, parameters, self.spark)
        expected_data =  [
            Row(product='C', sales=950, region='North', date='2024-01-15'),
            Row(product='D', sales=1400, region='West', date='2024-01-15')
        ]
        expected_schema = ["product", "sales", "region", "date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sql_operations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sql_operations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_sql_operations_9(self):
        data = [
            Row(product='A', sales=800, region='North', date='2024-03-15'),
            Row(product='B', sales=1200, region='North', date='2024-03-15'),
            Row(product='C', sales=950, region='North', date='2024-01-15'),
            Row(product='D', sales=1400, region='West', date='2024-01-15'),
        ]
        schema = ["product", "sales", "region", "date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"query": "SELECT product, sales FROM df"}]
        }
        df_sql_operations = self.sql_operations.execute(df, parameters, self.spark)
        expected_data =  [
             Row(product='A', sales=800),
            Row(product='B', sales=1200),
            Row(product='C', sales=950),
            Row(product='D', sales=1400),
        ]
        expected_schema = ["product", "sales"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_sql_operations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_sql_operations.collect()], [row.asDict() for row in expected_df.collect()])
