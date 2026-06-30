import re
import unittest
import pandas

from src.etl.transfrom.transformations_utilities.utilities import TransformerUtilities

util = TransformerUtilities()


class TestTransformerUtilities(unittest.TestCase):
    def test_get_pattern(self):
        target_character = "/"
        actual_output = util.get_pattern(target_character)
        expected_output = re.compile('[/]+')
        self.assertEqual(expected_output, actual_output)

    def test_get_pattern_if_target_character_is_None(self):
        target_character = None
        actual_output = util.get_pattern(target_character)
        expected_output = re.compile('[\\s\\W]+')
        self.assertEqual(expected_output, actual_output)

    def test_get_new_column_names(self):
        new_column = "name"
        columns_list = ["name", "age"]
        actual_output = util.get_new_column_name(new_column, columns_list)
        expected_output = "name_1"
        self.assertEqual(expected_output, actual_output)

    def test_get_new_column_names_increment(self):
        new_column = "name"
        columns_list = ["name", "name_1", "age"]
        actual_output = util.get_new_column_name(new_column, columns_list)
        expected_output = "name_2"
        self.assertEqual(expected_output, actual_output)

    def test_get_new_columns(self):
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19]
        }
        df = pandas.DataFrame(data)
        group = {"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS __newcolumn__\nFROM df;"}
        actual_result, actual_group = util.get_new_columns(group, df)
        expected_output = ['new_column_1']
        expected_group = {"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS new_column_1\nFROM df;"}
        self.assertEqual(expected_output, actual_result)
        self.assertEqual(expected_group, actual_group)

    def test_get_new_columns_for_increment(self):
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 19],
            "new_column_1": [1, 1, 1]
        }
        df = pandas.DataFrame(data)
        group = {"query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS __newcolumn__\nFROM df;"}
       
        actual_result, actual_group = util.get_new_columns(group, df)
        expected_output = ['new_column_2']
        expected_group = {
            "query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS new_column_2\nFROM df;"}
        self.assertEqual(expected_output, actual_result)
        self.assertEqual(expected_group, actual_group)

    def test_get_format(self):
        date_format = "ymd"
        actual_output = util.get_format(date_format)
        expected_output = "%Y%m%d"
        self.assertEqual(expected_output, actual_output)

    def test_get_unique_columns(self):
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        splitted_columns_df = dataframe["name"].str.split("_", expand=True)
        group = {'destination_columns': ['first_name', 'last_name'], 'columns': 'name', 'delimiter': '_'}
        unique_columns_df, group = util.get_unique_columns(splitted_columns_df, group, dataframe)
        expected_output = ['first_name', 'last_name']
        self.assertEqual(expected_output, unique_columns_df.columns.tolist())

    def test_get_unique_columns_less_length(self):
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        splitted_columns_df = dataframe["name"].str.split("_", expand=True)
        group = {'destination_columns': ['first_name'], 'column': 'name', 'delimiter': '_'}
        unique_columns_df, group = util.get_unique_columns(splitted_columns_df, group, dataframe)
        expected_output = ['first_name', 'new_column_1']
        self.assertEqual(expected_output, unique_columns_df.columns.tolist())

    def test_get_distinct_columns_less_length(self):
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        columns = ["name", "age"]
        distinct_columns= util.get_distinct_columns(columns, dataframe)
        expected_output = ['name_1', 'age_1']
        self.assertEqual(expected_output, distinct_columns)

    def test_generate_query(self):
        column = "marks"
        expr = "equals"
        value = 50
        actual_output = util.generate_query(column, expr, value)
        expected_output = "marks==50"
        self.assertEqual(expected_output, actual_output)

    def test_get_aggregate_function(self):
        aggregations = ["distinct"]
        actual_output = util.get_aggregate_function(aggregations)
        expected_output = ['nunique']
        self.assertEqual(expected_output, actual_output)

    def test_get_column_datatype_dict(self):
        data = {
            "name": ["pooja_shanmuk", "kavya_shetty", "bhavya_gowda"],
            "age": [10, 11, 12],
            "marks": [40, 39, 45]
        }
        dataframe = pandas.DataFrame(data)
        actual_output = util.get_column_datatype_dict(dataframe)
        expected_output = [{'name': 'name', 'dataType': 'object'},
                           {'name': 'age', 'dataType': 'int64'},
                           {'name': 'marks', 'dataType': 'int64'}]
        self.assertEqual(expected_output, actual_output)

    def test_generate_alias(self):
        dataframe_dict = {
            "source_id_1": {"alias": "dataframe_1"},
            "source_id_2": {"alias": "dataframe_2"},
            "source_id_3": {"alias": "df_union_1"},
            "source_id_4": {"alias": "df_union_2"}
        }
        new_alias = util.generate_alias(dataframe_dict, "df_union")
        self.assertEqual(new_alias, "df_union_3")
        new_alias = util.generate_alias(dataframe_dict, "df_join")
        self.assertEqual(new_alias, "df_join_1")


if __name__ == '__main__':
    unittest.main()
