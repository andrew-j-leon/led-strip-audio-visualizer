from typing import Iterable
from libraries.gui import CheckBox, Font, Widget
import unittest


class CheckBoxTestCase(unittest.TestCase):
    KEY = 'check_box_key'
    NO_KEY = None
    TEXT = 'hello i am a checkbox'
    FONT = Font('some font', 20)
    VALUE = True

    def setUp(self):
        self.check_box_with_key = CheckBox(self.KEY, self.TEXT, self.FONT, self.VALUE)
        self.check_box_with_no_key = CheckBox(self.NO_KEY, self.TEXT, self.FONT, self.VALUE)


class TestConstructor(CheckBoxTestCase):
    def test_with_key(self):
        self.assertEqual(self.check_box_with_key.key, self.KEY)
        self.assertEqual(self.check_box_with_key.text, self.TEXT)
        self.assertEqual(self.check_box_with_key.font, self.FONT)
        self.assertEqual(self.check_box_with_key.value, self.VALUE)

    def test_with_no_key(self):
        with self.assertRaises(AttributeError):
            self.check_box_with_no_key.key

        self.assertEqual(self.check_box_with_no_key.text, self.TEXT)
        self.assertEqual(self.check_box_with_no_key.font, self.FONT)
        self.assertEqual(self.check_box_with_no_key.value, self.VALUE)


class TestSettingValue(CheckBoxTestCase):
    def test_set_value(self):
        VALUE = not self.VALUE

        self.check_box_with_key.value = VALUE

        self.assertEqual(VALUE, self.check_box_with_key.disabled)


class TestRepr(CheckBoxTestCase):
    def test_with_key(self):
        EXPECTED = f'CheckBox(key={self.KEY}, text={self.TEXT}, font={self.FONT}, value={self.VALUE})'

        self.assertEqual(EXPECTED, repr(self.check_box_with_key))

    def test_with_no_key(self):
        EXPECTED = f'CheckBox(key={self.NO_KEY}, text={self.TEXT}, font={self.FONT}, value={self.VALUE})'

        self.assertEqual(EXPECTED, repr(self.check_box_with_no_key))


class TestEqual(CheckBoxTestCase):
    UNEQUAL_TEXT = f'new {CheckBoxTestCase.TEXT}'

    FONT_NAME = 'Arial'
    FONT_SIZE = CheckBoxTestCase.FONT.size + 2
    FONT_STYLE = 'bold'
    UNEQUAL_FONT = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)

    UNEQUAL_VALUE = not CheckBoxTestCase.VALUE

    def test_with_key(self):
        self.assertNotEqual(self.check_box_with_key, self.check_box_with_no_key)
        self.assertNotEqual(self.check_box_with_key, 'not a checkbox')

        EQUAL_CHECK_BOX = CheckBox(self.KEY, self.TEXT, self.FONT, self.VALUE)

        self.assertEqual(self.check_box_with_key, EQUAL_CHECK_BOX)

        UNEQUAL_KEY = f'new {self.KEY}'

        UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT, 'font': self.FONT, 'value': self.VALUE},
                              {'key': self.KEY, 'text': self.UNEQUAL_TEXT, 'font': self.FONT, 'value': self.VALUE},
                              {'key': self.KEY, 'text': self.TEXT, 'font': self.UNEQUAL_FONT, 'value': self.VALUE},
                              {'key': self.KEY, 'text': self.TEXT, 'font': self.FONT, 'value': self.UNEQUAL_VALUE}]

        self.check_not_equal_with_and_without_key(self.check_box_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        self.assertNotEqual(self.check_box_with_no_key, self.check_box_with_key)
        self.assertNotEqual(self.check_box_with_no_key, 'not a checkbox')

        EQUAL_CHECK_BOX = CheckBox(self.NO_KEY, self.TEXT, self.FONT, self.VALUE)

        self.assertEqual(self.check_box_with_no_key, EQUAL_CHECK_BOX)

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.UNEQUAL_TEXT, 'font': self.FONT, 'value': self.VALUE},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.UNEQUAL_FONT, 'value': self.VALUE},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'font': self.FONT, 'value': self.UNEQUAL_VALUE}]

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
