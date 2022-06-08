import unittest
from typing import Iterable

from libraries.widget import Widget, CheckBox
from util import Font


class CheckBoxTestCase(unittest.TestCase):
    KEY = 'check_box_key'
    NEW_KEY = f'new {KEY}'
    NO_KEY = None

    TEXT = 'hello i am a checkbox'
    NEW_TEXT = f'new {TEXT}'

    FONT = Font('Arial', 12, 'normal')
    NEW_FONT = Font('Times New Roman', 16, 'bold')

    VALUE = True
    NEW_VALUE = not VALUE

    ENABLED = False
    NEW_ENABLED = not ENABLED

    def setUp(self):
        self.check_box_with_key = CheckBox(self.KEY, self.TEXT, self.FONT, self.VALUE, self.ENABLED)
        self.check_box_with_no_key = CheckBox(self.NO_KEY, self.TEXT, self.FONT, self.VALUE, self.ENABLED)


class TestConstructor(CheckBoxTestCase):
    def test_with_key(self):
        self.assertEqual(self.check_box_with_key.key, self.KEY)
        self.assertEqual(self.check_box_with_key.text, self.TEXT)
        self.assertEqual(self.check_box_with_key.font, self.FONT)
        self.assertEqual(self.check_box_with_key.value, self.VALUE)
        self.assertEqual(self.check_box_with_key.enabled, self.ENABLED)

    def test_with_no_key(self):
        with self.assertRaises(AttributeError):
            self.check_box_with_no_key.key

        self.assertEqual(self.check_box_with_no_key.text, self.TEXT)
        self.assertEqual(self.check_box_with_no_key.font, self.FONT)
        self.assertEqual(self.check_box_with_no_key.value, self.VALUE)
        self.assertEqual(self.check_box_with_key.enabled, self.ENABLED)


class TestSettingValue(CheckBoxTestCase):
    def test_setting_value(self):
        self.check_box_with_key.value = self.NEW_VALUE

        self.assertEqual(self.NEW_VALUE, self.check_box_with_key.value)

    def test_setting_text(self):
        self.check_box_with_key.text = self.TEXT

        self.assertEqual(self.TEXT, self.check_box_with_key.text)

    def test_setting_font(self):
        with self.assertRaises(AttributeError):
            self.check_box_with_key.font = self.NEW_FONT

        self.assertEqual(self.FONT, self.check_box_with_key.font)

    def test_setting_enabled(self):
        self.check_box_with_key.enabled = self.NEW_ENABLED

        self.assertEqual(self.NEW_ENABLED, self.check_box_with_key.enabled)


class TestRepr(CheckBoxTestCase):
    def test_with_key(self):
        EXPECTED = f'CheckBox(key={self.KEY}, text={self.TEXT}, font={self.FONT}, value={self.VALUE}, enabled={self.ENABLED})'

        self.assertEqual(EXPECTED, repr(self.check_box_with_key))

    def test_with_no_key(self):
        EXPECTED = f'CheckBox(key={self.NO_KEY}, text={self.TEXT}, font={self.FONT}, value={self.VALUE}, enabled={self.ENABLED})'

        self.assertEqual(EXPECTED, repr(self.check_box_with_no_key))


class TestEqual(CheckBoxTestCase):
    def test_with_key(self):
        EQUAL_CHECK_BOX = CheckBox(self.KEY, self.TEXT, self.FONT, self.VALUE, self.ENABLED)
        self.assertEqual(self.check_box_with_key, EQUAL_CHECK_BOX)

        self.assertNotEqual(self.check_box_with_key, self.check_box_with_no_key)
        self.assertNotEqual(self.check_box_with_key, 'not a checkbox')

        UNEQUAL_PARAMETERS = [{'key': self.NEW_KEY, 'text': self.TEXT, 'font': self.FONT, 'value': self.VALUE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.NEW_TEXT, 'font': self.FONT, 'value': self.VALUE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'font': self.NEW_FONT, 'value': self.VALUE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'font': self.FONT, 'value': self.NEW_VALUE, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'font': self.FONT, 'value': self.VALUE, 'enabled': self.NEW_ENABLED}]

        self.check_not_equal_with_and_without_key(self.check_box_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        EQUAL_CHECK_BOX = CheckBox(self.NO_KEY, self.TEXT, self.FONT, self.VALUE, self.ENABLED)
        self.assertEqual(self.check_box_with_no_key, EQUAL_CHECK_BOX)

        self.assertNotEqual(self.check_box_with_no_key, self.check_box_with_key)
        self.assertNotEqual(self.check_box_with_no_key, 'not a checkbox')

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.NEW_TEXT, 'font': self.FONT, 'value': self.VALUE, 'enabled': self.ENABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.NEW_FONT, 'value': self.VALUE, 'enabled': self.ENABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.FONT, 'value': self.NEW_VALUE, 'enabled': self.ENABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.FONT, 'value': self.VALUE, 'enabled': self.NEW_ENABLED}]

        self.check_not_equal_with_and_without_key(self.check_box_with_no_key, UNEQUAL_PARAMETERS)

    def check_not_equal_with_and_without_key(self, widget: Widget, unequal_parameters: Iterable[dict]):
        for parameters in unequal_parameters:

            KEY = parameters['key']

            with self.subTest(parameters=parameters):
                try:
                    unequal_widget_with_key = CheckBox(**parameters)
                    self.assertNotEqual(widget, unequal_widget_with_key)

                    parameters.pop('key')

                    unequal_widget_without_key = CheckBox(**parameters)
                    self.assertNotEqual(widget, unequal_widget_without_key)

                finally:
                    parameters['key'] = KEY
