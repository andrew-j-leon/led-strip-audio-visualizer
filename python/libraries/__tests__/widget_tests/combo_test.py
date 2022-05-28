from collections import Counter
from typing import Iterable
from util import Font

from libraries.widget_gui import Combo, Widget
import unittest


class ComboTestCase(unittest.TestCase):
    KEY = 'combo_key'
    NEW_KEY = f'new {KEY}'
    NO_KEY = None

    VALUE = 'a'
    NEW_VALUE_IN_VALUES = 'c'
    NEW_VALUE_NOT_IN_VALUES = 'd'

    VALUES = ['a', 'b', 'c']
    NEW_VALUES = VALUES + [NEW_VALUE_NOT_IN_VALUES]
    EMPTY_VALUES = []

    FONT = Font('Arial', 12, 'normal')
    NEW_FONT = Font('Times New Roman', 16, 'bold')

    SIZE = (10, 20)
    NEW_SIZE = (40, 50)

    ENABLED = False
    NEW_ENABLED = not ENABLED

    def setUp(self):
        self.combo_with_key = Combo(self.KEY, self.VALUES, self.FONT, self.SIZE, self.ENABLED)
        self.combo_with_no_key = Combo(self.NO_KEY, self.VALUES, self.FONT, self.SIZE, self.ENABLED)


class TestConstructor(ComboTestCase):
    def test_no_values(self):
        combo = Combo()

        with self.assertRaises(AttributeError):
            combo.value

        EXPECTED_VALUES = []
        self.assertEqual(combo.values, EXPECTED_VALUES)

    def test_with_key(self):
        self.assertEqual(self.combo_with_key.key, self.KEY)
        self.assertEqual(self.combo_with_key.values, self.VALUES)
        self.assertEqual(self.combo_with_key.value, self.VALUE)
        self.assertEqual(self.combo_with_key.font, self.FONT)
        self.assertEqual(self.combo_with_key.size, self.SIZE)
        self.assertEqual(self.combo_with_key.enabled, self.ENABLED)

    def test_with_no_key(self):
        with self.assertRaises(AttributeError):
            self.combo_with_no_key.key

        self.assertEqual(self.combo_with_no_key.values, self.VALUES)
        self.assertEqual(self.combo_with_no_key.value, self.VALUE)
        self.assertEqual(self.combo_with_no_key.font, self.FONT)
        self.assertEqual(self.combo_with_no_key.size, self.SIZE)
        self.assertEqual(self.combo_with_key.enabled, self.ENABLED)


class TestSetters(ComboTestCase):
    def test_setting_value_to_a_value_that_is_in_the_combo(self):
        self.combo_with_key.value = self.NEW_VALUE_IN_VALUES

        self.assertEqual(self.combo_with_key.value, self.NEW_VALUE_IN_VALUES)

    def test_setting_value_to_a_value_that_is_NOT_in_the_combo(self):
        with self.assertRaises(ValueError):
            self.combo_with_key.value = self.NEW_VALUE_NOT_IN_VALUES

        self.assertEqual(self.combo_with_key.value, self.VALUE)

    def test_setting_font(self):
        self.combo_with_key.font = self.NEW_FONT

        self.assertEqual(self.combo_with_key.font, self.NEW_FONT)

    def test_setting_size(self):
        self.combo_with_key.size = self.NEW_SIZE

        self.assertEqual(self.combo_with_key.size, self.NEW_SIZE)

    def test_setting_enabled(self):
        self.combo_with_key.enabled = self.NEW_ENABLED

        self.assertEqual(self.combo_with_key.enabled, self.NEW_ENABLED)


class TestAddValue(ComboTestCase):
    def test_add_value_that_already_exists(self):
        PREVIOUS_COUNTS = Counter(self.combo_with_key.values)

        self.combo_with_key.add_value(self.VALUE)

        CURRENT_COUNTS = Counter(self.combo_with_key.values)

        self.assertEqual(PREVIOUS_COUNTS, CURRENT_COUNTS)

    def test_add_a_new_value(self):
        EXPECTED_VALUES = self.combo_with_key.values + [self.NEW_VALUE_NOT_IN_VALUES]
        EXPECTED_COUNTS = Counter(EXPECTED_VALUES)

        self.combo_with_key.add_value(self.NEW_VALUE_NOT_IN_VALUES)

        ACTUAL_COUNTS = Counter(self.combo_with_key.values)

        self.assertEqual(EXPECTED_COUNTS, ACTUAL_COUNTS)


class TestRepr(ComboTestCase):
    def test_with_key(self):
        EXPECTED = (f'Combo(key={self.KEY}, values={self.VALUES}, value={self.VALUE}, '
                    f'font={self.FONT}, size={self.SIZE}, enabled={self.ENABLED})')

        self.assertEqual(EXPECTED, repr(self.combo_with_key))

    def test_with_no_key(self):
        EXPECTED = (f'Combo(key={self.NO_KEY}, values={self.VALUES}, value={self.VALUE}, '
                    f'font={self.FONT}, size={self.SIZE}, enabled={self.ENABLED})')

        self.assertEqual(EXPECTED, repr(self.combo_with_no_key))


class TestEqual(ComboTestCase):
    def test_with_key(self):
        EQUAL_COMBO = Combo(self.KEY, self.VALUES, self.FONT, self.SIZE, self.ENABLED)
        self.assertEqual(self.combo_with_key, EQUAL_COMBO)

        self.assertNotEqual(self.combo_with_key, self.combo_with_no_key)
        self.assertNotEqual(self.combo_with_key, 'not a combo')

        UNEQUAL_PARAMETERS = [{'key': self.NEW_KEY, 'values': self.VALUES,
                               'font': self.FONT, 'size': self.SIZE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'values': self.NEW_VALUES,
                               'font': self.FONT, 'size': self.SIZE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.NEW_FONT, 'size': self.SIZE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.FONT, 'size': self.NEW_SIZE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.FONT, 'size': self.SIZE, 'enabled': self.NEW_ENABLED}]

        self.check_not_equal_with_and_without_key(self.combo_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        EQUAL_COMBO = Combo(self.NO_KEY, self.VALUES, self.FONT, self.SIZE, self.ENABLED)
        self.assertEqual(self.combo_with_no_key, EQUAL_COMBO)

        self.assertNotEqual(self.combo_with_no_key, self.combo_with_key)
        self.assertNotEqual(self.combo_with_no_key, 'not a combo')

        UNEQUAL_PARAMETERS = [{'key': self.KEY, 'values': self.NEW_VALUES,
                               'font': self.FONT, 'size': self.SIZE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.NEW_FONT, 'size': self.SIZE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.FONT, 'size': self.NEW_SIZE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.FONT, 'size': self.SIZE, 'enabled': self.NEW_ENABLED}]

        self.check_not_equal_with_and_without_key(self.combo_with_no_key, UNEQUAL_PARAMETERS)

    def check_not_equal_with_and_without_key(self, widget: Widget, unequal_parameters: Iterable[dict]):
        for parameters in unequal_parameters:

            KEY = parameters['key']

            with self.subTest(parameters=parameters):
                try:
                    unequal_widget_with_key = Combo(**parameters)
                    self.assertNotEqual(widget, unequal_widget_with_key)

                    parameters.pop('key')

                    unequal_widget_without_key = Combo(**parameters)
                    self.assertNotEqual(widget, unequal_widget_without_key)

                finally:
                    parameters['key'] = KEY
