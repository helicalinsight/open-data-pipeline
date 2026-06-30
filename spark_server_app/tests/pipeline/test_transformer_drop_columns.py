import unittest
from spark_server.pipeline.transformer import DropColumns
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerDropColumns(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerDropColumns").getOrCreate()
        cls.drop_cols = DropColumns()
    
    def test_drop_columns(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age"]}]
        }
        df_drop_cols = self.drop_cols.execute(df, parameters, self.spark)
        self.assertEqual(df_drop_cols.columns, ["id", "name"])
    
    def test_drop_columns_with_non_existing_column(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["test"]}]
        }
        df_drop_cols = self.drop_cols.execute(df, parameters, self.spark)
        self.assertEqual(df_drop_cols.columns, ["id", "name", "age"])
    
    def test_drop_columns_with_columns_as_list(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["name"]}, {"columns": ["age"]}]
        }
        df_drop_cols = self.drop_cols.execute(df, parameters, self.spark)
        self.assertEqual(df_drop_cols.columns, ["id"])
    