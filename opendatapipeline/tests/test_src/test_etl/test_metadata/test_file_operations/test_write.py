import unittest
import os
import pandas
import pytest

from src.exceptions.exception import *
from src.etl.metadata.file_operations.write import Write
from src.etl.metadata.file_operations.write import convert_mixed_types_to_object

class TestWrite(unittest.TestCase):
    # creating the instance of the class Write
    @classmethod
    def setUpClass(cls):
        cls.write = Write()

    def test_write_feather(self):
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12]
        }
        dataframe = pandas.DataFrame(data)
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f87", ".cache",
                            "65cb43f2007a5f38718b9d6f",
                            "be687a30-1329-4639-a606-16f083afa6e132.feather")
        success, path = self.write.feather(dataframe, path)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(success)

    def test_write_feather_for_non_existing_path(self):
        data = {
            "name": ["pooja", "kavya", "bhavya"],
            "age": [10, 11, 12]
        }
        dataframe = pandas.DataFrame(data)
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "hadoop", "65365001d9654d9ec1172f87", ".cache",
                            "65cb43f2007a5f38718b9d6f",
                            "be687a30-1329-4639-a606-16f083afa6e111.feather")
        with pytest.raises(UtilsException) as test_function:
            self.write.feather(dataframe, path)
        self.assertEqual("Failed to write the feather file.", str(test_function.value))
        
    def test_convert_mixed_types_to_object_df_with_multiple_types_should_turn_to_object(self):
        import pandas as pd
        data = {
            "name": ["a", "b", "c"],
            "mixed_col": ["y", 1, "x"]
        }
        dataframe = pd.DataFrame(data)

        updated_dataframe = convert_mixed_types_to_object(dataframe)  # Updated function name

        # Ensure column is of object type
        self.assertEqual(updated_dataframe["mixed_col"].dtype, "object")

        # Ensure all elements are stored as objects
        types_in_mixed_col = updated_dataframe["mixed_col"].apply(type).value_counts()
        self.assertEqual(len(types_in_mixed_col), 1)

    def test_convert_mixed_types_to_object_df_with_multiple_types_should_not_turn_nan_and_nat(self):
        import pandas as pd
        import numpy as np
        import pandas.testing as pdt
        data = {
            "name": ["a", "b", "c", "d", "e"],
            "mixed_col": ["y", 1, "x", np.nan, pd.NaT]
        }
        dataframe = pd.DataFrame(data)

        updated_dataframe = convert_mixed_types_to_object(dataframe)  # Updated function name

        expected_data = {
            "name": ["a", "b", "c", "d", "e"],
            "mixed_col": ["y", "1", "x", np.nan, pd.NaT]
        }
        expected_dataframe = pd.DataFrame(expected_data)

        # Ensure NaN and NaT remain unchanged
        pdt.assert_frame_equal(updated_dataframe, expected_dataframe, check_dtype=False)

if __name__ == '__main__':
    unittest.main()
