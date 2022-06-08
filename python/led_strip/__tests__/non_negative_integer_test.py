import unittest
from typing import Any, Callable, List, Tuple, Type

from led_strip.non_negative_integer_range import NonNegativeInteger


def get_error_message(callable: Callable) -> str:
    try:
        callable()
        return ''

    except Exception as error:
        return str(error)


class TestConstructor(unittest.TestCase):

    def test_int(self):
        NON_NEGATIVE_INTS = [0, 1, 20, 999994903493]

        self.check_valid_arguments(NON_NEGATIVE_INTS)

        NEGATIVE_INTS = [-1, -2, -539]

        self.check_arguments_less_than_zero_raise_value_error(NEGATIVE_INTS)

    def test_float(self):
        VALID_FLOATS = [0.0, -0.0, -0.0001, 0.0001, 0.9999, -0.9999, 1.0, 2.0, 453.356]

        self.check_valid_arguments(VALID_FLOATS)

        INVALID_FLOATS = [-1.0, -2.0, -453.356]

        self.check_arguments_less_than_zero_raise_value_error(INVALID_FLOATS)

    def test_bool(self):
        self.check_valid_arguments([True, False])

    def test_invalid_type(self):
        INVALID_TYPES = ['a', [], (), {}, None]

        self.check_cannot_convert_to_int(INVALID_TYPES)

    def check_valid_arguments(self, arguments: list):
        for argument in arguments:

            with self.subTest(f'NonNegativeInteger({argument})'):
                NonNegativeInteger(argument)

    def check_arguments_less_than_zero_raise_value_error(self, arguments: list):
        for argument in arguments:
            with self.subTest(f'NonNegativeInteger({argument})'):

                with self.assertRaises(ValueError):
                    NonNegativeInteger(argument)

    def check_cannot_convert_to_int(self, arguments: list):
        for argument in arguments:
            with self.subTest(f'NonNegativeInteger({argument})'):

                with self.assertRaises((TypeError, ValueError)):
                    NonNegativeInteger(argument)


class TestRepr(unittest.TestCase):
    def test_repr(self):
        NON_NEGATIVE_INTS = [0, 1, 24]

        for NON_NEGATIVE_INT in NON_NEGATIVE_INTS:
            with self.subTest(f'NonNegativeInteger({NON_NEGATIVE_INT})'):

                actual = NonNegativeInteger(NON_NEGATIVE_INT).__repr__()
                expected = f'NonNegativeInteger({NON_NEGATIVE_INT})'

                self.assertEqual(actual, expected)


class TestInt(unittest.TestCase):
    def test_int(self):
        NON_NEGATIVE_INTS = [0, 1, 20]

        for NON_NEGATIVE_INT in NON_NEGATIVE_INTS:

            non_negative_integer = NonNegativeInteger(NON_NEGATIVE_INT)

            with self.subTest(f'int({non_negative_integer})'):

                expected = int(non_negative_integer)
                self.assertEqual(non_negative_integer, expected)


class TestIndex(unittest.TestCase):

    def test_constructed_with_int(self):
        NON_NEGATIVE_INTS = [0, 1, 20, 999994903493]

        self.check_constructed_with(NON_NEGATIVE_INTS)

    def test_constructed_with_float(self):
        FLOATS = [0.0, -0.0, -0.0001, 0.0001, 0.9999, -0.9999, 1.0, 2.0, 453.356]

        self.check_constructed_with(FLOATS)

    def test_constructed_with_bool(self):
        BOOLS = [True, False]

        self.check_constructed_with(BOOLS)

    def check_constructed_with(self, constructor_arguments: list):
        for argument in constructor_arguments:

            non_negative_integer = NonNegativeInteger(argument)

            with self.subTest(f'NonNegativeInteger({repr(argument)}).__index__()'):

                actual = non_negative_integer.__index__()
                expected = int(argument)

                self.assertEqual(actual, expected)


class TestEqual(unittest.TestCase):

    def test_non_negative_integer(self):
        EQUAL_PAIRS = [(NonNegativeInteger(0),
                        NonNegativeInteger(0)),

                       (NonNegativeInteger(1),
                        NonNegativeInteger(1)),

                       (NonNegativeInteger(5834),
                        NonNegativeInteger(5834))]

        self.check_equal(EQUAL_PAIRS)

        UNEQUAL_PAIRS = [(NonNegativeInteger(0),
                          NonNegativeInteger(1)),

                         (NonNegativeInteger(15),
                          NonNegativeInteger(1651)),

                         (NonNegativeInteger(99999),
                          NonNegativeInteger(99998))]

        self.check_not_equal(UNEQUAL_PAIRS)

    def test_int(self):
        EQUAL_PAIRS = [(0, NonNegativeInteger(0)),

                       (1, NonNegativeInteger(1)),

                       (5834, NonNegativeInteger(5834))]

        self.check_equal(EQUAL_PAIRS)

        UNEQUAL_PAIRS = [(0, NonNegativeInteger(1)),

                         (15, NonNegativeInteger(1651)),

                         (999999, NonNegativeInteger(99998))]

        self.check_not_equal(UNEQUAL_PAIRS)

    def test_float(self):
        EQUAL_PAIRS = [(0.0, NonNegativeInteger(0)),

                       (1.0, NonNegativeInteger(1)),

                       (5834.0, NonNegativeInteger(5834)),

                       (0.0, NonNegativeInteger(-0.0)),

                       (0.0, NonNegativeInteger(-0.0001)),

                       (0.0, NonNegativeInteger(-0.999999)),

                       (1.0, NonNegativeInteger(1.000001)),

                       (1.0, NonNegativeInteger(1.5)),

                       (1.0, NonNegativeInteger(1.99999999)),

                       (10.0, NonNegativeInteger(10.0000001)),

                       (10.0, NonNegativeInteger(10.5)),

                       (10.0, NonNegativeInteger(10.9999999)),

                       (0.0, NonNegativeInteger(False)),

                       (1.0, NonNegativeInteger(True))]

        self.check_equal(EQUAL_PAIRS)

        UNEQUAL_PAIRS = [(0.9999, NonNegativeInteger(0.9999)),

                         (15.0, NonNegativeInteger(1651)),

                         (999999.0, NonNegativeInteger(99998)),

                         (573.54, NonNegativeInteger(573)),

                         (-1, NonNegativeInteger(1)),

                         (tuple(), NonNegativeInteger(10)),

                         (list(), NonNegativeInteger(0))]

        self.check_not_equal(UNEQUAL_PAIRS)

    def check_equal(self, pairs: List[Tuple[Any, Any]]):
        for value_1, value_2 in pairs:
            with self.subTest(f'{repr(value_1)} == {repr(value_2)}'):

                self.assertEqual(value_1, value_2)

    def check_not_equal(self, pairs: List[Tuple[Any, Any]]):
        for value_1, value_2 in pairs:
            with self.subTest(f'{repr(value_1)} != {repr(value_2)}'):

                self.assertNotEqual(value_1, value_2)


class TestLessThan(unittest.TestCase):
    def test_less_than_non_negative_integer(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]

        self.check_left_less_thans_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS)
        self.check_right_less_thans_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS)

    def test_less_than_int(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INTS = [-76, -1, 0, 1, 2168]

        self.check_left_less_thans_are_valid(NON_NEGATIVE_INTEGERS, INTS)
        self.check_right_less_thans_are_valid(INTS, NON_NEGATIVE_INTEGERS)

    def test_less_than_floats(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        FLOATS = [-53.4, -1.0, -0.03, 0.0, 0.02, 1.0, 42.67]

        self.check_left_less_thans_are_valid(NON_NEGATIVE_INTEGERS, FLOATS)
        self.check_right_less_thans_are_valid(FLOATS, NON_NEGATIVE_INTEGERS)

    def test_less_than_invalid_type(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INVALID_TYPES = ['hello', tuple(), list(), set(), dict(), None]

        self.check_left_less_than_raises_type_error(NON_NEGATIVE_INTEGERS, INVALID_TYPES)
        self.check_right_less_than_raises_type_error(INVALID_TYPES, NON_NEGATIVE_INTEGERS)

    def check_left_less_thans_are_valid(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} < {repr(right_value)}'):

                    actual = non_negative_integer < right_value
                    expected = int(non_negative_integer) < right_value

                    self.assertEqual(actual, expected)

    def check_right_less_thans_are_valid(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} < {repr(non_negative_integer)}'):

                    actual = left_value < non_negative_integer
                    expected = left_value < int(non_negative_integer)

                    self.assertEqual(actual, expected)

    def check_left_less_than_raises_type_error(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} < {repr(right_value)}'):

                    with self.assertRaises(TypeError):
                        non_negative_integer < right_value

    def check_right_less_than_raises_type_error(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} < {repr(non_negative_integer)}'):

                    with self.assertRaises(TypeError):
                        left_value < non_negative_integer


class TestLessThanOrEqualTo(unittest.TestCase):
    def test_less_than_or_equal_to_non_negative_integer(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]

        self.check_left_less_thans_or_equal_tos_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS)
        self.check_right_less_thans_or_equal_tos_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS)

    def test_less_than_or_equal_to_int(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INTS = [-76, -1, 0, 1, 2168]

        self.check_left_less_thans_or_equal_tos_are_valid(NON_NEGATIVE_INTEGERS, INTS)
        self.check_right_less_thans_or_equal_tos_are_valid(INTS, NON_NEGATIVE_INTEGERS)

    def test_less_than_or_equal_to_floats(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        FLOATS = [-53.4, -1.0, -0.03, 0.0, 0.02, 1.0, 42.67]

        self.check_left_less_thans_or_equal_tos_are_valid(NON_NEGATIVE_INTEGERS, FLOATS)
        self.check_right_less_thans_or_equal_tos_are_valid(FLOATS, NON_NEGATIVE_INTEGERS)

    def test_less_than_or_equal_to_invalid_type(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INVALID_TYPES = ['hello', tuple(), list(), set(), dict(), None]

        self.check_left_less_than_or_equal_to_raises_type_error(NON_NEGATIVE_INTEGERS, INVALID_TYPES)
        self.check_right_less_than_or_equal_to_raises_type_error(INVALID_TYPES, NON_NEGATIVE_INTEGERS)

    def check_left_less_thans_or_equal_tos_are_valid(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} <= {repr(right_value)}'):

                    actual = non_negative_integer <= right_value
                    expected = int(non_negative_integer) <= right_value

                    self.assertEqual(actual, expected)

    def check_right_less_thans_or_equal_tos_are_valid(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} <= {repr(non_negative_integer)}'):

                    actual = left_value <= non_negative_integer
                    expected = left_value <= int(non_negative_integer)

                    self.assertEqual(actual, expected)

    def check_left_less_than_or_equal_to_raises_type_error(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} <= {repr(right_value)}'):

                    with self.assertRaises(TypeError):
                        non_negative_integer <= right_value

    def check_right_less_than_or_equal_to_raises_type_error(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} <= {repr(non_negative_integer)}'):

                    with self.assertRaises(TypeError):
                        left_value <= non_negative_integer


class TestGreaterThan(unittest.TestCase):
    def test_greater_than_non_negative_integer(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]

        self.check_left_greater_thans_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS)
        self.check_right_greater_thans_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS)

    def test_greater_than_int(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INTS = [-76, -1, 0, 1, 2168]

        self.check_left_greater_thans_are_valid(NON_NEGATIVE_INTEGERS, INTS)
        self.check_right_greater_thans_are_valid(INTS, NON_NEGATIVE_INTEGERS)

    def test_greater_than_floats(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        FLOATS = [-53.4, -1.0, -0.03, 0.0, 0.02, 1.0, 42.67]

        self.check_left_greater_thans_are_valid(NON_NEGATIVE_INTEGERS, FLOATS)
        self.check_right_greater_thans_are_valid(FLOATS, NON_NEGATIVE_INTEGERS)

    def test_greater_than_invalid_type(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INVALID_TYPES = ['hello', tuple(), list(), set(), dict(), None]

        self.check_left_greater_than_raises_type_error(NON_NEGATIVE_INTEGERS, INVALID_TYPES)
        self.check_right_greater_than_raises_type_error(INVALID_TYPES, NON_NEGATIVE_INTEGERS)

    def check_left_greater_thans_are_valid(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} > {repr(right_value)}'):

                    actual = non_negative_integer > right_value
                    expected = int(non_negative_integer) > right_value

                    self.assertEqual(actual, expected)

    def check_right_greater_thans_are_valid(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} > {repr(non_negative_integer)}'):

                    actual = left_value > non_negative_integer
                    expected = left_value > int(non_negative_integer)

                    self.assertEqual(actual, expected)

    def check_left_greater_than_raises_type_error(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} > {repr(right_value)}'):

                    with self.assertRaises(TypeError):
                        non_negative_integer > right_value

    def check_right_greater_than_raises_type_error(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} > {repr(non_negative_integer)}'):

                    with self.assertRaises(TypeError):
                        left_value > non_negative_integer


class TestGreaterThanOrEqualTo(unittest.TestCase):
    def test_greater_than_or_equal_to_non_negative_integer(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]

        self.check_left_greater_thans_or_equal_tos_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS)
        self.check_right_greater_thans_or_equal_tos_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS)

    def test_greater_than_or_equal_to_int(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INTS = [-76, -1, 0, 1, 2168]

        self.check_left_greater_thans_or_equal_tos_are_valid(NON_NEGATIVE_INTEGERS, INTS)
        self.check_right_greater_thans_or_equal_tos_are_valid(INTS, NON_NEGATIVE_INTEGERS)

    def test_greater_than_or_equal_to_floats(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        FLOATS = [-53.4, -1.0, -0.03, 0.0, 0.02, 1.0, 42.67]

        self.check_left_greater_thans_or_equal_tos_are_valid(NON_NEGATIVE_INTEGERS, FLOATS)
        self.check_right_greater_thans_or_equal_tos_are_valid(FLOATS, NON_NEGATIVE_INTEGERS)

    def test_greater_than_or_equal_to_invalid_type(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INVALID_TYPES = ['hello', tuple(), list(), set(), dict(), None]

        self.check_left_greater_than_or_equal_to_raises_type_error(NON_NEGATIVE_INTEGERS, INVALID_TYPES)
        self.check_right_greater_than_or_equal_to_raises_type_error(INVALID_TYPES, NON_NEGATIVE_INTEGERS)

    def check_left_greater_thans_or_equal_tos_are_valid(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} >= {repr(right_value)}'):

                    actual = non_negative_integer >= right_value
                    expected = int(non_negative_integer) >= right_value

                    self.assertEqual(actual, expected)

    def check_right_greater_thans_or_equal_tos_are_valid(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} >= {repr(non_negative_integer)}'):

                    actual = left_value >= non_negative_integer
                    expected = left_value >= int(non_negative_integer)

                    self.assertEqual(actual, expected)

    def check_left_greater_than_or_equal_to_raises_type_error(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} >= {repr(right_value)}'):

                    with self.assertRaises(TypeError):
                        non_negative_integer >= right_value

    def check_right_greater_than_or_equal_to_raises_type_error(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} >= {repr(non_negative_integer)}'):

                    with self.assertRaises(TypeError):
                        left_value >= non_negative_integer


class TestAddition(unittest.TestCase):
    def test_add_non_negative_integer(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        EXPECTED_TYPE_OF_RESULT = NonNegativeInteger

        self.check_left_additions_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)
        self.check_right_additions_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)

    def test_add_int(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INTS = [-76, -1, 0, 1, 2168]
        EXPECTED_TYPE_OF_RESULT = int

        self.check_left_additions_are_valid(NON_NEGATIVE_INTEGERS, INTS, EXPECTED_TYPE_OF_RESULT)
        self.check_right_additions_are_valid(INTS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)

    def test_add_floats(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        FLOATS = [-53.4, -1.0, -0.03, 0.0, 0.02, 1.0, 42.67]
        EXPECTED_TYPE_OF_RESULT = float

        self.check_left_additions_are_valid(NON_NEGATIVE_INTEGERS, FLOATS, EXPECTED_TYPE_OF_RESULT)
        self.check_right_additions_are_valid(FLOATS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)

    def test_add_invalid_type(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INVALID_TYPES = ['hello', tuple(), list(), set(), dict(), None]

        self.check_left_addition_raises_type_error(NON_NEGATIVE_INTEGERS, INVALID_TYPES)
        self.check_right_addition_raises_type_error(INVALID_TYPES, NON_NEGATIVE_INTEGERS)

    def check_left_additions_are_valid(self, left_values: List[NonNegativeInteger], right_values: list, expected_type_of_result: Type[Any]):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} + {repr(right_value)}'):

                    actual = non_negative_integer + right_value
                    expected = int(non_negative_integer) + right_value

                    self.assertIs(type(actual), expected_type_of_result)
                    self.assertEqual(actual, expected)

    def check_right_additions_are_valid(self, left_values: list, right_values: List[NonNegativeInteger], expected_type_of_result: Type[Any]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} + {repr(non_negative_integer)}'):

                    actual = left_value + non_negative_integer
                    expected = left_value + int(non_negative_integer)

                    self.assertIs(type(actual), expected_type_of_result)
                    self.assertEqual(actual, expected)

    def check_left_addition_raises_type_error(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} + {repr(right_value)}'):

                    with self.assertRaises(TypeError):
                        non_negative_integer + right_value

    def check_right_addition_raises_type_error(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} + {repr(non_negative_integer)}'):

                    with self.assertRaises(TypeError):
                        left_value + non_negative_integer


class TestSubtraction(unittest.TestCase):
    def test_subtract_non_negative_integer(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        EXPECTED_TYPE_OF_RESULT = int

        self.check_left_subtractions_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)
        self.check_right_subtractions_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)

    def test_subtract_int(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INTS = [-76, -1, 0, 1, 2168]
        EXPECTED_TYPE_OF_RESULT = int

        self.check_left_subtractions_are_valid(NON_NEGATIVE_INTEGERS, INTS, EXPECTED_TYPE_OF_RESULT)
        self.check_right_subtractions_are_valid(INTS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)

    def test_subtract_floats(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        FLOATS = [-53.4, -1.0, -0.03, 0.0, 0.02, 1.0, 42.67]
        EXPECTED_TYPE_OF_RESULT = float

        self.check_left_subtractions_are_valid(NON_NEGATIVE_INTEGERS, FLOATS, EXPECTED_TYPE_OF_RESULT)
        self.check_right_subtractions_are_valid(FLOATS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)

    def test_subtract_invalid_type(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INVALID_TYPES = ['hello', tuple(), list(), set(), dict(), None]

        self.check_left_subtraction_raises_type_error(NON_NEGATIVE_INTEGERS, INVALID_TYPES)
        self.check_right_subtraction_raises_type_error(INVALID_TYPES, NON_NEGATIVE_INTEGERS)

    def check_left_subtractions_are_valid(self, left_values: List[NonNegativeInteger], right_values: list, expected_type_of_result: Type[Any]):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} - {repr(right_value)}'):

                    actual = non_negative_integer - right_value
                    expected = int(non_negative_integer) - right_value

                    self.assertIs(type(actual), expected_type_of_result)
                    self.assertEqual(actual, expected)

    def check_right_subtractions_are_valid(self, left_values: list, right_values: List[NonNegativeInteger], expected_type_of_result: Type[Any]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} - {repr(non_negative_integer)}'):

                    actual = left_value - non_negative_integer
                    expected = left_value - int(non_negative_integer)

                    self.assertIs(type(actual), expected_type_of_result)
                    self.assertEqual(actual, expected)

    def check_left_subtraction_raises_type_error(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} - {repr(right_value)}'):

                    with self.assertRaises(TypeError):
                        non_negative_integer - right_value

    def check_right_subtraction_raises_type_error(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} - {repr(non_negative_integer)}'):

                    with self.assertRaises(TypeError):
                        left_value - non_negative_integer


class TestMultiplication(unittest.TestCase):
    def test_multiply_non_negative_integer(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        EXPECTED_TYPE_OF_RESULT = NonNegativeInteger

        self.check_left_multiplications_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)
        self.check_right_multiplications_are_valid(NON_NEGATIVE_INTEGERS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)

    def test_multiply_int(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INTS = [-76, -1, 0, 1, 2168]
        EXPECTED_TYPE_OF_RESULT = int

        self.check_left_multiplications_are_valid(NON_NEGATIVE_INTEGERS, INTS, EXPECTED_TYPE_OF_RESULT)
        self.check_right_multiplications_are_valid(INTS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)

    def test_multiply_floats(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        FLOATS = [-53.4, -1.0, -0.03, 0.0, 0.02, 1.0, 42.67]
        EXPECTED_TYPE_OF_RESULT = float

        self.check_left_multiplications_are_valid(NON_NEGATIVE_INTEGERS, FLOATS, EXPECTED_TYPE_OF_RESULT)
        self.check_right_multiplications_are_valid(FLOATS, NON_NEGATIVE_INTEGERS, EXPECTED_TYPE_OF_RESULT)

    def test_multiply_invalid_type(self):
        NON_NEGATIVE_INTEGERS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(10)]
        INVALID_TYPES = [dict(), None]

        self.check_left_multiplication_raises_type_error(NON_NEGATIVE_INTEGERS, INVALID_TYPES)
        self.check_right_multiplication_raises_type_error(INVALID_TYPES, NON_NEGATIVE_INTEGERS)

    def check_left_multiplications_are_valid(self, left_values: List[NonNegativeInteger], right_values: list, expected_type_of_result: Type[Any]):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} * {repr(right_value)}'):

                    actual = non_negative_integer * right_value
                    expected = int(non_negative_integer) * right_value

                    self.assertIs(type(actual), expected_type_of_result)
                    self.assertEqual(actual, expected)

    def check_right_multiplications_are_valid(self, left_values: list, right_values: List[NonNegativeInteger], expected_type_of_result: Type[Any]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} * {repr(non_negative_integer)}'):

                    actual = left_value * non_negative_integer
                    expected = left_value * int(non_negative_integer)

                    self.assertIs(type(actual), expected_type_of_result)
                    self.assertEqual(actual, expected)

    def check_left_multiplication_raises_type_error(self, left_values: List[NonNegativeInteger], right_values: list):
        for non_negative_integer in left_values:
            for right_value in right_values:

                with self.subTest(f'{repr(non_negative_integer)} * {repr(right_value)}'):

                    with self.assertRaises(TypeError):
                        non_negative_integer * right_value

    def check_right_multiplication_raises_type_error(self, left_values: list, right_values: List[NonNegativeInteger]):
        for left_value in left_values:
            for non_negative_integer in right_values:

                with self.subTest(f'{repr(left_value)} * {repr(non_negative_integer)}'):

                    with self.assertRaises(TypeError):
                        left_value * non_negative_integer


class TestDivision(unittest.TestCase):

    def test_zero_division(self):
        NUMERATORS = [0, NonNegativeInteger(0), 0.0,
                      1, NonNegativeInteger(1), 1.0,
                      5, NonNegativeInteger(5), 5.0,
                      NonNegativeInteger(4.5), 4.5]

        self.check_zero_division_error(NUMERATORS)

    def check_zero_division_error(self, numerators: list):
        DENOMINATORS = [0, 0.0, NonNegativeInteger(0), False]

        for numerator in numerators:
            for DENOMINATOR in DENOMINATORS:

                with self.subTest(f'{numerator} / {DENOMINATOR}'):

                    with self.assertRaises(ZeroDivisionError):
                        numerator / DENOMINATOR

    def test_divide_non_negative_integer(self):
        EXPECTED_TYPE_OF_RESULT = float

        LEFT_DIVISION_NUMERATORS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(20)]
        LEFT_DIVISION_DENOMINATORS = [NonNegativeInteger(1), NonNegativeInteger(20)]

        self.check_left_divisions_are_valid(LEFT_DIVISION_NUMERATORS, LEFT_DIVISION_DENOMINATORS, EXPECTED_TYPE_OF_RESULT)

        RIGHT_DIVISION_NUMERATORS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(20)]
        RIGHT_DIVISION_DENOMINATORS = [NonNegativeInteger(1), NonNegativeInteger(20)]

        self.check_right_divisions_are_valid(RIGHT_DIVISION_NUMERATORS, RIGHT_DIVISION_DENOMINATORS, EXPECTED_TYPE_OF_RESULT)

    def test_divide_int(self):
        EXPECTED_TYPE_OF_RESULT = float

        LEFT_DIVISION_NUMERATORS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(20)]
        LEFT_DIVISION_DENOMINATORS = [-76, -1, 1, 2168]
        self.check_left_divisions_are_valid(LEFT_DIVISION_NUMERATORS, LEFT_DIVISION_DENOMINATORS, EXPECTED_TYPE_OF_RESULT)

        RIGHT_DIVISION_NUMERATORS = [-76, -1, 0, 1, 2168]
        RIGHT_DIVISION_DENOMINATORS = [NonNegativeInteger(1), NonNegativeInteger(20)]
        self.check_right_divisions_are_valid(RIGHT_DIVISION_NUMERATORS, RIGHT_DIVISION_DENOMINATORS, EXPECTED_TYPE_OF_RESULT)

    def test_divide_floats(self):
        EXPECTED_TYPE_OF_RESULT = float

        LEFT_DIVISION_NUMERATORS = [NonNegativeInteger(0), NonNegativeInteger(1), NonNegativeInteger(20)]
        LEFT_DIVISION_DENOMINATORS = [-53.4, -1.0, -0.03, 0.02, 1.0, 42.67]
        self.check_left_divisions_are_valid(LEFT_DIVISION_NUMERATORS, LEFT_DIVISION_DENOMINATORS, EXPECTED_TYPE_OF_RESULT)

        RIGHT_DIVISION_NUMERATORS = [-53.4, -1.0, -0.03, 0.0, 0.02, 1.0, 42.67]
        RIGHT_DIVISION_DENOMINATORS = [NonNegativeInteger(1), NonNegativeInteger(20)]
        self.check_right_divisions_are_valid(RIGHT_DIVISION_NUMERATORS, RIGHT_DIVISION_DENOMINATORS, EXPECTED_TYPE_OF_RESULT)

    def test_divide_invalid_type(self):
        LEFT_DIVISION_NUMERATORS = [NonNegativeInteger(0), NonNegativeInteger(10)]
        LEFT_DIVISION_DENOMINATORS = [dict(), None]

        self.check_left_division_raises_type_error(LEFT_DIVISION_NUMERATORS, LEFT_DIVISION_DENOMINATORS)

        RIGHT_DIVISION_NUMERATORS = [dict(), None]
        RIGHT_DIVISION_DENOMINATORS = [NonNegativeInteger(10)]
        self.check_right_division_raises_type_error(RIGHT_DIVISION_NUMERATORS, RIGHT_DIVISION_DENOMINATORS)

    def check_left_divisions_are_valid(self, numerators: List[NonNegativeInteger], denominators: list, expected_type_of_result: Type[Any]):
        for non_negative_integer in numerators:
            for denominator in denominators:

                with self.subTest(f'{repr(non_negative_integer)} / {repr(denominator)}'):

                    actual = non_negative_integer / denominator
                    expected = int(non_negative_integer) / denominator

                    self.assertIs(type(actual), expected_type_of_result)
                    self.assertEqual(actual, expected)

    def check_right_divisions_are_valid(self, numerators: list, denominators: List[NonNegativeInteger], expected_type_of_result: Type[Any]):
        for numerator in numerators:
            for non_negative_integer in denominators:

                with self.subTest(f'{repr(numerator)} / {repr(non_negative_integer)}'):

                    actual = numerator / non_negative_integer
                    expected = numerator / int(non_negative_integer)

                    self.assertIs(type(actual), expected_type_of_result)
                    self.assertEqual(actual, expected)

    def check_left_division_raises_type_error(self, numerators: List[NonNegativeInteger], denominators: list):
        for non_negative_integer in numerators:
            for denominator in denominators:

                with self.subTest(f'{repr(non_negative_integer)} / {repr(denominator)}'):

                    with self.assertRaises(TypeError):
                        non_negative_integer / denominator

    def check_right_division_raises_type_error(self, numerators: list, denominators: List[NonNegativeInteger]):
        for numerator in numerators:
            for non_negative_integer in denominators:

                with self.subTest(f'{repr(numerator)} / {repr(non_negative_integer)}'):

                    with self.assertRaises(TypeError):
                        numerator / non_negative_integer
