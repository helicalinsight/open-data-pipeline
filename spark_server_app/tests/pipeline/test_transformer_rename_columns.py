import unittest
from spark_server.pipeline.transformer import RenameColumns
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerRenameColumns(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerRenameColumns").getOrCreate()
        cls.rename_cols = RenameColumns()
    
    def test_rename_columns(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"new_name": "student_id", "old_name": "id"}]
        }
        df_col_renamed = self.rename_cols.execute(df, parameters, self.spark)
        self.assertEqual(df_col_renamed.columns, ["student_id", "name", "age"])

    def test_rename_columns_if_new_column_is_already_present(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"new_name": "name", "old_name": "name"}]
        }
        df_col_renamed = self.rename_cols.execute(df, parameters, self.spark)
        self.assertEqual(df_col_renamed.columns, ["id", "name", "age"])

