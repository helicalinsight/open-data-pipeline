import unittest
import pandas

from src.etl.metadata.data_profile import DataProfile

class TestDataProfile(unittest.TestCase):
    # creating the instance of the class Metadata
    @classmethod
    def setUpClass(cls):
        cls.data_profile_dict = {}
        cls.data_profile = DataProfile()
        # Create a DataFrame with missing values
        data = {'A': [1, 2, 3, 4], 'B': [pandas.to_datetime('2022-01-01'), pandas.to_datetime('2022-02-01'),
                                         pandas.to_datetime('2022-03-01'), pandas.to_datetime('2022-04-01')],
                'C': ["a", "b", "c", "d"]}
        cls.df = pandas.DataFrame(data)
        cls.file_name = "test.csv"

    def test_01_columns(self):
        self.data_profile.columns(self.df)
        expected_dict = {'columns': ['A', 'B', 'C']}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_02_concat(self):
        self.data_profile.concat(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_03_date_format(self):
        self.data_profile.date_format(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}]}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_04_deduplicate(self):
        self.data_profile.deduplicate(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}],
                         'deduplicate': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_05_drop_all_columns_except(self):
        self.data_profile.drop_all_columns_except(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}],
                         'deduplicate': [], 'drop_all_columns_except': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_06_drop_columns(self):
        self.data_profile.drop_columns(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}],
                         'deduplicate': [], 'drop_all_columns_except': [], 'drop_columns': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_07_filter(self):
        self.data_profile.filter(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}],
                         'deduplicate': [], 'drop_all_columns_except': [], 'drop_columns': [], 'filter': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_08_rename_columns(self):
        self.data_profile.rename_columns(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}],
                         'deduplicate': [], 'drop_all_columns_except': [], 'drop_columns': [], 'filter': [],
                         'rename_columns': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_09_replace_special_characters(self):
        self.data_profile.replace_special_characters(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}],
                         'deduplicate': [], 'drop_all_columns_except': [], 'drop_columns': [], 'filter': [],
                         'rename_columns': [], 'replace_special_characters': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_10_sort(self):
        self.data_profile.sort(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}],
                         'deduplicate': [], 'drop_all_columns_except': [], 'drop_columns': [], 'filter': [],
                         'rename_columns': [], 'replace_special_characters': [], 'sort': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_11_split(self):
        self.data_profile.split(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}],
                         'deduplicate': [], 'drop_all_columns_except': [], 'drop_columns': [], 'filter': [],
                         'rename_columns': [], 'replace_special_characters': [], 'sort': [], 'split': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)

    def test_99_execute(self):
        self.data_profile.execute(self.df)
        expected_dict = {'columns': ['A', 'B', 'C'], 'concat': [], 'date_format': [{'B': {'format': '%Y-%m-%d'}}],
                         'deduplicate': [], 'drop_all_columns_except': [], 'drop_columns': [], 'filter': [],
                         'rename_columns': [], 'replace_special_characters': [], 'sort': [], 'split': []}
        self.assertEqual(self.data_profile.data_profile_dict, expected_dict)


if __name__ == '__main__':
    unittest.main()