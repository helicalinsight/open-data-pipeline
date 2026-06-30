import unittest

from src.etl.transfrom.transformations_utilities.query_generator import *


class TestQueryGenerator(unittest.TestCase):
    def test_equals(self):
        generator = Equals()
        column = "name"
        value = "pooja"
        query = generator.execute(column, value)
        self.assertEqual("name==pooja", query)

    def test_not_equals(self):
        generator = NotEquals()
        column = "name"
        value = "pooja"
        query = generator.execute(column, value)
        self.assertEqual("name!=pooja", query)

    def test_contains(self):
        generator = Contains()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("name.str.contains('pooja', na=False)", query)

    def test_not_contains(self):
        generator = NotContains()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("~name.str.contains('pooja', na=False)", query)

    def test_startswith(self):
        generator = StartsWith()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("name.str.startswith('pooja', na=False)", query)

    def test_not_startswith(self):
        generator = NotStartsWith()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("~name.str.startswith('pooja', na=False)", query)

    def test_endswith(self):
        generator = EndsWith()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("name.str.endswith('pooja', na=False)", query)

    def test_not_endswith(self):
        generator = NotEndsWith()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("~name.str.endswith('pooja', na=False)", query)

    def test_is_null(self):
        generator = IsNull()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("name.isnull()", query)

    def test_is_not_null(self):
        generator = IsNotNull()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("name.notnull()", query)

    def test_is_one_of_the(self):
        generator = IsOneOfThe()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("name.isin(['pooja'])", query)

    def test_is_not_one_of_the(self):
        generator = IsNotOneOfThe()
        column = "name"
        value = ["pooja"]
        query = generator.execute(column, value)
        self.assertEqual("~name.isin(['pooja'])", query)

    def test_in_range(self):
        generator = InRange()
        column = "marks"
        value = [30, 60]
        query = generator.execute(column, value)
        self.assertEqual("30 <= marks <= 60", query)

    def test_not_in_range(self):
        generator = NotInRange()
        column = "marks"
        value = [30, 60]
        query = generator.execute(column, value)
        self.assertEqual("~(30 <= marks <= 60)", query)

    def test_is_greater(self):
        generator = IsGreaterThan()
        column = "marks"
        value = [30]
        query = generator.execute(column, value)
        self.assertEqual("marks > 30", query)

    def test_is_greater_than_or_equal_to(self):
        generator = IsGreaterThanOrEqualTo()
        column = "marks"
        value = [30]
        query = generator.execute(column, value)
        self.assertEqual("marks >= 30", query)

    def test_is_lesser(self):
        generator = IslesserThan()
        column = "marks"
        value = [30]
        query = generator.execute(column, value)
        self.assertEqual("marks < 30", query)

    def test_is_lesser_than_or_equal_to(self):
        generator = IslesserThanOrEqualTo()
        column = "marks"
        value = [30]
        query = generator.execute(column, value)
        self.assertEqual("marks <= 30", query)

    def test_is_true(self):
        generator = IsTrue()
        column = "marks"
        value = [30]
        query = generator.execute(column, value)
        self.assertEqual("marks == True", query)

    def test_is_false(self):
        generator = IsFalse()
        column = "marks"
        value = [30]
        query = generator.execute(column, value)
        self.assertEqual("marks == False", query)


if __name__ == '__main__':
    unittest.main()
