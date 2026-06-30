import unittest
import pandas
import pytest
import pyspark.pandas as spark_pandas
import pyspark

# from spark_server.helper.helper import *

class TestJobArguments(unittest.TestCase):
    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_get(self):
        config_dict = {"__read_file__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).get()
        self.assertEqual(config_dict, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_get_with_key(self):
        config_dict = {"__read_file__": {"mode": "append"}, "__read_table__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).get("__read_table__")
        expected_result = {"__read_table__": {"mode": "append"}}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_update(self):
        config_dict = {"__read_file__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).update("__config__", "true")
        expected_result = {"__read_file__": {"mode": "append"}, "__config__":"true"}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_update_existing_data(self):
        config_dict = {"__read_file__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).update("__read_file__", {"mode": "overwrite"})
        expected_result = {"__read_file__": {"mode": "overwrite"}}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_create(self):
        config_dict = {}
        actual_result = JobArguments(config_dict).create("config", "true")
        expected_result = {"config": "true"}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_create_if_config_key_already_present(self):
        config_dict = {"__config__":"true"}
        with pytest.raises(Exception) as test:
            JobArguments(config_dict).create("__config__", "false")
        self.assertEqual("The key __config__ already exists, please use a different key.", str(test.value))

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_delete(self):
        config_dict = {"__read_file__": {"mode": "append"}, "__config__":"true"}
        actual_result = JobArguments(config_dict).delete("__config__")
        expected_result = {"__read_file__": {"mode": "append"}}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_delete_with_non_existing_key(self):
        config_dict = {"__read_file__": {"mode": "append"}, "__config__":"true"}
        with pytest.raises(Exception) as test:
            JobArguments(config_dict).delete("__config")
        self.assertEqual("'__config'", str(test.value))

class TestDataframeInformation(unittest.TestCase):
    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_get_without_id_and_alias(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        actual_result = DataframeInformation(config_dict).get()
        expected_result = config_dict
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_get_with_id(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        actual_result = DataframeInformation(config_dict).get(id="11223344")
        expected_result = {"11223344": {"df": df, "alias": "students"}}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_get_with_alias(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        actual_result = DataframeInformation(config_dict).get(alias="teachers")
        expected_result = {"55667788": {"df": df, "alias": "teachers"}}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_get_with_non_existing_alias(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        with pytest.raises(Exception) as test:
            DataframeInformation(config_dict).get(alias="course")
        self.assertEqual("Alias name course is not found !", str(test.value))

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_get_with_non_existing_id(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        with pytest.raises(Exception) as test:
            DataframeInformation(config_dict).get(id="23")
        self.assertEqual("'23'", str(test.value))

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_create(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        actual_result = DataframeInformation().create(id="123456", alias="sample", dataframe=df)
        expected_result = {"123456": {"df": df, "alias": "sample"}}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_create_with_existing_id(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        with pytest.raises(Exception) as test:
            DataframeInformation(config_dict).create(id="11223344", alias="sample", dataframe=df)
        self.assertEqual("The Id '11223344' already exists, please use a different Id.", str(test.value))

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_create_with_existing_alias(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        with pytest.raises(Exception) as test:
            DataframeInformation(config_dict).create(id="11223341", alias="students", dataframe=df)
        self.assertEqual("The alias 'students' already exists, please use a different alias.", str(test.value))

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_update(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        data1 = {'name': ["arunraj", "ram"], 'age': [30, 40]}
        df1 = pandas.DataFrame(data1)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        actual_result = DataframeInformation(config_dict).update(id="11223344", alias="students", dataframe=df1)
        expected_result = {"11223344": {"df": df1, "alias": "students"}}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_delete_with_alias(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        actual_result = DataframeInformation(config_dict).delete(alias="students")
        expected_result = {"55667788": {"df": df, "alias": "teachers"}}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_delete_with_id(self):
        data = {'name': ["arun", "ram"], 'age': [3, 4]}
        df = pandas.DataFrame(data)
        config_dict = {"11223344": {"df": df, "alias": "students"}, 
                       "55667788": {"df": df, "alias": "teachers"}}
        actual_result = DataframeInformation(config_dict).delete(id="11223344")
        expected_result = {"55667788": {"df": df, "alias": "teachers"}}
        self.assertEqual(expected_result, actual_result)

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_convert_to_pandas(self):
        data = {'id': [1,2,3] , 'name': ["John", "Alice", "Bob"], 'age': [25, 30, 22]}
        df = pandas.DataFrame(data)
        df = spark_pandas.from_pandas(df)
        actual_result = DataframeInformation().convert_to_pandas(df)
        data = {'id': [1,2,3] , 'name': ["John", "Alice", "Bob"], 'age': [25, 30, 22]}
        expected_result = pandas.DataFrame(data)
        self.assertTrue(expected_result.equals(actual_result))
        self.assertTrue(isinstance(actual_result, pandas.DataFrame))

    @pytest.mark.skip(reason="helper should be tested in inbuilt modules")
    def test_convert_to_spark(self):
        data = {'id': [1,2,3] , 'name': ["John", "Alice", "Bob"], 'age': [25, 30, 22]}
        df = pandas.DataFrame(data)
        actual_result = DataframeInformation().convert_to_spark(df)
        self.assertTrue(isinstance(actual_result, pyspark.pandas.frame.DataFrame))
