import unittest

from util.rgb import RGB


class TestRGB(unittest.TestCase):
    def test_empty_constructor(self):
        RGB()

    def test_constructor(self):
        VALID_RGBS = [(0, 0, 0), (255, 255, 255), (1, 1, 1), (254, 254, 254),
                      (100, 34, 213)]

        for valid_rgb in VALID_RGBS:

            with self.subTest(f'rgb={valid_rgb}'):
                red, green, blue = valid_rgb

                rgb = RGB(red, green, blue)

                self.assertEqual(rgb.red, red)
                self.assertEqual(rgb.green, green)
                self.assertEqual(rgb.blue, blue)

        INVALID_RGBS = [(-1, 0, 0), (0, -1, 0), (0, 0, -1),
                        (-5, 0, 0), (0, -5, 0), (0, 0, -5),
                        (256, 0, 0), (0, 256, 0), (0, 0, 256),
                        (300, 0, 0), (0, 300, 0), (0, 0, 300)]

        for invalid_rgb in INVALID_RGBS:
            with self.subTest(f'rgb={invalid_rgb}'):

                with self.assertRaises(ValueError) as error:
                    red, green, blue = invalid_rgb

                    RGB(red, green, blue)

                actual_error_message = str(error.exception)
                expected_error_message = f'rgb values must be between 0 (inclusive) & 255 (inclusive), (red, green, blue) was {invalid_rgb}.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_repr(self):
        RED = 1
        GREEN = 2
        BLUE = 3

        rgb = RGB(RED, GREEN, BLUE)

        self.assertEqual(repr(rgb), f'RGB({RED}, {GREEN}, {BLUE})')

    def test_eq(self):
        RED = 10
        GREEN = 20
        BLUE = 30
        rgb = RGB(RED, GREEN, BLUE)

        EQUALS_RGB = (RGB(RED, GREEN, BLUE), (RED, GREEN, BLUE), [RED, GREEN, BLUE])

        for equals_rgb in EQUALS_RGB:
            with self.subTest(rgb=rgb, equals_rgb=equals_rgb):
                self.assertEqual(rgb, equals_rgb)

        DOES_NOT_EQUAL_RGB = [RGB(RED - 1, GREEN - 1, BLUE - 1), RGB(RED - 10, GREEN - 10, BLUE - 10),
                              (RED - 1, GREEN - 1, BLUE - 1), (RED - 10, GREEN - 10, BLUE - 10),
                              [RED - 1, GREEN - 1, BLUE - 1], [RED - 10, GREEN - 10, BLUE - 10],

                              RGB(RED + 1, GREEN + 1, BLUE + 1), RGB(RED + 10, GREEN + 10, BLUE + 10),
                              (RED + 1, GREEN + 1, BLUE + 1), (RED + 10, GREEN + 10, BLUE + 10),
                              [RED + 1, GREEN + 1, BLUE + 1], [RED + 10, GREEN + 10, BLUE + 10]]

        for does_not_equal_rgb in DOES_NOT_EQUAL_RGB:
            with self.subTest(rgb=rgb, does_not_equal_rgb=does_not_equal_rgb):
                self.assertNotEqual(rgb, does_not_equal_rgb)

    def test_iter(self):
        rgb_tuple = (10, 20, 30)
        rgb = RGB(*rgb_tuple)

        self.assertEqual(tuple(rgb), rgb_tuple)
