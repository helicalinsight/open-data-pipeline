import unittest
from spark_server.pipeline.combiner import *
from pyspark.sql import SparkSession, Row


class TestCombiner(unittest.TestCase):
    # creating the instance of the class Combiner
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestCombiner").getOrCreate()
        cls.union = Union()
        cls.join = Join()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
        
    def test_union(self):
        schema = ["id", "name", "age"]
        data_1 = [
            Row(id=1, name="John", age=25),
            Row(id=2, name="Alice", age=30),
            Row(id=3, name="Bob", age=22)
        ]
        df1 = self.spark.createDataFrame(data_1, schema=schema)
        data_2 = [
            Row(id=4, name="Jen", age=20),
            Row(id=5, name="Alex", age=35)
        ]
        df2 = self.spark.createDataFrame(data_2, schema=schema)
        dataframes = {"65cca96e00df89a55668f1af": {"df": df1, "alias": "student1"}, "65cca96e00df89a55668f1bf": {"df": df2, "alias": "student2"}}
        parameters = {'groups': [{'columns': None}], 'df_id': ['65cca96e00df89a55668f1af', '65cca96e00df89a55668f1bf'], 'file_names': ['Students', 'Students_1'], 'file_id': None}
        output = {
            "df_id": "65cca96e00df89a55668f1cf"
        }
        dataframes = self.union.execute(dataframes, parameters, output, self.spark)
        self.assertEqual(dataframes["65cca96e00df89a55668f1cf"]["df"].count(), 5)

    def test_join(self):
        schema_1 = ["id", "name", "dept_id"]
        data_1 = [
            Row(id=1, name="John", dept_id=101),
            Row(id=2, name="Alice", dept_id=102),
            Row(id=3, name="Bob", dept_id=103)
        ]
        df1 = self.spark.createDataFrame(data_1, schema=schema_1)
        schema_2 = ["dept_id", "dept_name"]
        data_2 = [
            Row(dept_id=101, dept_name="HR"),
            Row(dept_id=102, dept_name="Finance"),
            Row(dept_id=103, dept_name="Marketing")
        ]
        df2 = self.spark.createDataFrame(data_2, schema=schema_2)
        dataframes = {"65cca96e00df89a55668f3af": {"df": df1, "alias": "students"}, "65cca96e00df89a55668f3bf": {"df": df2, "alias": "dept"}}
        parameters = {
            "groups": [
                {
                    "join_type": "inner",
                    "left_on": [
                        "dept_id"
                    ],
                    "right_on": [
                        "dept_id"
                    ]
                }
            ],
            "df_id": [
              "65cca96e00df89a55668f3af",
              "65cca96e00df89a55668f3bf"
            ],
            "file_names": [
              "employees",
              "departments"
            ]
        }
        output = {
            "df_id": "65cca96e00df89a55668f3cf"
        }
        dataframes = self.join.execute(dataframes, parameters, output, self.spark)
        self.assertEqual(dataframes["65cca96e00df89a55668f3cf"]["df"].columns, ["id", "name", "dept_id_employees",
                                                                          "dept_id_departments", "dept_name"])

        schema_2 = ["department_id", "dept_name"]
        data_2 = [
            Row(department_id=101, dept_name="HR"),
            Row(department_id=102, dept_name="Finance"),
            Row(department_id=103, dept_name="Marketing")
        ]
        df2 = self.spark.createDataFrame(data_2, schema=schema_2)
        dataframes = {"65cca96e00df89a55668f3af": {"df": df1, "alias": "students"}, "65cca96e00df89a55668f3df": {"df": df2, "alias": "dept"}}
        parameters = {
            "groups": [
                {
                    "join_type": "inner",
                    "left_on": [
                        "dept_id"
                    ],
                    "right_on": [
                        "department_id"
                    ]
                }
            ],
            "df_id": [
              "65cca96e00df89a55668f3af",
              "65cca96e00df89a55668f3df"
            ],
            "file_names": [
              "employees",
              "departments"
            ]
        }
        output = {
            "df_id": "65cca96e00df89a55668f3ef"
        }
        dataframes = self.join.execute(dataframes, parameters, output, self.spark)
        self.assertEqual(dataframes["65cca96e00df89a55668f3ef"]["df"].columns, ["id", "name", "dept_id",
                                                                          "department_id", "dept_name"])

        schema_3 = ["id", "dept_id", "dept_name"]
        data_3 = [
            Row(id=1, dept_id=101, dept_name="HR"),
            Row(id=2, dept_id=102, dept_name="Finance"),
            Row(id=4, dept_id=103, dept_name="Marketing")
        ]
        df3 = self.spark.createDataFrame(data_3, schema=schema_3)
        dataframes = {"65cca96e00df89a55668f3af": {"df": df1, "alias": "students"}, "65cca96e00df89a55668f3ff": {"df": df3, "alias": "dept1"}}
        parameters = {
            "groups": [
                {
                    "join_type": "inner",
                    "left_on": [
                        "id",
                        "dept_id"
                    ],
                    "right_on": [
                        "id",
                        "dept_id"
                    ]
                }
            ],
            "df_id": [
              "65cca96e00df89a55668f3af",
              "65cca96e00df89a55668f3ff"
            ],
            "file_names": [
              "employees",
              "departments"
            ]
        }
        output = {
            "df_id": "65cca96e00df89a55668f4ff"
        }

        dataframes = self.join.execute(dataframes, parameters, output, self.spark)
        self.assertEqual(dataframes["65cca96e00df89a55668f4ff"]["df"].columns,
                         ["id_employees", "name", "dept_id_employees", "id_departments", "dept_id_departments",
                          "dept_name"])


if __name__ == "__main__":
    unittest.main()
