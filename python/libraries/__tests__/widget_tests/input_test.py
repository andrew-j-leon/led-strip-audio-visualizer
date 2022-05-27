from typing import Iterable
from libraries.widget_gui import Input, Widget
import unittest


class InputTestCase(unittest.TestCase):
    NO_KEY = None
    KEY = 'input_key'
    TEXT = 'some input text'

    def setUp(self):
        self.input_with_key = Input(self.KEY, self.TEXT)
        self.input_with_no_key = Input(self.NO_KEY, self.TEXT)


class TestConstructor(InputTestCase):
    def test_with_key(self):
        self.assertEqual(self.input_with_key.key, self.KEY)
        self.assertEqual(self.input_with_key.value, self.TEXT)

    def test_with_no_key(self):
        with self.assertRaises(AttributeError):
            self.input_with_no_key.key

        self.assertEqual(self.input_with_no_key.value, self.TEXT)


class TestSettingValue(InputTestCase):
    def test_set_value(self):
        VALUE = f'new {self.TEXT}'

        self.input_with_key.value = VALUE

        self.assertEqual(VALUE, self.input_with_key.value)


class TestRepr(InputTestCase):
    def test_with_key(self):
        EXPECTED = f'Input(key={self.KEY}, text={self.TEXT})'

        self.assertEqual(EXPECTED, repr(self.input_with_key))

    def test_with_no_key(self):
        EXPECTED = f'Input(key={self.NO_KEY}, text={self.TEXT})'

        self.assertEqual(EXPECTED, repr(self.input_with_no_key))


class TestEqual(InputTestCase):
    UNEQUAL_TEXT = f'new {InputTestCase.TEXT}'

    def test_with_key(self):
        self.assertNotEqual(self.input_with_key, self.input_with_no_key)
        self.assertNotEqual(self.input_with_key, 'not an Input')

        EQUAL_INPUT = Input(self.KEY, self.TEXT)

        self.assertEqual(self.input_with_key, EQUAL_INPUT)

        UNEQUAL_KEY = f'new {self.KEY}'

        UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT},
                              {'key': self.KEY, 'text': self.UNEQUAL_TEXT}]

        self.check_not_equal_with_and_without_key(self.input_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        self.assertNotEqual(self.input_with_no_key, self.input_with_key)
        self.assertNotEqual(self.input_with_no_key, 'not an Input')

        EQUAL_INPUT = Input(self.NO_KEY, self.TEXT)

        self.assertEqual(self.input_with_no_key, EQUAL_INPUT)

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.UNEQUAL_TEXT}]

        self.check_not_equal_with_and_without_key(self.input_with_no_key, UNEQUAL_PARAMETERS)

    def check_not_equal_with_and_without_key(self, widget: Widget, unequal_parameters: Iterable[dict]):
        for parameters in unequal_parameters:

            KEY = parameters['key']

            with self.subTest(parameters=parameters):
                try:
                    unequal_widget_with_key = Input(**parameters)
                    self.assertNotEqual(widget, unequal_widget_with_key)

                    parameters.pop('key')

                    unequal_widget_without_key = Input(**parameters)
                    self.assertNotEqual(widget, unequal_widget_without_key)

                finally:
                    parameters['key'] = KEY
