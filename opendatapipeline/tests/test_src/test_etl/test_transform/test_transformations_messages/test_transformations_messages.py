import unittest

from src.etl.transfrom.transformations_messages.transformations_messages import Messages


class TransformationMessages(unittest.TestCase):
    def test_add_columns_messages_true(self):
        parameters = {"groups": [{"columns": ["school"], "default": "MNS"}]}
        actual_message = Messages().add_columns(parameters, True)
        expected_message = "Successfully added column(s) school with default value MNS."
        self.assertEqual(expected_message, actual_message)

    def test_add_columns_messages_for_multiple_groups_true(self):
        parameters = {"groups": [{"columns": ["school"], "default": "MNS"},
                                 {"columns": ["city"], "default": "DVG"}]}
        actual_message = Messages().add_columns(parameters, True)
        expected_message = "Successfully added column(s) school with default value MNS and city with default value DVG."
        self.assertEqual(expected_message, actual_message)

    def test_rename_columns_messages_true(self):
        parameters = {"groups": [{"old_name": "name", "new_name": "Fullname"},
                                 {"old_name": "age", "new_name": "Age"}]}
        actual_message = Messages().rename_columns(parameters, True)
        expected_message = "Successfully renamed column(s) name with Fullname and age with Age."
        self.assertEqual(expected_message, actual_message)

    def test_sort_messages_true(self):
        parameters = {"groups": [{"columns": ["age"], "ascending": True},
                                 {"columns": ["marks"], "ascending": True}] }
        actual_message = Messages().sort(parameters, True)
        expected_message = "Successfully sorted column(s) age and marks."
        self.assertEqual(expected_message, actual_message)

    def test_drop_columns_messages_true(self):
        parameters = {"groups": [{"columns": ["age"]}]}
        actual_message = Messages().drop_columns(parameters, True)
        expected_message = "Successfully dropped column(s) age."
        self.assertEqual(expected_message, actual_message)

    def test_drop_columns_messages_with_multiple_groups_true(self):
        parameters = {"groups": [{"columns": ["age"]}, {"columns": ["marks"]}]}
        actual_message = Messages().drop_columns(parameters, True)
        expected_message = "Successfully dropped column(s) age and marks."
        self.assertEqual(expected_message, actual_message)

    def test_drop_all_columns_except_messages_true(self):
        parameters = {"groups": [{"columns": ["name", "age"]}]}
        actual_message = Messages().drop_all_columns_except(parameters, True)
        expected_message = "Successfully dropped all column(s) except name and age."
        self.assertEqual(expected_message, actual_message)

    def test_drop_all_columns_except_messages_for_multiple_groups_true(self):
        parameters = {"groups": [{"columns": ["name", "age"]}, {"columns": ["marks", "percent"]}]}
        actual_message = Messages().drop_all_columns_except(parameters, True)
        expected_message = "Successfully dropped all column(s) except name and age and marks and percent."
        self.assertEqual(expected_message, actual_message)

    def test_deduplicate_messages_true(self):
        parameters = {"groups": [{"columns": ["name"]}]}
        actual_message = Messages().deduplicate(parameters, True)
        expected_message = "Successfully deduplicated column(s) name."
        self.assertEqual(expected_message, actual_message)

    def test_deduplicate_messages_for_multiple_groups_true(self):
        parameters = {"groups": [{"columns": ["name"]}, {"columns": ["marks"]}]}
        actual_message = Messages().deduplicate(parameters, True)
        expected_message = "Successfully deduplicated column(s) name and marks."
        self.assertEqual(expected_message, actual_message)

    def test_split_messages_true(self):
        parameters = {"groups": [{"destination_columns": ["first_name", "last_name"], "column": "name", "delimiter": "_"}]}
        actual_message = Messages().split(parameters, True)
        expected_message = "Successfully splitted column(s) name into first_name, last_name at the delimiter '_'."
        self.assertEqual(expected_message, actual_message)

    def test_replace_special_characters_messages_true(self):
        parameters = { "delimiter": None, "groups": [{"target_character": "_", "columns": ["name"], "replacement_character": "-"}]}
        actual_message = Messages().replace_special_characters(parameters, True)
        expected_message = "Successfully replaced special characters in column(s) name: _ to -."
        self.assertEqual(expected_message, actual_message)

    def test_concat_messages_true(self):
        parameters = {"groups": [{"columns": ["age", "marks"],
                         "separator": "/", "destination_column": "code"}]}
        actual_message = Messages().concat(parameters, True)
        expected_message = "Successfully concatenated column(s) age, marks with '/' to the column 'code'."
        self.assertEqual(expected_message, actual_message)

    def test_whenotherwise_messages_true(self):
        parameters = {"groups":[{"destination_column":"final_res", "query": "SELECT *, CASE\n\tWHEN marks > 39 THEN 'PASS'\n\tWHEN marks < 20 THEN 'FAIL'\n\tELSE 'MODERATE'\nEND AS final_res\nFROM df;"}]}
        actual_message = Messages().when_otherwise(parameters, True)
        expected_message = "When otherwise query executed and stored in final_res successfully."
        self.assertEqual(expected_message, actual_message)

    def test_filter_value_messages_true(self):
        parameters = {"groups": [{"columns": ["name"], "expr":"equals", "value":["Bob"]}]}
        actual_message = Messages().filter_value(parameters, True)
        expected_message = "Successfully filtered column(s) 'name' based on the given criteria."
        self.assertEqual(expected_message, actual_message)

    def test_filter_value_messages_for_multiple_groups_true(self):
        parameters = {"groups": [{"columns": ["name"], "expr":"equals", "value":["Bob"]},
                                        {"columns": ["marks"], "expr":"equals", "value":[50]}]}
        actual_message = Messages().filter_value(parameters, True)
        expected_message = "Successfully filtered column(s) 'name' and 'marks' based on the given criteria."
        self.assertEqual(expected_message, actual_message)

    def test_date_format_messages_true(self):
        parameters = {"groups": [{"columns": ["exam_date"], "format": "YYYY.mm.DD"}]}
        actual_message = Messages().date_format(parameters, True)
        expected_message = "Successfully updated the format of the date for the column(s) exam_date to 'YYYY.mm.DD'."
        self.assertEqual(expected_message, actual_message)

    def test_correlation_messages_true(self):
        parameters = { "groups": [ {"columns": ["age", "marks"],  "destination_column":"age-marks-correlation"}]}
        actual_message = Messages().correlation(parameters, True)
        expected_message = "Successfully calculated correlation for the column(s) age, marks to age-marks-correlation."
        self.assertEqual(expected_message, actual_message)

    def test_trim_messages_true(self):
        parameters = {"groups": [{"number_of_characters": 1, "location": "right", "columns":["name"]},
                                    {"number_of_characters": 2, "location": "left", "columns":["city"]}]}
        actual_message = Messages().trim(parameters, True)
        expected_message = "Successfully trimmed column(s) name to '1' character(s) to its right, city to '2' character(s) to its left."
        self.assertEqual(expected_message, actual_message)

    def test_upper_case_messages_true(self):
        parameters = {"groups": [{"columns": ["name"]}, {"columns": ["city"]}]}
        actual_message = Messages().upper_case(parameters, True)
        expected_message = "Successfully updated column(s) name to uppercase, city to uppercase."
        self.assertEqual(expected_message, actual_message)

    def test_lower_case_messages_true(self):
        parameters = {"groups": [{"columns": ["name"]}, {"columns": ["city"]}]}
        actual_message = Messages().lower_case(parameters, True)
        expected_message = "Successfully updated column(s) name to lowercase, city to lowercase."
        self.assertEqual(expected_message, actual_message)

    def test_union_messages_true(self):
        parameters = {"groups":  [{"columns": ["grade"]}],"file_names": ["test_file1", "test_file2"],}
        actual_message = Messages().union(parameters, True)
        expected_message = "Successfully performed union based on column(s) grade for test_file1, test_file2."
        self.assertEqual(expected_message, actual_message)

    def test_joins_messages_true(self):
        parameters = {"groups": [{"join_type": "inner", "left_on": ["grade"], "right_on": ["grade"],
                                  }],"file_names": ["Students", "Enrollments"]
                      }
        actual_message = Messages().joins(parameters, True)
        expected_message = "Successfully performed joins on files Students, Enrollments on columns grade and grade with the type inner."
        self.assertEqual(expected_message, actual_message)

    def test_rearrange_columns_messages_true(self):
        parameters = {"groups": [{"columns": ['id', 'grade', 'name']}]}
        actual_message = Messages().rearrange_columns(parameters, True)
        expected_message = "Successfully rearranged column(s) in the given order "
        self.assertEqual(expected_message, actual_message)

    def test_cast_messages_true(self):
        parameters = {"groups": [{"columns": ["double_column"], "new_type": {"double_column":"float"}}]}
        actual_message, group = Messages().cast(parameters, True)
        expected_message = "Updated data type of the given column(s) double_column to 'float'."
        self.assertEqual(expected_message, actual_message)

    def test_cast_messages_with_multiple_groups_true(self):
        parameters = {"groups": [{"columns": ["double_column"], "new_type": {"double_column":"float"}},
                                 {"columns": ["int_column"], "new_type": {"int_column":"float"}}]}
        actual_message, group = Messages().cast(parameters, True)
        expected_message = "Updated data type of the given column(s) double_column to 'float' and int_column to 'float'."
        self.assertEqual(expected_message, actual_message)

    def test_aggregations_messages_true(self):
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
        actual_message = Messages().aggregations(parameters, True)
        expected_message = "Successfully performed aggregations on 'value1, value2' grouped by 'category, subcategory'."
        self.assertEqual(expected_message, actual_message)

    def test_arithmetic_messages_true(self):
        parameters = {"groups": [{"query": "units_sold+5", "destination_column": "units_total"}]}
        actual_message = Messages().arithmetic_operations(parameters, True)
        expected_message = "Arithmetic operation performed on the given query 'units_sold+5' and stored to 'units_total'."
        self.assertEqual(expected_message, actual_message)

    def test_sql_operations_messages_true(self):
        parameters = {"groups": [{"query": "SELECT * FROM df"}]}
        actual_message = Messages().sql_operations(parameters, True)
        expected_message = "Executed the given query 'SELECT * FROM df' successfully."
        self.assertEqual(expected_message, actual_message)


if __name__ == '__main__':
    unittest.main()
