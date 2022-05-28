from typing import Iterable
from libraries.widget_gui import Text, Widget
from util import Font

import unittest


class TextTestCase(unittest.TestCase):
    KEY = 'text_key'
    NEW_KEY = f'new {KEY}'
    NO_KEY = None

    TEXT = 'hello'
    NEW_TEXT = f'new {TEXT}'

    FONT = Font('Wing Dings', 20, 'italic')
    NEW_FONT = Font('Arial', 12, 'normal')

    def setUp(self):
        self.text_with_key = Text(self.KEY, self.TEXT, self.FONT)
        self.text_with_no_key = Text(self.NO_KEY, self.TEXT, self.FONT)


class TestConstructor(TextTestCase):
    def test_with_key(self):
        self.assertEqual(self.text_with_key.key, self.KEY)
        self.assertEqual(self.text_with_key.value, self.TEXT)
        self.assertEqual(self.text_with_key.font, self.FONT)

    def test_with_no_key(self):
        with self.assertRaises(AttributeError):
            self.text_with_no_key.key

        self.assertEqual(self.text_with_no_key.value, self.TEXT)
        self.assertEqual(self.text_with_no_key.font, self.FONT)


class TestSetters(TextTestCase):
    def test_setting_value(self):
        self.text_with_key.value = self.NEW_TEXT

        self.assertEqual(self.text_with_key.value, self.NEW_TEXT)

    def test_setting_font(self):
        self.text_with_key.font = self.NEW_FONT

        self.assertEqual(self.text_with_key.font, self.NEW_FONT)


class TestRepr(TextTestCase):
    def test_with_key(self):
        EXPECTED = f'Text(key={self.KEY}, text={self.TEXT}, font={self.FONT})'

        self.assertEqual(EXPECTED, repr(self.text_with_key))

    def test_with_no_key(self):
        EXPECTED = f'Text(key={self.NO_KEY}, text={self.TEXT}, font={self.FONT})'

        self.assertEqual(EXPECTED, repr(self.text_with_no_key))


class TestEqual(TextTestCase):
    def test_with_key(self):
        EQUAL_TEXT = Text(self.KEY, self.TEXT, self.FONT)
        self.assertEqual(self.text_with_key, EQUAL_TEXT)

        self.assertNotEqual(self.text_with_key, self.text_with_no_key)
        self.assertNotEqual(self.text_with_key, 'not Text')

        UNEQUAL_PARAMETERS = [{'key': self.NEW_KEY, 'text': self.TEXT, 'font': self.FONT},
                              {'key': self.KEY, 'text': self.NEW_TEXT, 'font': self.FONT},
                              {'key': self.KEY, 'text': self.FONT, 'font': self.NEW_FONT}]

        self.check_not_equal_with_and_without_key(self.text_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        EQUAL_TEXT = Text(self.NO_KEY, self.TEXT, self.FONT)
        self.assertEqual(self.text_with_no_key, EQUAL_TEXT)

        self.assertNotEqual(self.text_with_no_key, self.text_with_key)
        self.assertNotEqual(self.text_with_key, 'not Text')

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.NEW_TEXT, 'font': self.FONT},
                              {'key': self.NO_KEY, 'text': self.FONT, 'font': self.NEW_FONT}]

        self.check_not_equal_with_and_without_key(self.text_with_no_key, UNEQUAL_PARAMETERS)

    def check_not_equal_with_and_without_key(self, widget: Widget, unequal_parameters: Iterable[dict]):
        for parameters in unequal_parameters:

            KEY = parameters['key']

            with self.subTest(parameters=parameters):
                try:
                    unequal_widget_with_key = Text(**parameters)
                    self.assertNotEqual(widget, unequal_widget_with_key)

                    parameters.pop('key')

                    unequal_widget_without_key = Text(**parameters)
                    self.assertNotEqual(widget, unequal_widget_without_key)

                finally:
                    parameters['key'] = KEY
