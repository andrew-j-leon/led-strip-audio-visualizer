from typing import Iterable
from util import Font
from libraries.widget_gui import Button, Widget
import unittest


class ButtonTestCase(unittest.TestCase):
    KEY = 'button_key'
    NO_KEY = None
    TEXT = 'click me'
    FONT = Font('Times New Roman', 18, 'bold')
    DISABLED = False

    def setUp(self):
        self.button_with_key = Button(self.KEY, self.TEXT, self.FONT, self.DISABLED)
        self.button_with_no_key = Button(self.NO_KEY, self.TEXT, self.FONT, self.DISABLED)


class TestConstructor(ButtonTestCase):
    def test_with_key(self):
        self.assertEqual(self.button_with_key.key, self.KEY)
        self.assertEqual(self.button_with_key.value, self.TEXT)
        self.assertEqual(self.button_with_key.font, self.FONT)
        self.assertEqual(self.button_with_key.disabled, self.DISABLED)

    def test_without_key(self):
        with self.assertRaises(AttributeError):
            self.button_with_no_key.key

        self.assertEqual(self.button_with_no_key.value, self.TEXT)
        self.assertEqual(self.button_with_no_key.font, self.FONT)
        self.assertEqual(self.button_with_no_key.disabled, self.DISABLED)


class TestSettingValue(ButtonTestCase):
    def test_setting_value(self):
        VALUE = f'{self.TEXT} new'

        self.button_with_key.value = VALUE

        self.assertEqual(self.button_with_key.value, VALUE)


class TestRepr(ButtonTestCase):
    def test_with_key(self):
        EXPECTED = f'Button(key={self.KEY}, text={self.TEXT}, font={self.FONT}, disabled={self.DISABLED})'

        self.assertEqual(EXPECTED, repr(self.button_with_key))

    def test_with_no_key(self):
        EXPECTED = f'Button(key={self.NO_KEY}, text={self.TEXT}, font={self.FONT}, disabled={self.DISABLED})'

        self.assertEqual(EXPECTED, repr(self.button_with_no_key))


class TestEqual(ButtonTestCase):
    UNEQUAL_TEXT = f'new {ButtonTestCase.TEXT}'

    FONT_NAME = 'Arial'
    FONT_SIZE = ButtonTestCase.FONT.size + 2
    FONT_STYLE = 'bold'
    UNEQUAL_FONT = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)

    UNEQUAL_DISABLED = not ButtonTestCase.DISABLED

    def test_with_key(self):
        EQUAL_BUTTON = Button(self.KEY, self.TEXT, self.FONT, self.DISABLED)
        self.assertEqual(self.button_with_key, EQUAL_BUTTON)

        self.assertNotEqual(self.button_with_key, self.button_with_no_key)

        UNEQUAL_KEY = f'new {self.KEY}'

        UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT, 'font': self.FONT, 'disabled': self.DISABLED},
                              {'key': self.KEY, 'text': self.UNEQUAL_TEXT, 'font': self.FONT, 'disabled': self.DISABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'font': self.UNEQUAL_FONT, 'disabled': self.DISABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'font': self.FONT, 'disabled': self.UNEQUAL_DISABLED}]

        self.check_not_equal_with_and_without_key(self.button_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        EQUAL_BUTTON = Button(self.NO_KEY, self.TEXT, self.FONT, self.DISABLED)
        self.assertEqual(self.button_with_no_key, EQUAL_BUTTON)

        self.assertNotEqual(self.button_with_no_key, self.button_with_key)

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.UNEQUAL_TEXT, 'font': self.FONT, 'disabled': self.DISABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.UNEQUAL_FONT, 'disabled': self.DISABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.FONT, 'disabled': self.UNEQUAL_DISABLED}]

        self.check_not_equal_with_and_without_key(self.button_with_no_key, UNEQUAL_PARAMETERS)

    def check_not_equal_with_and_without_key(self, widget: Widget, unequal_parameters: Iterable[dict]):
        for parameters in unequal_parameters:

            KEY = parameters['key']

            with self.subTest(parameters=parameters):
                try:
                    unequal_widget_with_key = Button(**parameters)
                    self.assertNotEqual(widget, unequal_widget_with_key)

                    parameters.pop('key')

                    unequal_widget_without_key = Button(**parameters)
                    self.assertNotEqual(widget, unequal_widget_without_key)

                finally:
                    parameters['key'] = KEY
