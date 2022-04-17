from util import NonNegativeIntegerRange, NonNegativeInteger
import unittest


class TestConstructor(unittest.TestCase):
    def test_valid_arguments(self):
        VALID_ARGUMENTS = [(NonNegativeInteger(0), NonNegativeInteger(0)),
                           (0, 0), (0.0, 0.0),

                           (NonNegativeInteger(0), NonNegativeInteger(1)),
                           (0, 1), (0.0, 1.0),

                           (NonNegativeInteger(0), NonNegativeInteger(2)),
                           (0, 2), (0.0, 2.0),

                           (NonNegativeInteger(4), NonNegativeInteger(472)),
                           (4, 472), (4.0, 472.0)]

        for start, end in VALID_ARGUMENTS:
            with self.subTest(f'NonNegativeIntegerRange({repr(start), repr(end)}'):

                non_negative_integer_range = NonNegativeIntegerRange(start, end)

                self.assertEqual(non_negative_integer_range.start, start)
                self.assertEqual(non_negative_integer_range.end, end)

    def test_start_greater_than_end(self):
        START_GREATER_THAN_END_ARGUMENTS = [(NonNegativeInteger(1), NonNegativeInteger(0)),
                                            (1, 0), (1.0, 0.0),

                                            (NonNegativeInteger(546), NonNegativeInteger(4)),
                                            (546, 4), (546.0, 4.0)]

        for start, end in START_GREATER_THAN_END_ARGUMENTS:
            with self.subTest(f'NonNegativeIntegerRange({repr(start), repr(end)}'):

                with self.assertRaises(ValueError) as error:
                    NonNegativeIntegerRange(start, end)

                actual_error_message = str(error.exception)
                expected_error_message = f'start ({start}) must be < end ({end}).'

                self.assertEqual(actual_error_message, expected_error_message)


class TestRepr(unittest.TestCase):
    def test_repr(self):
        START = 0
        END = 10

        non_negative_integer_range = NonNegativeIntegerRange(START, END)

        actual = repr(non_negative_integer_range)
        EXPECTED = f'NonNegativeIntegerRange({START}, {END})'

        self.assertEqual(actual, EXPECTED)


class TestContains(unittest.TestCase):
    def test_int(self):
        START = 0
        END = 10

        non_negative_integer_range = NonNegativeIntegerRange(START, END)

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

        non_negative_integer_range = NonNegativeIntegerRange(START, END)

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

        non_negative_integer_range = NonNegativeIntegerRange(START, END)

        IN_BOUNDS_VALUES = [NonNegativeIntegerRange(1, 10),
                            NonNegativeIntegerRange(1, 5),
                            NonNegativeIntegerRange(5, 10),
                            NonNegativeIntegerRange(2, 9),
                            NonNegativeIntegerRange(0, 0),
                            NonNegativeIntegerRange(10, 10),
                            NonNegativeIntegerRange(11, 11),
                            NonNegativeIntegerRange(20, 20)]

        for value in IN_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertTrue(value in non_negative_integer_range)

        OUT_OF_BOUNDS_VALUES = [NonNegativeIntegerRange(0, 10),
                                NonNegativeIntegerRange(0, 1),
                                NonNegativeIntegerRange(10, 11),
                                NonNegativeIntegerRange(9, 11),
                                NonNegativeIntegerRange(20, 100)]

        for value in OUT_OF_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertFalse(value in non_negative_integer_range)
