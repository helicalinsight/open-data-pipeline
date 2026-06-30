import unittest
import pytest
import pandas
import numpy
from pandas import Timestamp, Timedelta
import yaml
from src.etl.transfrom.transformations.transfromations import *
from src.exceptions.exception import *
#from opendatapipeline.src.etl.transfrom.transformations.transfromations import *

from ......src.models.connector import MongoConnector
from ......src.models.mongo.mongo_factory import MongoFactory

mongo = MongoConnector()
mongo_client = mongo.client
session = MongoConnector().client._Database__client.start_session()
audit_runs_collection = MongoFactory(mongo_client, "audit_runs", session=session)


class TestTransformer(unittest.TestCase):

    def test_add_columns(self):
        transformer = AddColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["school"], "default": "MNS"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja", "kavya", "bhavya"], "age": [10, 11, 12],
                                            'school': ["MNS", "MNS", "MNS"]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        self.assertEqual(['name', 'age', 'school'], actual_dataframe.columns.tolist())
        expected_message = f"Successfully added column(s) school with default value MNS."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_add_columns_with_audit(self):
        transformer = AddColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        intent_name = "add_column"
        user_info = {
            "user_id": "6619156aa5f4c5c1b01e4d07",
            "chat_id": "66729ec22ee1491c32b05b54"
        }
        transformer = AddColumns(intent_name=intent_name, user_info=user_info)
        parameters = {"groups": [{"columns": ["school"], "default": "MNS"}]}
        previous_size_of_audit_runs_collection = audit_runs_collection.collection.count_documents({})

        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute_with_audit(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja", "kavya", "bhavya"], "age": [10, 11, 12],
                                            'school': ["MNS", "MNS", "MNS"]})
        
        new_size_of_audit_runs_collection = audit_runs_collection.collection.count_documents({})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        self.assertEqual(['name', 'age', 'school'], actual_dataframe.columns.tolist())
        expected_message = f"Successfully added column(s) school with default value MNS."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertEqual(new_size_of_audit_runs_collection, previous_size_of_audit_runs_collection+1)

    def test_add_columns_existing(self):
        transformer = AddColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["age"], "default": 20}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_values =[['pooja', 10, 20], ['kavya', 11, 20], ['bhavya', 12, 20]]
        self.assertEqual(['name', 'age', 'age_1'], actual_dataframe.columns.tolist())
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        expected_message = f"Successfully added column(s) age_1 with default value 20."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_add_columns_if_column_is_string(self):
        transformer = AddColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": "school", "default": "MNS"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to add columns.Failed to get distinct columns.", str(test_function.value))

    def test_add_columns_without_default(self):
        transformer = AddColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["school"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_values = [['pooja', 10, None], ['kavya', 11, None], ['bhavya', 12, None]]
        self.assertEqual(['name', 'age', 'school'], actual_dataframe.columns.tolist())
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        expected_message = f"Successfully added column(s) school with default value None."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_add_columns_without_default_as_none(self):
        transformer = AddColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["school"], "default": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja", "kavya", "bhavya"], "age": [10, 11, 12],
                                            'school': [None, None, None]})
        self.assertEqual(['name', 'age', 'school'], actual_dataframe.columns.tolist())
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully added column(s) school with default value None."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    '''def test_add_columns_with_None_in_columns(self):
        transformer = AddColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"column": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['pooja', 10], ['kavya', 11], ['bhavya', 12]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message ="Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
'''
    def test_add_columns_with_columns_as_none(self):
        transformer = AddColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja", "kavya", "bhavya"], "age": [10, 11, 12]
                                            })
        self.assertEqual(['name', 'age'], actual_dataframe.columns.tolist())
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_rename_columns(self):
        transformer = RenameColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"old_name": "name", "new_name": "Fullname"},
                                 {"old_name": "age", "new_name": "Age"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"Fullname": ["pooja", "kavya", "bhavya"], "Age": [10, 11, 12]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully renamed column(s) name with Fullname and age with Age."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_rename_columns_without_existing_name(self):
        transformer = RenameColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"old_name": "school_name", "new_name": "Fullname"},
                                 {"old_name": "age", "new_name": "Fullname"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to rename columns" in str(test_function.value))

    def test_rename_columns_with_none_in_old_name(self):
        transformer = RenameColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"old_name": None, "new_name": "Fullname"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['old_name']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_rename_columns_with_none_in_new_name(self):
        transformer = RenameColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"old_name": "name", "new_name": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['new_name']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_rename_columns_if_new_column_is_already_present(self):
        transformer = RenameColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"old_name": "name", "new_name": "name"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        #self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Successfully renamed column(s) name with name_1."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
    
    def test_rename_columns_old_name_not_present(self):
        transformer = RenameColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"new_name": "name"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['old_name']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_rename_columns_new_name_not_present(self):
        transformer = RenameColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"old_name": "name"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['new_name']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_rename_columns_old_name_new_name_not_present(self):
        transformer = RenameColumns()
        data = {
                  "name": ["pooja", "kavya", "bhavya"],
                  "age": [10, 11, 12]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['old_name', 'new_name']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_sort(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["age"], "ascending": True},
                                 {"columns": ["marks"], "ascending": True}] }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["kavya", "pooja", "bhavya"],
                                               "age": [11, 10, 12],
                                               "marks": [39, 40, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Successfully sorted column(s) age and marks."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_sort_1(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "customer": ["pooja", "kavya", "bhavya"],
            "customer_id": [9, 1, 6]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {'groups': [{'columns': ['customer_id'], 'ascending': True}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['kavya', 1], ['bhavya', 6], ['pooja', 9]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = "Successfully sorted column(s)  customer_id."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_sort_string_column_ascending(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "customer": ["pooja", "kavya", "bhavya"],
            "customer_id": [9, 1, 6]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {'groups': [{'columns': ['customer'], 'ascending': True}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['bhavya', 6], ['kavya', 1], ['pooja', 9]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = "Successfully sorted column(s)  customer."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_sort_string_column_without_ascending_parameter(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "customer": ["pooja", "kavya", "bhavya"],
            "customer_id": [9, 1, 6]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {'groups': [{'columns': ['customer']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['bhavya', 6], ['kavya', 1], ['pooja', 9]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = "Successfully sorted column(s)  customer."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_sort_string_column_without_ascending_as_none(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "customer": ["pooja", "kavya", "bhavya"],
            "customer_id": [9, 1, 6]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {'groups': [{'columns': ['customer'], 'ascending': None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['bhavya', 6], ['kavya', 1], ['pooja', 9]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = "Successfully sorted column(s)  customer."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_sort_string_column_descending(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "customer": ["pooja", "kavya", "bhavya"],
            "customer_id": [9, 1, 6]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {'groups': [{'columns': ['customer'], 'ascending': False}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['pooja', 9], ['kavya', 1], ['bhavya', 6]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = "Successfully sorted column(s)  customer."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_sort_integer_with_ascending_as_none(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "customer": ["pooja", "kavya", "bhavya"],
            "customer_id": [9, 1, 6]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {'groups': [{'columns': ['customer_id'], 'ascending': None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['kavya', 1], ['bhavya', 6], ['pooja', 9]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = "Successfully sorted column(s)  customer_id."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_sort_false(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "customer": ["pooja", "kavya", "bhavya"],
            "customer_id": [9, 1, 6]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {'groups': [{'columns': ['customer_id'], 'ascending': False}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['pooja', 9], ['bhavya', 6], ['kavya', 1]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = "Successfully sorted column(s)  customer_id."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_sort_with_non_existing_columns(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["Age"], "ascending": True},
                                 {"columns": ["marks"], "ascending": True}] }
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to sort columns.'Age'", str(test_function.value))

    def test_sort_with_columns_as_none(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": None, "ascending": True}] }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_sort_with_columns_as_empty_list(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": [], "ascending": True}] }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_sort_with_column_as_none(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": [None], "ascending": True}] }
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to sort columns.None", str(test_function.value))

    def test_sort_with_column_as_empty_string(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": [""], "ascending": True}] }
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to sort columns.''", str(test_function.value))

    def test_sort_without_ascending(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["marks"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["kavya", "pooja", "bhavya"],
                                               "age": [11, 10, 12],
                                               "marks": [39, 40, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Successfully sorted column(s)  marks."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_sort_without_columns(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_sort_without_columns_with_ascending(self):
        transformer = Sort()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"ascending": True}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_drop_columns(self):
        transformer = DropColumns()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["age"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja", "kavya", "bhavya"], "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully dropped column(s) age."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_drop_columns_with_non_existing_column(self):
        transformer = DropColumns()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["Age"]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to drop columns" in str(test_function.value))

    def test_drop_columns_with_none_in_columns(self):
        transformer = DropColumns()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": [None]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to drop columns.'[None] not found in axis'", str(test_function.value))

    def test_drop_columns_with_columns_as_none(self):
        transformer = DropColumns()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_drop_all_columns_except(self):
        transformer = DropAllColumnsExcept()
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name", "age"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja", "kavya", "bhavya"], "age": [10, 11, 12]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully dropped all column(s) except name and age."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_drop_all_columns_except_with_non_existing_column(self):
        transformer = DropAllColumnsExcept()
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["Fullname"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully dropped all column(s) except Fullname."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_drop_all_columns_except_with_none_in_columns(self):
        transformer = DropAllColumnsExcept()
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation completed with exception: sequence item 0: expected str instance, NoneType found"
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_drop_all_columns_except_with_columns_as_none(self):
        transformer = DropAllColumnsExcept()
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_deduplicate(self):
        transformer = Deduplicate()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya", "bhavya"],
            "age": [10, 11, 12, 11],
            "marks": [40, 39, 45, 30]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja", "kavya", "bhavya"], "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully deduplicated column(s) name."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_deduplicate_with_non_existing_column(self):
        transformer = Deduplicate()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya", "bhavya"],
            "age": [10, 11, 12, 11],
            "marks": [40, 39, 45, 30]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["Fullname"]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to deduplicate columns.Index(['Fullname'], dtype='object')", str(test_function.value))

    def test_deduplicate_with_none_in_columns(self):
        transformer = Deduplicate()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya", "bhavya"],
            "age": [10, 11, 12, 11],
            "marks": [40, 39, 45, 30]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": [None]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to deduplicate columns.Index([None], dtype='object')", str(test_function.value))

    def test_deduplicate_with_columns_as_none(self):
        transformer = Deduplicate()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya", "bhavya"],
            "age": [10, 11, 12, 11],
            "marks": [40, 39, 45, 30]
        }
        dataframe = pandas.DataFrame(data)
        # treats subset as entire dataframe
        parameters = {"groups": [{"columns": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)

    def test_split(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"destination_columns": ["first_name", "last_name"], "column": "name", "delimiter": "_"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45],
                                            "first_name": ["pooja", "kavya", "bhavya"],
                                            "last_name": ['shanmuk', 'shetty', 'gowda']})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully splitted column(s) name into first_name, last_name at the delimiter '_'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_split_date(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "date": ["5/9/2024", "5/9/2024", "5/9/2024"]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"destination_columns": ["month", "day", "year"], "column": "date", "delimiter": "/"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe,
                                                                                                   parameters)
        expected_values = [['pooja_shanmuk', 10, '5/9/2024', '5', '9', '2024'],
                           ['kavya_shetty', 11, '5/9/2024', '5', '9', '2024'],
                           ['bhavya_gowda', 12, '5/9/2024', '5', '9', '2024']]
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        expected_message = "Successfully splitted column(s) date into month, day, year at the delimiter '/'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_split_with_unknown_delimiter(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"destination_columns": ["first_name", "last_name"], "column": "name", "delimiter": "#"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45],
                                            "first_name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "last_name": [None, None, None]})
        # converting nan values to None in actual dataframe because it gives error even though if i use np.nan
        actual_dataframe = [[None if pandas.isna(value) else value for value in row] for row in actual_dataframe.values.tolist()]
        self.assertEqual(actual_dataframe, expected_dataframe.values.tolist())
        expected_message = "Successfully splitted column(s) name into first_name, last_name at the delimiter '#'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_split_with_unknown_column(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"destination_columns": ["first_name", "last_name"], "column": "student_name", "delimiter": "_"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to split columns.'student_name'", str(test_function.value))

    def test_split_with_existing_split_columns(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"destination_columns": ["name", "last_name"], "column": "name", "delimiter": "_"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_result=[['pooja_shanmuk', 10, 40, 'pooja', 'shanmuk'], ['kavya_shetty', 11, 39, 'kavya', 'shetty'], ['bhavya_gowda', 12, 45, 'bhavya', 'gowda']]
        self.assertEqual(actual_dataframe.values.tolist(), expected_result)
        self.assertEqual(['name', 'age', 'marks', 'name_1', 'last_name'], actual_dataframe.columns.tolist())
        expected_message = f"Successfully splitted column(s) name into name_1, last_name at the delimiter '_'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_split_with_split_columns_as_none(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"column": "name", "delimiter": "_"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_split_with_split_columns_as_empty_list(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"destination_columns": [], "column": "name", "delimiter": "_"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_split_with_source_column_as_none(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"destination_columns": ["name", "last_name"], "column": None, "delimiter": "_"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(['name', 'age', 'marks'], actual_dataframe.columns.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_split_with_source_column_as_empty_string(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"destination_columns": ["name", "last_name"], "column": "", "delimiter": "_"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to split columns.''", str(test_function.value))

    def test_split_with_delimiter_as_none(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja shanmuk", "kavya shetty", "bhavya gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"destination_columns": ["name", "last_name"], "column": "name", "delimiter": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_result=[['pooja shanmuk', 10, 40, 'pooja', 'shanmuk'], ['kavya shetty', 11, 39, 'kavya', 'shetty'], ['bhavya gowda', 12, 45, 'bhavya', 'gowda']]
        self.assertEqual(actual_dataframe.values.tolist(), expected_result)
        self.assertEqual(['name', 'age', 'marks', 'name_1', 'last_name'], actual_dataframe.columns.tolist())
        expected_message = f"Successfully splitted column(s) name into name_1, last_name at the delimiter ' '."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_split_with_delimiter_as_empty_string(self):
        transformer = Split()
        # Create a DataFrame
        data = {
            "name": ["pooja shanmuk", "kavya shetty", "bhavya gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"destination_columns": ["name", "last_name"], "column": "name", "delimiter": ""}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_result=[['pooja shanmuk', 10, 40, 'pooja', 'shanmuk'], ['kavya shetty', 11, 39, 'kavya', 'shetty'], ['bhavya gowda', 12, 45, 'bhavya', 'gowda']]
        self.assertEqual(actual_dataframe.values.tolist(), expected_result)
        self.assertEqual(['name', 'age', 'marks', 'name_1', 'last_name'], actual_dataframe.columns.tolist())
        expected_message = f"Successfully splitted column(s) name into name_1, last_name at the delimiter ' '."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
    
    def test_replace_special_characters(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "_", "columns": ["name"], "replacement_character": "-"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja-shanmuk", "kavya-shetty", "bhavya-gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully replaced special characters in column(s) name: _ to -."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_replace_special_characters_with_none_in_source_column(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "_", "columns": [None], "replacement_character": "-"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to replace special characters.None", str(test_function.value))

    def test_replace_special_characters_with_empty_string_in_source_column(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "_", "columns": [""], "replacement_character": "-"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to replace special characters.''", str(test_function.value))

    def test_replace_special_characters_with_empty_list_in_columns(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "_", "columns": [], "replacement_character": "-"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_replace_special_characters_without_source_column(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "_", "replacement_character": "-"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_replace_special_characters_with_target_character_as_none(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": None, "columns": ["name"], "replacement_character": "-"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['target_character']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_replace_special_characters_with_target_character_as_empty_string(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "", "columns": ["name"], "replacement_character": "-"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['target_character']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_replace_special_characters_without_target_character(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"columns": ["name"], "replacement_character": "-"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['target_character']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_replace_special_characters_with_replacement_character_as_none(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "_", "columns": ["name"], "replacement_character": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_values = [['poojashanmuk', 10, 40], ['kavyashetty', 11, 39], ['bhavyagowda', 12, 45]]
        self.assertEqual(expected_values, actual_dataframe.values.tolist())   
        expected_message = "Successfully replaced special characters in column(s) name: _ to ."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_replace_special_characters_with_replacement_character_as_empty_string(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "_", "columns": ["name"], "replacement_character": ""}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        #self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Successfully replaced special characters in column(s) name: _ to ."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_replace_special_characters_without_replacement_character(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "_", "columns": ["name"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_values = [['poojashanmuk', 10, 40], ['kavyashetty', 11, 39], ['bhavyagowda', 12, 45]]
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        expected_message = "Successfully replaced special characters in column(s) name: _ to ."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
    
    def test_replace_special_characters_with_non_existing_target_character(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "/", "columns": ["name"], "replacement_character": "-"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        # if the target charcter is not present the change
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"The target character does not exist in the given column."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_replace_special_characters_with_non_string_datatype(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "/", "columns": ["age"], "replacement_character": "-"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to replace special characters.Can only use .str accessor with string values!", str(test_function.value))

    def test_replace_special_characters_with_date_column(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45],
            "exam_date": ['2024-02-27', '2024-02-28', '2024-02-29']
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "-", "columns": ["exam_date"], "replacement_character": "/"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        # if the target charcter is not present the change
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        #self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully replaced special characters in column(s) exam_date: - to /."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_replace_special_characters_without_source_column_replacement_character(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"target_character": "-"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_replace_special_characters_without_source_column_target_character_replacement_character(self):
        transformer = ReplaceSpecialCharacters()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns', 'target_character']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_concat(self):
        transformer = Concat()
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": ["age", "marks"],
                         "separator": "/", "destination_column": "code"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45],
                                            "code": ["10/40", "11/39", "12/45"]
                                            })
        self.assertEqual(["name", "age", "marks", "code"], actual_dataframe.columns.tolist())
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully concatenated column(s) age, marks with '/' to the column 'code'."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_concat_with_unknown_columns(self):
        transformer = Concat()
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": ["Age", "marks"],
                         "separator": "/", "destination_column": "code"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to concat columns" in str(test_function.value))

    def test_concat_with_none_in_columns(self):
        transformer = Concat()
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": [None, "marks"],
                         "separator": "/", "destination_column": "code"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to concat columns.'[None] not in index'", str(test_function.value))

    def test_concat_with_columns_as_none(self):
        transformer = Concat()
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": None,
                         "separator": "/", "destination_column": "code"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(["name", "age", "marks"], actual_dataframe.columns.tolist())
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_concat_without_destination_columns(self):
        transformer = Concat()
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": ["age", "marks"],
                         "separator": "/"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45],
                                            "age_marks_concat": ["10/40", "11/39", "12/45"]
                                            })
        self.assertEqual(["name", "age", "marks", "age_marks_concat"], actual_dataframe.columns.tolist())
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Successfully concatenated column(s) age, marks with '/' to the column 'age_marks_concat'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_concat_without_separator(self):
        transformer = Concat()
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": ["name", "age"],
                         "separator": None, "destination_column": "name_age"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['pooja_shanmuk', 10, 40, 'pooja_shanmuk 10'],
                         ['kavya_shetty', 11, 39, 'kavya_shetty 11'],
                         ['bhavya_gowda', 12, 45, 'bhavya_gowda 12']]
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(["name", "age", "marks", "name_age"], actual_dataframe.columns.tolist())
        expected_message = "Successfully concatenated column(s) name, age with ' ' to the column 'name_age'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_concat_with_existing_destination_column(self):
        transformer = Concat()
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": ["age", "marks"],
                         "separator": "/", "destination_column": "marks"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45],
                                            "marks_1": ["10/40", "11/39", "12/45"]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        self.assertEqual(["name", "age", "marks", "marks_1"], actual_dataframe.columns.tolist())
        expected_message = f"Successfully concatenated column(s) age, marks with '/' to the column 'marks_1'."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_when_otherwise_without_new_column_name(self):
        transformer = WhenOtherwise()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        df = pandas.DataFrame(data)
        parameters ={"groups":[{"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS __newcolumn__\nFROM df;"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(df, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 19],
                                            "new_column_1": ["PASS", "MODERATE", "FAIL"]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"When otherwise query executed and stored in new_column_1 successfully."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_when_otherwise_with_existing_column_name_as_new_name(self):
        transformer = WhenOtherwise()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        df = pandas.DataFrame(data)
        parameters ={"groups":[{"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS marks\nFROM df;"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(df, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 19],
                                            "marks_1": ["PASS", "MODERATE", "FAIL"]
                                            })
        self.assertEqual(["name", "age", "marks", "marks_1"], actual_dataframe.columns.tolist())
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"When otherwise query executed and stored in marks_1 successfully."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_when_otherwise_with_new_column_name(self):
        transformer = WhenOtherwise()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        df = pandas.DataFrame(data)
        parameters ={"groups":[{"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS final_res\nFROM df;"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(df, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 19],
                                            "final_res": ["PASS", "MODERATE", "FAIL"]
                                            })
        self.assertEqual(["name", "age", "marks", "final_res"], actual_dataframe.columns.tolist())
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"When otherwise query executed and stored in final_res successfully."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_when_otherwise_with_new_column_name_1(self):
        transformer = WhenOtherwise()
        # Create a DataFrame
        data = {
            "full_name":['mya', 'vya', 'noj'],
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        df = pandas.DataFrame(data)
        parameters ={"groups":[
            {"query": "SELECT *, CASE WHEN full_name = 'mya' THEN 'helical' WHEN full_name = 'vya' THEN 'askdata' WHEN full_name = 'noj' THEN 'tech' ELSE NULL END AS __newcolumn__ FROM df;"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(df, parameters)
        expected_values = [['mya', 'pooja_shanmuk', 10, 40, 'helical'],
                              ['vya', 'kavya_shetty', 11, 39, 'askdata'],
                              ['noj', 'bhavya_gowda', 12, 19, 'tech']]
        self.assertEqual(["full_name", "name", "age", "marks", "new_column_1"], actual_dataframe.columns.tolist())
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        expected_message = f"When otherwise query executed and stored in new_column_1 successfully."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_when_otherwise_with_non_existing_column_name(self):
        transformer = WhenOtherwise()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        df = pandas.DataFrame(data)
        parameters ={"groups":[{"query": "SELECT *, CASE\n\tWHEN total_marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS final_res\nFROM df;"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=df, parameters=parameters)
        self.assertTrue('Failed to perform when otherwise' in  str(test_function.value))

    def test_when_otherwise_with_wrong_query(self):
        transformer = WhenOtherwise()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        df = pandas.DataFrame(data)
        parameters ={"groups":[{"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS final_res\nFROM "}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=df, parameters=parameters)
        self.assertEqual("Failed to perform when otherwise.Parser Error: syntax error at end of input", str(test_function.value))

    def test_when_otherwise_with_none_as_query(self):
        transformer = WhenOtherwise()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        df = pandas.DataFrame(data)
        parameters ={"groups":[{"query": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(df, parameters)

        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_date_format(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        dataframe['exam_date'] = pandas.to_datetime(dataframe['exam_date'])
        parameters ={"groups": [{"columns": ["exam_date"], "format": "YYYY.mm.DD"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 19],
                                            "exam_date": ['2000.12.22', '2000.11.24', '2000.12.28']
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully updated the format of the date for the column(s) exam_date to 'YYYY.mm.DD'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_date_format_1(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        dataframe['exam_date'] = pandas.to_datetime(dataframe['exam_date'])
        parameters ={"groups": [{"columns": ["exam_date"], "format": "MMM d, yyyy"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['pooja_shanmuk', 10, 40, 'Dec 22, 2000'],
                             ['kavya_shetty', 11, 39, 'Nov 24, 2000'],
                             ['bhavya_gowda', 12, 19, 'Dec 28, 2000']]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = f"Successfully updated the format of the date for the column(s) exam_date to 'MMM d, yyyy'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_date_format_2(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        dataframe['exam_date'] = pandas.to_datetime(dataframe['exam_date'])
        parameters ={"groups": [{"columns": ["exam_date"], "format": "dd-mm-yyyy"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['pooja_shanmuk', 10, 40, '22-12-2000'],
                         ['kavya_shetty', 11, 39, '24-11-2000'],
                         ['bhavya_gowda', 12, 19, '28-12-2000']]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = f"Successfully updated the format of the date for the column(s) exam_date to 'dd-mm-yyyy'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_date_format_3(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        dataframe['exam_date'] = pandas.to_datetime(dataframe['exam_date'])
        parameters ={"groups": [{"columns": ["exam_date"], "format": "d MMMM yyyy"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['pooja_shanmuk', 10, 40, '22 December 2000'],
                     ['kavya_shetty', 11, 39, '24 November 2000'],
                     ['bhavya_gowda', 12, 19, '28 December 2000']]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = f"Successfully updated the format of the date for the column(s) exam_date to 'd MMMM yyyy'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_date_format_4(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        dataframe['exam_date'] = pandas.to_datetime(dataframe['exam_date'])
        parameters ={"groups": [{"columns": ["exam_date"], "format": "d mmmm"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_data = [['pooja_shanmuk', 10, 40, '22 December'],
                         ['kavya_shetty', 11, 39, '24 November'],
                         ['bhavya_gowda', 12, 19, '28 December']]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        expected_message = f"Successfully updated the format of the date for the column(s) exam_date to 'd mmmm'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_date_format_without_casting_to_date_type(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": ["exam_date"], "format": "YYYY-MM-DD"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = "The column 'exam_date' provided is not in date format. Please cast it to date type to change the format."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertTrue(metadata)

    def test_date_format_with_unknown_column(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        parameters ={ "groups": [{"columns": ["exam"], "format": "YYYY-mm-DD"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to format the date.'exam'", str(test_function.value))

    def test_date_format_with_string_type_column(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": ["name"], "format": "YYYY-mm-DD"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "The column 'name' provided is not in date format. Please cast it to date type to change the format."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertTrue(metadata)

    def test_date_format_with_none_in_columns(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": None, "format": "YYYY-mm-DD"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertTrue(metadata)

    def test_date_format_with_none_in_date_format(self):
        transformer = DateFormat()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "exam_date": ['12/22/2000', '11/24/2000', '12/28/2000']
        }
        dataframe = pandas.DataFrame(data)
        dataframe['exam_date'] = pandas.to_datetime(dataframe['exam_date'])
        parameters ={"groups": [{"columns": ["exam_date"], "format": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertTrue(metadata)


    def test_correlation(self):
        transformer = Correlation()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = { "groups": [ {"columns": ["age", "marks"],  "destination_column":"age-marks-correlation"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja", "kavya", "bhavya"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45],
                                            "age-marks-correlation": [0.7777137710478187, 0.7777137710478187, 0.7777137710478187]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully calculated correlation for the column(s) age, marks to age-marks-correlation."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_correlation_with_existing_column_name(self):
        transformer = Correlation()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = { "groups": [ {"columns": ["age", "marks"],  "destination_column":"marks"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja", "kavya", "bhavya"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45],
                                            "marks_1": [0.7777137710478187, 0.7777137710478187, 0.7777137710478187]
                                            })
        self.assertEqual(["name", "age", "marks", "marks_1"], actual_dataframe.columns.tolist())
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully calculated correlation for the column(s) age, marks to marks_1."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_correlation_with_unknown_columns(self):
        transformer = Correlation()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = { "groups": [ {"columns": ["age1", "marks"],  "destination_column":"age-marks-correlation"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to find correlation of columns" in str(test_function.value))

    def test_correlation_with_single_column(self):
        transformer = Correlation()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = { "groups": [ {"columns": ["age"], "destination_column":"new_col"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = '''Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns'].'''
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_correlation_without_new_column_name(self):
        transformer = Correlation()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = { "groups": [ {"columns": ["age", "marks"], "destination_column":None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_values = [['pooja', 10, 40, 0.7777137710478187], ['kavya', 11, 39, 0.7777137710478187], ['bhavya', 12, 45, 0.7777137710478187]]
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        expected_message = '''Successfully calculated correlation for the column(s) age, marks to age_marks_correlation.'''
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_trim(self):
        transformer = Trim()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["davangere", "banglore", "hyderabad"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"number_of_characters": 1, "location": "right", "columns":["name"]},
                                    {"number_of_characters": 2, "location": "left", "columns":["city"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["a", "a", "a"],
                                            "city": ["da","ba", "hy"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully trimmed column(s) name to '1' character(s) to its right, city to '2' character(s) to its left."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_trim_without_parameter(self):
        transformer = Trim()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["davangere", "banglore", "hyderabad"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = None
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_values = [['pooja', 'davangere', 10, 40],
                                 ['kavya', 'banglore', 11, 39],
                                 ['bhavya', 'hyderabad', 12, 45]]
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_trim_with_unknown_columns(self):
        transformer = Trim()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["davangere", "banglore", "hyderabad"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"number_of_characters": 1, "location": "right", "columns":["name1"]},
                                    {"number_of_characters": 2, "location": "left", "columns":["city"]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to trim.'name1'", str(test_function.value))

    def test_trim_without_column_parameter(self):
        transformer = Trim()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["davangere", "banglore", "hyderabad"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"number_of_characters": 1, "location": "right"},
                                    {"number_of_characters": 2, "location": "left"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(actual_message, expected_message)

    def test_upper_case(self):
        transformer = UpperCase()
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["dvg", "bng", "hyd"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"]}, {"columns": ["city"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["POOJA", "KAVYA", "BHAVYA"],
                                            "city": ["DVG","BNG", "HYD"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully updated column(s) name to uppercase, city to uppercase."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_upper_case_with_unknown_columns(self):
        transformer = UpperCase()
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["dvg", "bng", "hyd"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name1"]}, {"columns": ["city"]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to perform upper case.'name1'", str(test_function.value))

    def test_upper_case_with_numeric_columns(self):
        transformer = UpperCase()
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["dvg", "bng", "hyd"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["age"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Successfully updated column(s) age to uppercase."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)


    def test_lower_case(self):
        transformer = LowerCase()
        # Create a DataFrame
        data = {
            "name": ["POOJA", "KAVYA", "BHAVYA"],
            "city": ["DVG", "BNG", "HYD"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"]}, {"columns": ["city"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
                                            "name": ["pooja", "kavya", "bhavya"],
                                            "city": ["dvg", "bng", "hyd"],
                                            "age": [10, 11, 12],
                                            "marks": [40, 39, 45]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully updated column(s) name to lowercase, city to lowercase."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_lower_case_with_unknown_columns(self):
        transformer = LowerCase()
        # Create a DataFrame
        data = {
            "name": ["POOJA", "KAVYA", "BHAVYA"],
            "city": ["DVG", "BNG", "HYD"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name1"]}, {"columns": ["city"]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to perform lower case.'name1'", str(test_function.value))

    def test_lower_case_with_columns_as_empty_list(self):
        transformer = LowerCase()
        data = {
            "name": ["POOJA", "KAVYA", "BHAVYA"],
            "city": ["DVG", "BNG", "HYD"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": []}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)

    def test_lower_case_with_columns_as_none(self):
        transformer = LowerCase()
        data = {
            "name": ["POOJA", "KAVYA", "BHAVYA"],
            "city": ["DVG", "BNG", "HYD"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)

    def test_lower_case_with_column_as_empty(self):
        transformer = LowerCase()
        data = {
            "name": ["POOJA", "KAVYA", "BHAVYA"],
            "city": ["DVG", "BNG", "HYD"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": [""]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to perform lower case.''", str(test_function.value))

    def test_lower_case_with_column_as_none(self):
        transformer = LowerCase()
        data = {
            "name": ["POOJA", "KAVYA", "BHAVYA"],
            "city": ["DVG", "BNG", "HYD"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": [None]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to perform lower case.None", str(test_function.value))

    def test_lower_case_without_columns(self):
        transformer = LowerCase()
        data = {
            "name": ["POOJA", "KAVYA", "BHAVYA"],
            "city": ["DVG", "BNG", "HYD"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = dataframe
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)

    def test_union_df_without_parameters(self):
        transformer = UnionDf()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, None)
        expected_dataframe = pandas.DataFrame({
                                            'id': [1, 2, 3, 101, 102, 103],
                                            'name': ['Alice', 'Bob', 'Charlie', 'Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
                                            'grade': [10, 11, 9, 10, 11, 9]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Union performed successfully."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_union_df_with_none_in_columns(self):
        transformer = UnionDf()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]
        parameters = {"groups": [{"columns": [None]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to perform union" in str(test_function.value))

    def test_union_df_if_columns_is_None(self):
        transformer = UnionDf()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]
        parameters = {"groups": [{"columns": None}], "file_names": ["test_file1", "test_file2"],}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
                                            'id': [1, 2, 3, 101, 102, 103],
                                            'name': ['Alice', 'Bob', 'Charlie', 'Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
                                            'grade': [10, 11, 9, 10, 11, 9]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Union performed successfully for test_file1, test_file2."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_union_df_with_parameters(self):
        transformer = UnionDf()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]
        parameters = {"groups":  [{"columns": ["grade"]}], "file_names": ["test_file1", "test_file2"],}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
                                            'grade': [10, 11, 9, 10, 11, 9]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully performed union based on column(s) grade for test_file1, test_file2."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
    
    def test_union_df_without_columns(self):
        transformer = UnionDf()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]
        parameters = {"groups":  [{}], "file_names": ["test_file1", "test_file2"],}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = f"Union performed successfully for test_file1, test_file2."
        self.assertEqual(actual_message, expected_message)

    def test_union_df_with_3_dataframes(self):
        transformer = UnionDf()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        exams_data = {
            'id': [201, 202, 203],
            'name': ['Ms. Smitha', 'Mr. John', 'Mrs. Brownie'],
            'grade': [10, 11, 9]
        }
        dataframe3 = pandas.DataFrame(exams_data)
        dataframe = [dataframe1, dataframe2, dataframe3]
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, None)
        expected_dataframe = pandas.DataFrame({
                                            'id': [1, 2, 3, 101, 102, 103, 201, 202, 203],
                                            'name': ['Alice', 'Bob', 'Charlie', 'Ms. Smith', 'Mr. Johnson', 'Mrs. Brown',
                                                     'Ms. Smitha', 'Mr. John', 'Mrs. Brownie'],
                                            'grade': [10, 11, 9, 10, 11, 9, 10, 11, 9]
                                            })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Union performed successfully."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_joins(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": ["grade"],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Successfully performed joins on files Students, Enrollments on columns grade and grade with the type inner."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_joins_unknown_columns(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade1"], "right_on": ["grade"],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to perform joins.'grade1'", str(test_function.value))

    def test_joins_with_join_type_as_none(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": None, "left_on": ["grade"], "right_on": ["grade"],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Successfully performed joins on files Students, Enrollments on columns grade and grade with the type inner."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
    
    def test_joins_with_join_type_as_empty_string(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "", "left_on": ["grade"], "right_on": ["grade"],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Successfully performed joins on files Students, Enrollments on columns grade and grade with the type inner."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_joins_with_left_on_as_none_list(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": [None], "right_on": ["grade"],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = "Operation completed with exception: sequence item 0: expected str instance, NoneType found"
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_joins_with_left_on_as_empty_list(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": [], "right_on": ["grade"],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['left_on']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_joins_with_left_on_as_none(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": None, "right_on": ["grade"],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['left_on']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_joins_with_right_on_as_none_list(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": [None],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = "Operation completed with exception: sequence item 0: expected str instance, NoneType found"
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_joins_with_right_on_as_empty_list(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": [],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['right_on']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_joins_with_right_on_as_none(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": None,
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['right_on']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_joins_with_left_on_right_on_as_none(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": None, "right_on": None,
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['left_on', 'right_on']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_joins_with_file_names_as_none_list(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": ["grade"],
                                  }],"file_names": [None]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['file_names']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_joins_with_file_names_as_empty_string_list(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": ["grade"],
                                  }],"file_names": ["", ""]
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Successfully performed joins on files ,  on columns grade and grade with the type inner."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_joins_with_file_names_as_empty_list(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": ["grade"],
                                  }],"file_names": []
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['file_names']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_joins_with_file_names_as_none(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": ["grade"],
                                  }],"file_names": None
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['file_names']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
        
    def test_joins_without_file_names_left_on_right_on(self):
        transformer = Joins()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]

        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": ["grade"],
                                  }],"file_names": None
                      }
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({
            'id_Students': [1, 2, 3], 'name_Students': ['Alice', 'Bob', 'Charlie'], 'grade': [10, 11, 9],
            'id_Enrollments': [101, 102, 103], 'name_Enrollments': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown']
        })
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['file_names']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
    
    def test_rearrange_columns_with_single_column_at_0(self):
        transformer = RearrangeColumns()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": [{"grade":0}]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_dataframe = pandas.DataFrame({
            'grade': [10, 11, 9],
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
        })
        self.assertEqual(['grade','id','name'], actual_dataframe.columns.tolist())
        self.assertEqual(expected_dataframe.values.tolist(), actual_dataframe.values.tolist())
        expected_message = f"Successfully rearranged column(s) in the given order "
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_rearrange_columns_with_single_column_position(self):
        transformer = RearrangeColumns()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": [{"grade":1}]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_dataframe = pandas.DataFrame({
            'id': [1, 2, 3],
            'grade': [10, 11, 9],
            'name': ['Alice', 'Bob', 'Charlie']
        })
        self.assertEqual(['id','grade','name'], actual_dataframe.columns.tolist())
        self.assertEqual(expected_dataframe.values.tolist(), actual_dataframe.values.tolist())
        expected_message = f"Successfully rearranged column(s) in the given order "
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_rearrange_columns_with_single_column_position_to_negative_index(self):
        transformer = RearrangeColumns()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": [{"id":-1}]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_dataframe = pandas.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9],
            'id': [1, 2, 3]
        })
        self.assertEqual(['name','grade','id'], actual_dataframe.columns.tolist())
        self.assertEqual(expected_dataframe.values.tolist(), actual_dataframe.values.tolist())
        expected_message = f"Successfully rearranged column(s) in the given order "
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_rearrange_columns_with_relative_columns_position_before(self):
        transformer = RearrangeColumns()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns":[{"grade":0},{"id":1}]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_dataframe = pandas.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9],
            'id': [1, 2, 3]
        })
        self.assertEqual(['name','grade','id'], actual_dataframe.columns.tolist())
        self.assertEqual(expected_dataframe.values.tolist(), actual_dataframe.values.tolist())
        expected_message = f"Successfully rearranged column(s) in the given order "
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
    
    def test_rearrange_columns_with_relative_columns_position_after(self):
        transformer = RearrangeColumns()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns":[{"id":0},{"grade":1}]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_dataframe = pandas.DataFrame({
            'id': [1, 2, 3],
            'grade': [10, 11, 9],
            'name': ['Alice', 'Bob', 'Charlie']
        })
        self.assertEqual(['id','grade','name'], actual_dataframe.columns.tolist())
        self.assertEqual(expected_dataframe.values.tolist(), actual_dataframe.values.tolist())
        expected_message = f"Successfully rearranged column(s) in the given order "
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_rearrange_columns_with_columns_as_empty_list(self):
        transformer = RearrangeColumns()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": []}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_dataframe = dataframe
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_rearrange_columns_different_cases(self):
        transformer = RearrangeColumns()
        user_input = """
        - parameters:
            groups:
                - columns:
                    - { "marks": 1 }
                    - { "name": 0 }
          expected_output:
            columns: ["id", "name", "marks", "grade", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "name": 0 }
                    - { "id": -2 }
                    - { "marks": 1 }
          expected_output:
            columns: ["name", "marks", "grade", "id", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "marks": 1 }
                    - { "name": 0 }
          expected_output:
            columns: ["id", "name", "marks", "grade", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "grade": -2 }
          expected_output:
            columns: ["id", "name", "marks", "grade", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "grade": -1 }
          expected_output:
            columns: ["id", "name", "marks", "sub", "grade"]
            
        - parameters:
            groups:
                - columns:
                    - { "grade": -3 }
          expected_output:
            columns: ["id", "name", "grade", "marks", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "grade": -4 }
          expected_output:
            columns: ["id", "grade", "name", "marks", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "sub": 0 }
                    - { "id": 1 }
          expected_output:
            columns: ["name", "grade", "marks", "sub", "id"]
            
        - parameters:
            groups:
                - columns:
                    - { "marks": 0 }
                    - { "name": 1 }
          expected_output:
            columns: ["id", "grade", "marks", "name", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "marks": 0 }
                    - { "name": 1 }
                    - { "grade": 2 }
          expected_output:
            columns: ["id", "marks", "name", "grade", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "id": 0 }
                    - { "marks": 1 }
                    - { "sub": 2 }
          expected_output:
            columns: ["id", "marks", "sub", "name", "grade"]
            
        - parameters:
            groups:
                - columns:
                    - { "marks": 0 }
                    - { "name": 1 }
                    - { "grade": 2 }                    
                    - { "id": 3 }
          expected_output:
            columns: ["marks", "name", "grade", "id", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "sub": 0 }
                    - { "grade": 1 }
          expected_output:
            columns: ["id", "name", "marks", "sub", "grade"]
            
        - parameters:
            groups:
                - columns:
                    - { "marks": 0 }
                    - { "name": 1 }
          expected_output:
            columns: ["id", "grade", "marks", "name", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "id": 0 }
          expected_output:
            columns: ["id", "name", "grade", "marks", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "name": 0 }
          expected_output:
            columns: ["name", "id", "grade", "marks", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "grade": 0 }
          expected_output:
            columns: ["grade", "id", "name", "marks", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "id": 2 }
          expected_output:
            columns: ["name", "grade", "id", "marks", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "id": 1 }
          expected_output:
            columns: ["name", "id", "grade", "marks", "sub"]
            
        - parameters:
            groups:
                - columns:
                    - { "id": -1 }
          expected_output:
            columns: ["name", "grade", "marks", "sub", "id"]
            
        - parameters:
            groups:
                - columns:
                    - { "grade": -1 }
          expected_output:
            columns: ["id", "name", "marks", "sub", "grade"]
        """
        tests = yaml.safe_load(user_input)
        for each_test in tests:                
            students_data = {
                'id': [1, 2, 3],
                'name': ['Alice', 'Bob', 'Charlie'],
                'grade': [10, 11, 9],
                'marks': [1,2,3],
                'sub': ['ab','bc','cs']
            }
            dataframe = pandas.DataFrame(students_data)
            parameters = each_test["parameters"]
            expected_columns = each_test["expected_output"]["columns"]
            actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
            self.assertEqual(expected_columns, actual_dataframe.columns.tolist())
            self.assertTrue(success)
            self.assertTrue(metadata)

    def test_filter_equals_with_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": ["name"], "expr":"equals", "value":["Bob"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_values = [[2, 'Bob', 11]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        self.assertEqual(expected_message, actual_message)

    def test_filter_equals_with_None_in_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        # parameters = {"groups": [{"columns": ["name"], "expr": "equals", "value": None}]}
        parameters = {"groups": [{"columns": ["name"], "expr": "equals", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_values = []
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        self.assertEqual(expected_message, actual_message)

    def test_filter_equals_without_value_equals(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        # parameters = {"groups": [{"columns": ["name"], "expr": "equals", "value": None}]}
        parameters = {"groups": [{"columns": ["name"], "expr": "equals"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_values = []
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        self.assertEqual(expected_message, actual_message)

    def test_filter_equals_with_None_in_value(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', None],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        # parameters = {"groups": [{"columns": ["name"], "expr": "equals", "value": None}]}
        parameters = {"groups": [{"columns": ["name"], "expr": "is_null"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_values = [[3, None, 9]]
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        self.assertEqual(expected_message, actual_message)


    def test_filter_equals_with_list_of_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": ["name"], "expr": "equals", "value": ["Bob", "Alice"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_values = [[1, 'Alice', 10], [2, 'Bob', 11]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        self.assertEqual(expected_message, actual_message)

    def test_filter_equals_with_list_of_integer(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [1, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": ["id", "grade"], "expr": "equals", "value": [1,2]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_values = [[1, 'Alice', 1]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'id', 'grade' based on the given criteria."
        self.assertEqual(expected_message, actual_message)

    def test_filter_equals_with_number_as_list(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 10, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": ["grade"], "expr":"equals", "value":[10]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_values = [[1, 'Alice', 10], [2, 'Bob', 10]]
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'grade' based on the given criteria."
        self.assertEqual(expected_message, actual_message)
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)

    def test_filter_equals_with_number_as_integer(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 10, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": ["grade"], "expr":"equals", "value":10}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_values = [[1, 'Alice', 10], [2, 'Bob', 10]]
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'grade' based on the given criteria."
        self.assertEqual(expected_message, actual_message)
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)

    def test_filter_not_equals_with_list_of_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": ["name"], "expr": "not_equals", "value": ["Bob", "Charlie"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_values = [[1, 'Alice', 10]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        self.assertEqual(expected_message, actual_message)

    def test_filter_not_equals_without_value(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": ["name"], "expr": "not_equals"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_values =  [[1, 'Alice', 10], [2, 'Bob', 11], [3, 'Charlie', 9]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        self.assertEqual(expected_message, actual_message)

    def test_filter_equals_with_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "start_date": ["8/3/2024", "2024-03-08"]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": ["start_date"], "expr":"equals", "value":["2024-03-08"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_values = [['2024-03-08']]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message="Successfully filtered column(s) 'start_date' based on the given criteria."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_not_equals_with_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2],
            'name': ['Alice', 'Bob'],
            'grade': [10, 11]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": ["name"], "expr":"not_equals", "value":["Alice"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_values = [[2, 'Bob', 11]]
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message= "Successfully filtered column(s) 'name' based on the given criteria."
        self.assertEqual(expected_message, actual_message)
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)

    def test_filter_not_equals_with_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [11, 10, 10]
        }
        dataframe = pandas.DataFrame(students_data)
        parameters = {"groups": [{"columns": ["grade"], "expr":"not_equals", "value":[10]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe, parameters=parameters)
        expected_values = [[1, 'Alice', 11]]
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        expected_message =  "Successfully filtered column(s) 'grade' based on the given criteria."
        self.assertEqual(expected_message, actual_message)
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)

    def test_filter_not_equals_with_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "start_date": ["8/3/2024", "2024-03-08"]
        }
        dataframe = pandas.DataFrame(data)
        parameters ={"groups": [{"columns": ["start_date"], "expr":"not_equals", "value":["8/3/2024"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_values = [['2024-03-08']]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        expected_message = "Successfully filtered column(s) 'start_date' based on the given criteria."
        self.assertEqual(expected_message, actual_message)
        self.assertEqual(actual_dataframe.values.tolist(), expected_values)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_contains_with_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["name"], "expr":"contains", "value":["pooja"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk"],
                                               "age": [10],
                                               "marks": [40]
                                               })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_does_not_contains_with_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty"],
            "age": [10, 11],
            "marks": [40, 39]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["name"], "expr":"not_contains", "value":["kavya"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["pooja_shanmuk"],
                                               "age": [10],
                                               "marks": [40]
                                               })
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_startswith_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "pooja_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "expr":"startswith", "value":["pooja"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(),[['pooja_shanmuk', 10, 40], ['pooja_shetty', 11, 39]])
        expected_message = f"Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_endswith_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["kavya_shetty", "pooja_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "expr":"endswith", "value":["shetty"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(),[['kavya_shetty', 10, 40], ['pooja_shetty', 11, 39]])
        expected_message = f"Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_not_startswith_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", "pooja_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "expr":"not_startswith", "value":["bhavya"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(),[['pooja_shanmuk', 10, 40], ['pooja_shetty', 11, 39]])
        expected_message = f"Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_not_endswith_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["kavya_shetty", "pooja_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "expr":"not_endswith", "value":["gowda"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(),[['kavya_shetty', 10, 40], ['pooja_shetty', 11, 39]])
        expected_message = f"Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_null_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", None, "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "expr": "is_null", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [[None, 11, 39]])
        expected_message = f"Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_not_null_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["pooja_shanmuk", None, "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "expr": "is_not_null", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['pooja_shanmuk', 10, 40], ['bhavya_gowda', 12, 19]])
        expected_message = f"Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_one_of_the_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["kavya", "pooja", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "expr":"is_one_of_the", "value":['kavya', 'pooja', 'doe']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['kavya', 10, 40], ['pooja', 11, 39]])
        expected_message = f"Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_not_one_of_the_string(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            "name": ["kavya", "pooja", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "expr":"is_not_one_of_the", "value":['bhavya','kavya']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['pooja', 11, 39]])
        expected_message = f"Successfully filtered column(s) 'name' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_in_range_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr":"in_range", "value":['2022-02-01', '2022-04-01']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-02-15', 20], ['2022-03-20', 30]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_in_range_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr":"in_range", "value":[20, 40]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-02-15', 20], ['2022-03-20', 30], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_in_range_number_list_is_not_exactly_2(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr":"in_range", "value":[20]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to filter values" in str(test_function.value))

    def test_filter_not_in_range_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr":"not_in_range", "value":['2022-02-01', '2022-04-01']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_not_in_range_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr":"not_in_range", "value":[20, 40]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_in_between_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr": "in_between", "value": ['2022-02-01', '2022-04-01']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-02-15', 20], ['2022-03-20', 30]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_in_between_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr": "in_between", "value": [20, 40]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-02-15', 20], ['2022-03-20', 30], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_in_between_number_list_is_not_exactly_2(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr": "in_between", "value": [20]}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to filter values.expr must be a string to be evaluated, <class 'NoneType'> given", str(test_function.value))

    def test_filter_not_in_between_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {
            "groups": [{"columns": ["date"], "expr": "not_in_between", "value": ['2022-02-01', '2022-04-01']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_not_in_between_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr": "not_in_between", "value": [20, 40]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_one_of_the_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_one_of_the", "value":['2022-01-01', '2022-02-15', '2022-08-15']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10], ['2022-02-15', 20]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_not_one_of_the_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_not_one_of_the", "value":['2022-01-01', '2022-02-15', '2022-08-15']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-03-20', 30], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_one_of_the_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_one_of_the", "value":[10, 20]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10], ['2022-02-15', 20]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_not_one_of_the_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_not_one_of_the", "value":[10, 20]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-03-20', 30], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_null_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', None, '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr": "is_null", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [[None, 20]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_not_null_date(self):
        transformer = FilterValue()
        data = {
            'date': ['2022-01-01', None],
            'value': [10, 20]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr": "is_not_null", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_null_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', None, '2022-03-20', '2022-04-10'],
            'value': [None, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr": "is_null", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        actual_dataframe_values = [[None if pandas.isna(value) else value for value in row] for row in
                                   actual_dataframe.values.tolist()]
        self.assertEqual(actual_dataframe_values, [['2022-01-01', None]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_not_null_number(self):
        transformer = FilterValue()
        data = {
            'date': ['2022-01-01', None],
            'value': [10, None]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr": "is_not_null", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        actual_dataframe_values = [[None if pandas.isna(value) else value for value in row] for row in
                                   actual_dataframe.values.tolist()]
        self.assertEqual(actual_dataframe_values, [['2022-01-01', 10]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_greater_than_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_greater_than", "value":["2022-02-15"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-03-20', 30], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_greater_than_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_greater_than", "value":[20]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-03-20', 30], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_greater_than_or_equal_to_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_greater_than_or_equal_to", "value":["2022-02-15"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-02-15', 20], ['2022-03-20', 30], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_greater_than_or_equal_to_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_greater_than_or_equal_to", "value":[20]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-02-15', 20], ['2022-03-20', 30], ['2022-04-10', 40]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_lesser_than_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_lesser_than", "value":["2022-02-15"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_lesser_than_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_lesser_than", "value":[20]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_lesser_than_or_equal_to_date(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date"], "expr":"is_lesser_than_or_equal_to", "value":["2022-02-15"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10], ['2022-02-15', 20]])
        expected_message = f"Successfully filtered column(s) 'date' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_lesser_than_or_equal_to_number(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'date': ['2022-01-01', '2022-02-15', '2022-03-20', '2022-04-10'],
            'value': [10, 20, 30, 40]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr":"is_lesser_than_or_equal_to", "value":[20]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['2022-01-01', 10], ['2022-02-15', 20]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_true(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'grade': ['A', 'C', 'A', 'D'],
            'value': [True, False, True, False]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr": "is_true", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['A', True], ['A', True]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_is_false(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'grade': ['A', 'C', 'A', 'D'],
            'value': [True, False, True, False]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "expr": "is_false", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        self.assertEqual(actual_dataframe.values.tolist(), [['C', False], ['D', False]])
        expected_message = f"Successfully filtered column(s) 'value' based on the given criteria."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_filter_without_columns(self):
        transformer = FilterValue()
        # Create a DataFrame
        data = {
            'grade': ['A', 'C', 'A', 'D'],
            'value': [True, False, True, False]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": None, "expr": "is_false", "value": [None]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message="Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)

    def test_cast_double_to_float(self):
        transformer = Cast()
        data = {
            'id': [1, 2, 3],
            'double_column': [175.51243237, 160.33253457, 180.23254778]
        }
        dataframe = pandas.DataFrame(data)

        # double to float converts from float64 to float32
        parameters = {"groups": [{"columns": ["double_column"], "new_type": "float"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'float32']
        self.assertEqual(expected_dtypes, actual_dtypes)
        expected_message = "Updated data type of the given column(s) double_column to 'float'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_double_to_int(self):
        transformer = Cast()
        # Create a DataFrame
        data = {
            'id': [1, 2, 3],
            'double_column': [175.51243237, 160.33253457, 180.23254778]
        }
        dataframe = pandas.DataFrame(data)

        # double to int
        parameters = {"groups": [{"columns": ["double_column"], "new_type": "integer"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'float64']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) double_column to 'float'.", actual_message)

    def test_cast_double_to_int_none(self):
        transformer = Cast()
        # Create a DataFrame
        data = {
            'id': [1, 2, 3],
            'double_column': [175.51243237, 160.33253457, None]
        }
        dataframe = pandas.DataFrame(data)

        # double to int
        parameters = {"groups": [{"columns": ["double_column"], "new_type": "integer"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'float64']
        self.assertEqual(expected_dtypes, actual_dtypes)
        expected_message = "Updated data type of the given column(s) double_column to 'float'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)

    def test_cast_float_to_int(self):
        transformer = Cast()
        # Create a DataFrame
        data = {
            'id': [1, 2, 3],
            'float_column': [175.51244, 160.33253, 180.23254]
        }
        dataframe = pandas.DataFrame(data)

        # float to int
        parameters = {"groups": [{"columns": ["float_column"], "new_type": "integer"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'float64']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        self.assertEqual("Updated data type of the given column(s) float_column to 'float'.", actual_message)

    def test_cast_int_to_float(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3],
            'int_column': [175, -160, 180]
        }
        dataframe = pandas.DataFrame(data)

        # int to float
        parameters = {"groups": [{"columns": ["int_column"], "new_type": "float"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'float32']
        self.assertEqual([[1.0, 175.0], [2.0, -160.0], [3.0, 180.0]], actual_dataframe.values.tolist())
        self.assertEqual(expected_dtypes, actual_dtypes,)
        self.assertEqual( "Updated data type of the given column(s) int_column to 'float'.", actual_message)

    def test_cast_float_to_object(self):
        transformer = Cast()
        # Create a DataFrame
        data = {
            'id': [1, 2, 3],
            'float_column': [175.51244, 160.33253, 180.23254]
        }
        dataframe = pandas.DataFrame(data)

        # float to object
        parameters = {"groups": [{"columns": ["float_column"], "new_type": "object"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'object']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        self.assertEqual("Updated data type of the given column(s) float_column to 'object'.", actual_message)

    def test_cast_boolean_to_object(self):
        transformer = Cast()
        # Create a DataFrame
        data = {
            'id': [1, 2, 3],
            'bool_column': [True, False, True]
        }
        dataframe = pandas.DataFrame(data)

        # boolean to object
        parameters = {"groups": [{"columns": ["bool_column"], "new_type": "object"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'object']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        self.assertEqual("Updated data type of the given column(s) bool_column to 'object'.", actual_message)

    def test_cast_without_new(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3],
            'int_column': [175, -160, 180]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["int_column"]}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'int64']
        self.assertEqual(expected_dtypes, actual_dtypes)
        expected_message="Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['new_type']."
        self.assertEqual(expected_message, actual_message)

    def test_cast_with_mixed_values_to_int(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3, 4, 5, 6, 7],
            'int_column': [175, -160, 12, '234', '2,345', 23.45, "1,222,3.9"]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["int_column"], "new_type": "integer"}]}
        with pytest.raises(DataTransformationException):
            actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(
                dataframe=dataframe, parameters=parameters)
            

    def test_cast_integer_to_object(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3, 4, 5, 6, 7],
            'int_column': [175, -160, 12, '234', '2,345', 23.45, "1,222,3.9"]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["id"], "new_type": "object"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(
            dataframe=dataframe, parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['object', 'object']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        expected_message ="Updated data type of the given column(s) id to 'object'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_mixed_type_to_object(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3, 4, 5, 6, 7],
            'int_column': [175, -160, 12, '234', '2,345', 23.45, "1,222,3.9"]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["int_column"], "new_type": "object"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(
            dataframe=dataframe, parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'object']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        expected_message ="Updated data type of the given column(s) int_column to 'object'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_with_mixed_values_to_float(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3, 4, 5, 6, 7],
            'int_column': [175, -160, 12, '234', '2,345', 2345, "1,222,3"]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["int_column"], "new_type": "float"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual('Failed to cast columns.Unable to parse string "2,345" at position 4', str(test_function.value))

    def test_cast_with_string_values_to_int(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3, 4, 5, 6, 7],
            'int_column': [175, -160, 12, 'date', '2,345', 2345, "1,222,3"]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["int_column"], "new_type": "integer"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual('Failed to cast columns.Unable to parse string "date" at position 3', str(test_function.value))

    def test_cast_with_string_values_to_float(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3, 4, 5, 6, 7],
            'int_column': [175, -160, 12, 'date', '2,345', 2345, "1,222,3"]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["int_column"], "new_type": "float"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual('Failed to cast columns.Unable to parse string "date" at position 3', str(test_function.value))


    def test_cast_with_mixed_values_to_int_none(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3, 4, 5, 6, 7],
            'int_column': [None, -160, None, '234', '2,345', 23.45, "1,222,3.9"]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["int_column"], "new_type": "integer"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual('Failed to cast columns.Unable to parse string "2,345" at position 4', str(test_function.value))

    def test_cast_mixed_type_to_string(self):
        transformer = Cast()

        data = {
            'mixed_column': [10, '20', 30.5, True, 'abc', None, 'hello', '2024-04-01']
        }

        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["mixed_column"], "new_type": "string"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['string']
        self.assertEqual(actual_dataframe.values.tolist(), [['10'], ['20'], ['30.5'], ['True'],
                                                            ['abc'], [pandas.NA], ['hello'], ['2024-04-01']])
        self.assertEqual(expected_dtypes, actual_dtypes,)
        expected_message = "Updated data type of the given column(s) mixed_column to 'string'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_mixed_data_to_boolean_with_unknown_column(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3, 4, 5],
            'bool_column': [True, False, 'TRUE', 'FALSE', '1']
        }

        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["boolean_column"], "new_type": "boolean"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to cast columns" in  str(test_function.value))
            
    def test_cast_mixed_data_to_boolean(self):
        transformer = Cast()
        data = {
            'bool_column': [True, False, 'TRUE', 'FALSE', '1', '0', 1, 0, "true", "false"]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["bool_column"], "new_type": "boolean"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['bool']
        expected_values = [[True], [False], [True], [False], [True], [False], [True], [False], [True], [False]]
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        self.assertEqual(details, {'exception': False, 'exception_message': None, 'exception_name': None})
        self.assertEqual(expected_dtypes, actual_dtypes)
        expected_message= "Updated data type of the given column(s) bool_column to 'boolean'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_mixed_data_to_bool(self):
        transformer = Cast()
        data = {
            'bool_column': [True, False, 'TRUE', 'FALSE', '1', '0', 1, 0, "true", "false"]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["bool_column"], "new_type": "bool"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['bool']
        expected_values = [[True], [False], [True], [False], [True], [False], [True], [False], [True], [False]]
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        self.assertEqual(details, {'exception': False, 'exception_message': None, 'exception_name': None})
        self.assertEqual(expected_dtypes, actual_dtypes)
        expected_message= "Updated data type of the given column(s) bool_column to 'boolean'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_mixed_data_to_boolean_with_none_and_other_values(self):
        transformer = Cast()
        data = {
            'bool_column': ["yes", False, None, -9, "no", "Yes", "No", "", "true", "false", "null"]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["bool_column"], "new_type": "boolean"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to cast columns" in str(test_function.value))

    def test_cast_mixed_data_to_boolean_with_none_and_other_values_(self):
        transformer = Cast()
        data = {
            'bool_column': ["yes", False, None, -9, "no", "Yes", "No", "", "true", "false", "null"],
            'bool_col': [True, False, None, True, False, "1", "0", "true", "true", "false", "null"]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["bool_column", "bool_col"], "new_type": "boolean", "old_type":None}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to cast columns" in str(test_function.value))

    def test_cast_mixed_data_to_boolean_with_none_and_other_values_with_duplicate(self):
        transformer = Cast()
        data = {
            'bool_column': ["yes", False, None, -9, "no", "Yes", "No", "", "true", "false", "null"],
            'bool_col': ["yes", "yes", "yes", "yes", "yes", "yes", "yes", "yes", "true", "false", "yes"]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["bool_col"], "new_type": "boolean", "old_type":None}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to cast columns.Cannot map values to boolean: bool_col contains ['yes']", str(test_function.value))


    def test_cast_boolean_to_int(self):
        transformer = Cast()

        data = {
            'boolean_column': [True, False, True, True],
            'string_column': ["true", "yes", "1", "test"]
        }

        dataframe = pandas.DataFrame(data)

        # boolean to int
        parameters = {"groups": [{"columns": ["boolean_column"], "new_type": "integer"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['bool', 'object']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) boolean_column to 'boolean'.", actual_message)

    def test_cast_boolean_to_string(self):
        transformer = Cast()

        data = {
            'int_column': [1, 0, 1, 2],
            'boolean_column': [True, True, False, True]
        }

        dataframe = pandas.DataFrame(data)

        # boolean to string
        parameters = {"groups": [{"columns": ["boolean_column"], "new_type": "string"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'string']
        self.assertEqual(actual_dataframe.values.tolist(), [[1, 'True'], [0, 'True'], [1, 'False'], [2, 'True']])
        self.assertEqual(expected_dtypes, actual_dtypes,)
        expected_message = "Updated data type of the given column(s) boolean_column to 'string'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_bigint_to_int(self):
        transformer = Cast()

        data = {
            'id': [1, 3, 5],
            'bigint_column': [9223372036854775807, 0, -123456789]
        }
        dataframe = pandas.DataFrame(data)

        # bigint to int
        parameters = {"groups": [{"columns": ["bigint_column"], "new_type": "integer"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'int64']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        self.assertEqual("Updated data type of the given column(s) bigint_column to 'integer'.", actual_message)

    def test_cast_bigint_to_int_with_none(self):
        transformer = Cast()

        data = {
            'id': [1, 3, 5, 7],
            'bigint_column': [9223372036854775807, 0, -123456789, None]
        }
        dataframe = pandas.DataFrame(data)

        # bigint to int
        parameters = {"groups": [{"columns": ["bigint_column"], "new_type": "integer"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'float64']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        expected_message = "Updated data type of the given column(s) bigint_column to 'float'."
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)

    def test_cast_bigint_to_float_with_none(self):
        transformer = Cast()

        data = {
            'id': [1, 3, 5, 7],
            'bigint_column': [9223372036854775807, 0, -123456789, None]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["bigint_column"], "new_type": "float"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'float64']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        self.assertEqual(details, {'exception': False, 'exception_message': None, 'exception_name': None})
        expected_message = "Updated data type of the given column(s) bigint_column to 'float'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_int_to_bigint(self):
        transformer = Cast()
        data = {
            'id': [1, 2, 3, 5],
            'int_column': [2147483647, -2147483648, 0, 123456789]
        }
        dataframe = pandas.DataFrame(data)
        print(dataframe.dtypes)

        # int to bigint int64 to int32.. values doesnt change
        parameters = {"groups": [{"columns": ["int_column"], "new_type": "integer"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'int32']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual([[1, 2147483647], [2, -2147483648], [3, 0], [5, 123456789]], actual_dataframe.values.tolist())
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual("Updated data type of the given column(s) int_column to 'integer'.", actual_message)

    def test_cast_int_to_string(self):
        transformer = Cast()

        data = {
            'id': [1, 3, 5],
            'int_column': [123, 0, -101112]
        }
        dataframe = pandas.DataFrame(data)

        # int to string
        parameters = {"groups": [{"columns": ["int_column"], "new_type": "string"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'string']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        self.assertEqual("Updated data type of the given column(s) int_column to 'string'.", actual_message)

    def test_cast_string_to_float(self):
        transformer = Cast()

        data = {
            'string_column': [175, -160, 12, '234', '2,345', 23.45, "1,222,3.9"]
        }
        dataframe = pandas.DataFrame(data)

        # int to string
        parameters = {"groups": [{"columns": ["string_column"], "new_type": "integer"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual('Failed to cast columns.Unable to parse string "2,345" at position 4', str(test_function.value))

    def test_cast_string_to_int_with_comma_in_values(self):
        transformer = Cast()

        data = {
            'id': [1, 3, 5],
            'string_column': ["1,230", "3452.09", "-101112"]
        }
        dataframe = pandas.DataFrame(data)

        # int to string
        parameters = {"groups": [{"columns": ["string_column"], "new_type": "integer"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual('Failed to cast columns.Unable to parse string "1,230" at position 0', str(test_function.value))

    def test_cast_string_to_int_without_comma_in_values(self):
        transformer = Cast()

        data = {
            'id': [1, 3, 5],
            'string_column': ["1230", "3452.09", "-101112"]
        }
        dataframe = pandas.DataFrame(data)

        # int to string
        parameters = {"groups": [{"columns": ["string_column"], "new_type": "integer"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'float64']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        expected_message = """Updated data type of the given column(s) string_column to 'float'."""
        self.assertEqual(expected_message, actual_message)

    def test_cast_int_to_string_if_string_column_has_numeric_and_string(self):
        transformer = Cast()

        data = {
            'id': [1, 2, 3, 5],
            'string_column': ["123", "test", "0", "-101112"]
        }
        dataframe = pandas.DataFrame(data)

        # int to string
        parameters = {"groups": [{"columns": ["string_column"], "new_type": "integer"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual('Failed to cast columns.Unable to parse string "test" at position 1', str(test_function.value))
            
    def test_cast_unix_to_date(self):
        transformer = Cast()

        # Create a DataFrame
        data = {
            'last_date': [1709689270, 1709775670, 1490195805],
            'exam_date': [1709689270, 1709775670, 1490195805]
        }
        dataframe = pandas.DataFrame(data)

        # int to date(unix to date)
        parameters = {"groups": [{"columns": ["last_date"], "new_type": "date", "old_type": "unix"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'int64']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) last_date to 'date'.", actual_message)

    def test_cast_unix_to_date_without_old(self):
        transformer = Cast()

        # Create a DataFrame
        data = {
            'last_date': [1709689270, 1709775670, 1490195805],
            'exam_date': [1709689270, 1709775670, 1490195805]
        }
        dataframe = pandas.DataFrame(data)

        # int to date(unix to date without giving old_type)
        parameters = {"groups": [{"columns": ["last_date"], "new_type": "date"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'int64']
        expected_values = [[Timestamp('2024-03-06 01:41:10'), 1709689270], [Timestamp('2024-03-07 01:41:10'), 1709775670], [Timestamp('2017-03-22 15:16:45'), 1490195805]]
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual(expected_values, actual_dataframe.values.tolist())
        expected_message = "Updated data type of the given column(s) last_date to 'date'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_unix_to_timestamp(self):
        transformer = Cast()

        data = {
            'last_date': [1562007679, 1709775670],
            'exam_date': ["1562007679", "1709775670"],
        }
        dataframe = pandas.DataFrame(data)

        # int to date(unix to timestamp)
        parameters = {"groups": [{"columns": ["last_date"], "new_type": "timestamp", "old_type": "unix"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]

        expected_dtypes = ['datetime64[ns]', 'object']

        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) last_date to 'timestamp'.", actual_message)

    def test_cast_unix_to_timestamp_none(self):
        transformer = Cast()

        data = {
            'last_date': [1562007679, None],
            'exam_date': ["1562007679", "1709775670"],
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["last_date"], "new_type": "timestamp", "old_type": "unix"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]

        expected_dtypes = ['datetime64[ns]', 'object']

        self.assertEqual(expected_dtypes, actual_dtypes)
        
        self.assertEqual("Updated data type of the given column(s) last_date to 'timestamp'.", actual_message)

    def test_cast_string_to_unix_timestamp(self):
        transformer = Cast()

        data = {
            'last_date': [1562007679, 1709775670],
            'exam_date': ["1562007679", "1709775670"],
        }
        dataframe = pandas.DataFrame(data)

        # string to date(unix to timestamp)
        parameters = {"groups": [{"columns": ["exam_date"], "new_type": "timestamp", "old_type": "unix"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['int64', 'datetime64[ns]']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) exam_date to 'timestamp'.", actual_message)

    @pytest.mark.skip("Values differ decimal places")
    def test_cast_mixed_unix_to_date(self):
        transformer = Cast()

        data = {
            'unix_timestamp_int': [1616688744, 1616692344, 1616695944],
            'unix_timestamp_float': [1616688744.123, 1616692344.456, 1616695944.789],
            'unix_timestamp_ms': [1616688744000, 1616692344000, 1616695944000],
            'unix_timestamp_string': ['1616688744', '1616692344', '1616695944'],
            'unix_timestamp_negative': [-1616688744, -1616692344, -1616695944]
        }
        dataframe = pandas.DataFrame(data)

        # string to date(unix to timestamp)
        parameters = {"groups": [{"columns": ["unix_timestamp_int", "unix_timestamp_float", "unix_timestamp_ms",
                                              "unix_timestamp_string", "unix_timestamp_negative"],
                                  "new_type": "date", "old_type": "unix"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        data_list = [list(row) for row in actual_dataframe.itertuples(index=False, name=None)]
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]',
                           'datetime64[ns]']
        expected_values = [[Timestamp('2021-03-25 16:12:24'), Timestamp('1970-01-01 00:00:01.616688744'), Timestamp('1970-01-01 00:26:56.688744'), Timestamp('2021-03-25 16:12:48'), Timestamp('1969-12-31 23:59:58.383311256')], [Timestamp('2021-03-25 17:12:24'), Timestamp('1970-01-01 00:00:01.616692344'), Timestamp('1970-01-01 00:26:56.692344'), Timestamp('2021-03-25 17:12:32'), Timestamp('1969-12-31 23:59:58.383307656')], [Timestamp('2021-03-25 18:12:24'), Timestamp('1970-01-01 00:00:01.616695944'), Timestamp('1970-01-01 00:26:56.695944'), Timestamp('2021-03-25 18:12:16'), Timestamp('1969-12-31 23:59:58.383304056')]]
        self.assertEqual(data_list, expected_values)
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual( "Updated data type of the given column(s) unix_timestamp_int, unix_timestamp_float, unix_timestamp_ms, "
                                         "unix_timestamp_string, unix_timestamp_negative to 'date'.", actual_message)

    @pytest.mark.skip("Values differ decimal places")
    def test_cast_mixed_unix_to_date_without_old_type(self):
        transformer = Cast()

        data = {
            'unix_timestamp_int': [1616688744, 1616692344, 1616695944],
            'unix_timestamp_float': [1616688744.123, 1616692344.456, 1616695944.789],
            'unix_timestamp_ms': [1616688744000, 1616692344000, 1616695944000],
            'unix_timestamp_string': ['1616688744', '1616692344', '1616695944'],
            'unix_timestamp_negative': [-1616688744, -1616692344, -1616695944]
        }
        dataframe = pandas.DataFrame(data)

        # string to date(unix to timestamp)
        parameters = {"groups": [{"columns": ["unix_timestamp_int", "unix_timestamp_float", "unix_timestamp_ms",
                                              "unix_timestamp_string", "unix_timestamp_negative"],
                                  "new_type": "date"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        data_list = [list(row) for row in actual_dataframe.itertuples(index=False, name=None)]
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]',
                           'datetime64[ns]']
        expected_values = [[Timestamp('2021-03-25 16:12:24'), Timestamp('1970-01-01 00:00:01.616688744'), Timestamp('1970-01-01 00:26:56.688744'), Timestamp('2021-03-25 16:12:48'), Timestamp('1969-12-31 23:59:58.383311256')], [Timestamp('2021-03-25 17:12:24'), Timestamp('1970-01-01 00:00:01.616692344'), Timestamp('1970-01-01 00:26:56.692344'), Timestamp('2021-03-25 17:12:32'), Timestamp('1969-12-31 23:59:58.383307656')], [Timestamp('2021-03-25 18:12:24'), Timestamp('1970-01-01 00:00:01.616695944'), Timestamp('1970-01-01 00:26:56.695944'), Timestamp('2021-03-25 18:12:16'), Timestamp('1969-12-31 23:59:58.383304056')]]
        self.assertEqual(data_list, expected_values)
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual( "Updated data type of the given column(s) unix_timestamp_int, unix_timestamp_float, unix_timestamp_ms, "
                                         "unix_timestamp_string, unix_timestamp_negative to 'date'.", actual_message)

    def test_cast_mixed_type_unix_to_date(self):
        transformer = Cast()
        data = {
            'mixed_timestamp': [1616688744, '1616692344', 1616695944.0]
        }
        dataframe = pandas.DataFrame(data)

        parameters = {"groups": [{"columns": ["mixed_timestamp"], "new_type": "date", "old_type": "unix"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to cast columns.year 1616692344 is out of range: 1616692344, at position 1", str(test_function.value))

    def test_cast_date_type_with_hms(self):
        transformer = Cast()

        # Create a DataFrame
        data = {"date_column":
                    ["Mon, Jan 3, 2022 08:09:05", "Tue, Jan 4, 2022 08:09:05"]}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date_column"], "new_type": "date", "old_type": "ddd, MMM DD, YYYY HH:MM:SS"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date_column to 'date'.", actual_message)

    def test_cast_date_type_with_hms_2(self):
        transformer = Cast()

        # Create a DataFrame
        data = {"date_column":
                    ["24-04-16 10:30:00", "25-04-16 10:30:00"]}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date_column"], "new_type": "date", "old_type": "yy-mm-dd HH:MM:SS"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date_column to 'date'.", actual_message)

    def test_cast_date_type_1(self):
        transformer = Cast()

        # Create a DataFrame
        data = {"date_column":
                    ["24-04-16 10:30:00", "25-04-16 10:30:00"]}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date_column"], "new_type": "date", "old_type": "y-m-d H:M:S"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date_column to 'date'.", actual_message)

    def test_cast_date_type_2(self):
        transformer = Cast()

        # Create a DataFrame
        data = {"date_column":
                    ["2024-04-16 10:30:00", "2025-04-16 10:30:00"]}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date_column"], "new_type": "date", "old_type": "Y-m-D H:M:S"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date_column to 'date'.", actual_message)

    def test_cast_date_type_with_M_instead_of_m_hms(self):
        transformer = Cast()

        # Create a DataFrame
        data = {"date_column":
                    ["2024-04-16 10:30:00", "2025-04-16 10:30:00"]}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date_column"], "new_type": "date", "old_type": "Y-M-D H:M:S"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to cast columns.redefinition of group name 'M' as group 5; was group 2 at position 107", str(test_function.value))

    def test_cast_date_type_with_M_instead_of_m(self):
        transformer = Cast()

        # Create a DataFrame
        data = {"date_column":
                    ["2024-04-16", "2025-04-16"]}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date_column"], "new_type": "date", "old_type": "Y-M-D"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]']
        data_list = [list(row) for row in actual_dataframe.itertuples(index=False, name=None)]
        expected_values = [[Timestamp('2024-01-16 00:04:00')], [Timestamp('2025-01-16 00:04:00')]]
        self.assertEqual(expected_values, data_list)
        self.assertEqual(expected_dtypes, actual_dtypes)
        expected_message = "Updated data type of the given column(s) date_column to 'date'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_date_type_without_format(self):
        transformer = Cast()

        # Create a DataFrame
        data = {"date_column":
                    ["2024-04-16", "2025/04/16"]}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date_column"], "new_type": "date"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]']
        data_list = [list(row) for row in actual_dataframe.itertuples(index=False, name=None)]
        expected_values = [[Timestamp('2024-04-16 00:00:00')], [Timestamp('2025-04-16 00:00:00')]]
        self.assertEqual(expected_values, data_list)
        self.assertEqual(expected_dtypes, actual_dtypes)
        expected_message ="Updated data type of the given column(s) date_column to 'date'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_date_type_with_wrong_format_as_ymd(self):
        transformer = Cast()

        # Create a DataFrame
        data = {"date_column":
                    ["2024-04-16", "2025-04-16"]}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date_column"], "new_type": "date", "old_type": "ymd"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to cast columns" in str(test_function.value))

    def test_cast_date_type_with_ymd_format(self):
        transformer = Cast()

        # Create a DataFrame
        data = {"date_column":
                    ["20240416", "20250416"]}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date_column"], "new_type": "date", "old_type": "ymd"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]']
        data_list = [list(row) for row in actual_dataframe.itertuples(index=False, name=None)]
        expected_values = [[Timestamp('2024-04-16 00:00:00')], [Timestamp('2025-04-16 00:00:00')]]
        self.assertEqual(expected_values, data_list)
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date_column to 'date'.",actual_message)

    def test_cast_date_type(self):
        transformer = Cast()

        # Create a DataFrame
        data = {
            'date': ["2024-03-06", "2024-03-05"],
            'date1': ["jan 2, 2024", "jan 3, 2024"],
            'date2': ["2024/03/06", "2024/03/05"],
            'date3': ["03-06-2024", "23-05-2024"],
            'date4': ["03.06.2024", "23.05.2024"],
            'date5': ["1 January 2024", "1 January 2024"],
        }
        dataframe = pandas.DataFrame(data)

        # string to date
        parameters = {"groups": [{"columns": ["date"], "new_type": "date", "old_type": "YYYY-mm-DD"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'object', 'object', 'object', 'object', 'object']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date to 'date'.", actual_message)

        # string to date (jan 2, 2024: %b %d, %Y)
        parameters = {"groups": [{"columns": ["date1"], "new_type": "date", "old_type": "MMM d, YYYY"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'datetime64[ns]', 'object', 'object', 'object', 'object']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date1 to 'date'.", actual_message)

        # string to date
        parameters = {"groups": [{"columns": ["date2"], "new_type": "date", "old_type": "YYYY/mm/DD"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]', 'object', 'object', 'object']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date2 to 'date'.", actual_message)

        # string to date (dd-mm-yyyy, %d-%m-%Y, dd-MM-yyyy)
        parameters = {"groups": [{"columns": ["date3"], "new_type": "date", "old_type": "DD-mm-YYYY"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]', 'object', 'object']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date3 to 'date'.", actual_message)

        # string to date (dd.mm.yyyy, %d.%m.%Y, dd.MM.yyyy)
        parameters = {"groups": [{"columns": ["date4"], "new_type": "date", "old_type": "DD.mm.YYYY"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]',
                           'object']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        self.assertEqual("Updated data type of the given column(s) date4 to 'date'.", actual_message)

        # string to date (1 January 2024, d MMMM yyyy, %d %B %Y)
        parameters = {"groups": [{"columns": ["date5"], "new_type": "date", "old_type": "d MMMM YYYY"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]', 'datetime64[ns]',
                           'datetime64[ns]']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        self.assertEqual("Updated data type of the given column(s) date5 to 'date'.", actual_message)

        data = {
            'date6': ["01 January", "11 January"],
        }
        dataframe = pandas.DataFrame(data)
        # d MMMM, %d %B
        parameters = {"groups": [{"columns": ["date6"], "new_type": "date", "old_type": "d mmmm"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]']
        self.assertEqual(expected_dtypes, actual_dtypes,)
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        expected_message = "Updated data type of the given column(s) date6 to 'date'."
        self.assertEqual(expected_message, actual_message)

        data = {
            'date7': ["01 January", "11 January"],
        }
        dataframe = pandas.DataFrame(data)
        # d MMMM, %d %B
        parameters = {"groups": [{"columns": ["date7"], "new_type": "date", "old_type": "d MMMM"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                                   parameters=parameters)
        
        actual_dtypes = [str(actual_dataframe[column].dtypes) for column in actual_dataframe.columns]
        expected_dtypes = ['datetime64[ns]']
        self.assertEqual(expected_dtypes, actual_dtypes)
        self.assertEqual("Updated data type of the given column(s) date7 to 'date'.", actual_message)

    def test_cast_without_existing_columns(self):
        transformer = Cast()

        # Create a DataFrame
        data = {
            'date': ["2024-03-06", "2024-03-05"],
            'date1': ["jan 2, 2024", "jan 3, 2024"],
            'date2': ["2024/03/06", "2024/03/05"],
            'date3': ["03-06-2024", "23-05-2024"],
            'date4': ["03.06.2024", "23.05.2024"],
            'date5': ["1 January 2024", "1 January 2024"],
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["date6"], "new_type": "string"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to cast columns" in str(test_function.value))

    def test_cast_without_columns(self):
        transformer = Cast()

        # Create a DataFrame
        data = {
            'date': ["2024-03-06", "2024-03-05"],
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": None, "new_type": "unix"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)

    def test_cast_with_invalid_cast_type(self):
        transformer = Cast()

        # Create a DataFrame
        data = {
            'value': ["2024", "202"],
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "new_type": "int"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Please provide the casting type from the below list: ['float', 'integer','bool', 'boolean', 'string', 'date', 'timestamp','object']"
        self.assertEqual(expected_message, actual_message)

    def test_cast_int_to_date(self):
        transformer = Cast()

        # Create a DataFrame
        data = {
            'value': ["2024", "202"],
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["value"], "new_type": "date", "old_type": "yy"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to cast columns" in str(test_function.value))

    def test_aggregations_sum(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["sum"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }

        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data = [['A', 'K', 70, 35], ['A', 'X', 50, 25], ['B', 'K', 80, 40], ['B', 'Y', 70, 35], ['C', 'K', 90, 45], ['C', 'Z', 90, 45]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertTrue(success)
        self.assertEqual(
            message, "Successfully performed aggregations on 'value1, value2' grouped by 'category, subcategory'."
        )

    def test_aggregations_sum_when_source_column_isnull(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": [],
                    "destination_columns": [],
                    "agg": ["sum"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }

        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data = [['A', 'K', 70, 35], ['A', 'X', 50, 25], ['B', 'K', 80, 40], ['B', 'Y', 70, 35], ['C', 'K', 90, 45], ['C', 'Z', 90, 45]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(
            message, "Either source_column or aggregation function is not present"
        )

    def test_aggregations_sum_when_aggregation_function_isnull(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": [],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }

        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data = [['A', 'K', 70, 35], ['A', 'X', 50, 25], ['B', 'K', 80, 40], ['B', 'Y', 70, 35], ['C', 'K', 90, 45], ['C', 'Z', 90, 45]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(
            message, "Either source_column or aggregation function is not present"
        )


    def test_aggregations_sum_without_groupby(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["sum"],
                    "group_by": [],
                }
            ]
        }

        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data = [['A', 'X', 10, 5, 450, 225], ['B', 'Y', 20, 10, 450, 225], ['C', 'Z', 30, 15, 450, 225], ['A', 'X', 40, 20, 450, 225], ['B', 'Y', 50, 25, 450, 225], ['C', 'Z', 60, 30, 450, 225], ['A', 'K', 70, 35, 450, 225], ['B', 'K', 80, 40, 450, 225], ['C', 'K', 90, 45, 450, 225]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertTrue(success)
        self.assertEqual(
            message, "Successfully performed aggregations on 'value1, value2' grouped by ''."
        )

    def test_aggregations_mean(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["mean"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }


        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data = [['A', 'K', 70.0, 35.0], ['A', 'X', 25.0, 12.5], ['B', 'K', 80.0, 40.0], ['B', 'Y', 35.0, 17.5], ['C', 'K', 90.0, 45.0], ['C', 'Z', 45.0, 22.5]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertTrue(success)
        self.assertEqual(
            message, "Successfully performed aggregations on 'value1, value2' grouped by 'category, subcategory'."
        )

    def test_aggregations_count(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["count"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }

        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data = [['A', 'K', 1, 1],['A', 'X', 2, 2],['B', 'K', 1, 1],['B', 'Y', 2, 2],['C', 'K', 1, 1],['C', 'Z', 2, 2]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertTrue(success)
        self.assertEqual(
            message, "Successfully performed aggregations on 'value1, value2' grouped by 'category, subcategory'."
        )


    def test_aggregations_median(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["median"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }
        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data =  [['A', 'K', 70.0, 35.0], ['A', 'X', 25.0, 12.5], ['B', 'K', 80.0, 40.0], ['B', 'Y', 35.0, 17.5], ['C', 'K', 90.0, 45.0], ['C', 'Z', 45.0, 22.5]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertTrue(success)
        self.assertEqual(
            message, "Successfully performed aggregations on 'value1, value2' grouped by 'category, subcategory'."
        )

    def test_aggregations_std(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["stddev"],
                    "group_by": ["category"],
                }
            ]
        }

        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data = [['A', 30.0, 15.0], ['B', 30.0, 15.0], ['C', 30.0, 15.0]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertTrue(success)
        self.assertEqual(
            message, "Successfully performed aggregations on 'value1, value2' grouped by 'category'."
        )


    def test_aggregations_min_and_max(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["min", "max"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }

        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data = [['A', 'K', 70, 70, 35, 35], ['A', 'X', 10, 40, 5, 20], ['B', 'K', 80, 80, 40, 40], ['B', 'Y', 20, 50, 10, 25], ['C', 'K', 90, 90, 45, 45], ['C', 'Z', 30, 60, 15, 30]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertTrue(success)
        self.assertEqual(
            message, "Successfully performed aggregations on 'value1, value2' grouped by 'category, subcategory'."
        )


    def test_aggregations_variance(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["variance"],
                    "group_by": ["category"],
                }
            ]
        }

        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data = [['A', 900.0, 225.0], ['B', 900.0, 225.0], ['C', 900.0, 225.0]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertTrue(success)
        self.assertEqual(
            message, "Successfully performed aggregations on 'value1, value2' grouped by 'category'."
        )

    def test_aggregations_distinct(self):
        transformer = Aggregations()
        data = {
            'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'K', 'K', 'K'],
            'value1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'value2': [5, 10, 15, 20, 25, 30, 35, 40, 45]
        }
        df = pandas.DataFrame(data)
        parameters = {
            "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["distinct"],
                    "group_by": ["category", "subcategory"],
                }
            ]
        }

        actual_dataframe, success, metadata, message, new_df, details = transformer.execute(df, parameters)
        expected_data =[['A', 'K', 1, 1], ['A', 'X', 2, 2], ['B', 'K', 1, 1], ['B', 'Y', 2, 2], ['C', 'K', 1, 1], ['C', 'Z', 2, 2]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertTrue(success)
        self.assertEqual(
            message, "Successfully performed aggregations on 'value1, value2' grouped by 'category, subcategory'."
        )

    def test_arithmetic_operations_for_addition(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "units_sold+5", "destination_column": "units_total"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'units_sold+5' and stored to 'units_total'."
        expected_data = [['A', 100, 10, 1000, 105], ['B', 200, 20, 4000, 205]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'units_total'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_for_addition_if_new_column_is_none(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "units_sold+5", "destination_column": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'units_sold+5' and stored to 'new_column_1'."
        expected_data = [['A', 100, 10, 1000, 105], ['B', 200, 20, 4000, 205]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(expected_message, actual_message)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'new_column_1'])
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_for_subtraction(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "units_sold-5", "destination_column": "units_lost"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'units_sold-5' and stored to 'units_lost'."
        expected_data = [['A', 100, 10, 1000, 95], ['B', 200, 20, 4000, 195]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'units_lost'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_for_subtraction_for_two_columns(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "units_sold-unit_price", "destination_column": "units_lost"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'units_sold-unit_price' and stored to 'units_lost'."
        expected_data = [['A', 100, 10, 1000, 90], ['B', 200, 20, 4000, 180]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'units_lost'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_for_multiplication_for_two_columns(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "units_sold*unit_price", "destination_column": "total"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'units_sold*unit_price' and stored to 'total'."
        expected_data = [['A', 100, 10, 1000, 1000], ['B', 200, 20, 4000, 4000]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'total'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_if_column_in_not_of_integer_type(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "product*unit_price", "destination_column": "total"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to perform arithmetic.unsupported operand type(s) for *: 'object' and 'int64'", str(test_function.value))

    def test_arithmetic_operations_for_division(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "revenue/2", "destination_column": "revenue"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'revenue/2' and stored to 'revenue_1'."
        expected_data = [['A', 100, 10, 1000, 500.0], ['B', 200, 20, 4000, 2000.0]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'revenue_1'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_for_power(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "unit_price**3", "destination_column": "total"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'unit_price**3' and stored to 'total'."
        expected_data = [['A', 100, 10, 1000, 1000], ['B', 200, 20, 4000, 8000]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'total'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_multiple_operations_without_new_column(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "unit_price**3", "destination_column": None},
                                 {"query": "unit_price**2", "destination_column": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'unit_price**3','unit_price**2' and stored to 'new_column_1','new_column_2'."
        expected_data = [['A', 100, 10, 1000, 1000, 100], ['B', 200, 20, 4000, 8000, 400]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'new_column_1', 'new_column_2'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_multiple_operations_with_new_column(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "unit_price**3", "destination_column": "total"},
                                 {"query": "unit_price**2", "destination_column": "total"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'unit_price**3','unit_price**2' and stored to 'total','total_1'."
        expected_data = [['A', 100, 10, 1000, 1000, 100], ['B', 200, 20, 4000, 8000, 400]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'total', 'total_1'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_multiple_operations_with_existing_column_as_new_column(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "unit_price**3", "destination_column": "revenue"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'unit_price**3' and stored to 'revenue_1'."
        expected_data = [['A', 100, 10, 1000, 1000], ['B', 200, 20, 4000, 8000]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'revenue_1'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_for_modulo(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "revenue%3", "destination_column": "total"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'revenue%3' and stored to 'total'."
        expected_data = [['A', 100, 10, 1000, 1], ['B', 200, 20, 4000, 1]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'total'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_for_floor_division(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "revenue//2", "destination_column": "total"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'revenue//2' and stored to 'total'."
        expected_data = [['A', 100, 10, 1000, 500], ['B', 200, 20, 4000, 2000]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'total'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_abs(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [-1000, -4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "abs(revenue)", "destination_column": "result"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'abs(revenue)' and stored to 'result'."
        expected_data = [['A', 100, 10, -1000, 1000], ['B', 200, 20, -4000, 4000]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'result'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_log(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "log(revenue)", "destination_column": "result"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'log(revenue)' and stored to 'result'."
        expected_data = [['A', 100, 10, 1000, 6.907755278982137],
                        ['B', 200, 20, 4000, 8.294049640102028]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'result'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_expr1(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "(revenue + 100) // (2 * 3)", "destination_column": "total"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query '(revenue + 100) // (2 * 3)' and stored to 'total'."
        expected_data = [['A', 100, 10, 1000, 183], ['B', 200, 20, 4000, 683]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue', 'total'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_with_query_as_none(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": None, "destination_column": "total"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue'])
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_expr2(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "(revenue + 100)/(2 * 3)", "destination_column": "total"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query '(revenue + 100)/(2 * 3)' and stored to 'total'."
        expected_data = [['A', 100, 10, 1000, 183.33333333333334], ['B', 200, 20, 4000, 683.3333333333334]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        self.assertEqual(['product', 'units_sold', 'unit_price', 'revenue', 'total'], actual_dataframe.columns.tolist())
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_date_columns_1_subtract(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'date_1': ['2024-03-20', '2024-03-21'],
            'date_2': ['2024-03-10', '2024-03-10']
        }
        dataframe = pandas.DataFrame(data)
        dataframe['date_1'] = pandas.to_datetime(dataframe['date_1'])
        dataframe['date_2'] = pandas.to_datetime(dataframe['date_2'])
        parameters = {"groups": [{"query": "date_1-date_2", "destination_column": "date_difference"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_message = "Arithmetic operation performed on the given query 'date_1-date_2' and stored to 'date_difference'."
        expected_data = [[Timestamp('2024-03-20 00:00:00'),
                          Timestamp('2024-03-10 00:00:00'),
                          Timedelta('10 days 00:00:00')],
                         [Timestamp('2024-03-21 00:00:00'),
                          Timestamp('2024-03-10 00:00:00'),
                          Timedelta('11 days 00:00:00')]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['date_1', 'date_2', 'date_difference'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertFalse(new_df)

    def test_arithmetic_operations_date_columns_2(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'date_1': ['2024-03-20', '2024-03-21'],
            'date_2': ['2024-03-10', '2024-03-10']
        }
        dataframe = pandas.DataFrame(data)
        dataframe['date_1'] = pandas.to_datetime(dataframe['date_1'])
        parameters = {"groups": [{"query": "date_1 - '2024-03-23'", "destination_column": "date_difference"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to perform arithmetic.unsupported operand type(s) for -: 'datetime64[ns]' and '<class 'pandas._libs.tslibs.timestamps.Timestamp'>'", str(test_function.value))

    def test_arithmetic_operations_date_columns_without_date_type(self):
        transformer = Arithmetic()
        # Create a DataFrame
        data = {
            'date_1': ['2024-03-20', '2024-03-21'],
            'date_2': ['2024-03-10', '2024-03-10']
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "date_1 - date_2", "destination_column": "date_difference"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        # self.assertEqual("Failed to perform arithmetic.maximum recursion depth exceeded while calling a Python object", str(test_function.value))

    def test_sql_operations_1(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B'],
            'units_sold': [100, 200],
            'unit_price': [10, 20],
            'revenue': [1000, 4000]
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT * FROM df"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'SELECT * FROM df' successfully."
        expected_data = df.values.tolist()
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'units_sold', 'unit_price', 'revenue'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_2(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 22],
            'city': ['New York', 'SF', 'LA']
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT age FROM df"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'SELECT age FROM df' successfully."
        expected_data = [[25], [30], [22]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),['age'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_3(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 22],
            'city': ['New York', 'SF', 'LA']
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT * FROM df WHERE age > 25"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'SELECT * FROM df WHERE age > 25' successfully."
        expected_data = [['Bob', 30, 'SF']]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['name', 'age', 'city'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_4(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400]
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT * FROM df WHERE sales > 1000"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'SELECT * FROM df WHERE sales > 1000' successfully."
        expected_data = [['B', 1200], ['D', 1400]]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'sales'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_5(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'customer': ['Alice', 'Bob', 'Alice', 'David'],
            'order_amount': [100, 150, 200, 120]
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT customer, SUM(order_amount) AS total_sales FROM df GROUP BY customer"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'SELECT customer, SUM(order_amount) AS total_sales FROM df GROUP BY customer' successfully."
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['customer', 'total_sales'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_6(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400],
            'region': ['North', 'North', 'North', 'West']
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT * FROM df WHERE sales > 1000 AND region = 'North'"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'SELECT * FROM df WHERE sales > 1000 AND region = 'North'' successfully."
        expected_data = [['B', 1200, 'North']]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'sales', 'region'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_7(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400],
            'region': ['North', 'North', 'North', 'West']
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT * FROM df limit 2"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'SELECT * FROM df limit 2' successfully."
        expected_data = [['A', 800, 'North'], ['B', 1200, 'North']]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'sales', 'region'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    #@pytest.mark.skip("Transformation not working properly")
    def test_sql_operations_for_date_based_on_month(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400],
            'region': ['North', 'North', 'North', 'West'],
            'date': ['2024-03-15', '2024-03-15', '2024-01-15', '2024-01-15']}
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT * FROM df WHERE MONTH(CAST(date AS DATE)) = 1"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)
        expected_message = "Executed the given query 'SELECT * FROM df WHERE MONTH(CAST(date AS DATE)) = 1' successfully."
        expected_data = [['C', 950, 'North', '2024-01-15'], ['D', 1400, 'West', '2024-01-15']]
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'sales', 'region', 'date'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_for_date_based_on_date(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400],
            'region': ['North', 'North', 'North', 'West'],
            'date': ['2024-03-15', '2024-03-15', '2024-01-15', '2024-01-15']}
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT * FROM df WHERE date = '2024-01-15'"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'SELECT * FROM df WHERE date = '2024-01-15'' successfully."
        expected_data = [['C', 950, 'North', '2024-01-15'], ['D', 1400, 'West', '2024-01-15']]
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product', 'sales', 'region', 'date'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_8(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'Product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400],
            'region': ['North', 'North', 'North', 'West']
        }
        df = pandas.DataFrame(data)
        # column names in uppercase
        parameters = {"groups": [{"query": "SELECT  \"Product\"  FROM df limit 2"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'SELECT  \"Product\"  FROM df limit 2' successfully."
        expected_data = [['A'], ['B']]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['Product'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_with_query_in_lower_case(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400],
            'region': ['North', 'North', 'North', 'West']
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "select  product  from df limit 2"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)

        expected_message = "Executed the given query 'select  product  from df limit 2' successfully."
        expected_data = [['A'], ['B']]
        expected_details = {'exception': False, 'exception_message': None, 'exception_name': None}
        self.assertEqual(details, expected_details)
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(),
                         ['product'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_if_columns_are_uppercase(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'Product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400],
            'region': ['North', 'North', 'North', 'West']
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT Product FROM df limit 2"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=df,
                                                                                  parameters=parameters)
        expected_message = "Executed the given query 'SELECT Product FROM df limit 2' successfully."
        expected_data = [['A'], ['B']]
        self.assertEqual(actual_dataframe.values.tolist(), expected_data)
        self.assertEqual(actual_dataframe.columns.tolist(), ['Product'])
        self.assertEqual(expected_message, actual_message)
        self.assertTrue(success)
        self.assertTrue(metadata)
        self.assertTrue(new_df)

    def test_sql_operations_with_wrong_query(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'Product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400],
            'region': ['North', 'North', 'North', 'West']
        }
        df = pandas.DataFrame(data)
        parameters = {"groups": [{"query": "SELECT"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=df, parameters=parameters)
        self.assertEqual("Failed to perform sql operations.Parser Error: SELECT clause without selection list", str(test_function.value))

    def test_drop_na(self):
        transformer = DropNa()
        data = {"name": ['Alfred', 'Batman', 'Catwoman'],
                    "toy": [numpy.nan, 'Batmobile', 'Bullwhip'],
                    "born": [pandas.NaT, pandas.Timestamp("1940-04-25"), pandas.NaT]
                }
        dataframe = pandas.DataFrame(data)
        parameters = None
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["Batman"], "toy": ["Batmobile"], "born": [pandas.Timestamp("1940-04-25")]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Dropped NaN values"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_drop_na_with_subset(self):
        transformer = DropNa()
        data = {"name": ['Alfred', 'Batman', 'Catwoman'],
                    "toy": [numpy.nan, 'Batmobile', 'Bullwhip'],
                    "born": [pandas.NaT, pandas.Timestamp("1940-04-25"), pandas.NaT]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"subset":['name', 'toy']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["Batman", "Catwoman"], "toy": ["Batmobile", "Bullwhip"], "born": [pandas.Timestamp("1940-04-25"), pandas.NaT]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Dropped NaN values for ['name', 'toy'] columns"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)


    def test_sql_operations_with_query_as_none(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": None}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)

        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
        self.assertFalse(new_df)

    def test_sql_operations_with_query_as_empty_list(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"query": ""}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)

        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
        self.assertFalse(new_df)

    def test_sql_operations_without_query(self):
        transformer = SqlOperations()
        # Create a DataFrame
        data = {
            'product': ['A', 'B', 'C', 'D'],
            'sales': [800, 1200, 950, 1400]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)

        expected_message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
        self.assertEqual(expected_message, actual_message)
        self.assertFalse(success)
        self.assertFalse(metadata)
        self.assertFalse(new_df)

    def test_trim_without_number_of_characters_parameter(self):
        transformer = Trim()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["davangere", "banglore", "hyderabad"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "location": "right"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = f"Successfully trimmed column(s) name to '1' character(s) to its right."
        expected_data = [['a', 'davangere', 10, 40], ['a', 'banglore', 11, 39], ['a', 'hyderabad', 12, 45]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        self.assertEqual(expected_message, actual_message)

    def test_trim_without_location_parameter(self):
        transformer = Trim()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["davangere", "banglore", "hyderabad"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "number_of_characters": 1}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = f"Successfully trimmed column(s) name to '1' character(s) to its left."
        expected_data = [['p', 'davangere', 10, 40], ['k', 'banglore', 11, 39], ['b', 'hyderabad', 12, 45]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        self.assertEqual(expected_message, actual_message)

    def test_trim_with_integer_column(self):
        transformer = Trim()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["davangere", "banglore", "hyderabad"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["age"], "number_of_characters": 1}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = f"Successfully trimmed column(s) age to '1' character(s) to its left."
        expected_data =[['pooja', 'davangere', '1', 40], ['kavya', 'banglore', '1', 39],['bhavya', 'hyderabad', '1', 45]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        self.assertEqual(expected_message, actual_message)

    def test_trim_without_location_parameter_with_exceed_number_of_characters(self):
        transformer = Trim()
        # Create a DataFrame
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["davangere", "banglore", "hyderabad"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": ["name"], "number_of_characters": 10}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = f"Successfully trimmed column(s) name to '10' character(s) to its left."
        expected_data = [['pooja', 'davangere', 10, 40],
                         ['kavya', 'banglore', 11, 39],
                         ['bhavya', 'hyderabad', 12, 45]]
        self.assertEqual(expected_data, actual_dataframe.values.tolist())
        self.assertEqual(expected_message, actual_message)

    def test_upper_case_without_column_parameter(self):
        transformer = UpperCase()
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "city": ["dvg", "bng", "hyd"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"columns": []}, {"columns": []}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
        self.assertEqual(expected_message, actual_message)


    def test_union_df_with_parameters_with_unknown_columns(self):
        transformer = UnionDf()
        # Create a DataFrame
        students_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'grade': [10, 11, 9]
        }
        dataframe1 = pandas.DataFrame(students_data)
        teachers_data = {
            'id': [101, 102, 103],
            'name': ['Ms. Smith', 'Mr. Johnson', 'Mrs. Brown'],
            'grade': [10, 11, 9]
        }
        dataframe2 = pandas.DataFrame(teachers_data)
        dataframe = [dataframe1, dataframe2]
        parameters = {"groups":  [{"columns": ["grade1"]}], "file_names": ["test_file1", "test_file2"],}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to perform union" in str(test_function.value))
        
    def test_drop_na(self):
        transformer = DropNa()
        data = {"name": ['Alfred', 'Batman', 'Catwoman'],
                    "toy": [numpy.nan, 'Batmobile', 'Bullwhip'],
                    "born": [pandas.NaT, pandas.Timestamp("1940-04-25"), pandas.NaT]
                }
        dataframe = pandas.DataFrame(data)
        parameters = None
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["Batman"], "toy": ["Batmobile"], "born": [pandas.Timestamp("1940-04-25")]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Dropped NaN values"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_drop_na_with_subset(self):
        transformer = DropNa()
        data = {"name": ['Alfred', 'Batman', 'Catwoman'],
                    "toy": [numpy.nan, 'Batmobile', 'Bullwhip'],
                    "born": [pandas.NaT, pandas.Timestamp("1940-04-25"), pandas.NaT]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"subset":['name', 'toy']}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"name": ["Batman", "Catwoman"], "toy": ["Batmobile", "Bullwhip"], "born": [pandas.Timestamp("1940-04-25"), pandas.NaT]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Dropped NaN values for ['name', 'toy'] columns"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_extract_year(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"column": "joining_date", "component": ["year"], "destination_column": "joining_year"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_dataframe = pandas.DataFrame({'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00'],
                                            'year_column': [2024, 2024, 2025]})
        expected_dataframe['joining_date'] = pandas.to_datetime(expected_dataframe['joining_date'])
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Extracted '['year']' from 'joining_date' column"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_extract_month(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"column": "joining_date", "component": ["month"], "destination_column": "joining_month"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_dataframe = pandas.DataFrame({'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00'],
                                            'year_column': [4, 4, 5]})
        expected_dataframe['joining_date'] = pandas.to_datetime(expected_dataframe['joining_date'])
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Extracted '['month']' from 'joining_date' column"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_extract_day(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"column": "joining_date", "component": ["day"], "destination_column": "joining_day"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe=dataframe,
                                                                                  parameters=parameters)
        expected_dataframe = pandas.DataFrame({'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00'],
                                            'year_column': [29, 30, 1]})
        expected_dataframe['joining_date'] = pandas.to_datetime(expected_dataframe['joining_date'])
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Extracted '['day']' from 'joining_date' column"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_extract_with_component_as_none(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"column": "joining_date", "component": None, "destination_column": "joining_day"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to extract" in str(test_function.value))
    
    def test_extract_with_component_as_empty_string(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"column": "joining_date", "component": "", "destination_column": "joining_day"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to extract" in str(test_function.value))

    def test_extract_without_component(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"column": "joining_date", "destination_column": "joining_day"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to extract" in str(test_function.value))
        
    def test_extract_with_column_as_none(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"column": None, "component": ["day"], "destination_column": "joining_day"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to extract." in str(test_function.value))
    
    def test_extract_with_column_as_empty_string(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"column": "", "component": ["day"], "destination_column": "joining_day"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column'].", str(test_function.value))

    def test_extract_without_column(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"component": ["day"], "destination_column": "joining_day"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to extract" in str(test_function.value))
        
    def test_extract_without_column_component(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['2024-04-29 08:30:00', '2024-04-30 09:45:00', '2025-05-01 10:15:00']}
        dataframe = pandas.DataFrame(data)
        dataframe['joining_date'] = pandas.to_datetime(dataframe['joining_date'])
        parameters = {"groups": [{"destination_column": "joining_day"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertTrue("Failed to extract" in str(test_function.value))

    def test_extract_year_from_non_date_column(self):
        transformer = Extract()
        # Create a DataFrame
        data = {'joining_date': ['test', 'test1', 'test2']}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"column": "joining_date", "component": ["year"], "destination_column": "joining_year"}]}
        with pytest.raises(DataTransformationException) as test_function:
            transformer.execute(dataframe=dataframe, parameters=parameters)
        self.assertEqual("Failed to extract.The column 'joining_date' provided is not in date format. Please cast it to date type to change the format.", str(test_function.value))

    def test_fill_na_with_value(self):
        transformer = FillNa()
        data = {
                  "A": [1, 2, None],
                  "B": [None, 5, 6]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"value": 0}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"A": [1, 2, 0], "B": [0, 5, 6]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Filled NaN values with '0' value"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_fill_na_with_dictionary(self):
        transformer = FillNa()
        data = {
                  "A": [1, 2, None],
                  "B": [None, 5, 6]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"value": {'A': 0, 'B': 10}}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"A": [1, 2, 0], "B": [10, 5, 6]})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Filled NaN values with '{'A': 0, 'B': 10}' value"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_fill_na_with_value_axis(self):
        transformer = FillNa()
        data = {
                  'name': ['John', 'Jane', 'Jade', 'Jan'], 
                  'age': [25, 30, 35, 40], 
                  'city': ['New York', None, 'Paris', None]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"value": "Unknown", "axis": "columns"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({'name': ['John', 'Jane', 'Jade', 'Jan'], 'age': [25, 30, 35, 40], 'city': ['New York', 'Unknown', 'Paris', 'Unknown']})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Filled NaN values with 'Unknown' along the columns"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_fill_na_with_value_column(self):
        transformer = FillNa()
        data = {
                'name': ['John', 'Jane', 'Jade', 'Jan'], 
                'age': [25, 30, 35, 40], 
                'city': [None, 'London', 'Paris', None]
               }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"column": "city", "value": "No City"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({'name': ['John', 'Jane', 'Jade', 'Jan'], 'age': [25, 30, 35, 40], 'city': ['No City', 'London', 'Paris', 'No City']})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = f"Filled NaN values in column 'city' with 'No City' value"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_fill_na_with_ffill(self):
        transformer = FillNa()
        data = {
                  "A": [1, None, 3, None],
                  "B": [None, 5, None, 7]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"method": "ffill"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"A": [1, 1, 3, 3], "B": [None, 5, 5, 7]})
        np.testing.assert_array_equal(actual_dataframe.values, expected_dataframe.values)
        expected_message = "Filled NaN values using ffill method"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_fill_na_with_bfill(self):
        transformer = FillNa()
        data = {
                  "A": [1, None, 3, None],
                  "B": [None, 5, None, 7]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"method": "bfill"}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"A": [1, 3, 3, None], "B": [5, 5, 7, 7]})
        np.testing.assert_array_equal(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Filled NaN values using bfill method"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_fill_na_with_ffill_column_limit(self):
        transformer = FillNa()
        data = {'name': ['John', 'Jane', 'Jade', 'Jan'], 
                'age': [25, 30, 35, 40], 
                'city': ['New York', None, None, 'Paris']}
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{"column": "city", "method": "ffill", "limit": 1}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({'name': ['John', 'Jane', 'Jade', 'Jan'], 'age': [25, 30, 35, 40], 'city': ['New York', 'New York', None, 'Paris']})
        self.assertEqual(actual_dataframe.values.tolist(), expected_dataframe.values.tolist())
        expected_message = "Filled NaN values in column 'city' using ffill method with limit 1"
        self.assertEqual(actual_message, expected_message)
        self.assertTrue(success)
        self.assertTrue(metadata)

    def test_fill_na_without_value_method(self):
        transformer = FillNa()
        data = {
                  "A": [1, None, 3, None],
                  "B": [None, 5, None, 7]
                }
        dataframe = pandas.DataFrame(data)
        parameters = {"groups": [{}]}
        actual_dataframe, success, metadata, actual_message, new_df, details = transformer.execute(dataframe, parameters)
        expected_dataframe = pandas.DataFrame({"A": [1, 3, 3, None], "B": [5, 5, 7, 7]})
        expected_message = "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."
        self.assertEqual(actual_message, expected_message)
        self.assertFalse(success)
        self.assertFalse(metadata)


if __name__ == "__main__":
    unittest.main()
