import unittest
from typing import Iterable

from libraries.widget_gui import Input, Widget


class InputTestCase(unittest.TestCase):
    KEY = 'input_key'
    NEW_KEY = f'new {KEY}'
    NO_KEY = None

    TEXT = 'some input text'
    NEW_TEXT = f'new {TEXT}'

    ENABLED = False
    NEW_ENABLED = not ENABLED

    def setUp(self):
        self.input_with_key = Input(self.KEY, self.TEXT, self.ENABLED)
        self.input_with_no_key = Input(self.NO_KEY, self.TEXT, self.ENABLED)


class TestConstructor(InputTestCase):
    def test_with_key(self):
        self.assertEqual(self.input_with_key.key, self.KEY)
        self.assertEqual(self.input_with_key.value, self.TEXT)
        self.assertEqual(self.input_with_key.enabled, self.ENABLED)

    def test_with_no_key(self):
        with self.assertRaises(AttributeError):
            self.input_with_no_key.key

        self.assertEqual(self.input_with_no_key.value, self.TEXT)
        self.assertEqual(self.input_with_key.enabled, self.ENABLED)


class TestSetters(InputTestCase):
    def test_setting_value(self):
        self.input_with_key.value = self.NEW_TEXT

        self.assertEqual(self.NEW_TEXT, self.input_with_key.value)

    def test_setting_enabled(self):
        self.input_with_key.enabled = self.NEW_ENABLED

        self.assertEqual(self.input_with_key.enabled, self.NEW_ENABLED)


class TestRepr(InputTestCase):
    def test_with_key(self):
        EXPECTED = f'Input(key={self.KEY}, text={self.TEXT}, enabled={self.ENABLED})'

        self.assertEqual(EXPECTED, repr(self.input_with_key))

    def test_with_no_key(self):
        EXPECTED = f'Input(key={self.NO_KEY}, text={self.TEXT}, enabled={self.ENABLED})'

        self.assertEqual(EXPECTED, repr(self.input_with_no_key))


class TestEqual(InputTestCase):
    def test_with_key(self):
        EQUAL_INPUT = Input(self.KEY, self.TEXT, self.ENABLED)
        self.assertEqual(self.input_with_key, EQUAL_INPUT)

        self.assertNotEqual(self.input_with_key, self.input_with_no_key)
        self.assertNotEqual(self.input_with_key, 'not an Input')

        UNEQUAL_PARAMETERS = [{'key': self.NEW_KEY, 'text': self.TEXT, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.NEW_TEXT, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'enabled': self.NEW_ENABLED}]

        self.check_not_equal_with_and_without_key(self.input_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        EQUAL_INPUT = Input(self.NO_KEY, self.TEXT, self.ENABLED)
        self.assertEqual(self.input_with_no_key, EQUAL_INPUT)

        self.assertNotEqual(self.input_with_no_key, self.input_with_key)
        self.assertNotEqual(self.input_with_no_key, 'not an Input')

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.NEW_TEXT, 'enabled': self.ENABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'enabled': self.NEW_ENABLED}]

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
