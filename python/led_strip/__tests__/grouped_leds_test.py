import unittest
from typing import List, Tuple

from led_strip.grouped_leds import GroupedLeds


class TestConstructor(unittest.TestCase):
    def test_number_of_leds(self):
        VALID_NUMBER_OF_LEDS = [0, 1, 100,
                                1.5, 100.5]

        for number_of_leds in VALID_NUMBER_OF_LEDS:

            led_range = (0, number_of_leds)

            with self.subTest(led_range=led_range):
                group_led_ranges = []

                GroupedLeds(led_range, group_led_ranges)

        INVALID_NUMBER_OF_LEDS = [-1, -100]

        for number_of_leds in INVALID_NUMBER_OF_LEDS:

            led_range = (0, number_of_leds)

            with self.subTest(led_range=led_range):

                with self.assertRaises(ValueError):
                    group_led_ranges = []

                    GroupedLeds(led_range, group_led_ranges)

    def test_led_ranges(self):
        VALID_LED_RANGES = [(0, 0), (0, 1), (0, 150), (1, 1), (1, 150)]

        for valid_led_range in VALID_LED_RANGES:
            with self.subTest(led_range=valid_led_range):

                group_led_ranges = []

                GroupedLeds(valid_led_range, group_led_ranges)

        INVALID_LED_RANGES = [(-1, 0), (0, -1), (-1, -1),
                              (-10, 0), (0, -10),
                              (1, 0), (10, 0),
                              (10, 9), (10, 5)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(ValueError):
                    group_led_ranges = []

                    GroupedLeds(invalid_led_range, group_led_ranges)

    def test_group_led_ranges_with_led_range_starting_at_0(self):
        LED_RANGE_STARTING_AT_0 = (0, 150)

        VALID_GROUP_LED_RANGES = [[(0, 0)], [(0, 1)], [(0, 150)], [(1, 1)], [(1, 150)],
                                  [(150, 150), (151, 151), (300, 300)]]

        INVALID_GROUP_LED_RANGES = [[(-1, 0)], [(0, -1)], [(-1, -1)],
                                    [(-10, 0)], [(0, -10)],
                                    [(1, 0)], [(10, 0)],
                                    [(10, 9)], [(10, 5)]]

        self.check_valid_group_led_ranges(LED_RANGE_STARTING_AT_0, VALID_GROUP_LED_RANGES)
        self.check_invalid_group_led_ranges(LED_RANGE_STARTING_AT_0, INVALID_GROUP_LED_RANGES)

    def test_group_led_ranges_with_led_range_starting_at_10(self):

        LED_RANGE_STARTING_AT_10 = (10, 150)

        VALID_GROUP_LED_RANGES = [
            [(10, 10)], [(10, 11)], [(10, 150)],
            [(149, 150)], [(150, 150)],
            [(10, 90), (90, 150)]
        ]

        INVALID_GROUP_LED_RANGES = [
            [(0, 1)], [(0, 10)], [(0, 150)], [(0, 151)], [(0, 300)],
            [(9, 10)], [(9, 11)], [(9, 150)], [(9, 300)],
            [(10, 151)], [(10, 300)],
            [(50, 151)], [(50, 300)],
            [(150, 151)], [(150, 300)],
            [(151, 152)], [(152, 300)]
        ]

        self.check_valid_group_led_ranges(LED_RANGE_STARTING_AT_10, VALID_GROUP_LED_RANGES)
        self.check_invalid_group_led_ranges(LED_RANGE_STARTING_AT_10, INVALID_GROUP_LED_RANGES)

    def check_valid_group_led_ranges(self, led_range: Tuple[int, int], valid_group_led_ranges: List[Tuple[int, int]]):
        for group_led_ranges in valid_group_led_ranges:
            with self.subTest(led_range=led_range, group_led_ranges=group_led_ranges):

                GroupedLeds(led_range, group_led_ranges)

    def check_invalid_group_led_ranges(self, led_range: Tuple[int, int], invalid_group_led_ranges: List[Tuple[int, int]]):
        for group_led_ranges in invalid_group_led_ranges:
            with self.subTest(led_range=led_range, group_led_ranges=group_led_ranges):

                with self.assertRaises(ValueError):
                    GroupedLeds(led_range, group_led_ranges)


class TestNumberOfGroups(unittest.TestCase):
    def test_number_of_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = [[],
                            [(0, 10)],
                            [(0, 10), (10, 20)],

                            [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
                            (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]]

        for group_led_ranges in GROUP_LED_RANGES:
            with self.subTest(number_of_groups=len(group_led_ranges)):

                led_strip = GroupedLeds(LED_RANGE, group_led_ranges)

                self.assertEqual(led_strip.number_of_groups, len(group_led_ranges))


class TestNumberOfLeds(unittest.TestCase):
    def test_number_of_leds(self):
        NUMBER_OF_LEDS = [0, 1, 15, 300]

        for number_of_leds in NUMBER_OF_LEDS:
            with self.subTest(number_of_leds=number_of_leds):

                led_range = (0, number_of_leds)
                group_led_ranges = []

                led_strip = GroupedLeds(led_range, group_led_ranges)

                self.assertEqual(number_of_leds, led_strip.number_of_leds)


class TestStartLedAndEndLed(unittest.TestCase):
    def test_start_led_and_end_led(self):
        LED_RANGES = [(0, 0), (0, 1), (0, 100), (1, 100), (40, 1000)]

        for led_range in LED_RANGES:
            with self.subTest(led_range=led_range):

                group_led_ranges = []

                leds = GroupedLeds(led_range, group_led_ranges)

                start, end = led_range

                self.assertEqual(leds.start_led, start)
                self.assertEqual(leds.end_led, end)


class GroupMethodsTestCase(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 10), (10, 20), (20, 30)]

    GROUP_0 = 0
    GROUP_1 = 1
    GROUP_2 = 2

    def setUp(self):
        self.leds = GroupedLeds(self.LED_RANGE, self.GROUP_LED_RANGES)


class TestGetGroupRGB(GroupMethodsTestCase):
    def test_after_setting_group_rgb(self):
        RGB = (10, 11, 12)
        BLACK_RGB = (0, 0, 0)

        self.leds.set_group_rgb(self.GROUP_0, RGB)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_1), BLACK_RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_2), BLACK_RGB)

    def test_no_group_rgbs_set(self):
        BLACK_RGB = (0, 0, 0)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), BLACK_RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_1), BLACK_RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_2), BLACK_RGB)

    def test_group_rgb_altered_twice(self):
        RGB_OLD = (10, 11, 12)
        RGB_NEW = (100, 110, 120)

        self.leds.set_group_rgb(self.GROUP_0, RGB_OLD)
        self.leds.set_group_rgb(self.GROUP_0, RGB_NEW)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB_NEW)

    def test_no_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = []

        leds = GroupedLeds(LED_RANGE, GROUP_LED_RANGES)

        GROUPS = [0, 1, 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):
                    leds.get_group_rgb(group)

    def test_group_less_than_0(self):
        GROUPS = [-1, -2, -100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(ValueError) as error:
                    self.leds.get_group_rgb(group)

                actual_error_message = str(error.exception)
                expected_error_message = f'group must be >= 0, but was {group}.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_index_error(self):
        GROUPS = [3, 4, 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):
                    self.leds.get_group_rgb(group)


class TestSetGroupRGB(GroupMethodsTestCase):
    def test_set_one_group(self):
        RGB = (10, 11, 12)
        BLACK_RGB = (0, 0, 0)

        self.leds.set_group_rgb(self.GROUP_0, RGB)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_1), BLACK_RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_2), BLACK_RGB)

    def test_set_multiple_groups(self):
        RGB_0 = (1, 2, 3)
        RGB_1 = (4, 5, 6)
        RGB_2 = (7, 8, 9)

        self.leds.set_group_rgb(self.GROUP_0, RGB_0)
        self.leds.set_group_rgb(self.GROUP_1, RGB_1)
        self.leds.set_group_rgb(self.GROUP_2, RGB_2)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB_0)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_1), RGB_1)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_2), RGB_2)

    def test_set_same_group_multiple_times(self):
        RGB_OLD = (10, 11, 12)
        RGB_NEW = (100, 110, 120)

        self.leds.set_group_rgb(self.GROUP_0, RGB_OLD)
        self.leds.set_group_rgb(self.GROUP_0, RGB_NEW)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB_NEW)

    def test_no_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = []

        leds = GroupedLeds(LED_RANGE, GROUP_LED_RANGES)

        GROUPS = [0, 1, 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):
                    rgb = (10, 20, 30)
                    leds.set_group_rgb(group, rgb)

    def test_group_less_than_0(self):
        GROUPS = [-1, -2, -100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(ValueError) as error:
                    rgb = (10, 20, 30)
                    self.leds.set_group_rgb(group, rgb)

                actual_error_message = str(error.exception)
                expected_error_message = f'group must be >= 0, but was {group}.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_index_error(self):
        GROUPS = [3, 4, 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):
                    rgb = (10, 20, 30)
                    self.leds.set_group_rgb(group, rgb)


class TestGetGroupLedRange(GroupMethodsTestCase):
    def test_valid(self):
        for group in range(len(self.GROUP_LED_RANGES)):

            group_led_range = self.GROUP_LED_RANGES[group]

            with self.subTest(group=group, group_led_range=group_led_range):
                led_range = self.leds.get_group_led_range(group)

                start_led, end_led = group_led_range

                self.assertEqual(led_range.start, start_led)
                self.assertEqual(led_range.end, end_led)

    def test_no_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = []

        leds = GroupedLeds(LED_RANGE, GROUP_LED_RANGES)

        GROUPS = [0, 1, 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):

                    leds.get_group_led_range(group)

    def test_group_less_than_0(self):
        GROUPS = [-1, -2, -100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(ValueError) as error:

                    self.leds.get_group_led_range(group)

                actual_error_message = str(error.exception)
                expected_error_message = f'group must be >= 0, but was {group}.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_index_error(self):
        GROUPS = [3, 4, 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):
                    self.leds.get_group_led_range(group)
