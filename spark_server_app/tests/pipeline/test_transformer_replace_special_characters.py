import unittest
from spark_server.pipeline.transformer import ReplaceSpecialCharacters
from pyspark.sql import SparkSession, Row
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerReplaceSpecialCharacters(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerAddColumns").getOrCreate()
        cls.replace = ReplaceSpecialCharacters()

    def test_replace_special_characters(self):
        data = [
            Row(id=1, age=10, marks=40, name='pooja_shanmuk'),
            Row(id=2, age=11, marks=39, name='kavya_shetty'),
            Row(id=3, age=12, marks=45, name='bhavya_gowda')
        ]
        schema = ["id", "age", "marks", "name"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = { "groups": [{"target_character": "_", "columns": ["name"], "replacement_character": "-"}]}      
        df_col_added = self.replace.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, age=10, marks=40, name='pooja-shanmuk'),
            Row(id=2, age=11, marks=39, name='kavya-shetty'),
            Row(id=3, age=12, marks=45, name='bhavya-gowda')
            ]
        expected_schema = ["id", "age", "marks", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])

    def test_replace_special_characters_with_replacement_character_as_none(self):
        data = [
            Row(id=1, age=10, marks=40, name='pooja_shanmuk'),
            Row(id=2, age=11, marks=39, name='kavya_shetty'),
            Row(id=3, age=12, marks=45, name='bhavya_gowda')
        ]
        schema = ["id", "age", "marks", "name"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters ={ "groups": [{"target_character": "_", "columns": ["name"], "replacement_character": ""}]}
        df_col_added = self.replace.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, age=10, marks=40, name='poojashanmuk'),
            Row(id=2, age=11, marks=39, name='kavyashetty'),
            Row(id=3, age=12, marks=45, name='bhavyagowda')
            ]
        expected_schema = ["id", "age", "marks", "name"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])

    def test_replace_special_characters_for_date_column(self):
        data = [
            Row(id=1, name="John", age=25, exam_date='12/22/2000'),
            Row(id=2, name="Alice", age=30, exam_date='11/24/2000'),
            Row(id=3, name="Bob", age=22, exam_date='12/28/2000')
        ]
        schema = ["id", "name", "age", "exam_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = { "groups": [{"target_character": "/", "columns": ["exam_date"], "replacement_character": '.'}]}

        df_col_added = self.replace.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, exam_date='12.22.2000'),
            Row(id=2, name="Alice", age=30, exam_date='11.24.2000'),
            Row(id=3, name="Bob", age=22, exam_date='12.28.2000')
            ]
        expected_schema = ["id", "name", "age", "exam_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])


if __name__ == '__main__':
    unittest.main()
