import unittest
from spark_server.pipeline.pytool import *
from pyspark.sql import SparkSession

class TestPyTool(unittest.TestCase):
    # creating the instance of the class PyTool
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestPyTool").config("spark.jars.packages", "org.postgresql:postgresql:42.7.1").getOrCreate()
        cls.pytool = PyTool()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_execute(self):
        parameters = {"spark_code": """job = JobArguments.get()\nprint("job",job)"""}
        dataframes = {}
        self.pytool.execute(dataframes, parameters, self.spark, conf={})
        self.assertEqual({}, dataframes)

    def test_execute_with_method(self):
        parameters = {"spark_code": """import pandas as pd\ndef sample(a):\n    data = [['Alice', 25, 'New York'],['Bob', 30, 'Los Angeles'],['Charlie', 35, 'Chicago']]\n    df = pd.DataFrame(data, columns=['Name', 'Age', 'City'])\n    print("df",DataframeInformation.get())\n    DataframeInformation.create(id="1234", alias="students", dataframe=df)\n    print("df",DataframeInformation.get())\n    print("sampleWord",a, df)\nsample("utkarsh")"""}
        dataframes = {}
        self.pytool.execute(dataframes, parameters, self.spark, conf={})
        self.assertTrue("1234" in dataframes.keys())
