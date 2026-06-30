import unittest
from spark_server.pipeline.transformer import AddColumns
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerAddColumns(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerAddColumns").getOrCreate()
        cls.add_cols = AddColumns()

    def test_add_columns(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["salary"], "default": "100000"}]
        }
        df_col_added = self.add_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, salary="100000"),
            Row(id=2, name="Alice", age=30, salary="100000"),
            Row(id=3, name="Bob", age=22, salary="100000")
        ]
        expected_schema = ["id", "name", "age", "salary"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_added.columns, ["id", "name", "age", "salary"])
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])

    def test_add_columns_with_audit(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["salary"], "default": "100000"}]
        }
        
        conf = {
            "schedule_id": "665ded10aea87247ea56712b",
            "user_id": "6641ad931a3ba5058c56af19",
            "chat_id": "665e937aaea87247ea567131",
            "run_id": "80acea50-a81e-49bc-ba73-238a8041065c",
            "function": "add_columns"
        }
        transformer = AddColumns(conf)
        
        # Using the execute_with_audit function
        df_col_added_with_audit = transformer.execute_with_audit(df, parameters, self.spark)
        
        # Expected output DataFrame
        expected_data = [
            Row(id=1, name="John", age=25, salary="100000"),
            Row(id=2, name="Alice", age=30, salary="100000"),
            Row(id=3, name="Bob", age=22, salary="100000")
        ]
        expected_schema = ["id", "name", "age", "salary"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        
        # Asserting columns
        self.assertEqual(df_col_added_with_audit.columns, expected_df.columns)
        
        # Asserting the content of DataFrame
        self.assertEqual([row.asDict() for row in df_col_added_with_audit.collect()],
                         [row.asDict() for row in expected_df.collect()])


    def test_add_columns_with_list_of_columns(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["loans", "debts"], "default": 0}, {"columns": ["salary"], "default": "100000"}]
        }
        df_col_added = self.add_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, loans=0, debts=0, salary="100000"),
            Row(id=2, name="Alice", age=30, loans=0, debts=0, salary="100000"),
            Row(id=3, name="Bob", age=22, loans=0, debts=0, salary="100000")
        ]
        expected_schema = ["id", "name", "age", "loans", "debts", "salary"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_added.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])

    def test_add_columns_existing_column(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["age"], "default": 20}]
        }
        df_col_added = self.add_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=20),
            Row(id=2, name="Alice", age=20),
            Row(id=3, name="Bob", age=20)
        ]
        expected_schema = ["id", "name", "age"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_added.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])
    
    def test_add_columns_without_default(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["marks"]}]
        }
        df_col_added = self.add_cols.execute(df, parameters, self.spark)
        expected_schema = StructType([
            StructField("id", IntegerType(), nullable=False),
            StructField("name", StringType(), nullable=False),
            StructField("age", IntegerType(), nullable=False),
            StructField("marks", StringType(), nullable=True)
        ])
        expected_data = [
            Row(id=1, name="John", age=25, marks=None),
            Row(id=2, name="Alice", age=30, marks=None),
            Row(id=3, name="Bob", age=22, marks=None)
        ]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_added.columns, ['id', 'name', 'age', 'marks'])
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])
    
    def test_add_columns_with_default_as_none(self):
        data = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["marks"], "default": None}]
        }
        df_col_added = self.add_cols.execute(df, parameters, self.spark)
        expected_schema = StructType([
            StructField("id", IntegerType(), nullable=False),
            StructField("name", StringType(), nullable=False),
            StructField("age", IntegerType(), nullable=False),
            StructField("marks", StringType(), nullable=True)
        ])
        expected_data = [
            Row(id=1, name="John", age=25, marks=None),
            Row(id=2, name="Alice", age=30, marks=None),
            Row(id=3, name="Bob", age=22, marks=None)
        ]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_added.columns, ['id', 'name', 'age', 'marks'])
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])
                    
    def test_add_columns_numeric_columns(self):
        data = [
            Row(id=1, name="John", age=25)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["number"], "default": 123},
                       {"columns": ["decimal"], "default": 45.67},
                       {"columns": ["fraction"], "default": 1/2},
                       {"columns": ["scientific"], "default": 1.23E+04},
                       {"columns": ["scientific_1"], "default": 4.56E-07},
                       {"columns": ["special"], "default": 12345},
                       {"columns": ["negative_int"], "default": -10},
                       {"columns": ["negative_decimal"], "default": -50.6},
                       {"columns": ["special_1"], "default": 123456-7890},
                       {"columns": ["phone_number"], "default": 9934565324}]
        }
        df_col_added = self.add_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, number=123, decimal=45.67, fraction=0.5, scientific=12300.0, scientific_1=4.56E-07, 
                special=12345, negative_int=-10, negative_decimal=-50.6, special_1=115566, phone_number=9934565324)
        ]
        expected_schema = ["id", "name", "age", "number", "decimal", "fraction", "scientific", "scientific_1", "special", "negative_int", 
                           "negative_decimal", "special_1", "phone_number"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_added.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])

    def test_add_columns_boolean_column(self):
        data = [
            Row(id=1, name="John", age=25)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["bool_true"], "default": True},
                       {"columns": ["bool_false"], "default": False}]
        }
        df_col_added = self.add_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, n1=True, n2=False)
        ]
        expected_schema = ["id", "name", "age", "bool_true", "bool_false"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_added.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])

    def test_add_columns_date_column(self):
        data = [
            Row(id=1, name="John", age=25)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["number"], "default": 44927},
                       {"columns": ["short_date"], "default": "1/1/2024"},
                       {"columns": ["long_date"], "default": "Monday, January 1, 2024"},
                       ]
        }
        df_col_added = self.add_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, number=44927, short_date="1/1/2024", long_date="Monday, January 1, 2024")
        ]
        expected_schema = ["id", "name", "age", "number", "short_date", "long_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_added.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])

    def test_add_columns_string_column(self):
        data = [
            Row(id=1, name="John", age=25)
        ]
        schema = ["id", "name", "age"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["short_text"], "default": "test"},
                       {"columns": ["long_text"], "default": "This is a long description of a product that goes into great detail about its features and benefits."},
                       {"columns": ["number"], "default": "01234"},
                       {"columns": ["number_1"], "default": "987654321"},
                       {"columns": ["date"], "default": "29-05-2024"},
                       {"columns": ["boolean"], "default": "True"},
                       {"columns": ["email"], "default": "john.doe@example.com"},
                       {"columns": ["url"], "default": "https://www.example.com"},
                       {"columns": ["phone_number"], "default": "+1-800-555-1234"},
                       {"columns": ["address"], "default": "123 Main St, Anytown, USA"},
                       {"columns": ["hex"], "default": "0x1A3F"}]
        }
        df_col_added = self.add_cols.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="John", age=25, short_text="test", long_text="This is a long description of a product that goes into great detail about its features and benefits.", 
                number="01234", number_1="987654321", date="29-05-2024", boolean="True", email="john.doe@example.com", url="https://www.example.com",
                phone_number="+1-800-555-1234", address="123 Main St, Anytown, USA", hex="0x1A3F")]
        expected_schema = ["id", "name", "age", "short_text", "long_text", "number", "number_1", "date", "boolean", "email", "url",
                           "phone_number", "address", "hex"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_col_added.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_col_added.collect()], [row.asDict() for row in expected_df.collect()])


if __name__ == '__main__':
    unittest.main()
