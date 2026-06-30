import unittest
import pytest
from spark_server.pipeline.transformer import Aggregations
from pyspark.sql import SparkSession, Row
import os


#@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestTransformerAggregations(unittest.TestCase):
    # creating the instance of the class Transformer 
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestTransformerAggregations").getOrCreate()
        cls.aggregations = Aggregations()

    def test_aggregation_sum(self):
        data = [
            Row(category='A', subcategory='X', value1=10, value2=5),
            Row(category='B', subcategory='Y', value1=20, value2=10),
            Row(category='C', subcategory='Z', value1=30, value2=15),
            Row(category='A', subcategory='X', value1=40, value2=20),
            Row(category='B', subcategory='Y', value1=50, value2=25),
            Row(category='C', subcategory='Z', value1=60, value2=30),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45),
        ]
        schema = ["category", "subcategory", "value1", "value2"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": ["sum_value1", "sum_value2"],
                    "agg": ["sum"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }
        df_aggregations = self.aggregations.execute(df, parameters, self.spark)
        expected_data = [
            Row(category='A', subcategory='X', value1=50, value2=25),
            Row(category='B', subcategory='Y', value1=70, value2=35),
            Row(category='C', subcategory='Z', value1=90, value2=45),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45)
        ]
        expected_schema = ['category', 'subcategory', 'sum_value1', 'sum_value2']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_aggregations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_aggregations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_aggregations_sum_without_groupby(self):
        data = [
            Row(category='A', subcategory='X', value1=10, value2=5),
            Row(category='B', subcategory='Y', value1=20, value2=10),
            Row(category='C', subcategory='Z', value1=30, value2=15),
            Row(category='A', subcategory='X', value1=40, value2=20),
            Row(category='B', subcategory='Y', value1=50, value2=25),
            Row(category='C', subcategory='Z', value1=60, value2=30),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45),
        ]
        schema = ["category", "subcategory", "value1", "value2"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns":  ["sum_value1", "sum_value2"],
                    "agg": ["sum"],
                    "group_by": [],
                }
            ]
        }
        df_aggregations = self.aggregations.execute(df, parameters, self.spark)
        df_aggregations.show()
        expected_data = [
            Row(category='A', subcategory='X', value1=10, value2=5, sum_value1=450, sum_value2=225),
            Row(category='B', subcategory='Y', value1=20, value2=10, sum_value1=450, sum_value2=225),
            Row(category='C', subcategory='Z', value1=30, value2=15, sum_value1=450, sum_value2=225),
            Row(category='A', subcategory='X', value1=40, value2=20, sum_value1=450, sum_value2=225),
            Row(category='B', subcategory='Y', value1=50, value2=25, sum_value1=450, sum_value2=225),
            Row(category='C', subcategory='Z', value1=60, value2=30, sum_value1=450, sum_value2=225),
            Row(category='A', subcategory='K', value1=70, value2=35, sum_value1=450, sum_value2=225),
            Row(category='B', subcategory='K', value1=80, value2=40, sum_value1=450, sum_value2=225),
            Row(category='C', subcategory='K', value1=90, value2=45, sum_value1=450, sum_value2=225),
        ]
        expected_schema = ['category', 'subcategory', 'value1', 'value2', 'sum_value1', 'sum_value2']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_aggregations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_aggregations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_aggregation_mean(self):
        data = [
            Row(category='A', subcategory='X', value1=10, value2=5),
            Row(category='B', subcategory='Y', value1=20, value2=10),
            Row(category='C', subcategory='Z', value1=30, value2=15),
            Row(category='A', subcategory='X', value1=40, value2=20),
            Row(category='B', subcategory='Y', value1=50, value2=25),
            Row(category='C', subcategory='Z', value1=60, value2=30),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45),
        ]
        schema = ["category", "subcategory", "value1", "value2"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns":  ["mean_value1", "mean_value2"],
                    "agg": ["mean"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }
        df_aggregations = self.aggregations.execute(df, parameters, self.spark)
        expected_data = [
                Row(category='A', subcategory='X', mean_value1=25.0, mean_value2=12.5),
                Row(category='B', subcategory='Y', mean_value1=35.0, mean_value2=17.5),
                Row(category='C', subcategory='Z', mean_value1=45.0, mean_value2=22.5),
                Row(category='A', subcategory='K', mean_value1=70.0, mean_value2=35.0),
                Row(category='B', subcategory='K', mean_value1=80.0, mean_value2=40.0),
                Row(category='C', subcategory='K', mean_value1=90.0, mean_value2=45.0)
            ]
        expected_schema = ['category', 'subcategory', 'mean_value1', 'mean_value2']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_aggregations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_aggregations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_aggregation_count(self):
        data = [
            Row(category='A', subcategory='X', value1=10, value2=5),
            Row(category='B', subcategory='Y', value1=20, value2=10),
            Row(category='C', subcategory='Z', value1=30, value2=15),
            Row(category='A', subcategory='X', value1=40, value2=20),
            Row(category='B', subcategory='Y', value1=50, value2=25),
            Row(category='C', subcategory='Z', value1=60, value2=30),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45),
        ]
        schema = ["category", "subcategory", "value1", "value2"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns":  ["count_value1", "count_value2"],
                    "agg": ["count"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }
        df_aggregations = self.aggregations.execute(df, parameters, self.spark)
        expected_data = [                
                Row(category='A', subcategory='X', count_value1=2, count_value2=2),
                Row(category='B', subcategory='Y', count_value1=2, count_value2=2),
                Row(category='C', subcategory='Z', count_value1=2, count_value2=2),
                Row(category='A', subcategory='K', count_value1=1, count_value2=1),
                Row(category='B', subcategory='K', count_value1=1, count_value2=1),                
                Row(category='C', subcategory='K', count_value1=1, count_value2=1)               
            ]
        expected_schema = ['category', 'subcategory', 'count_value1', 'count_value2']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_aggregations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_aggregations.collect()], [row.asDict() for row in expected_df.collect()])

    @pytest.mark.skip("Median is not working")
    def test_aggregation_median(self):
        # median is not supported in pyspark 3.3.3 and  approxQuantile is also not working
        # tried to use percentile_approx the values are differing from pandas
        data = [
            Row(category='A', subcategory='X', value1=10, value2=5),
            Row(category='B', subcategory='Y', value1=20, value2=10),
            Row(category='C', subcategory='Z', value1=30, value2=15),
            Row(category='A', subcategory='X', value1=40, value2=20),
            Row(category='B', subcategory='Y', value1=50, value2=25),
            Row(category='C', subcategory='Z', value1=60, value2=30),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45),
        ]
        schema = ["category", "subcategory", "value1", "value2"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns":  ["median_value1", "median_value2"],
                    "agg": ["median"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }
        df_aggregations = self.aggregations.execute(df, parameters, self.spark)
        df_aggregations.show()
        expected_data = [
                Row(category='A', subcategory='K', median_value1=70.0, median_value2=35.0),
                Row(category='A', subcategory='X', median_value1=25.0, median_value2=12.5),
                Row(category='B', subcategory='K', median_value1=80.0, median_value2=40.0),
                Row(category='B', subcategory='Y', median_value1=35.0, median_value2=17.5),
                Row(category='C', subcategory='K', median_value1=90.0, median_value2=45.0),
                Row(category='C', subcategory='Z', median_value1=45.0, median_value2=22.5)
            ]
        expected_schema = ['category', 'subcategory', 'median_value1', 'median_value2']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_aggregations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_aggregations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_aggregation_std(self):
        # column name is std_value1 in pandas and stddev is spark
        data = [
            Row(category='A', subcategory='X', value1=10, value2=5),
            Row(category='B', subcategory='Y', value1=20, value2=10),
            Row(category='C', subcategory='Z', value1=30, value2=15),
            Row(category='A', subcategory='X', value1=40, value2=20),
            Row(category='B', subcategory='Y', value1=50, value2=25),
            Row(category='C', subcategory='Z', value1=60, value2=30),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45),
        ]
        schema = ["category", "subcategory", "value1", "value2"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns":  ["std_value1", "std_value2"],
                    "agg": ["stddev"],
                    "group_by": ["category"],
                }
            ]
        }
        df_aggregations = self.aggregations.execute(df, parameters, self.spark)
        expected_data = [
                Row(category='A', std_value1=30.0, std_value2=15.0),
                Row(category='B', std_value1=30.0, std_value2=15.0),
                Row(category='C', std_value1=30.0, std_value2=15.0)

            ]
        expected_schema = ['category', 'std_value1', 'std_value2']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_aggregations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_aggregations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_aggregation_min_max(self):
        data = [
            Row(category='A', subcategory='X', value1=10, value2=5),
            Row(category='B', subcategory='Y', value1=20, value2=10),
            Row(category='C', subcategory='Z', value1=30, value2=15),
            Row(category='A', subcategory='X', value1=40, value2=20),
            Row(category='B', subcategory='Y', value1=50, value2=25),
            Row(category='C', subcategory='Z', value1=60, value2=30),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45),
        ]
        schema = ["category", "subcategory", "value1", "value2"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns":  ["min_value1", "max_value1", "min_value2", "max_value2"],
                    "agg": ["min", "max"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }
        df_aggregations = self.aggregations.execute(df, parameters, self.spark)
        expected_data = [
                Row(category='A', subcategory='X', min_value1=10, max_value1=40, min_value2=5, max_value2=20),
                Row(category='B', subcategory='Y', min_value1=20, max_value1=50, min_value2=10, max_value2=25),
                Row(category='C', subcategory='Z', min_value1=30, max_value1=60, min_value2=15, max_value2=30),
                Row(category='A', subcategory='K', min_value1=70, max_value1=70, min_value2=35, max_value2=35),
                Row(category='B', subcategory='K', min_value1=80, max_value1=80, min_value2=40, max_value2=40),
                Row(category='C', subcategory='K', min_value1=90, max_value1=90, min_value2=45, max_value2=45)
            ]
        expected_schema = ['category', 'subcategory','min_value1', 'max_value1', 'min_value2', 'max_value2']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_aggregations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_aggregations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_aggregation_variance(self):
        data = [
            Row(category='A', subcategory='X', value1=10, value2=5),
            Row(category='B', subcategory='Y', value1=20, value2=10),
            Row(category='C', subcategory='Z', value1=30, value2=15),
            Row(category='A', subcategory='X', value1=40, value2=20),
            Row(category='B', subcategory='Y', value1=50, value2=25),
            Row(category='C', subcategory='Z', value1=60, value2=30),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45),
        ]
        schema = ["category", "subcategory", "value1", "value2"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": ["var_value1", "var_value2"],
                    "agg": ["variance"],
                    "group_by": ["category"],
                }
            ]
        }
        df_aggregations = self.aggregations.execute(df, parameters, self.spark)
        expected_data = [
                Row(category='A', var_value1=900.0, var_value2=225.0),
                Row(category='B', var_value1=900.0, var_value2=225.0),
                Row(category='C', var_value1=900.0, var_value2=225.0)
            ]
        expected_schema = ['category', 'var_value1','var_value2']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_aggregations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_aggregations.collect()], [row.asDict() for row in expected_df.collect()])

    def test_aggregation_distinct(self):
        data = [
            Row(category='A', subcategory='X', value1=10, value2=5),
            Row(category='B', subcategory='Y', value1=20, value2=10),
            Row(category='C', subcategory='Z', value1=30, value2=15),
            Row(category='A', subcategory='X', value1=40, value2=20),
            Row(category='B', subcategory='Y', value1=50, value2=25),
            Row(category='C', subcategory='Z', value1=60, value2=30),
            Row(category='A', subcategory='K', value1=70, value2=35),
            Row(category='B', subcategory='K', value1=80, value2=40),
            Row(category='C', subcategory='K', value1=90, value2=45),
        ]
        schema = ["category", "subcategory", "value1", "value2"]
        df = self.spark.createDataFrame(data, schema=schema)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": ["distinct_value1", "distinct_value2"],
                    "agg": ["distinct"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }
        df_aggregations = self.aggregations.execute(df, parameters, self.spark)
        expected_data = [
                Row(category='A', subcategory='X', distinct_value1=2, distinct_value2=2),
                Row(category='B', subcategory='Y', distinct_value1=2, distinct_value2=2),
                Row(category='A', subcategory='K', distinct_value1=1, distinct_value2=1),
                Row(category='B', subcategory='K', distinct_value1=1, distinct_value2=1),
                Row(category='C', subcategory='Z', distinct_value1=2, distinct_value2=2),
                Row(category='C', subcategory='K', distinct_value1=1, distinct_value2=1)
            ]
        expected_schema =  ['category', 'subcategory', 'distinct_value1', 'distinct_value2']
        expected_df = self.spark.createDataFrame(expected_data, schema=expected_schema)
        self.assertEqual(df_aggregations.columns, expected_schema)
        self.assertEqual([row.asDict() for row in df_aggregations.collect()], [row.asDict() for row in expected_df.collect()])


if __name__ == '__main__':
    unittest.main()
