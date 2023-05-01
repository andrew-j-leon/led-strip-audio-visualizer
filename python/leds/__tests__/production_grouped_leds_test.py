import unittest
from typing import List, Tuple

from leds.frequency_band_leds import ProductionFrequencyBandLeds


class TestConstructor(unittest.TestCase):

    def test_valid_led_ranges(self):
        VALID_LED_RANGES = [(0, 0), (0, 1), (0, 150), (1, 1), (1, 150)]

        for valid_led_range in VALID_LED_RANGES:
            with self.subTest(led_range=valid_led_range):

                band_led_ranges = []

                ProductionFrequencyBandLeds(valid_led_range, band_led_ranges)

    def test_led_ranges_where_start_is_greater_than_end(self):
        INVALID_LED_RANGES = [(-1, 0), (0, -1), (-1, -1),
                              (-10, 0), (0, -10),
                              (1, 0), (10, 0),
                              (10, 9), (10, 5)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(ValueError):
                    band_led_ranges = []

                    ProductionFrequencyBandLeds(invalid_led_range, band_led_ranges)

    def test_led_ranges_where_start_is_not_int(self):
        INVALID_LED_RANGES = [(0.0, 1), (1.0, 10), (100.0, 200)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(TypeError):
                    band_led_ranges = []

                    ProductionFrequencyBandLeds(invalid_led_range, band_led_ranges)

    def test_led_ranges_where_end_is_float(self):
        INVALID_LED_RANGES = [(0, 0.0), (0, 1.0), (0, 100.0)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(TypeError):
                    band_led_ranges = []

                    ProductionFrequencyBandLeds(invalid_led_range, band_led_ranges)

    def test_group_led_ranges_with_varying_lengths(self):
        START_LED = 0
        END_LED = 100
        LED_RANGE = (START_LED, END_LED)
        GROUP_LED_RANGES = [set(), {(0, 10)}, {(10, 20), (20, 30)}, {(30, 40), (40, 50), (70, 80), (90, 100)}]

        frequency_band_leds = ProductionFrequencyBandLeds(LED_RANGE, GROUP_LED_RANGES)

        self.assertEqual(frequency_band_leds.start_led, START_LED)
        self.assertEqual(frequency_band_leds.end_led, END_LED)
        self.assertEqual(frequency_band_leds.number_of_bands, len(GROUP_LED_RANGES))
        self.assertEqual(frequency_band_leds.number_of_leds, END_LED - START_LED)

        for band_number in range(len(GROUP_LED_RANGES)):
            with self.subTest(band_number=band_number):
                self.assertEqual(frequency_band_leds.get_band_led_ranges(band_number), GROUP_LED_RANGES[band_number])

    def test_group_led_ranges_with_led_range_starting_at_0(self):
        LED_RANGE_STARTING_AT_0 = (0, 150)

        VALID_GROUP_LED_RANGES = [[[(0, 1)]],
                                  [[(0, 150)]],
                                  [[(1, 150)]]]

        INVALID_GROUP_LED_RANGES = [[[(-1, 0)]],
                                    [[(0, -1)]],
                                    [[(-1, -1)]],
                                    [[(-10, 0)]],
                                    [[(0, -10)]],
                                    [[(1, 0)]],
                                    [[(10, 0)]],
                                    [[(10, 9)]],
                                    [[(10, 5)]],
                                    [[(0, 0)]], [[(1, 1)]], [[(150, 150)], [(151, 151)], [(300, 300)]]]

        self.check_valid_group_led_ranges(LED_RANGE_STARTING_AT_0, VALID_GROUP_LED_RANGES)
        self.check_invalid_group_led_ranges(LED_RANGE_STARTING_AT_0, INVALID_GROUP_LED_RANGES)

    def test_group_led_ranges_with_led_range_starting_at_10(self):
        LED_RANGE_STARTING_AT_10 = (10, 150)

        VALID_GROUP_LED_RANGES = [
            [[(10, 11)]],
            [[(10, 150)]],
            [[(149, 150)]],
            [[(10, 90)], [(90, 150)]]
        ]

        INVALID_GROUP_LED_RANGES = [
            [[(0, 1)]],
            [[(0, 10)]],
            [[(0, 150)]],
            [[(0, 151)]],
            [[(0, 300)]],
            [[(9, 10)]],
            [[(9, 11)]],
            [[(9, 150)]],
            [[(9, 300)]],
            [[(10, 151)]],
            [[(10, 300)]],
            [[(50, 151)]],
            [[(50, 300)]],
            [[(150, 151)]],
            [[(150, 300)]],
            [[(151, 152)]],
            [[(152, 300)]],
            [[(10, 10)]], [[(150, 150)]]
        ]

        self.check_valid_group_led_ranges(LED_RANGE_STARTING_AT_10, VALID_GROUP_LED_RANGES)
        self.check_invalid_group_led_ranges(LED_RANGE_STARTING_AT_10, INVALID_GROUP_LED_RANGES)

    def check_valid_group_led_ranges(self, led_range: Tuple[int, int],
                                     valid_group_led_ranges: List[List[List[Tuple[int, int]]]]):
        for led_ranges in valid_group_led_ranges:
            with self.subTest(led_range=led_range, led_ranges=led_ranges):

                ProductionFrequencyBandLeds(led_range, led_ranges)

    def check_invalid_group_led_ranges(self, led_range: Tuple[int, int],
                                       invalid_group_led_ranges: List[List[List[Tuple[int, int]]]]):
        for led_ranges in invalid_group_led_ranges:
            with self.subTest(led_range=led_range, led_ranges=led_ranges):

                with self.assertRaises(ValueError):
                    ProductionFrequencyBandLeds(led_range, led_ranges)


class TestMethods(unittest.TestCase):
    def test_number_of_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = [[],
                            [[(0, 10)]],
                            [[(0, 10)], [(10, 20)]],

                            [[(0, 10)], [(10, 20)], [(20, 30)], [(30, 40)], [(40, 50)],
                            [(50, 60)], [(60, 70)], [(70, 80)], [(80, 90)], [(90, 100)]]]

        for band_led_ranges in GROUP_LED_RANGES:
            with self.subTest(number_of_bands=len(band_led_ranges)):

                led_strip = ProductionFrequencyBandLeds(LED_RANGE, band_led_ranges)

                self.assertEqual(led_strip.number_of_bands, len(band_led_ranges))

    def test_number_of_leds(self):
        NUMBER_OF_LEDS = [0, 1, 15, 300]

        for number_of_leds in NUMBER_OF_LEDS:
            with self.subTest(number_of_leds=number_of_leds):

                led_range = (0, number_of_leds)
                band_led_ranges = []

                led_strip = ProductionFrequencyBandLeds(led_range, band_led_ranges)

                self.assertEqual(number_of_leds, led_strip.number_of_leds)

    def test_start_led_and_end_led(self):
        LED_RANGES = [(0, 0), (0, 1), (0, 100), (1, 100), (40, 1000)]

        for led_range in LED_RANGES:
            with self.subTest(led_range=led_range):

                band_led_ranges = []

                leds = ProductionFrequencyBandLeds(led_range, band_led_ranges)

                start, end = led_range

                self.assertEqual(leds.start_led, start)
                self.assertEqual(leds.end_led, end)


class GroupMethodsTestCase(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [{(0, 10)}, {(10, 20)}, {(20, 30)}]

    NUMBER_OF_GROUPS = len(GROUP_LED_RANGES)

    BLACK_RGB = (0, 0, 0)

    GROUP_0 = 0
    GROUP_1 = 1
    GROUP_2 = 2

    def setUp(self):
        self.leds = ProductionFrequencyBandLeds(self.LED_RANGE, self.GROUP_LED_RANGES)


class TestGetGroupRGB(GroupMethodsTestCase):
    def test_after_setting_group_rgb(self):
        RGB = (10, 11, 12)

        GROUP_RGBS = [(self.GROUP_0, RGB)]

        self.leds.set_band_colors(GROUP_RGBS)

        self.assertEqual(self.leds.get_band_color(self.GROUP_0), RGB)
        self.assertEqual(self.leds.get_band_color(self.GROUP_1), self.BLACK_RGB)
        self.assertEqual(self.leds.get_band_color(self.GROUP_2), self.BLACK_RGB)

    def test_no_group_rgbs_set(self):
        for band in range(self.NUMBER_OF_GROUPS):
            with self.subTest(band=band):
                self.assertEqual(self.leds.get_band_color(band), self.BLACK_RGB)

    def test_group_rgb_altered_twice(self):
        RGB_OLD = (10, 11, 12)
        RGB_NEW = (100, 110, 120)

        GROUP_RGBS_OLD = [(self.GROUP_0, RGB_OLD)]
        GROUP_RGBS_NEW = [(self.GROUP_0, RGB_NEW)]

        self.leds.set_band_colors(GROUP_RGBS_OLD)
        self.leds.set_band_colors(GROUP_RGBS_NEW)

        self.assertEqual(self.leds.get_band_color(self.GROUP_0), RGB_NEW)

    def test_no_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = []

        leds = ProductionFrequencyBandLeds(LED_RANGE, GROUP_LED_RANGES)

        GROUPS = [0, 1, 100]

        for band in GROUPS:
            with self.subTest(band=band):

                with self.assertRaises(IndexError):
                    leds.get_band_color(band)

    def test_group_less_than_0(self):
        GROUPS = [-1, -2, -100]

        for band in GROUPS:
            with self.subTest(band=band):

                with self.assertRaises(ValueError):
                    self.leds.get_band_color(band)

    def test_group_exceeds_max_group(self):
        GROUPS = [self.NUMBER_OF_GROUPS, self.NUMBER_OF_GROUPS + 1, self.NUMBER_OF_GROUPS + 100]

        for band in GROUPS:
            with self.subTest(band=band):

                with self.assertRaises(IndexError):
                    self.leds.get_band_color(band)


class TestSetGroupRGB(GroupMethodsTestCase):
    def test_set_one_group(self):
        RGB = (10, 11, 12)

        GROUP_RGBS = [(self.GROUP_0, RGB)]

        self.leds.set_band_colors(GROUP_RGBS)

        self.assertEqual(self.leds.get_band_color(self.GROUP_0), RGB)
        self.assertEqual(self.leds.get_band_color(self.GROUP_1), self.BLACK_RGB)
        self.assertEqual(self.leds.get_band_color(self.GROUP_2), self.BLACK_RGB)

    def test_set_no_group(self):
        GROUP_RGBS = []

        self.leds.set_band_colors(GROUP_RGBS)

        for band in range(self.NUMBER_OF_GROUPS):
            with self.subTest(band=band):
                self.assertEqual(self.leds.get_band_color(band), self.BLACK_RGB)

    def test_set_multiple_groups(self):
        RGB_0 = (1, 2, 3)
        RGB_1 = (4, 5, 6)
        RGB_2 = (7, 8, 9)

        GROUP_RGBS_0 = [(self.GROUP_0, RGB_0)]
        GROUP_RGBS_1 = [(self.GROUP_1, RGB_1)]
        GROUP_RGBS_2 = [(self.GROUP_2, RGB_2)]

        self.leds.set_band_colors(GROUP_RGBS_0)
        self.leds.set_band_colors(GROUP_RGBS_1)
        self.leds.set_band_colors(GROUP_RGBS_2)

        self.assertEqual(self.leds.get_band_color(self.GROUP_0), RGB_0)
        self.assertEqual(self.leds.get_band_color(self.GROUP_1), RGB_1)
        self.assertEqual(self.leds.get_band_color(self.GROUP_2), RGB_2)

    def test_set_same_group_multiple_times_separate_calls(self):
        RGB_OLD = (10, 11, 12)
        RGB_NEW = (100, 110, 120)

        GROUP_RGBS_OLD = [(self.GROUP_0, RGB_OLD)]
        GROUP_RGBS_NEW = [(self.GROUP_0, RGB_NEW)]

        self.leds.set_band_colors(GROUP_RGBS_OLD)
        self.leds.set_band_colors(GROUP_RGBS_NEW)

        self.assertEqual(self.leds.get_band_color(self.GROUP_0), RGB_NEW)

    def test_set_same_group_multiple_times_same_call(self):
        RGB_OLD = (10, 11, 12)
        RGB_NEW = (100, 110, 120)

        GROUP_RGBS = [(self.GROUP_0, RGB_OLD), (self.GROUP_0, RGB_NEW)]

        self.leds.set_band_colors(GROUP_RGBS)

        self.assertEqual(self.leds.get_band_color(self.GROUP_0), RGB_NEW)

    def test_no_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = []

        leds = ProductionFrequencyBandLeds(LED_RANGE, GROUP_LED_RANGES)

        GROUPS = [0, 1, 100]

        for band in GROUPS:
            with self.subTest(band=band):

                with self.assertRaises(IndexError):
                    rgb = (10, 20, 30)
                    band_colors = [(band, rgb)]

                    leds.set_band_colors(band_colors)

    def test_group_less_than_0(self):
        GROUPS = [-1, -2, -100]

        for band in GROUPS:
            with self.subTest(band=band):

                with self.assertRaises(ValueError):
                    rgb = (10, 20, 30)

                    band_colors = [(band, rgb)]

                    self.leds.set_band_colors(band_colors)

    def test_group_exceeds_max_group(self):
        GROUPS = [self.NUMBER_OF_GROUPS, self.NUMBER_OF_GROUPS + 1, self.NUMBER_OF_GROUPS + 100]

        for band in GROUPS:
            with self.subTest(band=band):

                with self.assertRaises(IndexError):
                    rgb = (10, 20, 30)

                    band_colors = [(band, rgb)]

                    self.leds.set_band_colors(band_colors)


class TestGetGroupLedRanges(GroupMethodsTestCase):
    def test_valid(self):
        for band in range(len(self.GROUP_LED_RANGES)):
            with self.subTest(band=band):
                expected_led_ranges = self.GROUP_LED_RANGES[band]
                actual_led_ranges = self.leds.get_band_led_ranges(band)
                self.assertEqual(expected_led_ranges, actual_led_ranges)

    def test_no_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = []

        leds = ProductionFrequencyBandLeds(LED_RANGE, GROUP_LED_RANGES)

        GROUPS = [0, 1, 100]

        for band in GROUPS:
            with self.subTest(band=band):

                with self.assertRaises(IndexError):
                    leds.get_band_led_ranges(band)

    def test_group_less_than_0(self):
        GROUPS = [-1, -2, -100]

        for band in GROUPS:
            with self.subTest(band=band):

                with self.assertRaises(ValueError):
                    self.leds.get_band_led_ranges(band)

    def test_group_exceeds_max_group(self):
        GROUPS = [self.NUMBER_OF_GROUPS, self.NUMBER_OF_GROUPS + 1, self.NUMBER_OF_GROUPS + 100]

        for band in GROUPS:
            with self.subTest(band=band):

                with self.assertRaises(IndexError):
                    self.leds.get_band_led_ranges(band)
