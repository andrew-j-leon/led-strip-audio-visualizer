import unittest
from typing import Iterable

from libraries.widget_gui import Button, Widget
from util import Font


class ButtonTestCase(unittest.TestCase):
    KEY = 'button_key'
    NEW_KEY = f'new {KEY}'
    NO_KEY = None

    TEXT = 'click me'
    NEW_TEXT = f'new {TEXT}'

    FONT = Font('Arial', 12, 'normal')
    NEW_FONT = Font('Times New Roman', 16, 'bold')

    ENABLED = False
    NEW_ENABLED = not ENABLED

    def setUp(self):
        self.button_with_key = Button(self.KEY, self.TEXT, self.FONT, self.ENABLED)
        self.button_with_no_key = Button(self.NO_KEY, self.TEXT, self.FONT, self.ENABLED)


class TestConstructor(ButtonTestCase):
    def test_with_key(self):
        self.assertEqual(self.button_with_key.key, self.KEY)
        self.assertEqual(self.button_with_key.value, self.TEXT)
        self.assertEqual(self.button_with_key.font, self.FONT)
        self.assertEqual(self.button_with_key.enabled, self.ENABLED)

    def test_without_key(self):
        with self.assertRaises(AttributeError):
            self.button_with_no_key.key

        self.assertEqual(self.button_with_no_key.value, self.TEXT)
        self.assertEqual(self.button_with_no_key.font, self.FONT)
        self.assertEqual(self.button_with_no_key.enabled, self.ENABLED)


class TestSetters(ButtonTestCase):
    def test_setting_value(self):
        self.button_with_key.value = self.NEW_TEXT

        self.assertEqual(self.button_with_key.value, self.NEW_TEXT)

    def test_setting_font(self):
        with self.assertRaises(AttributeError):
            self.button_with_key.font = self.NEW_FONT

        self.assertEqual(self.button_with_key.font, self.FONT)

    def test_setting_enabled(self):
        self.button_with_key.enabled = self.NEW_ENABLED

        self.assertEqual(self.button_with_key.enabled, self.NEW_ENABLED)


class TestRepr(ButtonTestCase):
    def test_with_key(self):
        EXPECTED = f'Button(key={self.KEY}, text={self.TEXT}, font={self.FONT}, enabled={self.ENABLED})'

        self.assertEqual(EXPECTED, repr(self.button_with_key))

    def test_with_no_key(self):
        EXPECTED = f'Button(key={self.NO_KEY}, text={self.TEXT}, font={self.FONT}, enabled={self.ENABLED})'

        self.assertEqual(EXPECTED, repr(self.button_with_no_key))


class TestEqual(ButtonTestCase):
    def test_with_key(self):
        EQUAL_BUTTON = Button(self.KEY, self.TEXT, self.FONT, self.ENABLED)
        self.assertEqual(self.button_with_key, EQUAL_BUTTON)

        self.assertNotEqual(self.button_with_key, self.button_with_no_key)
        self.assertNotEqual(self.button_with_key, 'not a Button')

        UNEQUAL_PARAMETERS = [{'key': self.NEW_KEY, 'text': self.TEXT, 'font': self.FONT, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.NEW_TEXT, 'font': self.FONT, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'font': self.NEW_FONT, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'font': self.FONT, 'enabled': self.NEW_ENABLED}]

        self.check_not_equal_with_and_without_key(self.button_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        EQUAL_BUTTON = Button(self.NO_KEY, self.TEXT, self.FONT, self.ENABLED)
        self.assertEqual(self.button_with_no_key, EQUAL_BUTTON)

        self.assertNotEqual(self.button_with_no_key, self.button_with_key)
        self.assertNotEqual(self.button_with_no_key, 'not a Button')

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.NEW_TEXT, 'font': self.FONT, 'enabled': self.ENABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.NEW_FONT, 'enabled': self.ENABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.FONT, 'enabled': self.NEW_ENABLED}]

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
