import unittest
import pandas as pd
import pytest
import os
from pyspark.sql import SparkSession
from helper.helper import create_file_operations, create_dataframe_operations, JobArguments, Connection
class TestJobArguments(unittest.TestCase):
    def test_get(self):
        config_dict = {"__read_file__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).get()
        self.assertEqual(config_dict, actual_result)

    def test_get_with_key(self):
        config_dict = {"__read_file__": {"mode": "append"}, "__read_table__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).get("__read_table__")
        expected_result = {"__read_table__": {"mode": "append"}}
        self.assertEqual(expected_result, actual_result)

    def test_update(self):
        config_dict = {"__read_file__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).update("__config__", "true")
        expected_result = {"__read_file__": {"mode": "append"}, "__config__":"true"}
        self.assertEqual(expected_result, actual_result)

    def test_update_existing_data(self):
        config_dict = {"__read_file__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).update("__read_file__", {"mode": "overwrite"})
        expected_result = {"__read_file__": {"mode": "overwrite"}}
        self.assertEqual(expected_result, actual_result)

    def test_create(self):
        config_dict = {}
        actual_result = JobArguments(config_dict).create("config", "true")
        expected_result = {"config": "true"}
        self.assertEqual(expected_result, actual_result)

    def test_create_if_config_key_already_present(self):
        config_dict = {"__config__":"true"}
        with pytest.raises(Exception) as test:
            JobArguments(config_dict).create("__config__", "false")
        self.assertEqual("The key __config__ already exists, please use a different key.", str(test.value))

    def test_delete(self):
        config_dict = {"__read_file__": {"mode": "append"}, "__config__":"true"}
        actual_result = JobArguments(config_dict).delete("__config__")
        expected_result = {"__read_file__": {"mode": "append"}}
        self.assertEqual(expected_result, actual_result)

    def test_delete_with_non_existing_key(self):
        config_dict = {"__read_file__": {"mode": "append"}, "__config__":"true"}
        with pytest.raises(Exception) as test:
            JobArguments(config_dict).delete("__config")
        self.assertEqual("'__config'", str(test.value))


class TestDltReadOrWriteFiles(unittest.TestCase):
    """Test cases for DLT engine - pandas only functionality"""
    
    def setUp(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
        self.basepath = os.path.join(project_root, 'hadoop_local')
        
        # Create DLT engine instance (pandas-only)
        self.dlt_file_ops = create_file_operations("dlt", user_id="20240710", basepath=self.basepath)
        
        # Test data
        self.pandas_df = pd.DataFrame({'Name': ['Alice', 'Bob'], 'Age': [25, 30]})
        self.json_data = {"name": "Alice", "age": 23, "class": "BE"}

    def test_write_csv_file_pandas(self):
        """Test writing CSV file with pandas engine in DLT mode"""
        actual_result = self.dlt_file_ops.write_csv(engine="pandas", file_name="students_write.csv", dataframe=self.pandas_df)
        self.assertTrue(actual_result)

    def test_write_csv_file_pandas_with_kwargs(self):
        """Test writing CSV file with pandas engine and custom parameters"""
        config = {"sep": "|"}
        actual_result = self.dlt_file_ops.write_csv(engine="pandas", file_name="students_write_pipe.csv", dataframe=self.pandas_df, **config)
        self.assertTrue(actual_result)

    def test_write_excel_file_pandas(self):
        """Test writing Excel file with pandas engine in DLT mode"""
        actual_result = self.dlt_file_ops.write_excel(engine="pandas", file_name="students.xlsx", dataframe=self.pandas_df)
        self.assertTrue(actual_result)

    def test_read_csv_pandas(self):
        """Test reading CSV file with pandas engine in DLT mode"""
        # First write the file
        self.dlt_file_ops.write_csv(engine="pandas", file_name="students_read.csv", dataframe=self.pandas_df)
        
        # Then read it back
        actual_result = self.dlt_file_ops.read_csv(engine="pandas", file_name="students_read.csv")
        expected_result = [['Alice', 25], ['Bob', 30]]
        self.assertEqual(expected_result, actual_result.values.tolist())

    def test_read_excel_pandas(self):
        """Test reading Excel file with pandas engine in DLT mode"""
        # First write the file
        self.dlt_file_ops.write_excel(engine="pandas", file_name="students_read.xlsx", dataframe=self.pandas_df)
        
        # Then read it back
        actual_result = self.dlt_file_ops.read_excel(engine="pandas", file_name="students_read.xlsx")
        expected_result = [['Alice', 25], ['Bob', 30]]
        self.assertEqual(expected_result, actual_result.values.tolist())

    def test_read_excel_pandas_with_kwargs(self):
        """Test reading Excel file with pandas engine and custom parameters"""
        # Create a larger dataframe for this test
        larger_df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'], 
            'Age': [25, 30, 35],
            'City': ['NYC', 'LA', 'Chicago']
        })
        
        # First write the larger file
        self.dlt_file_ops.write_excel(engine="pandas", file_name="students_large.xlsx", dataframe=larger_df)
        
        # Read with custom parameters - now we have 3 columns
        config = {
            "sheet_name": "Sheet1",
            "skiprows": 1,  # Skip header row
            "nrows": 1      # Read only 1 data row
        }
        actual_result = self.dlt_file_ops.read_excel(engine="pandas", file_name="students_large.xlsx", **config)
        expected_result = [['Bob', 30, 'LA']]
        self.assertEqual(expected_result, actual_result.values.tolist())

    def test_read_json(self):
        """Test reading JSON file (engine-independent)"""
        self.dlt_file_ops.write_json(file_name="students.json", json_data=self.json_data)
        actual_result = self.dlt_file_ops.read_json(file_name="students.json")
        expected_result = {'name': 'Alice', 'age': 23, 'class': 'BE'}
        self.assertEqual(actual_result, expected_result)

    def test_write_json(self):
        """Test writing JSON file (engine-independent)"""
        actual_result = self.dlt_file_ops.write_json(file_name="students_data.json", json_data=self.json_data)
        self.assertTrue(actual_result)

    def test_write_csv_file_spark_blocked(self):
        """Test that spark engine is blocked in DLT mode"""
        with pytest.raises(Exception) as test_func:
            self.dlt_file_ops.write_csv(engine="spark", file_name="students.csv", dataframe=self.pandas_df)
        self.assertEqual("Spark engine is not supported in DLT mode. Use engine='pandas'", str(test_func.value))

    def test_read_csv_spark_blocked(self):
        """Test that spark engine is blocked for reading CSV in DLT mode"""
        with pytest.raises(Exception) as test_func:
            self.dlt_file_ops.read_csv(engine="spark", file_name="students.csv")
        self.assertEqual("Spark engine is not supported in DLT mode. Use engine='pandas'", str(test_func.value))

    def test_write_excel_spark_blocked(self):
        """Test that spark engine is blocked for writing Excel in DLT mode"""
        with pytest.raises(Exception) as test_func:
            self.dlt_file_ops.write_excel(engine="spark", file_name="students.xlsx", dataframe=self.pandas_df)
        self.assertEqual("Spark engine is not supported in DLT mode. Use engine='pandas'", str(test_func.value))

    def test_read_excel_spark_blocked(self):
        """Test that spark engine is blocked for reading Excel in DLT mode"""
        with pytest.raises(Exception) as test_func:
            self.dlt_file_ops.read_excel(engine="spark", file_name="students.xlsx")
        self.assertEqual("Spark engine is not supported in DLT mode. Use engine='pandas'", str(test_func.value))

    def test_unsupported_engine_error(self):
        """Test that unsupported engines throw proper error"""
        with pytest.raises(Exception) as test_func:
            self.dlt_file_ops.read_csv(engine="dask", file_name="students.csv")
        self.assertEqual("Unsupported engine: dask", str(test_func.value))


class TestDltDataframeInformation(unittest.TestCase):
    """Test cases for DLT DataFrame Information - pandas only functionality"""
    
    def setUp(self):
        # Create DLT engine instance (pandas-only)
        self.dlt_df_ops = create_dataframe_operations("dlt", config_dict={})
        
        # Test data
        self.pandas_df = pd.DataFrame({'name': ["arun", "ram"], 'age': [3, 4]})

    def test_get_without_id_and_alias(self):
        """Test getting all dataframes without specific ID or alias"""
        config_dict = {"11223344": {"df": self.pandas_df, "alias": "students"}, 
                       "55667788": {"df": self.pandas_df, "alias": "teachers"}}
        dlt_df_ops = create_dataframe_operations("dlt", config_dict=config_dict)
        actual_result = dlt_df_ops.get()
        expected_result = config_dict
        self.assertEqual(expected_result, actual_result)

    def test_get_with_id(self):
        """Test getting dataframe by ID"""
        config_dict = {"11223344": {"df": self.pandas_df, "alias": "students"}, 
                       "55667788": {"df": self.pandas_df, "alias": "teachers"}}
        dlt_df_ops = create_dataframe_operations("dlt", config_dict=config_dict)
        actual_result = dlt_df_ops.get(id="11223344")
        self.assertEqual(self.pandas_df.values.tolist(), actual_result.values.tolist())

    def test_get_with_alias(self):
        """Test getting dataframe by alias"""
        config_dict = {"11223344": {"df": self.pandas_df, "alias": "students"}, 
                       "55667788": {"df": self.pandas_df, "alias": "teachers"}}
        dlt_df_ops = create_dataframe_operations("dlt", config_dict=config_dict)
        actual_result = dlt_df_ops.get(alias="teachers")
        self.assertEqual(self.pandas_df.values.tolist(), actual_result.values.tolist())

    def test_get_with_non_existing_alias(self):
        """Test error when getting non-existing alias"""
        config_dict = {"11223344": {"df": self.pandas_df, "alias": "students"}}
        dlt_df_ops = create_dataframe_operations("dlt", config_dict=config_dict)
        with pytest.raises(Exception) as test:
            dlt_df_ops.get(alias="course")
        self.assertEqual("Alias 'course' not found.", str(test.value))

    def test_get_with_non_existing_id(self):
        """Test error when getting non-existing ID"""
        config_dict = {"11223344": {"df": self.pandas_df, "alias": "students"}}
        dlt_df_ops = create_dataframe_operations("dlt", config_dict=config_dict)
        with pytest.raises(Exception) as test:
            dlt_df_ops.get(id="23")
        self.assertEqual("ID '23' not found.", str(test.value))

    def test_create(self):
        """Test creating dataframe entry"""
        actual_result = self.dlt_df_ops.create(dataframe=self.pandas_df, alias="sample", id="123456")
        expected_result = {"source_id": "123456", "alias": "sample"}
        self.assertEqual(expected_result, actual_result)

    def test_update(self):
        """Test updating dataframe entry"""
        # First create an entry
        self.dlt_df_ops.create(dataframe=self.pandas_df, alias="students", id="11223344")
        
        # Create new dataframe to update with
        new_data = {'name': ["arunraj", "ram"], 'age': [30, 40]}
        new_df = pd.DataFrame(new_data)
        
        # Update the entry
        actual_result = self.dlt_df_ops.update(alias="students", dataframe=new_df, id="11223344")
        self.assertTrue(actual_result)

    def test_delete_with_alias(self):
        """Test deleting dataframe entry by alias"""
        # First create an entry
        self.dlt_df_ops.create(dataframe=self.pandas_df, alias="students", id="11223344")
        
        # Delete the entry
        actual_result = self.dlt_df_ops.delete(alias="students")
        self.assertTrue(actual_result)

    def test_delete_with_id_and_alias(self):
        """Test deleting dataframe entry by both ID and alias"""
        # First create an entry
        self.dlt_df_ops.create(dataframe=self.pandas_df, alias="students", id="11223344")
        
        # Delete the entry
        actual_result = self.dlt_df_ops.delete(alias="students", id="11223344")
        self.assertTrue(actual_result)

    def test_convert_to_pandas_with_pandas_dataframe(self):
        """Test converting pandas DataFrame to pandas (should return same)"""
        actual_result = self.dlt_df_ops.convert_to_pandas(self.pandas_df)
        self.assertTrue(self.pandas_df.equals(actual_result))
        self.assertTrue(isinstance(actual_result, pd.DataFrame))

    # DLT ENGINE SPECIFIC TESTS - SPARK CONVERSION SHOULD BE BLOCKED

    def test_convert_to_spark_blocked(self):
        """Test that spark conversion is blocked in DLT mode"""
        with pytest.raises(Exception) as test_func:
            self.dlt_df_ops.convert_to_spark(self.pandas_df)
        self.assertEqual("Spark conversion is not supported in DLT mode. Use Spark engine instead.", str(test_func.value))


class TestDltEngineIndependentClasses(unittest.TestCase):
    """Test cases for engine-independent classes (should work same in DLT)"""
    
    def test_job_arguments_get(self):
        """Test JobArguments.get() functionality"""
        config_dict = {"__read_file__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).get()
        self.assertEqual(config_dict, actual_result)

    def test_job_arguments_get_with_key(self):
        """Test JobArguments.get() with specific key"""
        config_dict = {"__read_file__": {"mode": "append"}, "__read_table__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).get("__read_table__")
        expected_result = {"__read_table__": {"mode": "append"}}
        self.assertEqual(expected_result, actual_result)

    def test_job_arguments_update(self):
        """Test JobArguments.update() functionality"""
        config_dict = {"__read_file__": {"mode": "append"}}
        actual_result = JobArguments(config_dict).update("__config__", "true")
        expected_result = {"__read_file__": {"mode": "append"}, "__config__": "true"}
        self.assertEqual(expected_result, actual_result)

    def test_job_arguments_create(self):
        """Test JobArguments.create() functionality"""
        config_dict = {}
        actual_result = JobArguments(config_dict).create("config", "true")
        expected_result = {"config": "true"}
        self.assertEqual(expected_result, actual_result)

    def test_job_arguments_create_existing_key_error(self):
        """Test JobArguments.create() with existing key throws error"""
        config_dict = {"__config__": "true"}
        with pytest.raises(Exception) as test:
            JobArguments(config_dict).create("__config__", "false")
        self.assertEqual("The key __config__ already exists, please use a different key.", str(test.value))

    def test_job_arguments_delete(self):
        """Test JobArguments.delete() functionality"""
        config_dict = {"__read_file__": {"mode": "append"}, "__config__": "true"}
        actual_result = JobArguments(config_dict).delete("__config__")
        expected_result = {"__read_file__": {"mode": "append"}}
        self.assertEqual(expected_result, actual_result)


class TestDltFactoryFunctions(unittest.TestCase):
    """Test cases for factory functions with DLT engine"""
    
    def test_create_file_operations_dlt(self):
        """Test factory function creates DLT file operations correctly"""
        file_ops = create_file_operations("dlt", user_id="test_user", basepath="/tmp")
        
        # Should be an instance of DltReadOrWriteFiles
        self.assertEqual(file_ops.__class__.__name__, "DltReadOrWriteFiles")
        
        # Test that it works correctly (inheritance pattern)
        # Try a basic operation to ensure it's working
        self.assertEqual(file_ops.create_file_path("test.csv").endswith("test.csv"), True)

    def test_create_dataframe_operations_dlt(self):
        """Test factory function creates DLT dataframe operations correctly"""
        df_ops = create_dataframe_operations("dlt", config_dict={"test": "value"})
        
        # Should be an instance of DltDataframeInformation
        self.assertEqual(df_ops.__class__.__name__, "DltDataframeInformation")
        
        # Test inheritance pattern
        result = df_ops.get()
        self.assertEqual(result, {"test": "value"})

    def test_factory_unsupported_engine_type(self):
        """Test factory functions throw error for unsupported engine types"""
        with pytest.raises(ValueError) as test_func:
            create_file_operations("unsupported", user_id="test", basepath="/tmp")
        self.assertIn("Unsupported engine type", str(test_func.value))
        
        with pytest.raises(ValueError) as test_func:
            create_dataframe_operations("unsupported", config_dict={})
        self.assertIn("Unsupported engine type", str(test_func.value))


class TestDltEngineIntegration(unittest.TestCase):
    """Integration test cases for DLT engine - simulating actual usage"""
    
    def setUp(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
        self.basepath = os.path.join(project_root, 'hadoop_local')
        
        # Simulate DLT engine initialization
        self.connection_id_dict = {}
        self.config = {"test_config": "value"}
        
        # Create DLT instances using factory (as done in dlt_runner.py)
        file_ops = create_file_operations("dlt", user_id="integration_test", basepath=self.basepath)
        df_ops = create_dataframe_operations("dlt", config_dict={})
        
        # Simulate global_scope as exposed to user
        self.global_scope = {
            "Connection": Connection(self.connection_id_dict),
            "JobArguments": JobArguments(self.config),
            "DataframeInformation": df_ops,
            "ReadOrWriteFiles": file_ops
        }

    def test_user_experience_pandas_workflow(self):
        """Test complete user workflow with pandas in DLT engine"""
        # Extract classes from global scope (as user would)
        ReadOrWriteFiles = self.global_scope["ReadOrWriteFiles"]
        DataframeInformation = self.global_scope["DataframeInformation"]
        
        # User creates a pandas DataFrame
        df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
        
        # User writes CSV file
        result = ReadOrWriteFiles.write_csv(engine="pandas", file_name="test_integration.csv", dataframe=df)
        self.assertTrue(result)
        
        #reads CSV file back
        df_read = ReadOrWriteFiles.read_csv(engine="pandas", file_name="test_integration.csv")
        self.assertEqual(df.values.tolist(), df_read.values.tolist())
        
        # stores dataframe in DataframeInformation
        create_result = DataframeInformation.create(dataframe=df_read, alias="test_data")
        self.assertIn("source_id", create_result)
        self.assertEqual(create_result["alias"], "test_data")
        
        #  retrieves dataframe by alias
        retrieved_df = DataframeInformation.get(alias="test_data")
        self.assertEqual(df.values.tolist(), retrieved_df.values.tolist())
        
        #  converts to pandas (should work)
        pandas_df = DataframeInformation.convert_to_pandas(retrieved_df)
        self.assertTrue(isinstance(pandas_df, pd.DataFrame))

    def test_user_experience_spark_blocked(self):
        """Test that user cannot accidentally use spark in DLT engine"""
        ReadOrWriteFiles = self.global_scope["ReadOrWriteFiles"]
        DataframeInformation = self.global_scope["DataframeInformation"]
        
        df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
        
        # User tries to use spark engine - should be blocked
        with pytest.raises(Exception) as test_func:
            ReadOrWriteFiles.read_csv(engine="spark", file_name="test.csv")
        self.assertEqual("Spark engine is not supported in DLT mode. Use engine='pandas'", str(test_func.value))
        
        # User tries to convert to spark - should be blocked
        with pytest.raises(Exception) as test_func:
            DataframeInformation.convert_to_spark(df)
        self.assertEqual("Spark conversion is not supported in DLT mode. Use Spark engine instead.", str(test_func.value))

class SparkDataframeInformation(unittest.TestCase):
    
    def setUp(self):
        # Create Spark engine instance
        self.spark_df_ops = create_dataframe_operations("spark", config_dict={})
        # Create Spark session
        self.spark = SparkSession.builder.appName("UnitTest").getOrCreate()

        # Test data
        self.pandas_df = pd.DataFrame({'name': ["abc", "xyz"], 'age': [20, 25]})
        data = [("abc", 20), ("xyz", 25)]
        columns = ['name', 'age']
        self.spark_df = self.spark.createDataFrame(data, columns)

    def test_spark_convert_to_pandas_from_spark_dataframe(self):
        """Test converting spark dataframe to pandas dataframe"""
        actual_result = self.spark_df_ops.convert_to_pandas(self.spark_df)
        self.assertIsInstance(actual_result, pd.DataFrame)

    def test_spark_convert_to_spark_from_pandas_dataframe(self):
        """Test converting pandas dataframe to spark dataframe"""
        actual_result = self.spark_df_ops.convert_to_pandas(self.pandas_df)
        self.assertTrue(actual_result.__class__.__name__, "DataFrame")