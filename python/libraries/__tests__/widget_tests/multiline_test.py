import unittest
from typing import Iterable

from libraries.widget import Widget, Multiline


class MultilineTestCase(unittest.TestCase):
    KEY = 'multiline_key'
    NEW_KEY = f'new {KEY}'
    NO_KEY = None

    TEXT = 'some multiline text'
    NEW_TEXT = f'new {TEXT}'

    SIZE = (20, 30)
    NEW_SIZE = (40, 50)

    AUTO_SCROLL = False
    NEW_AUTO_SCROLL = not AUTO_SCROLL

    ENABLED = False
    NEW_ENABLED = not ENABLED

    def setUp(self):
        self.multiline_with_key = Multiline(self.KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL, self.ENABLED)
        self.multiline_with_no_key = Multiline(self.NO_KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL, self.ENABLED)


class TestConstructor(MultilineTestCase):
    def test_with_key(self):
        self.assertEqual(self.multiline_with_key.key, self.KEY)
        self.assertEqual(self.multiline_with_key.value, self.TEXT)
        self.assertEqual(self.multiline_with_key.size, self.SIZE)
        self.assertEqual(self.multiline_with_key.auto_scroll, self.AUTO_SCROLL)
        self.assertEqual(self.multiline_with_key.enabled, self.ENABLED)

    def test_with_no_key(self):
        with self.assertRaises(AttributeError):
            self.multiline_with_no_key.key

        self.assertEqual(self.multiline_with_no_key.value, self.TEXT)
        self.assertEqual(self.multiline_with_no_key.size, self.SIZE)
        self.assertEqual(self.multiline_with_no_key.auto_scroll, self.AUTO_SCROLL)
        self.assertEqual(self.multiline_with_key.enabled, self.ENABLED)


class TestSetters(MultilineTestCase):
    def test_setting_value(self):
        self.multiline_with_key.value = self.NEW_TEXT

        self.assertEqual(self.NEW_TEXT, self.multiline_with_key.value)

    def test_setting_size(self):
        self.multiline_with_key.size = self.NEW_SIZE

        self.assertEqual(self.multiline_with_key.size, self.NEW_SIZE)

    def test_setting_auto_scroll(self):
        self.multiline_with_key.auto_scroll = self.NEW_AUTO_SCROLL

        self.assertEqual(self.multiline_with_key.auto_scroll, self.NEW_AUTO_SCROLL)

    def test_setting_enabled(self):
        self.multiline_with_key.enabled = self.NEW_ENABLED

        self.assertEqual(self.multiline_with_key.enabled, self.NEW_ENABLED)


class TestRepr(MultilineTestCase):
    def test_with_key(self):
        EXPECTED = f'Multiline(key={self.KEY}, text={self.TEXT}, size={self.SIZE}, auto_scroll={self.AUTO_SCROLL}, enabled={self.ENABLED})'

        self.assertEqual(EXPECTED, repr(self.multiline_with_key))

    def test_with_no_key(self):
        EXPECTED = f'Multiline(key={self.NO_KEY}, text={self.TEXT}, size={self.SIZE}, auto_scroll={self.AUTO_SCROLL}, enabled={self.ENABLED})'

        self.assertEqual(EXPECTED, repr(self.multiline_with_no_key))


class TestEqual(MultilineTestCase):
    def test_with_key(self):
        EQUAL_MULTILINE = Multiline(self.KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL, self.ENABLED)
        self.assertEqual(self.multiline_with_key, EQUAL_MULTILINE)

        self.assertNotEqual(self.multiline_with_key, self.multiline_with_no_key)
        self.assertNotEqual(self.multiline_with_key, 'not a Multiline')

        UNEQUAL_PARAMETERS = [{'key': self.NEW_KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.NEW_TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'size': self.NEW_SIZE, 'auto_scroll': self.AUTO_SCROLL, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': self.NEW_AUTO_SCROLL, 'enabled': self.ENABLED},
                              {'key': self.KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL, 'enabled': self.NEW_ENABLED}]

        self.check_not_equal_with_and_without_key(self.multiline_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        EQUAL_MULTILINE = Multiline(self.NO_KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL, self.ENABLED)
        self.assertEqual(self.multiline_with_no_key, EQUAL_MULTILINE)

        self.assertNotEqual(self.multiline_with_no_key, self.multiline_with_key)
        self.assertNotEqual(self.multiline_with_no_key, 'not a Multiline')

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.NEW_TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL, 'enabled': self.ENABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'size': self.NEW_SIZE, 'auto_scroll': self.AUTO_SCROLL, 'enabled': self.ENABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': self.NEW_AUTO_SCROLL, 'enabled': self.ENABLED},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL, 'enabled': self.NEW_ENABLED}]

        self.check_not_equal_with_and_without_key(self.multiline_with_no_key, UNEQUAL_PARAMETERS)

    def check_not_equal_with_and_without_key(self, widget: Widget, unequal_parameters: Iterable[dict]):
        for parameters in unequal_parameters:

            KEY = parameters['key']

            with self.subTest(parameters=parameters):
                try:
                    unequal_widget_with_key = Multiline(**parameters)
                    self.assertNotEqual(widget, unequal_widget_with_key)

                    parameters.pop('key')

                    unequal_widget_without_key = Multiline(**parameters)
                    self.assertNotEqual(widget, unequal_widget_without_key)

                finally:
                    parameters['key'] = KEY
