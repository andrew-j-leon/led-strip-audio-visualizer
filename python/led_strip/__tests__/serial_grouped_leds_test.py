import unittest
from typing import Any, List, Tuple

from led_strip.grouped_leds import SerialGroupedLeds
from libraries.serial import Serial


class FakeSerial(Serial):
    def __init__(self, number_of_leds: int):
        self.__number_of_leds = number_of_leds

    @property
    def number_of_bytes_in_buffer(self) -> int:
        return 1

    @property
    def number_of_leds(self) -> int:
        return self.__number_of_leds

    def read(self, number_of_bytes: int) -> Any:
        LENGTH = 2
        BYTE_ORDER = 'big'

        return self.__number_of_leds.to_bytes(LENGTH, BYTE_ORDER)

    def write(self, data: bytes):
        pass

    def close(self):
        pass

    def open(self):
        pass


class TestConstructor(unittest.TestCase):
    NUMBER_OF_LEDS = 100
    BRIGHTNESS = 10

    def test_serial_reports_fewer_leds_than_led_range_implies(self):
        SERIAL_NUMBER_OF_LEDS = 100
        SERIAL = FakeSerial(SERIAL_NUMBER_OF_LEDS)

        NUMBER_OF_LEDS = [SERIAL_NUMBER_OF_LEDS + 1, SERIAL_NUMBER_OF_LEDS + 100]

        for number_of_leds in NUMBER_OF_LEDS:
            with self.subTest(serial_number_of_leds=SERIAL_NUMBER_OF_LEDS, number_of_leds=number_of_leds):

                with self.assertRaises(ValueError):
                    led_range = (0, number_of_leds)
                    group_led_ranges = []
                    brightness = 10

                    SerialGroupedLeds(led_range, group_led_ranges, SERIAL, brightness)

    def test_led_range_outside_of_serial_led_range(self):
        SERIAL_NUMBER_OF_LEDS = 100
        SERIAL = FakeSerial(SERIAL_NUMBER_OF_LEDS)

        LED_RANGES = [(1, SERIAL_NUMBER_OF_LEDS + 1),
                      (10, SERIAL_NUMBER_OF_LEDS + 10)]

        for led_range in LED_RANGES:
            with self.subTest(serial_led_range=(0, SERIAL_NUMBER_OF_LEDS), led_range=led_range):

                with self.assertRaises(ValueError):
                    group_led_ranges = []
                    brightness = 10

                    SerialGroupedLeds(led_range, group_led_ranges, SERIAL, brightness)

    def test_brightness(self):
        SERIAL_NUMBER_OF_LEDS = 100
        SERIAL = FakeSerial(SERIAL_NUMBER_OF_LEDS)

        LED_RANGE = (0, SERIAL_NUMBER_OF_LEDS)

        GROUP_LED_RANGES = []

        VALID_BRIGHTNESSES = [0, 1, 10, 255]

        for valid_brightness in VALID_BRIGHTNESSES:
            with self.subTest(brightness=valid_brightness):

                SerialGroupedLeds(LED_RANGE, GROUP_LED_RANGES, SERIAL, valid_brightness)

        INVALID_BRIGHTNESSES = [-10, -2, -1, 256, 846]

        for invalid_brightness in INVALID_BRIGHTNESSES:
            with self.subTest(brightness=invalid_brightness):

                with self.assertRaises(ValueError):
                    SerialGroupedLeds(LED_RANGE, GROUP_LED_RANGES, SERIAL, invalid_brightness)

    def test_valid_led_ranges(self):
        VALID_LED_RANGES = [(0, 0), (0, 1), (0, self.NUMBER_OF_LEDS), (1, 1), (1, self.NUMBER_OF_LEDS)]

        for valid_led_range in VALID_LED_RANGES:
            with self.subTest(led_range=valid_led_range):

                group_led_ranges = []
                serial = FakeSerial(self.NUMBER_OF_LEDS)

                SerialGroupedLeds(valid_led_range, group_led_ranges, serial, self.BRIGHTNESS)

    def test_led_ranges_where_start_is_greater_than_end(self):
        INVALID_LED_RANGES = [(-1, 0), (0, -1), (-1, -1),
                              (-10, 0), (0, -10),
                              (1, 0), (10, 0),
                              (10, 9), (10, 5)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(ValueError):
                    group_led_ranges = []
                    serial = FakeSerial(self.NUMBER_OF_LEDS)

                    SerialGroupedLeds(invalid_led_range, group_led_ranges, serial, self.BRIGHTNESS)

    def test_led_ranges_where_start_is_not_int(self):
        INVALID_LED_RANGES = [(0.0, 1), (1.0, 10), (100.0, 200)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(TypeError):
                    group_led_ranges = []
                    serial = FakeSerial(self.NUMBER_OF_LEDS)

                    SerialGroupedLeds(invalid_led_range, group_led_ranges, serial, self.BRIGHTNESS)

    def test_led_ranges_where_end_is_float(self):
        INVALID_LED_RANGES = [(0, 0.0), (0, 1.0), (0, 100.0)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(TypeError):
                    group_led_ranges = []
                    serial = FakeSerial(self.NUMBER_OF_LEDS)

                    SerialGroupedLeds(invalid_led_range, group_led_ranges, serial, self.BRIGHTNESS)

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

                number_of_leds = led_range[1]
                serial = FakeSerial(number_of_leds)

                SerialGroupedLeds(led_range, group_led_ranges, serial, self.BRIGHTNESS)

    def check_invalid_group_led_ranges(self, led_range: Tuple[int, int], invalid_group_led_ranges: List[Tuple[int, int]]):
        for group_led_ranges in invalid_group_led_ranges:
            with self.subTest(led_range=led_range, group_led_ranges=group_led_ranges):

                with self.assertRaises(ValueError):
                    number_of_leds = led_range[1]
                    serial = FakeSerial(number_of_leds)

                    SerialGroupedLeds(led_range, group_led_ranges, serial, self.BRIGHTNESS)


class TestSetGroupRGB(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 10), (10, 20), (20, 30)]
    NUMBER_OF_GROUPS = len(GROUP_LED_RANGES)

    BLACK_RGB = (0, 0, 0)

    GROUP_0 = 0
    GROUP_1 = 1
    GROUP_2 = 2

    BRIGHTNESS = 10

    def setUp(self):
        NUMBER_OF_SERIAL_LEDS = self.LED_RANGE[1]

        self.serial = FakeSerial(NUMBER_OF_SERIAL_LEDS)

        self.leds = SerialGroupedLeds(self.LED_RANGE, self.GROUP_LED_RANGES, self.serial, self.BRIGHTNESS)

    def test_set_no_group(self):
        GROUP_RGBS = []

        self.leds.set_group_rgbs(GROUP_RGBS)

        for group in range(self.NUMBER_OF_GROUPS):
            with self.subTest(group=group):
                self.assertEqual(self.leds.get_group_rgb(group), self.BLACK_RGB)

    def test_set_one_group(self):
        RGB = (10, 11, 12)

        GROUP_RGBS = [(self.GROUP_0, RGB)]

        self.leds.set_group_rgbs(GROUP_RGBS)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_1), self.BLACK_RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_2), self.BLACK_RGB)

    def test_set_multiple_groups(self):
        RGB_0 = (1, 2, 3)
        RGB_1 = (4, 5, 6)
        RGB_2 = (7, 8, 9)

        GROUP_RGBS_0 = [(self.GROUP_0, RGB_0)]
        GROUP_RGBS_1 = [(self.GROUP_1, RGB_1)]
        GROUP_RGBS_2 = [(self.GROUP_2, RGB_2)]

        self.leds.set_group_rgbs(GROUP_RGBS_0)
        self.leds.set_group_rgbs(GROUP_RGBS_1)
        self.leds.set_group_rgbs(GROUP_RGBS_2)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB_0)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_1), RGB_1)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_2), RGB_2)

    def test_set_same_group_multiple_times_with_separate_calls(self):
        RGB_OLD = (10, 11, 12)
        RGB_NEW = (100, 110, 120)

        GROUP_RGBS_OLD = [(self.GROUP_0, RGB_OLD)]
        GROUP_RGBS_NEW = [(self.GROUP_0, RGB_NEW)]

        self.leds.set_group_rgbs(GROUP_RGBS_OLD)
        self.leds.set_group_rgbs(GROUP_RGBS_NEW)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB_NEW)

    def test_set_same_group_multiple_times_with_one_call(self):
        RGB_OLD = (10, 11, 12)
        RGB_NEW = (100, 110, 120)

        GROUP_RGBS = [(self.GROUP_0, RGB_OLD), (self.GROUP_0, RGB_NEW)]

        self.leds.set_group_rgbs(GROUP_RGBS)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB_NEW)

    def test_no_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = []

        leds = SerialGroupedLeds(LED_RANGE, GROUP_LED_RANGES, self.serial, self.BRIGHTNESS)

        GROUPS = [0, 1, 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):
                    rgb = (10, 20, 30)
                    group_rgbs = [(group, rgb)]

                    leds.set_group_rgbs(group_rgbs)

    def test_group_less_than_0(self):
        GROUPS = [-1, -2, -100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(OverflowError):
                    rgb = (10, 20, 30)

                    group_rgbs = [(group, rgb)]

                    self.leds.set_group_rgbs(group_rgbs)

    def test_group_exceeds_max_group(self):
        GROUPS = [self.NUMBER_OF_GROUPS, self.NUMBER_OF_GROUPS + 1, self.NUMBER_OF_GROUPS + 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):
                    rgb = (10, 20, 30)

                    group_rgbs = [(group, rgb)]

                    self.leds.set_group_rgbs(group_rgbs)
