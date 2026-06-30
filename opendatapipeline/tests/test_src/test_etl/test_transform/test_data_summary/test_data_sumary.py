import unittest
import pytest
import pandas

from src.etl.transfrom.data_summary.data_summary import DataSummary
from src.exceptions.exception import *

# @pytest.mark.skip("Parameters Missing")
class TestDataSummary(unittest.TestCase):
    def test_file_preview(self):
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        alias = "csv file"
        source_id = "6602a3a74475001648200351"
        success, actual_result = DataSummary().file_preview(dataframe, source_id, alias)

        expected_result = [{'_id': '6602a3a74475001648200351', 'alias': 'csv file', 'total_records': 3,
                            'total_records_dataframe': 3, 'columns': [
                                        {'name': 'name', 'dataType': 'object'},
                                        {'name': 'age', 'dataType': 'int64'},
                                        {'name': 'marks', 'dataType': 'int64'}],
                            'data': [{'name': 'pooja', 'age': 10, 'marks': 40},
                                     {'name': 'kavya', 'age': 11, 'marks': 39},
                                     {'name': 'bhavya', 'age': 12, 'marks': 45}]}]
        self.assertEqual(actual_result, expected_result)
        self.assertTrue(success)

    def test_file_preview_date_column(self):
        data = {
            "date": ["1/2/2024", "1/2/2024", "1/2/2024"]
        }
        dataframe = pandas.DataFrame(data)
        dataframe['date'] = pandas.to_datetime(dataframe['date'])
        alias = "csv file"
        source_id = "6602a3a74475001648200351"
        success, actual_result = DataSummary().file_preview(dataframe, source_id, alias)

        expected_result = [{'_id': '6602a3a74475001648200351',
                      'alias': 'csv file',
                      'columns': [{'dataType': 'datetime64[ns]', 'name': 'date'}],
                      'data': [{'date': '2024-01-02'},
                               {'date': '2024-01-02'},
                               {'date': '2024-01-02'}],
                      'total_records': 3,
                      'total_records_dataframe': 3}]
        self.assertEqual(actual_result, expected_result)
        self.assertTrue(success)

    def test_file_preview_without_dataframe(self):
        dataframe = None
        alias = "csv file"
        source_id = "6602a3a74475001648200351"
        with pytest.raises(PreviewException) as test_function:
            DataSummary().file_preview(dataframe, source_id, alias)
        self.assertEqual("Failed to preview the data.", str(test_function.value))

    def test_file_preview_with_empty_dataframe(self):
        data = {}
        dataframe = pandas.DataFrame(data)
        alias = "csv file"
        source_id = "6602a3a74475001648200351"
        success, actual_result = DataSummary().file_preview(dataframe, source_id, alias)
        expected_result = [{'_id': '6602a3a74475001648200351', 'alias': 'csv file', 'total_records': 0,
                            'total_records_dataframe': 0, 'columns': [], 'data': []}]
        self.assertEqual(actual_result, expected_result)
        self.assertTrue(success)

    def test_file_preview_with_empty_string_and_None_values(self):
        data = {
            "name": ["Alice", "Bob", None, "Eve", ""],
            "description": ["Hello!", None, "Special characters: é, ç, ö", None, ""],
            "date": ["2024-01-01", None, None, "2024-04-25", ""],
            "binary_data": [b"binary1", None, b"binary3", b"binary4", None],
            "empty_column": [None, None, None, None, None]
        }
        dataframe = pandas.DataFrame(data)
        dataframe["date"] = pandas.to_datetime(dataframe["date"], errors="coerce")
        id = "12345"
        alias = "df_with_empty_strings_and_None_values"
        success, actual_result = DataSummary().file_preview(dataframe, id, alias)
        expected_result = [
            {
                '_id': '12345', 
                'alias': 'df_with_empty_strings_and_None_values', 
                'total_records': 5, 
                'total_records_dataframe': 5, 
                'columns': [
                    {'name': 'name', 'dataType': 'object'}, 
                    {'name': 'description', 'dataType': 'object'}, 
                    {'name': 'date', 'dataType': 'datetime64[ns]'}, 
                    {'name': 'binary_data', 'dataType': 'object'}, 
                    {'name': 'empty_column', 'dataType': 'object'}
                ], 
                'data': [
                    {'name': 'Alice', 'description': 'Hello!', 'date': '2024-01-01', 'binary_data': 'YmluYXJ5MQ==', 'empty_column': None},
                    {'name': 'Bob', 'description': None, 'date': 'NaT', 'binary_data': None, 'empty_column': None},
                    {'name': None, 'description': 'Special characters: é, ç, ö', 'date': 'NaT', 'binary_data': 'YmluYXJ5Mw==', 'empty_column': None},
                    {'name': 'Eve', 'description': None, 'date': '2024-04-25', 'binary_data': 'YmluYXJ5NA==', 'empty_column': None},
                    {'name': "", 'description': "", 'date': 'NaT', 'binary_data': None, 'empty_column': None}
                ]
            }
        ]
        self.assertEqual(actual_result, expected_result)
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
