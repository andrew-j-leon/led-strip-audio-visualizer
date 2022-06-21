import unittest

from libraries.widget import ColorPicker


class TestColorPicker(unittest.TestCase):
    KEY = 'color_picker_key'

    COLOR = '#1a2B3f'
    NEW_COLOR = '#abCDeF'

    def setUp(self):
        self.color_picker = ColorPicker(self.KEY, self.COLOR)

    def test_constructor(self):
        self.assertEqual(self.color_picker.key, self.KEY)
        self.assertEqual(self.color_picker.value, self.COLOR)

    def test_setting_value_to_valid_hex_color(self):
        VALID_HEX_COLORS = ['#123456', '#abcdef', '#ABCDEF']

        for valid_hex_color in VALID_HEX_COLORS:
            with self.subTest(value=valid_hex_color):
                self.color_picker.value = valid_hex_color

                self.assertEqual(self.color_picker.value, valid_hex_color)

    def test_setting_value_to_invalid_hex_color(self):
        INVALID_HEX_COLORS = ['', '#12345', '#', '#1', '123456', '#12345G', None]

        for invalid_hex_color in INVALID_HEX_COLORS:
            with self.subTest(value=invalid_hex_color):

                with self.assertRaises(ValueError):
                    self.color_picker.value = invalid_hex_color

                self.assertEqual(self.color_picker.value, self.COLOR)

    def test_repr(self):
        EXPECTED = f'ColorPicker(key={self.KEY}, color={self.COLOR})'

        self.assertEqual(repr(self.color_picker), EXPECTED)

    def test_are_equal(self):
        EQUAL_COLOR_PICKER = ColorPicker(self.KEY, self.COLOR)

        self.assertEqual(self.color_picker, EQUAL_COLOR_PICKER)

    def test_are_not_equal(self):
        NEW_KEY = f'new {self.color_picker.key}'
        UNEQUAL_COLOR_PICKER = ColorPicker(NEW_KEY, self.color_picker.value)

        self.assertNotEqual(self.color_picker, UNEQUAL_COLOR_PICKER)
        self.assertNotEqual(self.color_picker, 'not a color picker')
