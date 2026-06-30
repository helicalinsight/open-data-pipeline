import unittest
from spark_server.pipeline.transformer import Cast
from pyspark.sql import SparkSession, Row
from datetime import date
from pyspark.sql.types import *
from pyspark.sql.functions import *
import os
import pytest


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerCast(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        # using this .config("spark.sql.legacy.timeParserPolicy", "LEGACY") because the format
        # ddd, MMM DD, YYYY HH:MM:SS (E, MMM d, y H:m:s ....in spark) is not able to recognize and it throws below error
        # pyspark.sql.utils.SparkUpgradeException: You may get a different result due to the upgrading to Spark >= 3.0: Fail to recognize 
        # 'E, MMM d, y H:m:s' pattern in the DateTimeFormatter. 1) You can set spark.sql.legacy.timeParserPolicy to LEGACY to restore the 
        # behavior before Spark 3.0. 2) 
        cls.spark = SparkSession.builder.appName("TestCast").config("spark.sql.legacy.timeParserPolicy", "LEGACY").getOrCreate()
        cls.cast = Cast()

    def test_cast(self):
        data = [(1.1,), (2.2,), (3.3,), (4.4,)]
        schema = StructType([
            StructField("avg", DoubleType(), True)
        ])
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["avg"], "new_type": "integer"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [(1,), (2,), (3,), (4,)]
        expected_schema = StructType([
            StructField("avg", IntegerType(), True)
        ])
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.columns, ["avg"])
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_unix_with_old_type(self):
        data = [(1709689270,), (1709775670,), (1490195805,)]
        schema = StructType([
            StructField("last_date", IntegerType(), True)
        ])
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date", "old_type": "unix"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [(date(2024, 3, 6),), (date(2024, 3, 7),), (date(2017, 3, 22),)]
        expected_schema = StructType([
            StructField("last_date", DateType(), True)
        ])
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.columns, ["last_date"])
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_unix_without_old_type(self):
        data = [(1709689270,), (1709775670,), (1490195805,)]
        schema = StructType([
            StructField("last_date", IntegerType(), True)
        ])
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [(date(2024, 3, 6),), (date(2024, 3, 7),), (date(2017, 3, 22),)]
        expected_schema = StructType([
            StructField("last_date", DateType(), True)
        ])
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.columns, ["last_date"])
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_unix_to_date(self):
        data = [(1709689270,), (1709775670,), (1490195805,)]
        schema = StructType([
            StructField("last_date", IntegerType(), True)
        ])
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        df_cast.show()
        expected_data = [
            Row(last_date=date(2024, 3, 6)),
            Row(last_date=date(2024, 3, 7)),
            Row(last_date=date(2017, 3, 22))
        ]
        expected_schema = ["last_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_float_to_int(self):
        data = [(1.0,), (2.0,), (3.0,), (4.0,)]
        schema = StructType([
            StructField("avg", FloatType(), True)
        ])
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["avg"], "new_type": "float"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [(1.0,), (2.0,), (3.0,), (4.0,)]
        expected_schema = StructType([
            StructField("avg", FloatType(), True)
        ])
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, ["avg"])
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_int_to_float(self):
        data = [(1,), (2,), (3,), (4,)]
        schema = StructType([
            StructField("avg", IntegerType(), True)
        ])
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["avg"], "new_type": "float"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [(1.0,), (2.0,), (3.0,), (4.0,)]
        expected_schema = StructType([
            StructField("avg", FloatType(), True)
        ])
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, ["avg"])
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping object cases")
    def test_cast_float_to_object(self):
        data = [
            Row(id=1, avg=175.51243237),
            Row(id=2, avg=160.33253457),
            Row(id=3, avg=180.23254778)
        ]
        schema = ["id", "avg"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["avg"], "new_type": "object"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, avg=175),
            Row(id=2, avg=160),
            Row(id=3, avg=180)
        ]
        expected_schema = ["id","avg"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping object cases")
    def test_cast_int_to_object(self):
        data = [
            Row(id=1, avg=175.51243237),
            Row(id=2, avg=160.33253457),
            Row(id=3, avg=180.23254778)
        ]
        schema = ["id", "avg"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["id"], "new_type": "object"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, avg=175),
            Row(id=2, avg=160),
            Row(id=3, avg=180)
        ]
        expected_schema = ["id","avg"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping object cases")
    def test_cast_boolean_to_object(self):
        data = [
            Row(id=1, bool_col=True),
            Row(id=2, bool_col=True),
            Row(id=3, bool_col=False)
        ]
        schema = ["id", "bool_col"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["bool_col"], "new_type": "object"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, bool_col=True),
            Row(id=2, bool_col=True),
            Row(id=3, bool_col=False)
        ]
        expected_schema = ["id","bool_col"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping object cases")
    def test_cast_string_to_object(self):
        data = [
            Row(id=1, name="tom"),
            Row(id=2, name="manish"),
            Row(id=3, name="dev")
        ]
        schema = ["id", "bool_col"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["name"], "new_type": "object"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(id=1, name="tom"),
            Row(id=2, name="manish"),
            Row(id=3, name="dev")
        ]
        expected_schema = ["id","bool_col"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping object cases")
    def test_cast_mixed_type_to_object(self):
        data = [
            Row(int_column=175),
            Row(int_column=-160),
            Row(int_column=12),
            Row(int_column='234'),
            Row(int_column='2,345'),
            Row(int_column=23.44),
            Row(int_column="1,222,3.9")
        ]
        schema = ["int_column"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["int_column"], "new_type": "object"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(int_column=175),
            Row(int_column=-160),
            Row(int_column=12),
            Row(int_column='234'),
            Row(int_column='2,345'),
            Row(int_column=23.44),
            Row(int_column="1,222,3.9")
        ]
        expected_schema = ["int_column"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_mixed_values_to_boolean(self):
        data = [
            Row(bool_col="true"),
            Row(bool_col="false"),
            Row(bool_col="TruE"),
            Row(bool_col="FaLSe"),
            Row(bool_col="1"),
            Row(bool_col="0"),
        ]
        schema = ["bool_col"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["bool_col"], "new_type": "boolean"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(bool_col=True),
            Row(bool_col=False),
            Row(bool_col=True),
            Row(bool_col=False),
            Row(bool_col=True),
            Row(bool_col=False),
        ]
        expected_schema = ["bool_col"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_boolean_to_string(self):
        data = [(True,), (False,),]
        schema = StructType([
            StructField("bool_col", BooleanType(), True)
        ])
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["bool_col"], "new_type": "string"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [("True",), ("False",)]
        expected_schema = StructType([
            StructField("bool_col", StringType(), True)
        ])
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, ['bool_col'])
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_int_to_string(self):
        data = [(175,), (160,), (180,)]
        schema = StructType([
            StructField("marks", IntegerType(), True)
        ])
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["marks"], "new_type": "string"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [("175",), ("160",), ("180",)]
        expected_schema = StructType([
            StructField("marks", StringType(), True)
        ])
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, ["marks"])
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_string_to_int(self):
        data = [("175",), ("160",), ("180",)]
        schema = StructType([
            StructField("marks", StringType(), True)
        ])
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["marks"], "new_type": "integer"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [(175,), (160,), (180,)]
        expected_schema = StructType([
            StructField("marks", IntegerType(), True)
        ])
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, ["marks"])
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_unix_without_old_type_if_dates_are_as_string(self):
        data = [
            Row(last_date="1709689270"),
            Row(last_date="1709775670"),
            Row(last_date="1490195805")
        ]
        schema = ["last_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(last_date=date(2024, 3, 6)),
            Row(last_date=date(2024, 3, 7)),
            Row(last_date=date(2017, 3, 22))
        ]
        expected_schema = ["last_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_unix_without_old_type_with_ms_unix_dates(self):
        data = [
            Row(last_date="1616688744000"),
            Row(last_date="1616692344000"),
            Row(last_date="1616695944000")
        ]
        schema = ["last_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(last_date=date(2021, 3, 25)),
            Row(last_date=date(2021, 3, 25)),
            Row(last_date=date(2021, 3, 25))
        ]
        expected_schema = ["last_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_unix_without_old_type_with_negative_ms_unix_dates(self):
        data = [
            Row(last_date="-1616688744000"),
            Row(last_date="-1616692344000"),
            Row(last_date="-1616695944000")
        ]
        schema = ["last_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(last_date=date(1918, 10, 9)),
            Row(last_date=date(1918, 10, 9)),
            Row(last_date=date(1918, 10, 9))
        ]
        expected_schema = ["last_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_unix_without_old_type_with_float_unix(self):
        data = [
            Row(last_date="1616688744.123"),
            Row(last_date="1616692344.456"),
            Row(last_date="1616695944.789")
        ]
        schema = ["last_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(last_date=date(1970, 1, 19)),
            Row(last_date=date(1970, 1, 19)),
            Row(last_date=date(1970, 1, 19))
        ]
        expected_schema = ["last_date"]        
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_to_date_with_old_type(self):
        data = [
            Row(last_date="2024/01/01"),
            Row(last_date="2024/05/20"),
            Row(last_date="2024/12/31")
        ]
        schema = ["last_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date", "old_type": "yyyy/mm/dd"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(last_date=date(2024, 1, 1)),
            Row(last_date=date(2024, 5, 20)),
            Row(last_date=date(2024, 12, 31))
        ]
        expected_schema = ["last_date"]       
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_to_date_without_old_type(self):
        data = [
            Row(last_date="2024/01/01"),
            Row(last_date="2024/05/20"),
            Row(last_date="2024/12/31")
        ]
        schema = ["last_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(last_date=date(2024, 1, 1)),
            Row(last_date=date(2024, 5, 20)),
            Row(last_date=date(2024, 12, 31))
        ]
        expected_schema = ["last_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])

    def test_cast_to_date_with_hms(self):
        data = [
            Row(last_date="Mon, Jan 3, 2022 08:09:05"),
            Row(last_date="Tue, Jan 4, 2022 08:09:05")
        ]
        schema = ["last_date"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [{"columns": ["last_date"], "new_type": "date", "old_type": "ddd, MMM DD, YYYY HH:MM:SS"}]
        }
        df_cast = self.cast.execute(df, parameters, self.spark)
        expected_data = [
            Row(last_date=date(2022, 1, 3)),
            Row(last_date=date(2022, 1, 4))
        ]
        expected_schema = ["last_date"]
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_cast.dtypes, expected_df.dtypes)
        self.assertEqual(df_cast.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_cast.collect()], [row.asDict() for row in expected_df.collect()])
