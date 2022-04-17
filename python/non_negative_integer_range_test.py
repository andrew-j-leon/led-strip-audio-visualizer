from typing import List, Tuple
from util import NonNegativeIntegerRange, NonNegativeInteger
import unittest


class TestConstructor(unittest.TestCase):
    def test_valid_arguments(self):
        VALID_ARGUMENTS = [(NonNegativeInteger(0), NonNegativeInteger(1)),
                           (NonNegativeInteger(0), NonNegativeInteger(2)),
                           (NonNegativeInteger(4), NonNegativeInteger(472))]

        self.check_valid_arguments(VALID_ARGUMENTS)

    def test_invalid_types(self):
        INVALID_TYPES = [0, 3.5, True, tuple(), list(), str(), dict()]

        self.check_start_arguments_raise_type_error(INVALID_TYPES)
        self.check_end_arguments_raise_type_error(INVALID_TYPES)

    def test_start_greater_than_or_equal_to_end(self):
        START_GREATER_THAN_OR_EQUAL_TO_END_PAIRS = [(NonNegativeInteger(0), NonNegativeInteger(0)),
                                                    (NonNegativeInteger(1), NonNegativeInteger(0)),
                                                    (NonNegativeInteger(43), NonNegativeInteger(43)),
                                                    (NonNegativeInteger(546), NonNegativeInteger(4))]

        self.check_start_greater_than_or_equal_to_end_raises_value_error(START_GREATER_THAN_OR_EQUAL_TO_END_PAIRS)

    def check_start_greater_than_or_equal_to_end_raises_value_error(self, arguments: List[Tuple[NonNegativeInteger, NonNegativeInteger]]):
        for start, end in arguments:

            with self.subTest(f'NonNegativeIntegerRange({start, end}'):

                with self.assertRaises(ValueError) as error:

                    NonNegativeIntegerRange(start, end)

                actual_error_message = str(error.exception)
                expected_error_message = f'start ({start}) must be < end ({end}).'

                self.assertEqual(actual_error_message, expected_error_message)

    def check_valid_arguments(self, arguments: List[Tuple[NonNegativeInteger, NonNegativeInteger]]):
        for start, end in arguments:
            with self.subTest(f'NonNegativeIntegerRange({start, end}'):

                non_negative_integer_range = NonNegativeIntegerRange(start, end)

                self.assertEqual(non_negative_integer_range.start, start)
                self.assertEqual(non_negative_integer_range.end, end)

    def check_start_arguments_raise_type_error(self, start_arguments: list):
        for start in start_arguments:
            non_negative_integer = NonNegativeInteger(10)

            with self.subTest(f'NonNegativeIntegerRange({start}, {non_negative_integer})'):

                with self.assertRaises(TypeError) as error:
                    NonNegativeIntegerRange(start, non_negative_integer)

                actual_error_message = str(error.exception)
                expected_error_message = f"start ({start}) was of type '{type(start).__name__}', but should be of type '{NonNegativeInteger.__name__}'."

                self.assertEqual(actual_error_message, expected_error_message)

    def check_end_arguments_raise_type_error(self, end_arguments: list):
        for end in end_arguments:
            non_negative_integer = NonNegativeInteger(10)

            with self.subTest(f'NonNegativeIntegerRange({end}, {non_negative_integer})'):

                with self.assertRaises(TypeError) as error:
                    NonNegativeIntegerRange(non_negative_integer, end)

                actual_error_message = str(error.exception)
                expected_error_message = f"end ({end}) was of type '{type(end).__name__}', but should be of type '{NonNegativeInteger.__name__}'."

                self.assertEqual(actual_error_message, expected_error_message)


class TestRepr(unittest.TestCase):
    def test_repr(self):
        START = NonNegativeInteger(0)
        END = NonNegativeInteger(10)

        non_negative_integer_range = NonNegativeIntegerRange(START, END)

        actual = repr(non_negative_integer_range)
        EXPECTED = f'NonNegativeIntegerRange({repr(START)}, {repr(END)})'

        self.assertEqual(actual, EXPECTED)


class TestContains(unittest.TestCase):
    def test_true(self):
        START = NonNegativeInteger(0)
        END = NonNegativeInteger(10)

        non_negative_integer_range = NonNegativeIntegerRange(START, END)

        IN_BOUNDS_VALUES = [0, 1, 5, 8, 9]

        for value in IN_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertTrue(value in non_negative_integer_range)

    def test_false(self):
        START = NonNegativeInteger(0)
        END = NonNegativeInteger(10)

        non_negative_integer_range = NonNegativeIntegerRange(START, END)

        OUT_OF_BOUNDS_VALUES = [-1, -2, -5, 10, 11, 100]

        for value in OUT_OF_BOUNDS_VALUES:
            with self.subTest(f'{value} in {repr(non_negative_integer_range)}'):
                self.assertFalse(value in non_negative_integer_range)
