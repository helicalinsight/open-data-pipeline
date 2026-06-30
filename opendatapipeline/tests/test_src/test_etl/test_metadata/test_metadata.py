import unittest
from unittest.mock import Mock
import pandas
from numpy import *
import pytest

from src.etl.metadata.metadata import Metadata

class TestMetadata(unittest.TestCase):
    # creating the instance of the class Metadata
    @classmethod
    def setUpClass(cls):
        cls.metadata = Metadata()
        # Create a DataFrame with missing values
        data = {'A': [1, 2, None], 'B': [4, None, 6], 'C': [None, 8, 9]}
        cls.df = pandas.DataFrame(data)

    def test_04_column_names(self):
        self.metadata.column_names(self.df)
        expected_dict = {'column_names': ['A', 'B', 'C']}
        self.assertEqual(self.metadata.column_info_dict, expected_dict)

    def test_05_datatypes(self):
        self.metadata.datatypes(self.df)
        expected_dict = {'column_names': ['A', 'B', 'C'], 'datatypes': {'A': dtype('float64'), 'B': dtype('float64'),
                                                                        'C': dtype('float64')}}
        self.assertEqual(self.metadata.column_info_dict, expected_dict)

    def test_06_num_of_columns(self):
        self.metadata.num_of_columns(self.df)
        expected_dict = {'column_names': ['A', 'B', 'C'], 'datatypes': {'A': 'float64', 'B': 'float64', 'C': 'float64'},
                         'num_of_columns': 3}
        self.assertEqual(self.metadata.column_info_dict, expected_dict)

    @pytest.mark.skip()
    def test_07_num_of_rows(self):
        self.metadata.num_of_rows(self.df)
        expected_dict = {'column_names': ['A', 'B', 'C'], 'datatypes': {'A': 'float64', 'B': 'float64', 'C': 'float64'},
                         'num_of_columns': 3, 'num_of_rows': 3}
        self.assertEqual(self.metadata.column_info_dict, expected_dict)

    @pytest.mark.skip("code commented")
    def test_08_missing_values(self):
        self.metadata.missing_values(self.df)
        expected_dict = {'column_names': ['A', 'B', 'C'], 'datatypes': {'A': 'float64', 'B': 'float64', 'C': 'float64'},
                         'num_of_columns': 3, 'num_of_rows': 3, 'missing_values': {'A': 1, 'B': 1, 'C': 1}}
        self.assertEqual(self.metadata.column_info_dict, expected_dict)

    @pytest.mark.skip("code commented")
    def test_09_summary_statistics(self):
        self.metadata.summary_statistics(self.df)
        expected_dict = {'summary_statistics': {'A': {'count': 2.0, 'mean': 1.5, 'std': 0.7071067811865476, 'min': 1.0,
                                                      '25%': 1.25, '50%': 1.5, '75%': 1.75, 'max': 2.0},
                                                'B': {'count': 2.0, 'mean': 5.0, 'std': 1.4142135623730951, 'min': 4.0,
                                                      '25%': 4.5, '50%': 5.0, '75%': 5.5, 'max': 6.0},
                                                'C': {'count': 2.0, 'mean': 8.5, 'std': 0.7071067811865476, 'min': 8.0,
                                                      '25%': 8.25, '50%': 8.5, '75%': 8.75, 'max': 9.0}}}
        self.assertEqual(self.metadata.statistics_dict, expected_dict)

    @pytest.mark.skip("code commented")
    def test_10_skewness(self):
        df_no_nan = self.df.fillna(0)
        self.metadata.skewness(df_no_nan)
        expected_dict = {'summary_statistics': {'A': {'count': 2.0, 'mean': 1.5, 'std': 0.7071067811865476, 'min': 1.0,
                                                      '25%': 1.25, '50%': 1.5, '75%': 1.75, 'max': 2.0},
                                                'B': {'count': 2.0, 'mean': 5.0, 'std': 1.4142135623730951, 'min': 4.0,
                                                      '25%': 4.5, '50%': 5.0, '75%': 5.5, 'max': 6.0},
                                                'C': {'count': 2.0, 'mean': 8.5, 'std': 0.7071067811865476, 'min': 8.0,
                                                      '25%': 8.25, '50%': 8.5, '75%': 8.75, 'max': 9.0}},
                         'skewness': {'A': df_no_nan['A'].skew(), 'B': df_no_nan['B'].skew(),
                                      'C': df_no_nan['C'].skew()}}
        self.assertEqual(self.metadata.statistics_dict, expected_dict)

    @pytest.mark.skip("pending")
    def test_11_kurtosis(self):
        """
        pending
        """
        df_no_nan = self.df.fillna(0)
        self.metadata.kurtosis(self.df)
        self.metadata.kurtosis(df_no_nan)
        expected_dict = {'summary_statistics': {'A': {'count': 2.0, 'mean': 1.5, 'std': 0.7071067811865476, 'min': 1.0,
                                                      '25%': 1.25, '50%': 1.5, '75%': 1.75, 'max': 2.0},
                                                'B': {'count': 2.0, 'mean': 5.0, 'std': 1.4142135623730951, 'min': 4.0,
                                                      '25%': 4.5, '50%': 5.0, '75%': 5.5, 'max': 6.0},
                                                'C': {'count': 2.0, 'mean': 8.5, 'std': 0.7071067811865476, 'min': 8.0,
                                                      '25%': 8.25, '50%': 8.5, '75%': 8.75, 'max': 9.0}},
                         'skewness': {'A': df_no_nan['A'].skew(), 'B': df_no_nan['B'].skew(),
                                      'C': df_no_nan['C'].skew()},
                         'kurtosis': {'A': df_no_nan['A'].kurtosis(), 'B': df_no_nan['B'].kurtosis(),
                                      'C': df_no_nan['C'].kurtosis()}}
        expected_dict = {'kurtosis': {'A': df_no_nan['A'].kurtosis(), 'B': df_no_nan['B'].kurtosis(),
                                      'C': df_no_nan['C'].kurtosis()}}
        self.assertEqual(self.metadata.statistics_dict, expected_dict)

    @pytest.mark.skip("code commented")
    def test_12_quantiles(self):
        self.metadata.quantiles(self.df)
        expected_dict = {'summary_statistics': {'A': {'count': 2.0, 'mean': 1.5, 'std': 0.7071067811865476, 
                                                'min': 1.0, '25%': 1.25, '50%': 1.5, '75%': 1.75, 'max': 2.0}, 
                                                'B': {'count': 2.0, 'mean': 5.0, 'std': 1.4142135623730951, 
                                                'min': 4.0, '25%': 4.5, '50%': 5.0, '75%': 5.5, 'max': 6.0}, 
                                                'C': {'count': 2.0, 'mean': 8.5, 'std': 0.7071067811865476, 
                                                'min': 8.0, '25%': 8.25, '50%': 8.5, '75%': 8.75, 'max': 9.0}}, 
                                                'skewness': {'A': 0.0, 'B': -0.9352195295828248, 
                                                'C': -1.6523167403329906}, 'quantiles': {'A': 
                                                {'0.25': 1.25, '0.5': 1.5, '0.75': 1.75}, 'B': 
                                                {'0.25': 4.5, '0.5': 5.0, '0.75': 5.5}, 'C': 
                                                {'0.25': 8.25, '0.5': 8.5, '0.75': 8.75}}}
        self.assertEqual(self.metadata.statistics_dict, expected_dict)

    @pytest.mark.skip("code commented")
    def test_13_categorized_data(self):
        data = {'ID': [1, 2, 3, 4, 5],
                'Temperature': [20.5, 25.3, 30, 22.8, 18.2],
                'Gender': ['male', 'female', 'male', 'female', 'female'],
                'Grades': ['excellent', 'good', 'average', 'bad', 'worst']}
        df = pandas.DataFrame(data)
        self.metadata.categorized_data(df)
        expected_dict = {'categorized_data': {'categorical': {'nominal': ['Grades'],
                                                              'ordinal': ['Gender']},
                                              'numerical': {'continuous': ['ID', 'Temperature'],
                                                            'discrete': []}}}
        self.assertEqual(self.metadata.categorical_dict, expected_dict)

    def test_99_execute(self):
        test_data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
        mock_df = Mock()
        mock_df.columns = ['A', 'B']
        mock_df.return_value = test_data
        mock_file_name = "test_file.csv"
        mock_file_path = "/path/to/test_file.csv"
        result = self.metadata.execute(mock_df)
        print('result', result)
        #self.assertEqual(result["file_information"], mock_file_name)


if __name__ == '__main__':
    unittest.main()