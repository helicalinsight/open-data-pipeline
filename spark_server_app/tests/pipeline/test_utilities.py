import unittest
from spark_server.pipeline.utilities import Utilities


class TestUtilities(unittest.TestCase):
    # creating the instance of the class Utilities
    @classmethod
    def setUpClass(cls):
        cls.util = Utilities()

    def test_infer_date_format(self):
        date_strings = ['2022-01-01']
        expected_format = 'yyyy-mm-dd'
        self.assertEqual(self.util.infer_date_format(date_strings), expected_format)

        date_strings = ['11/14/2020', None, '10/27/2020', '1/8/2021']
        expected_format = 'M/d/yyyy'
        self.assertEqual(self.util.infer_date_format(date_strings), expected_format)

        date_strings = ['1-1-2022']
        expected_format = 'M-d-yyyy'
        self.assertEqual(self.util.infer_date_format(date_strings), expected_format)

        # Test for invalid date strings
        date_strings = ['not-a-date']
        self.assertIsNone(self.util.infer_date_format(date_strings))

    def test_convert_to_date_format(self):
        self.assertEqual(self.util.convert_to_date_format("YYYY-MM-DD"), "yyyy-MM-dd")


if __name__ == '__main__':
    unittest.main()
