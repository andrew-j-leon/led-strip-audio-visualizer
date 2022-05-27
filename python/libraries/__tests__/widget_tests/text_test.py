from typing import Iterable
from libraries.widget_gui import Text, Widget
from util import Font

import unittest


class TextTestCase(unittest.TestCase):
    KEY = 'text_key'
    NO_KEY = None
    TEXT = 'hello'
    FONT = Font('Wing Dings', 20, 'italic')

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


class TestSettingValue(TextTestCase):
    def test_set_value(self):
        VALUE = f'{self.TEXT} new'

        self.text_with_key.value = VALUE

        self.assertEqual(self.text_with_key.value, VALUE)


class TestRepr(TextTestCase):
    def test_with_key(self):
        EXPECTED = f'Text(key={self.KEY}, text={self.TEXT}, font={self.FONT})'

        self.assertEqual(EXPECTED, repr(self.text_with_key))

    def test_with_no_key(self):
        EXPECTED = f'Text(key={self.NO_KEY}, text={self.TEXT}, font={self.FONT})'

        self.assertEqual(EXPECTED, repr(self.text_with_no_key))


class TestEqual(TextTestCase):
    UNEQUAL_TEXT = f'new {TextTestCase.TEXT}'

    FONT_NAME = 'Arial'
    FONT_SIZE = TextTestCase.FONT.size + 2
    FONT_STYLE = 'bold'
    UNEQUAL_FONT = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)

    def test_with_key(self):
        self.assertNotEqual(self.text_with_key, self.text_with_no_key)

        EQUAL_TEXT = Text(self.KEY, self.TEXT, self.FONT)

        self.assertEqual(self.text_with_key, EQUAL_TEXT)

        UNEQUAL_KEY = f'new {self.KEY}'

        UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT, 'font': self.FONT},
                              {'key': self.KEY, 'text': self.UNEQUAL_TEXT, 'font': self.FONT},
                              {'key': self.KEY, 'text': self.FONT, 'font': self.UNEQUAL_FONT}]

        self.check_not_equal_with_and_without_key(self.text_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        self.assertNotEqual(self.text_with_no_key, self.text_with_key)

        EQUAL_TEXT = Text(self.NO_KEY, self.TEXT, self.FONT)

        self.assertEqual(self.text_with_no_key, EQUAL_TEXT)

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.UNEQUAL_TEXT, 'font': self.FONT},
                              {'key': self.NO_KEY, 'text': self.FONT, 'font': self.UNEQUAL_FONT}]

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
