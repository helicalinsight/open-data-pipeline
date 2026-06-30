import unittest
import os

import pandas
import pyarrow
import pytest

from src.etl.extract.file_operations.read import Read
from src.exceptions.exception import *
from ......tests.create_data import setup_files

class TestRead(unittest.TestCase):
    # creating the instance of the class Read
    @classmethod
    def setUpClass(cls) -> None:
        cls.read = Read()
        setup_files()

    def test_read_csv(self):
        settings = {
            "files": {
                "num_records": 6
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "dept.csv")
        success, df = self.read.csv(path, settings)
        self.assertEqual("public_id", df.columns.tolist()[0])
        self.assertEqual(len(df), 6)

    def test_read_csv_with_minus_one(self):
        settings = {
            "files": {
                "num_records": -1
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "dept.csv")
        success, df = self.read.csv(path, settings)
        self.assertEqual(len(df), 12)

    def test_read_csv_with_none(self):
        settings = {
            "files": {
                "num_records": None
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "dept.csv")
        success, df = self.read.csv(path, settings)
        self.assertEqual(len(df), 12)

    def test_read_csv_with_records_greater_than_existing(self):
        settings = {
            "files": {
                "num_records": 500
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "dept.csv")
        success, df = self.read.csv(path, settings)
        self.assertEqual(len(df), 12)

    def test_read_excel(self):
        settings = {
            "files": {
                "num_records": 2
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data1.xlsx")
        success, df = self.read.xlsx(path, settings)
        self.assertEqual("id", df.columns.tolist()[0])
        self.assertEqual(len(df), 2)

    def test_read_excel_with_minus_one(self):
        settings = {
            "files": {
                "num_records": -1
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data2.xlsx")
        success, df = self.read.xlsx(path, settings)
        self.assertEqual(len(df), 4)

    def test_read_excel_with_none(self):
        settings = {
            "files": {
                "num_records": None
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data2.xlsx")
        success, df = self.read.xlsx(path, settings)
        self.assertEqual(len(df), 4)

    def test_read_excel_with_exceed_data(self):
        settings = {
            "files": {
                "num_records": 400
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data1.xlsx")
        success, df = self.read.xlsx(path, settings)
        self.assertEqual("id", df.columns.tolist()[0])
        self.assertEqual(len(df), 4)

    def test_read_excel_with_exceed_data_xlsx(self):
        settings = {
            "files": {
                "num_records": 500
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data1.xlsx")
        success, df = self.read.xlsx(path, settings)
        self.assertEqual(len(df), 4)

    def test_read_excel_with_minus_one_xlsx(self):
        settings = {
            "files": {
                "num_records": -1
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data1.xlsx")
        success, df = self.read.xlsx(path, settings)
        self.assertEqual(len(df), 4)

    def test_read_excel_xlxs(self):
        settings = {
            "files": {
                "num_records": 1
            }
        }
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data1.xlsx")
        success, df = self.read.xlsx(path, settings)
        self.assertEqual(len(df), 1)

    def test_read_feather(self):
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        feather_file_path = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f87", ".cache",
                                         "65cb43f2007a5f38718b9d6f",
                                         "be687a30-1329-4639-a606-16f083afa6e6.feather")
        success, df = self.read.feather(feather_file_path)
        expected_column_names = ['id', 'name', 'age', 'join_date']
        self.assertEqual(expected_column_names, df.columns.tolist())
        self.assertEqual(len(df), 4)

    def test_csv_file_not_found(self):
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data9.csv")
        with pytest.raises(UtilsException) as test_function:
            self.read.csv(path)
        self.assertEqual("Failed to read the csv file.", str(test_function.value))

    def test_csv_empty_file(self):
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "empty_file.csv")
        with open(path, "w") as f:
            pass              
        with pytest.raises(UtilsException) as test_function:
            self.read.csv(path)
        self.assertEqual("Failed to read the csv file.", str(test_function.value))

    def test_xlsx_file_not_found(self):
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        path = os.path.join(absolute_path, "test_files", "data7.csv")
        with pytest.raises(UtilsException) as test_function:
            self.read.xlsx(path)
        self.assertEqual("Failed to read the excel file.", str(test_function.value))

    def test_read_feather_not_found(self):
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        feather_file_path = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f87", ".cache",
                                         "65cb43f2007a5f38718b9d6f",
                                         "be687a30-1329-4639-a606-16f083afa6e623.feather")
        with pytest.raises(UtilsException) as test_function:
            self.read.feather(feather_file_path)
        self.assertEqual("Failed to read the feather file.", str(test_function.value))

    def test_feather_empty_file(self):
        absolute_path = os.path.abspath(os.path.join(__file__, "../../../../../.."))
        feather_file_path = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f87", ".cache",
                                         "65cb43f2007a5f38718b9d6f",
                                         "be687a30-1329-4639-a606-16f083afa6a1.feather")
        with pytest.raises(UtilsException) as test_function:
            self.read.feather(feather_file_path)
        self.assertEqual("Failed to read the feather file.", str(test_function.value))


if __name__ == '__main__':
    unittest.main()
