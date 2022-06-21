import unittest

from color_palette import ColorPalette


class ColorPaletteTestCase(unittest.TestCase):
    AMPLITUDE_RGBS = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    NEW_AMPLITUDE_RGBS = [(3, 3, 3), (4, 4, 4), (5, 5, 5)]

    def setUp(self):
        self.color_palette = ColorPalette(self.AMPLITUDE_RGBS)


class TestConstructor(ColorPaletteTestCase):
    def test_constructor(self):
        self.assertEqual(self.color_palette.amplitude_rgbs, self.AMPLITUDE_RGBS)


class TestEqual(ColorPaletteTestCase):
    def test_equal(self):
        color_palette = ColorPalette(self.AMPLITUDE_RGBS)

        self.assertEqual(self.color_palette, color_palette)

    def test_not_equal(self):
        non_equal_color_palette = ColorPalette(self.NEW_AMPLITUDE_RGBS)

        self.assertNotEqual(self.color_palette, non_equal_color_palette)

        self.assertNotEqual(self.color_palette, None)


class TestSettingAmplitudeRgbs(ColorPaletteTestCase):

    def test_valid_amplitude_rgbs(self):
        AMPLITUDE_RGBS = [[(0, 0, 0)],

                          [(100, 0, 0)], [(0, 100, 0)], [(0, 0, 100)],

                          [(255, 0, 0)], [(0, 255, 0)], [(0, 0, 255)]]

        for amplitude_rgbs in AMPLITUDE_RGBS:

            with self.subTest(amplitude_rgbs=amplitude_rgbs):
                self.color_palette.amplitude_rgbs = amplitude_rgbs

                self.assertEqual(self.color_palette.amplitude_rgbs, amplitude_rgbs)

    def test_empty_amplitude_rgbs(self):
        AMPLITUDE_RGBS = []

        self.color_palette.amplitude_rgbs = AMPLITUDE_RGBS

        self.assertEqual(self.color_palette.amplitude_rgbs, AMPLITUDE_RGBS)

    def test_color_value_out_of_range(self):
        AMPLITUDE_RGBS = [[(-1, 0, 0)], [(0, -1, 0)], [(0, 0, -1)],

                          [(-10, 0, 0)], [(0, -10, 0)], [(0, 0, -10)],

                          [(256, 0, 0)], [(0, 256, 0)], [(0, 0, 256)],

                          [(300, 0, 0)], [(0, 300, 0)], [(0, 0, 300)]]

        for amplitude_rgbs in AMPLITUDE_RGBS:

            with self.subTest(amplitude_rgbs=amplitude_rgbs):

                with self.assertRaises(ValueError):
                    self.color_palette.amplitude_rgbs = amplitude_rgbs

    def test_not_an_rgb(self):
        NOT_AMPLITUDE_RGBS = [[(1, 2, 3, 4)], [(1, 2)]]

        for amplitude_rgbs in NOT_AMPLITUDE_RGBS:

            with self.subTest(amplitude_rgbs=amplitude_rgbs):

                with self.assertRaises(ValueError):
                    self.color_palette.amplitude_rgbs = amplitude_rgbs
