import unittest

from non_negative_int_range import NonNegativeInt, NonNegativeIntRange


class TestConstructor(unittest.TestCase):
    def test_valid_arguments(self):
        VALID_ARGUMENTS = [(0, 0), (0, 1), (0, 2), (4, 472)]

        for start, end in VALID_ARGUMENTS:
            with self.subTest(f'NonNegativeIntRange({repr(start), repr(end)}'):

                non_negative_integer_range = NonNegativeIntRange(start, end)

                self.assertEqual(non_negative_integer_range.start, start)
                self.assertEqual(non_negative_integer_range.end, end)

    def test_start_is_not_int(self):
        INVALID_ARGUMENTS = [(NonNegativeInt(0), 1),
                             (0.0, 1)]

        for start, end in INVALID_ARGUMENTS:
            with self.subTest(f'NonNegativeIntRange({repr(start), repr(end)}'):

                with self.assertRaises(TypeError):
                    NonNegativeIntRange(start, end)

    def test_end_is_not_int(self):
        INVALID_ARGUMENTS = [(0, NonNegativeInt(0)),
                             (0, 1.0)]

        for start, end in INVALID_ARGUMENTS:
            with self.subTest(f'NonNegativeIntRange({repr(start), repr(end)}'):

                with self.assertRaises(TypeError):
                    NonNegativeIntRange(start, end)

    def test_start_greater_than_end(self):
        START_GREATER_THAN_END_ARGUMENTS = [(1, 0), (546, 4)]

        for start, end in START_GREATER_THAN_END_ARGUMENTS:
            with self.subTest(f'NonNegativeIntRange({repr(start), repr(end)}'):

                with self.assertRaises(ValueError):
                    NonNegativeIntRange(start, end)


class TestRepr(unittest.TestCase):
    def test_repr(self):
        START = 0
        END = 10

        non_negative_integer_range = NonNegativeIntRange(START, END)

        actual = repr(non_negative_integer_range)
        EXPECTED = f'NonNegativeIntRange({START}, {END})'

        self.assertEqual(actual, EXPECTED)


class TestContains(unittest.TestCase):
    def test_empty_range(self):
        range = NonNegativeIntRange()

        self.assertFalse(0 in range)

    def test_int(self):
        START = 0
        END = 10

        non_negative_integer_range = NonNegativeIntRange(START, END)

        IN_BOUNDS_VALUES = [0, 1, 5, 8, 9]

        for value in IN_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertTrue(value in non_negative_integer_range)

        OUT_OF_BOUNDS_VALUES = [-1, -2, -5, 10, 11, 100]

        for value in OUT_OF_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertFalse(value in non_negative_integer_range)

    def test_float(self):
        START = 0
        END = 10

        non_negative_integer_range = NonNegativeIntRange(START, END)

        IN_BOUNDS_VALUES = [0.0, 1.0, 0.5, 1.5, 5.7, 9.0, 8.9]

        for value in IN_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertTrue(value in non_negative_integer_range)

        OUT_OF_BOUNDS_VALUES = [-1.0, -2.0, -5.5, 10.0, 11.0, 9.1, 20.5]

        for value in OUT_OF_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertFalse(value in non_negative_integer_range)

    def test_non_negative_integer_range(self):
        START = 1
        END = 10

        non_negative_integer_range = NonNegativeIntRange(START, END)

        IN_BOUNDS_VALUES = [NonNegativeIntRange(1, 10),
                            NonNegativeIntRange(1, 5),
                            NonNegativeIntRange(5, 10),
                            NonNegativeIntRange(2, 9),
                            NonNegativeIntRange(0, 0),
                            NonNegativeIntRange(10, 10),
                            NonNegativeIntRange(11, 11),
                            NonNegativeIntRange(20, 20)]

        for value in IN_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertTrue(value in non_negative_integer_range)

        OUT_OF_BOUNDS_VALUES = [NonNegativeIntRange(0, 10),
                                NonNegativeIntRange(0, 1),
                                NonNegativeIntRange(10, 11),
                                NonNegativeIntRange(9, 11),
                                NonNegativeIntRange(20, 100)]

        for value in OUT_OF_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertFalse(value in non_negative_integer_range)


class TestIter(unittest.TestCase):
    def test_iter(self):
        ARGS = [(0, 0), (0, 1), (0, 10)]

        for start, end in ARGS:

            non_negative_integer_range = NonNegativeIntRange(start, end)

            with self.subTest(repr(non_negative_integer_range)):

                actual_values = [i for i in non_negative_integer_range]
                expected_values = [i for i in range(start, end)]

                self.assertEqual(actual_values, expected_values)
