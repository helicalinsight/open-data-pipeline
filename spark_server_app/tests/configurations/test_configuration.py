import unittest
from spark_server.configurations.configuration import Configuration
from unittest.mock import patch
import yaml
import pytest
from spark_server.exceptions.exceptions import *


class TestConfiguration(unittest.TestCase):

    def test_get(self):
        actual_result = Configuration().get("65cb43f2007a5f38718b9d6c")
        expected_result = {'__read_tables__0': {'table': 'example_table'}}
        self.assertEqual(actual_result, expected_result)

    def test_get_spark_conf(self):
        actual_result = Configuration().get("65cb43f2007a5f38718b9111")
        expected_result = {'--conf': {'spark.executor.memory': '4g'}}
        self.assertEqual(actual_result, expected_result)
