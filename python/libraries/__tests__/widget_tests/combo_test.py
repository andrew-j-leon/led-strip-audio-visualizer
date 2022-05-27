from typing import Iterable
from util import Font

from libraries.widget_gui import Combo, Widget
import unittest


class ComboTestCase(unittest.TestCase):
    KEY = 'combo_key'
    NO_KEY = None
    VALUES = ['a', 'b', 'c']
    VALUE = 'a'
    NEW_VALUE = 'c'
    NON_EXISTENT_VALUE = 'd'
    FONT = Font()
    SIZE = (10, 20)

    EMPTY_VALUES = []

    def setUp(self):
        self.combo_with_key = Combo(self.KEY, self.VALUES, self.FONT, self.SIZE)
        self.combo_with_no_key = Combo(self.NO_KEY, self.VALUES, self.FONT, self.SIZE)


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

    def test_with_no_key(self):
        with self.assertRaises(AttributeError):
            self.combo_with_no_key.key

        self.assertEqual(self.combo_with_no_key.values, self.VALUES)
        self.assertEqual(self.combo_with_no_key.value, self.VALUE)
        self.assertEqual(self.combo_with_no_key.font, self.FONT)
        self.assertEqual(self.combo_with_no_key.size, self.SIZE)


class TestSettingValue(ComboTestCase):
    def test_set_to_a_new_value_that_is_in_the_combo(self):
        self.combo_with_key.value = self.NEW_VALUE
        self.assertEqual(self.combo_with_key.value, self.NEW_VALUE)

    def test_set_to_a_value_that_is_NOT_in_the_combo(self):
        with self.assertRaises(ValueError):
            self.combo_with_key.value = self.NON_EXISTENT_VALUE


class TestRepr(ComboTestCase):
    def test_with_key(self):
        EXPECTED = (f'Combo(key={self.KEY}, values={self.VALUES}, '
                    f'font={self.FONT}, size={self.SIZE})')

        self.assertEqual(EXPECTED, repr(self.combo_with_key))

    def test_with_no_key(self):
        EXPECTED = (f'Combo(key={self.NO_KEY}, values={self.VALUES}, '
                    f'font={self.FONT}, size={self.SIZE})')

        self.assertEqual(EXPECTED, repr(self.combo_with_no_key))


class TestEqual(ComboTestCase):
    UNEQUAL_KEY = f'new {ComboTestCase.KEY}'

    FONT_NAME = 'Arial'
    FONT_SIZE = ComboTestCase.FONT.size + 2
    FONT_STYLE = 'bold'
    UNEQUAL_FONT = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)

    UNEQUAL_SIZE = (ComboTestCase.SIZE[0] + 10,
                    ComboTestCase.SIZE[1] + 20)

    def test_with_key(self):
        self.assertNotEqual(self.combo_with_key, self.combo_with_no_key)

        self.assertNotEqual(self.combo_with_key, 'not a combo')

        EQUAL_COMBO = Combo(self.KEY, self.VALUES, self.FONT, self.SIZE)
        self.assertEqual(self.combo_with_key, EQUAL_COMBO)

        UNEQUAL_VALUES = self.VALUES + ['d']

        UNEQUAL_PARAMETERS = [{'key': self.UNEQUAL_KEY, 'values': self.VALUES,
                               'font': self.FONT, 'size': self.SIZE},
                              {'key': self.KEY, 'values': UNEQUAL_VALUES,
                               'font': self.FONT, 'size': self.SIZE},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.UNEQUAL_FONT, 'size': self.SIZE},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.FONT, 'size': self.UNEQUAL_SIZE}]

        self.check_not_equal_with_and_without_key(self.combo_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        self.assertNotEqual(self.combo_with_no_key, self.combo_with_key)

        self.assertNotEqual(self.combo_with_no_key, 'not a combo')

        EQUAL_COMBO = Combo(values=self.VALUES, font=self.FONT, size=self.SIZE)
        self.assertEqual(self.combo_with_no_key, EQUAL_COMBO)

        UNEQUAL_VALUES = self.VALUES + ['d']

        UNEQUAL_PARAMETERS = [{'key': self.KEY, 'values': UNEQUAL_VALUES,
                               'font': self.FONT, 'size': self.SIZE},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.UNEQUAL_FONT, 'size': self.SIZE},
                              {'key': self.KEY, 'values': self.VALUES,
                               'font': self.FONT, 'size': self.UNEQUAL_SIZE}]

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
