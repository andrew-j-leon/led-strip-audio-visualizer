from typing import Callable, Iterable
from libraries.gui import Button, CheckBox, Combo, Font, Input, Multiline, Text, Widget
import unittest


class WidgetTestCase(unittest.TestCase):
    NO_KEY = None

    def check_no_key_attribute(self, widget: Widget):
        with self.assertRaises(AttributeError) as error:
            widget.key

        ACTUAL_ERROR_MESSAGE = str(error.exception)
        EXPECTED_ERROR_MESSAGE = 'This Widget does not have a key attribute.'

        self.assertEqual(ACTUAL_ERROR_MESSAGE, EXPECTED_ERROR_MESSAGE)

    def check_not_equal_with_and_without_key(self, widget: Widget,
                                             make_widget: Callable[..., Widget],
                                             unequal_parameters: Iterable[dict]):
        for parameters in unequal_parameters:

            KEY = parameters['key']

            with self.subTest(parameters=parameters):
                try:
                    unequal_widget_with_key = make_widget(**parameters)
                    self.assertNotEqual(widget, unequal_widget_with_key)

                    parameters.pop('key')

                    unequal_widget_without_key = make_widget(**parameters)
                    self.assertNotEqual(widget, unequal_widget_without_key)

                finally:
                    parameters['key'] = KEY


class TestButton(WidgetTestCase):
    KEY = 'button_key'
    TEXT = 'click me'
    FONT = Font('Times New Roman', 18, 'bold')
    DISABLED = False

    def setUp(self):
        self.button_with_key = Button(self.KEY, self.TEXT, self.FONT, self.DISABLED)
        self.button_with_no_key = Button(self.NO_KEY, self.TEXT, self.FONT, self.DISABLED)

    def test_constructor(self):
        with self.subTest(button_with_key=self.button_with_key):
            self.assertEqual(self.button_with_key.key, self.KEY)
            self.assertEqual(self.button_with_key.value, self.TEXT)
            self.assertEqual(self.button_with_key.font, self.FONT)
            self.assertEqual(self.button_with_key.disabled, self.DISABLED)

        with self.subTest(button_with_no_key=self.button_with_no_key):
            self.check_no_key_attribute(self.button_with_no_key)
            self.assertEqual(self.button_with_no_key.value, self.TEXT)
            self.assertEqual(self.button_with_no_key.font, self.FONT)
            self.assertEqual(self.button_with_no_key.disabled, self.DISABLED)

    def test_setting_value(self):
        VALUE = f'{self.TEXT} new'

        self.button_with_key.value = VALUE

        self.assertEqual(self.button_with_key.value, VALUE)

    def test_repr(self):
        with self.subTest('With key attribute'):
            expected = f'Button(key={self.KEY}, text={self.TEXT}, font={self.FONT}, disabled={self.DISABLED})'
            actual = repr(self.button_with_key)

            self.assertEqual(actual, expected)

        with self.subTest('With no attribute'):
            expected = f'Button(key={self.NO_KEY}, text={self.TEXT}, font={self.FONT}, disabled={self.DISABLED})'
            actual = repr(self.button_with_no_key)

            self.assertEqual(actual, expected)

    def test_equal_with_key(self):
        UNEQUAL_TEXT = f'new {self.TEXT}'

        FONT_NAME = 'Arial'
        FONT_SIZE = self.FONT.size + 2
        FONT_STYLE = 'bold'
        UNEQUAL_FONT = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)

        UNEQUAL_DISABLED = not self.DISABLED

        with self.subTest(button_with_key=self.button_with_key):
            EQUAL_BUTTON = Button(self.KEY, self.TEXT, self.FONT, self.DISABLED)
            self.assertEqual(self.button_with_key, EQUAL_BUTTON)

            self.assertNotEqual(self.button_with_key, self.button_with_no_key)

            UNEQUAL_KEY = f'new {self.KEY}'

            UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT, 'font': self.FONT, 'disabled': self.DISABLED},
                                  {'key': self.KEY, 'text': UNEQUAL_TEXT, 'font': self.FONT, 'disabled': self.DISABLED},
                                  {'key': self.KEY, 'text': self.TEXT, 'font': UNEQUAL_FONT, 'disabled': self.DISABLED},
                                  {'key': self.KEY, 'text': self.TEXT, 'font': self.FONT, 'disabled': UNEQUAL_DISABLED}]

            self.check_not_equal_with_and_without_key(self.button_with_key, Button, UNEQUAL_PARAMETERS)

        with self.subTest(button_with_no_key=self.button_with_no_key):
            EQUAL_BUTTON = Button(self.NO_KEY, self.TEXT, self.FONT, self.DISABLED)
            self.assertEqual(self.button_with_no_key, EQUAL_BUTTON)

            self.assertNotEqual(self.button_with_no_key, self.button_with_key)

            UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': UNEQUAL_TEXT, 'font': self.FONT, 'disabled': self.DISABLED},
                                  {'key': self.NO_KEY, 'text': self.TEXT, 'font': UNEQUAL_FONT, 'disabled': self.DISABLED},
                                  {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.FONT, 'disabled': UNEQUAL_DISABLED}]

            self.check_not_equal_with_and_without_key(self.button_with_no_key, Button, UNEQUAL_PARAMETERS)


class TestText(WidgetTestCase):
    KEY = 'text_key'
    TEXT = 'hello'
    FONT = Font('Wing Dings', 20, 'italic')

    def setUp(self):
        self.text_with_key = Text(self.KEY, self.TEXT, self.FONT)
        self.text_with_no_key = Text(self.NO_KEY, self.TEXT, self.FONT)

    def test_constructor(self):
        with self.subTest(text_with_key=self.text_with_key):
            self.assertEqual(self.text_with_key.key, self.KEY)
            self.assertEqual(self.text_with_key.value, self.TEXT)
            self.assertEqual(self.text_with_key.font, self.FONT)

        with self.subTest(text_with_no_key=self.text_with_no_key):
            self.check_no_key_attribute(self.text_with_no_key)
            self.assertEqual(self.text_with_no_key.value, self.TEXT)
            self.assertEqual(self.text_with_no_key.font, self.FONT)

    def test_set_value(self):
        VALUE = f'{self.TEXT} new'

        self.text_with_key.value = VALUE

        self.assertEqual(self.text_with_key.value, VALUE)

    def test_repr(self):
        with self.subTest('With key attribute'):
            EXPECTED = f'Text(key={self.KEY}, text={self.TEXT}, font={self.FONT})'
            ACTUAL = repr(self.text_with_key)

            self.assertEqual(EXPECTED, ACTUAL)

        with self.subTest('With no attribute'):
            EXPECTED = f'Text(key={self.NO_KEY}, text={self.TEXT}, font={self.FONT})'
            ACTUAL = repr(self.text_with_no_key)

            self.assertEqual(EXPECTED, ACTUAL)

    def test_equal(self):
        UNEQUAL_TEXT = f'new {self.TEXT}'

        FONT_NAME = 'Arial'
        FONT_SIZE = self.FONT.size + 2
        FONT_STYLE = 'bold'
        UNEQUAL_FONT = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)

        with self.subTest(text_with_key=self.text_with_key):
            self.assertNotEqual(self.text_with_key, self.text_with_no_key)

            EQUAL_TEXT = Text(self.KEY, self.TEXT, self.FONT)

            self.assertEqual(self.text_with_key, EQUAL_TEXT)

            UNEQUAL_KEY = f'new {self.KEY}'

            UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT, 'font': self.FONT},
                                  {'key': self.KEY, 'text': UNEQUAL_TEXT, 'font': self.FONT},
                                  {'key': self.KEY, 'text': self.FONT, 'font': UNEQUAL_FONT}]

            self.check_not_equal_with_and_without_key(self.text_with_key, Text, UNEQUAL_PARAMETERS)

        with self.subTest(text_with_no_key=self.text_with_no_key):
            self.assertNotEqual(self.text_with_no_key, self.text_with_key)

            EQUAL_TEXT = Text(self.NO_KEY, self.TEXT, self.FONT)

            self.assertEqual(self.text_with_no_key, EQUAL_TEXT)

            UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': UNEQUAL_TEXT, 'font': self.FONT},
                                  {'key': self.NO_KEY, 'text': self.FONT, 'font': UNEQUAL_FONT}]

            self.check_not_equal_with_and_without_key(self.text_with_no_key, Text, UNEQUAL_PARAMETERS)


class TestCombo(WidgetTestCase):
    KEY = 'combo_key'
    VALUES = ['a', 'b', 'c']
    VALUE = 1
    UNSET_VALUE = 2
    FONT = Font()
    SIZE = (10, 20)

    EMPTY_VALUES = []
    NO_VALUE = None

    def setUp(self):
        self.combo_with_key = Combo(self.KEY, self.VALUES, self.VALUE, self.FONT, self.SIZE)
        self.combo_with_no_key = Combo(self.NO_KEY, self.VALUES, self.VALUE, self.FONT, self.SIZE)

        self.combo_with_no_values = Combo(self.KEY, self.EMPTY_VALUES, self.NO_VALUE, self.FONT, self.SIZE)
        self.combo_with_values_and_no_set_value = Combo(self.KEY, self.VALUES, self.NO_VALUE, self.FONT, self.SIZE)

    def test_constructor(self):
        with self.subTest(combo_with_key=self.combo_with_key):
            self.assertEqual(self.combo_with_key.key, self.KEY)
            self.assertEqual(self.combo_with_key.values, self.VALUES)
            self.assertEqual(self.combo_with_key.value, self.VALUES[self.VALUE])
            self.assertEqual(self.combo_with_key.font, self.FONT)
            self.assertEqual(self.combo_with_key.size, self.SIZE)

        with self.subTest(combo_with_no_key=self.combo_with_no_key):
            self.check_no_key_attribute(self.combo_with_no_key)
            self.assertEqual(self.combo_with_no_key.values, self.VALUES)
            self.assertEqual(self.combo_with_no_key.value, self.VALUES[self.VALUE])
            self.assertEqual(self.combo_with_no_key.font, self.FONT)
            self.assertEqual(self.combo_with_no_key.size, self.SIZE)

        with self.subTest(combo_with_no_values=self.combo_with_no_values):
            self.check_no_value_attribute(self.combo_with_no_values)
            self.assertEqual(self.combo_with_no_values.key, self.KEY)
            self.assertEqual(self.combo_with_no_values.values, self.EMPTY_VALUES)
            self.assertEqual(self.combo_with_no_values.font, self.FONT)
            self.assertEqual(self.combo_with_no_values.size, self.SIZE)

        with self.subTest('With no values AND a set value'):
            VALUE = 0

            with self.assertRaises(IndexError) as error:
                Combo(values=self.EMPTY_VALUES, value=VALUE)

            ACTUAL_ERROR_MESSAGE = str(error.exception)
            EXPECTED_ERROR_MESSAGE = (f'This Combo does not have a value at index {VALUE}. '
                                      f'Its values include: {self.EMPTY_VALUES}')

            self.assertEqual(ACTUAL_ERROR_MESSAGE, EXPECTED_ERROR_MESSAGE)

        with self.subTest('Invalid type for value'):
            VALUE = 'hello'

            with self.assertRaises(TypeError) as error:
                Combo(values=self.VALUES, value=VALUE)

            ACTUAL_ERROR_MESSAGE = str(error.exception)
            EXPECTED_ERROR_MESSAGE = ('value must be an int or NoneType. However, the '
                                      f'given value {VALUE} was of type {type(VALUE)}.')

            self.assertEqual(ACTUAL_ERROR_MESSAGE, EXPECTED_ERROR_MESSAGE)

        with self.subTest('With values AND no set value'):
            self.check_no_value_attribute(self.combo_with_values_and_no_set_value)
            self.assertEqual(self.combo_with_values_and_no_set_value.key, self.KEY)
            self.assertEqual(self.combo_with_values_and_no_set_value.values, self.VALUES)
            self.assertEqual(self.combo_with_values_and_no_set_value.font, self.FONT)
            self.assertEqual(self.combo_with_values_and_no_set_value.size, self.SIZE)

    def test_setting_value(self):
        VALUES = ['a', 'b']

        VALUE_0 = 0
        VALUE_1 = 1

        def make_combo():
            return Combo(values=VALUES, value=VALUE_0)

        with self.subTest('New, valid value'):
            combo = make_combo()

            combo.value = VALUE_1

            self.assertIs(combo.value, VALUES[VALUE_1])

        with self.subTest('None'):
            combo = make_combo()

            combo.value = None

            self.check_no_value_attribute(combo)

        with self.subTest('TypeError'):
            combo = make_combo()
            VALUE = 'hello'

            with self.assertRaises(TypeError) as error:
                combo.value = VALUE

            ACTUAL_ERROR_MESSAGE = str(error.exception)
            EXPECTED_ERROR_MESSAGE = ('value must be an int or NoneType. However, the '
                                      f'given value {VALUE} was of type {type(VALUE)}.')

            self.assertEqual(ACTUAL_ERROR_MESSAGE, EXPECTED_ERROR_MESSAGE)

        with self.subTest('IndexError'):
            combo = make_combo()
            VALUE = VALUE_1 + 1

            with self.assertRaises(IndexError) as error:
                combo.value = VALUE

            ACTUAL_ERROR_MESSAGE = str(error.exception)
            EXPECTED_ERROR_MESSAGE = (f'This Combo does not have a value at index {VALUE}. '
                                      f'Its values include: {VALUES}')

            self.assertEqual(ACTUAL_ERROR_MESSAGE, EXPECTED_ERROR_MESSAGE)

    def test_repr(self):
        with self.subTest('With key'):
            EXPECTED = (f'Combo(key={self.KEY}, values={self.VALUES}, value={self.VALUE}, '
                        f'font={self.FONT}, size={self.SIZE})')
            ACTUAL = repr(self.combo_with_key)

            self.assertEqual(EXPECTED, ACTUAL)

        with self.subTest('With no key'):
            EXPECTED = (f'Combo(key={self.NO_KEY}, values={self.VALUES}, value={self.VALUE}, '
                        f'font={self.FONT}, size={self.SIZE})')
            ACTUAL = repr(self.combo_with_no_key)

            self.assertEqual(EXPECTED, ACTUAL)

        with self.subTest('With no values AND no set value'):
            EXPECTED = (f'Combo(key={self.KEY}, values={self.EMPTY_VALUES}, value={self.NO_VALUE}, '
                        f'font={self.FONT}, size={self.SIZE})')
            ACTUAL = repr(self.combo_with_no_values)

            self.assertEqual(EXPECTED, ACTUAL)

        with self.subTest('With values AND no set value'):
            EXPECTED = (f'Combo(key={self.KEY}, values={self.VALUES}, value={self.NO_VALUE}, '
                        f'font={self.FONT}, size={self.SIZE})')
            ACTUAL = repr(self.combo_with_values_and_no_set_value)

            self.assertEqual(EXPECTED, ACTUAL)

    def test_equal(self):
        UNEQUAL_KEY = f'new {self.KEY}'

        FONT_NAME = 'Arial'
        FONT_SIZE = self.FONT.size + 2
        FONT_STYLE = 'bold'
        UNEQUAL_FONT = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)

        UNEQUAL_SIZE = (self.SIZE[0] + 10,
                        self.SIZE[1] + 20)

        with self.subTest(combo_with_key=self.combo_with_key):
            self.assertNotEqual(self.combo_with_key, self.combo_with_no_key)
            self.assertNotEqual(self.combo_with_key, self.combo_with_no_values)
            self.assertNotEqual(self.combo_with_key, self.combo_with_values_and_no_set_value)

            self.assertNotEqual(self.combo_with_key, 'not a combo')

            EQUAL_COMBO = Combo(self.KEY, self.VALUES, self.VALUE, self.FONT, self.SIZE)
            self.assertEqual(self.combo_with_key, EQUAL_COMBO)

            UNEQUAL_VALUES = self.VALUES + ['d']
            UNEQUAL_VALUE = self.UNSET_VALUE

            UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'values': self.VALUES, 'value': self.VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': UNEQUAL_VALUES, 'value': self.VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.VALUES, 'value': UNEQUAL_VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.VALUES, 'value': self.VALUE,
                                   'font': UNEQUAL_FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.VALUES, 'value': self.VALUE,
                                   'font': self.FONT, 'size': UNEQUAL_SIZE}]

            self.check_not_equal_with_and_without_key(self.combo_with_key, Combo, UNEQUAL_PARAMETERS)
            self.check_not_equal_with_and_without_value(self.combo_with_key, UNEQUAL_PARAMETERS)

        with self.subTest(combo_with_no_key=self.combo_with_no_key):
            self.assertNotEqual(self.combo_with_no_key, self.combo_with_key)
            self.assertNotEqual(self.combo_with_no_key, self.combo_with_no_values)
            self.assertNotEqual(self.combo_with_no_key, self.combo_with_values_and_no_set_value)

            self.assertNotEqual(self.combo_with_no_key, 'not a combo')

            EQUAL_COMBO = Combo(values=self.VALUES, value=self.VALUE, font=self.FONT, size=self.SIZE)
            self.assertEqual(self.combo_with_no_key, EQUAL_COMBO)

            UNEQUAL_VALUES = self.VALUES + ['d']
            UNEQUAL_VALUE = self.UNSET_VALUE

            UNEQUAL_PARAMETERS = [{'key': self.KEY, 'values': UNEQUAL_VALUES, 'value': self.VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.VALUES, 'value': UNEQUAL_VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.VALUES, 'value': self.VALUE,
                                   'font': UNEQUAL_FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.VALUES, 'value': self.VALUE,
                                   'font': self.FONT, 'size': UNEQUAL_SIZE}]

            self.check_not_equal_with_and_without_key(self.combo_with_no_key, Combo, UNEQUAL_PARAMETERS)
            self.check_not_equal_with_and_without_value(self.combo_with_no_key, UNEQUAL_PARAMETERS)

        with self.subTest(combo_with_no_values=self.combo_with_no_values):
            self.assertNotEqual(self.combo_with_no_values, self.combo_with_key)
            self.assertNotEqual(self.combo_with_no_values, self.combo_with_no_key)
            self.assertNotEqual(self.combo_with_no_values, self.combo_with_values_and_no_set_value)

            self.assertNotEqual(self.combo_with_no_values, 'not a combo')

            EQUAL_COMBO = Combo(self.KEY, self.EMPTY_VALUES, self.NO_VALUE, self.FONT, self.SIZE)
            self.assertEqual(self.combo_with_no_values, EQUAL_COMBO)

            UNEQUAL_VALUES = self.VALUES
            UNEQUAL_VALUE = self.VALUE

            UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'values': self.EMPTY_VALUES, 'value': self.NO_VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': UNEQUAL_VALUES, 'value': self.NO_VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': UNEQUAL_VALUES, 'value': UNEQUAL_VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.EMPTY_VALUES, 'value': self.NO_VALUE,
                                   'font': UNEQUAL_FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.EMPTY_VALUES, 'value': self.NO_VALUE,
                                   'font': self.FONT, 'size': UNEQUAL_SIZE}]

            self.check_not_equal_with_and_without_key(self.combo_with_no_values, Combo, UNEQUAL_PARAMETERS)
            self.check_not_equal_with_and_without_value(self.combo_with_no_values, UNEQUAL_PARAMETERS)

        with self.subTest(combo_with_values_and_no_set_value=self.combo_with_values_and_no_set_value):
            self.assertNotEqual(self.combo_with_values_and_no_set_value, self.combo_with_key)
            self.assertNotEqual(self.combo_with_values_and_no_set_value, self.combo_with_no_key)
            self.assertNotEqual(self.combo_with_values_and_no_set_value, self.combo_with_no_values)

            self.assertNotEqual(self.combo_with_values_and_no_set_value, 'not a Combo')

            EQUAL_COMBO = Combo(self.KEY, self.VALUES, self.NO_VALUE, self.FONT, self.SIZE)
            self.assertEqual(self.combo_with_values_and_no_set_value, EQUAL_COMBO)

            UNEQUAL_VALUES = self.VALUES + ['d']
            UNEQUAL_VALUE = self.VALUE

            UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'values': self.VALUES, 'value': self.NO_VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': UNEQUAL_VALUES, 'value': self.NO_VALUE,
                                   'font': self.FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.VALUES, 'value': self.NO_VALUE,
                                   'font': UNEQUAL_FONT, 'size': self.SIZE},
                                  {'key': self.KEY, 'values': self.VALUES, 'value': self.NO_VALUE,
                                   'font': self.FONT, 'size': UNEQUAL_SIZE}]

            UNEQUAL_COMBO = Combo(self.KEY, self.VALUES, UNEQUAL_VALUE, self.FONT, self.SIZE)
            self.assertNotEqual(self.combo_with_values_and_no_set_value, UNEQUAL_COMBO)

            self.check_not_equal_with_and_without_key(self.combo_with_values_and_no_set_value, Combo, UNEQUAL_PARAMETERS)
            self.check_not_equal_with_and_without_value(self.combo_with_values_and_no_set_value, UNEQUAL_PARAMETERS)

    def check_no_value_attribute(self, combo: Combo):
        with self.assertRaises(AttributeError) as error:
            combo.value

        ACTUAL_ERROR_MESSAGE = str(error.exception)
        EXPECTED_ERROR_MESSAGE = 'This Combo does not have a set value.'

        self.assertEqual(ACTUAL_ERROR_MESSAGE, EXPECTED_ERROR_MESSAGE)

    def check_not_equal_with_and_without_value(self, combo: Combo, unequal_parameters: Iterable[dict]):
        for parameters in unequal_parameters:

            VALUE = parameters['value']

            with self.subTest(parameters=parameters):
                try:
                    unequal_combo_with_value = Combo(**parameters)
                    self.assertNotEqual(combo, unequal_combo_with_value)

                    parameters.pop('value')

                    unequal_combo_without_value = Combo(**parameters)
                    self.assertNotEqual(combo, unequal_combo_without_value)

                finally:
                    parameters['value'] = VALUE


class TestCheckBox(WidgetTestCase):
    KEY = 'check_box_key'
    TEXT = 'hello i am a checkbox'
    FONT = Font('some font', 20)
    VALUE = True

    def setUp(self):
        self.check_box_with_key = CheckBox(self.KEY, self.TEXT, self.FONT, self.VALUE)
        self.check_box_with_no_key = CheckBox(self.NO_KEY, self.TEXT, self.FONT, self.VALUE)

    def test_constructor(self):
        with self.subTest(check_box_with_key=self.check_box_with_key):
            self.assertEqual(self.check_box_with_key.key, self.KEY)
            self.assertEqual(self.check_box_with_key.text, self.TEXT)
            self.assertEqual(self.check_box_with_key.font, self.FONT)
            self.assertEqual(self.check_box_with_key.value, self.VALUE)

        with self.subTest(check_box_with_no_key=self.check_box_with_no_key):
            self.check_no_key_attribute(self.check_box_with_no_key)
            self.assertEqual(self.check_box_with_no_key.text, self.TEXT)
            self.assertEqual(self.check_box_with_no_key.font, self.FONT)
            self.assertEqual(self.check_box_with_no_key.value, self.VALUE)

    def test_repr(self):
        with self.subTest('With key attribute'):
            expected = f'CheckBox(key={self.KEY}, text={self.TEXT}, font={self.FONT}, value={self.VALUE})'
            actual = repr(self.check_box_with_key)

            self.assertEqual(expected, actual)

        with self.subTest('With no key attribute'):
            expected = f'CheckBox(key={self.NO_KEY}, text={self.TEXT}, font={self.FONT}, value={self.VALUE})'
            actual = repr(self.check_box_with_no_key)

            self.assertEqual(expected, actual)

    def test_equal(self):
        UNEQUAL_TEXT = f'new {self.TEXT}'

        FONT_NAME = 'Arial'
        FONT_SIZE = self.FONT.size + 2
        FONT_STYLE = 'bold'
        UNEQUAL_FONT = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)

        UNEQUAL_VALUE = not self.VALUE

        with self.subTest(check_box_with_key=self.check_box_with_key):
            self.assertNotEqual(self.check_box_with_key, self.check_box_with_no_key)
            self.assertNotEqual(self.check_box_with_key, 'not a checkbox')

            EQUAL_CHECK_BOX = CheckBox(self.KEY, self.TEXT, self.FONT, self.VALUE)

            self.assertEqual(self.check_box_with_key, EQUAL_CHECK_BOX)

            UNEQUAL_KEY = f'new {self.KEY}'

            UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT, 'font': self.FONT, 'value': self.VALUE},
                                  {'key': self.KEY, 'text': UNEQUAL_TEXT, 'font': self.FONT, 'value': self.VALUE},
                                  {'key': self.KEY, 'text': self.TEXT, 'font': UNEQUAL_FONT, 'value': self.VALUE},
                                  {'key': self.KEY, 'text': self.TEXT, 'font': self.FONT, 'value': UNEQUAL_VALUE}]

            self.check_not_equal_with_and_without_key(self.check_box_with_key, CheckBox, UNEQUAL_PARAMETERS)

        with self.subTest(check_box_with_no_key=self.check_box_with_no_key):
            self.assertNotEqual(self.check_box_with_no_key, self.check_box_with_key)
            self.assertNotEqual(self.check_box_with_no_key, 'not a checkbox')

            EQUAL_CHECK_BOX = CheckBox(self.NO_KEY, self.TEXT, self.FONT, self.VALUE)

            self.assertEqual(self.check_box_with_no_key, EQUAL_CHECK_BOX)

            UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': UNEQUAL_TEXT, 'font': self.FONT, 'value': self.VALUE},
                                  {'key': self.NO_KEY, 'text': self.TEXT, 'font': UNEQUAL_FONT, 'value': self.VALUE},
                                  {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.FONT, 'value': UNEQUAL_VALUE}]

            self.check_not_equal_with_and_without_key(self.check_box_with_no_key, CheckBox, UNEQUAL_PARAMETERS)


class TestMultiline(WidgetTestCase):
    KEY = 'multiline_key'
    TEXT = 'some multiline text'
    SIZE = (20, 30)
    AUTO_SCROLL = False

    def setUp(self):
        self.multiline_with_key = Multiline(self.KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)
        self.multiline_with_no_key = Multiline(self.NO_KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)

    def test_constructor(self):
        with self.subTest(multiline_with_key=self.multiline_with_key):
            self.assertEqual(self.multiline_with_key.key, self.KEY)
            self.assertEqual(self.multiline_with_key.value, self.TEXT)
            self.assertEqual(self.multiline_with_key.size, self.SIZE)
            self.assertEqual(self.multiline_with_key.auto_scroll, self.AUTO_SCROLL)

        with self.subTest(multiline_with_no_key=self.multiline_with_no_key):
            self.check_no_key_attribute(self.multiline_with_no_key)
            self.assertEqual(self.multiline_with_no_key.value, self.TEXT)
            self.assertEqual(self.multiline_with_no_key.size, self.SIZE)
            self.assertEqual(self.multiline_with_no_key.auto_scroll, self.AUTO_SCROLL)

    def test_repr(self):
        with self.subTest('With key attribute'):
            EXPECTED = f'Multiline(key={self.KEY}, text={self.TEXT}, size={self.SIZE}, auto_scroll={self.AUTO_SCROLL})'
            ACTUAL = repr(self.multiline_with_key)

            self.assertEqual(EXPECTED, ACTUAL)

        with self.subTest('With no key attribute'):
            EXPECTED = f'Multiline(key={self.NO_KEY}, text={self.TEXT}, size={self.SIZE}, auto_scroll={self.AUTO_SCROLL})'
            ACTUAL = repr(self.multiline_with_no_key)

            self.assertEqual(EXPECTED, ACTUAL)

    def test_equal(self):
        UNEQUAL_TEXT = f'new {self.TEXT}'
        UNEQUAL_SIZE = (self.SIZE[0] + 10,
                        self.SIZE[1] + 20)
        UNEQUAL_AUTO_SCROLL = not self.AUTO_SCROLL

        with self.subTest(multiline_with_key=self.multiline_with_key):
            self.assertNotEqual(self.multiline_with_key, self.multiline_with_no_key)
            self.assertNotEqual(self.multiline_with_key, 'not a Multiline')

            EQUAL_MULTILINE = Multiline(self.KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)

            self.assertEqual(self.multiline_with_key, EQUAL_MULTILINE)

            UNEQUAL_KEY = f'new {self.KEY}'

            UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL},
                                  {'key': self.KEY, 'text': UNEQUAL_TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL},
                                  {'key': self.KEY, 'text': self.TEXT, 'size': UNEQUAL_SIZE, 'auto_scroll': self.AUTO_SCROLL},
                                  {'key': self.KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': UNEQUAL_AUTO_SCROLL}]

            self.check_not_equal_with_and_without_key(self.multiline_with_key, Multiline, UNEQUAL_PARAMETERS)

        with self.subTest(multiline_with_no_key=self.multiline_with_no_key):
            self.assertNotEqual(self.multiline_with_no_key, self.multiline_with_key)
            self.assertNotEqual(self.multiline_with_no_key, 'not a Multiline')

            EQUAL_MULTILINE = Multiline(self.NO_KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)

            self.assertEqual(self.multiline_with_no_key, EQUAL_MULTILINE)

            UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': UNEQUAL_TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL},
                                  {'key': self.NO_KEY, 'text': self.TEXT, 'size': UNEQUAL_SIZE, 'auto_scroll': self.AUTO_SCROLL},
                                  {'key': self.NO_KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': UNEQUAL_AUTO_SCROLL}]

            self.check_not_equal_with_and_without_key(self.multiline_with_no_key, Multiline, UNEQUAL_PARAMETERS)


class TestInput(WidgetTestCase):
    KEY = 'input_key'
    TEXT = 'some input text'

    def setUp(self):
        self.input_with_key = Input(self.KEY, self.TEXT)
        self.input_with_no_key = Input(self.NO_KEY, self.TEXT)

    def test_constructor(self):
        with self.subTest(input_with_key=self.input_with_key):
            self.assertEqual(self.input_with_key.key, self.KEY)
            self.assertEqual(self.input_with_key.value, self.TEXT)

        with self.subTest(input_with_no_key=self.input_with_no_key):
            self.check_no_key_attribute(self.input_with_no_key)
            self.assertEqual(self.input_with_no_key.value, self.TEXT)

    def test_repr(self):
        with self.subTest('With key attribute'):
            EXPECTED = f'Input(key={self.KEY}, text={self.TEXT})'
            ACTUAL = repr(self.input_with_key)

            self.assertEqual(EXPECTED, ACTUAL)

        with self.subTest('With no key attribute'):
            EXPECTED = f'Input(key={self.NO_KEY}, text={self.TEXT})'
            ACTUAL = repr(self.input_with_no_key)

            self.assertEqual(EXPECTED, ACTUAL)

    def test_equal(self):
        UNEQUAL_TEXT = f'new {self.TEXT}'

        with self.subTest(input_with_key=self.input_with_key):
            self.assertNotEqual(self.input_with_key, self.input_with_no_key)
            self.assertNotEqual(self.input_with_key, 'not an Input')

            EQUAL_INPUT = Input(self.KEY, self.TEXT)

            self.assertEqual(self.input_with_key, EQUAL_INPUT)

            UNEQUAL_KEY = f'new {self.KEY}'

            UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT},
                                  {'key': self.KEY, 'text': UNEQUAL_TEXT}]

            self.check_not_equal_with_and_without_key(self.input_with_key, Input, UNEQUAL_PARAMETERS)

        with self.subTest(input_with_no_key=self.input_with_no_key):
            self.assertNotEqual(self.input_with_no_key, self.input_with_key)
            self.assertNotEqual(self.input_with_no_key, 'not an Input')

            EQUAL_INPUT = Input(self.NO_KEY, self.TEXT)

            self.assertEqual(self.input_with_no_key, EQUAL_INPUT)

            UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': UNEQUAL_TEXT}]

            self.check_not_equal_with_and_without_key(self.input_with_no_key, Input, UNEQUAL_PARAMETERS)
