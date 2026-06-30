import unittest
import main
from unittest.mock import patch
import yaml
import os
from spark_server.logger.logger import Logger, logger
from spark_server.exceptions.exceptions import *
from pyspark.sql import SparkSession
from pyspark import SparkConf


class TestMain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spark_conf = SparkConf()
        cls.spark = spark_conf.set("spark.jars.packages", "org.postgresql:postgresql:42.7.1,com.crealytics:spark-excel_2.12:3.3.3_0.20.3")
    
    @patch('sys.argv', ['main.py', '65cb43f2007a5f38718b9d6a', '6619156aa5f4c5c1b01e4d07', '65cb43f2007a5f38718b9d6c', '456', 'pipeline'])
    def test_main_with_arguments(self):
        with patch('main.main') as mocked_main:
            main.main(self.spark)
            mocked_main.assert_called_once()

    #@patch('sys.argv', ['main.py', '66597475aea87247ea567115', '6641ad931a3ba5058c56af19'])
    @patch('sys.argv', ['main.py', '665e937aaea87247ea567131', '6641ad931a3ba5058c56af19', '665ded10aea87247ea56712b', '456', 'pipeline'])
    def test_main_file(self):
        output = main.main(self.spark)
        self.assertTrue(output)
        #self.assertIsInstance(yaml.safe_load(output), list)

    #@patch('sys.argv', ['main.py', '6659a80eaea87247ea56711b', '6641ad931a3ba5058c56af19'])
    @patch('sys.argv', ['main.py', '665e937aaea87247ea567131', '6641ad931a3ba5058c56af19', '65cb43f2007a5f38718b9d6c', '456', 'pipeline'])
    def test_main_db(self):
        output = main.main(self.spark)
        self.assertTrue(output)
        #self.assertIsInstance(yaml.safe_load(output), list)

    #@patch('sys.argv', ['main.py', '6659a80eaea87247ea56711b', '6641ad931a3ba5058c56af19'])
    @patch('sys.argv', ['main.py', '665e937aaea87247ea567131', '6641ad931a3ba5058c56af19', '65cb43f2007a5f38718b9d6c', '456', 'code'])
    def test_main_code(self):
        output = main.main(self.spark)
        self.assertTrue(output)
        #self.assertIsInstance(yaml.safe_load(output), list)

    @patch('sys.argv', ['main.py', '665e937aaea87247ea567131', '6641ad931a3ba5058c56af19', '65cb43f2007a5f38718b9d6d', '456', 'code'])
    def test_main_code_with_method(self):
        output = main.main(self.spark)
        self.assertTrue(output)
        #self.assertIsInstance(yaml.safe_load(output), list)

    @patch('sys.argv', ['main.py', '665e937aaea87247ea567131', '6641ad931a3ba5058c56af19', '65cb43f2007a5f38718b9d5e', '456', 'code'])
    def test_main_code_with_job_args(self):
        output = main.main(self.spark)
        self.assertTrue(output)

    @patch('sys.argv', ['main.py'])
    def test_main_missing_arguments(self):
        with self.assertRaises(SystemExit) as cm:
            main.main(self.spark)
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
