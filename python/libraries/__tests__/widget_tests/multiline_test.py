from typing import Iterable
from libraries.gui import Multiline, Widget
import unittest


class MultilineTestCase(unittest.TestCase):
    KEY = 'multiline_key'
    NO_KEY = None
    TEXT = 'some multiline text'
    SIZE = (20, 30)
    AUTO_SCROLL = False

    def setUp(self):
        self.multiline_with_key = Multiline(self.KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)
        self.multiline_with_no_key = Multiline(self.NO_KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)


class TestConstructor(MultilineTestCase):
    def test_with_key(self):
        self.assertEqual(self.multiline_with_key.key, self.KEY)
        self.assertEqual(self.multiline_with_key.value, self.TEXT)
        self.assertEqual(self.multiline_with_key.size, self.SIZE)
        self.assertEqual(self.multiline_with_key.auto_scroll, self.AUTO_SCROLL)

    def test_with_no_key(self):
        with self.assertRaises(AttributeError):
            self.multiline_with_no_key.key

        self.assertEqual(self.multiline_with_no_key.value, self.TEXT)
        self.assertEqual(self.multiline_with_no_key.size, self.SIZE)
        self.assertEqual(self.multiline_with_no_key.auto_scroll, self.AUTO_SCROLL)


class TestSettingValue(MultilineTestCase):
    def test_set_value(self):
        TEXT = f'New {self.TEXT}'

        self.multiline_with_key.value = TEXT

        self.assertEqual(TEXT, self.multiline_with_key.value)


class TestRepr(MultilineTestCase):
    def test_with_key(self):
        EXPECTED = f'Multiline(key={self.KEY}, text={self.TEXT}, size={self.SIZE}, auto_scroll={self.AUTO_SCROLL})'

        self.assertEqual(EXPECTED, repr(self.multiline_with_key))

    def test_with_no_key(self):
        EXPECTED = f'Multiline(key={self.NO_KEY}, text={self.TEXT}, size={self.SIZE}, auto_scroll={self.AUTO_SCROLL})'

        self.assertEqual(EXPECTED, repr(self.multiline_with_no_key))


class TestEqual(MultilineTestCase):
    UNEQUAL_TEXT = f'new {MultilineTestCase.TEXT}'
    UNEQUAL_SIZE = (MultilineTestCase.SIZE[0] + 10,
                    MultilineTestCase.SIZE[1] + 20)
    UNEQUAL_AUTO_SCROLL = not MultilineTestCase.AUTO_SCROLL

    def test_with_key(self):
        self.assertNotEqual(self.multiline_with_key, self.multiline_with_no_key)
        self.assertNotEqual(self.multiline_with_key, 'not a Multiline')

        EQUAL_MULTILINE = Multiline(self.KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)

        self.assertEqual(self.multiline_with_key, EQUAL_MULTILINE)

        UNEQUAL_KEY = f'new {self.KEY}'

        UNEQUAL_PARAMETERS = [{'key': UNEQUAL_KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL},
                              {'key': self.KEY, 'text': self.UNEQUAL_TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL},
                              {'key': self.KEY, 'text': self.TEXT, 'size': self.UNEQUAL_SIZE, 'auto_scroll': self.AUTO_SCROLL},
                              {'key': self.KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': self.UNEQUAL_AUTO_SCROLL}]

        self.check_not_equal_with_and_without_key(self.multiline_with_key, UNEQUAL_PARAMETERS)

    def test_with_no_key(self):
        self.assertNotEqual(self.multiline_with_no_key, self.multiline_with_key)
        self.assertNotEqual(self.multiline_with_no_key, 'not a Multiline')

        EQUAL_MULTILINE = Multiline(self.NO_KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)

        self.assertEqual(self.multiline_with_no_key, EQUAL_MULTILINE)

        UNEQUAL_PARAMETERS = [{'key': self.NO_KEY, 'text': self.UNEQUAL_TEXT, 'size': self.SIZE, 'auto_scroll': self.AUTO_SCROLL},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'size': self.UNEQUAL_SIZE, 'auto_scroll': self.AUTO_SCROLL},
                              {'key': self.NO_KEY, 'text': self.TEXT, 'size': self.SIZE, 'auto_scroll': self.UNEQUAL_AUTO_SCROLL}]

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
