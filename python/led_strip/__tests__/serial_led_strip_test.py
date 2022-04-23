import unittest

from led_strip.serial_led_strip import SerialLedStrip
from libraries.serial import FakeSerial


class TestConstructor(unittest.TestCase):
    def test_number_of_leds(self):
        VALID_NUMBER_OF_LEDS = [0, 1, 100,
                                1.5, 100.5]

        for number_of_leds in VALID_NUMBER_OF_LEDS:
            led_range = (0, number_of_leds)

            with self.subTest(led_range=led_range):
                group_led_ranges = []
                brightness = 10

                SerialLedStrip(led_range, group_led_ranges, FakeSerial(number_of_leds), brightness)

        INVALID_NUMBER_OF_LEDS = [-1, -100]

        for number_of_leds in INVALID_NUMBER_OF_LEDS:
            led_range = (0, number_of_leds)

            with self.subTest(led_range=led_range):

                with self.assertRaises(ValueError):
                    group_led_ranges = []
                    brightness = 10

                    SerialLedStrip(led_range, group_led_ranges, FakeSerial(number_of_leds), brightness)

    def test_led_ranges(self):
        VALID_LED_RANGES = [(0, 0), (0, 1), (0, 150), (1, 1), (1, 150)]

        for valid_led_range in VALID_LED_RANGES:
            with self.subTest(led_range=valid_led_range):
                group_led_ranges = []
                brightness = 10

                number_of_leds = valid_led_range[1]
                serial = FakeSerial(number_of_leds)

                SerialLedStrip(valid_led_range, group_led_ranges, serial, brightness)

        INVALID_LED_RANGES = [(-1, 0), (0, -1), (-1, -1),
                              (-10, 0), (0, -10),
                              (1, 0), (10, 0),
                              (10, 9), (10, 5)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(ValueError):
                    group_led_ranges = []
                    brightness = 10

                    number_of_leds = valid_led_range[1]
                    serial = FakeSerial(number_of_leds)

                    SerialLedStrip(invalid_led_range, group_led_ranges, serial, brightness)

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

    def check_valid_group_led_ranges(self, led_range, valid_group_led_ranges):
        for group_led_ranges in valid_group_led_ranges:
            with self.subTest(led_range=led_range, group_led_ranges=group_led_ranges):
                brightness = 10

                number_of_leds = led_range[1]
                serial = FakeSerial(number_of_leds)

                SerialLedStrip(led_range, group_led_ranges, serial, brightness)

    def check_invalid_group_led_ranges(self, led_range, invalid_group_led_ranges):
        for group_led_ranges in invalid_group_led_ranges:
            with self.subTest(led_range=led_range, group_led_ranges=group_led_ranges):

                with self.assertRaises(ValueError):
                    brightness = 10

                    number_of_leds = led_range[1]
                    serial = FakeSerial(number_of_leds)

                    SerialLedStrip(led_range, group_led_ranges, serial, brightness)

    def test_valid_serial(self):
        LED_RANGE = (0, 150)
        GROUP_LED_RANGES = [(0, 50), (50, 100), (100, 150)]

        NUMBER_OF_LEDS = 150
        SERIAL = FakeSerial(NUMBER_OF_LEDS)

        BRIGHTNESS = 10

        SerialLedStrip(LED_RANGE, GROUP_LED_RANGES, SERIAL, BRIGHTNESS)

    def test_serial_reports_fewer_leds_than_led_range_implies(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = [(0, 50), (50, 100)]
        BRIGHTNESS = 10

        NUMBER_OF_LEDS = [99, 50, 0]

        for NUMBER_OF_LEDS in NUMBER_OF_LEDS:

            with self.subTest(f'serial_number_of_leds={NUMBER_OF_LEDS}'):
                with self.assertRaises(ValueError) as error:

                    SERIAL = FakeSerial(NUMBER_OF_LEDS)

                    SerialLedStrip(LED_RANGE, GROUP_LED_RANGES, SERIAL, BRIGHTNESS)

                actual_error_message = str(error.exception)

                LED_STRIP_NUMBER_OF_LEDS = LED_RANGE[1] - LED_RANGE[0]
                expected_error_message = f'The serial connection stated that there are {NUMBER_OF_LEDS} leds, but this LedStrip object is set for {LED_STRIP_NUMBER_OF_LEDS} leds.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_led_range_extends_beyond_serial_range(self):
        LED_RANGE = (10, 110)
        GROUP_LED_RANGES = [(10, 60), (60, 110)]
        BRIGHTNESS = 10

        NUMBER_OF_LEDS = [100, 101, 109]

        for NUMBER_OF_LEDS in NUMBER_OF_LEDS:

            with self.subTest(f'serial_led_range={(0, NUMBER_OF_LEDS)}; led strip led_range={LED_RANGE}'):
                with self.assertRaises(ValueError) as error:

                    SERIAL = FakeSerial(NUMBER_OF_LEDS)

                    SerialLedStrip(LED_RANGE, GROUP_LED_RANGES, SERIAL, BRIGHTNESS)

                actual_error_message = str(error.exception)
                expected_error_message = f"The serial connection stated that its led indicies range from 0 (inclusive) to {NUMBER_OF_LEDS} (exclusive), but this LedStrip ranges from {LED_RANGE[0]} (inclusive) to {LED_RANGE[1]} (exclusive)."

                self.assertEqual(actual_error_message, expected_error_message)

    def test_brightness(self):
        VALID_BRIGHTNESSES = [0, 1, 10, 255]

        LED_RANGE = (0, 100)

        GROUP_LED_RANGES = [(0, 50), (50, 100)]

        NUMBER_OF_LEDS = 100
        SERIAL = FakeSerial(NUMBER_OF_LEDS)

        for VALID_BRIGHTNESS in VALID_BRIGHTNESSES:

            with self.subTest(f'brightness={VALID_BRIGHTNESS}'):

                SerialLedStrip(LED_RANGE, GROUP_LED_RANGES, SERIAL, VALID_BRIGHTNESS)

        INVALID_BRIGHTNESSES = [-10, -2, -1, 256, 846]

        for INVALID_BRIGHTNESS in INVALID_BRIGHTNESSES:

            with self.subTest(f'brightness={INVALID_BRIGHTNESS}'):

                with self.assertRaises(ValueError) as error:
                    SerialLedStrip(LED_RANGE, GROUP_LED_RANGES, SERIAL, INVALID_BRIGHTNESS)

                actual_error_message = str(error.exception)

                expected_error_message = f'brightness must be within the range [0,255], but was {INVALID_BRIGHTNESS}.'

                self.assertEqual(actual_error_message, expected_error_message)


class TestNumberOfGroups(unittest.TestCase):

    def test_number_of_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = [[],
                            [(0, 10)],
                            [(0, 10), (10, 20)],

                            [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
                             (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]]

        for group_led_ranges in GROUP_LED_RANGES:

            with self.subTest(f'number_of_groups={len(group_led_ranges)}'):
                number_of_leds = LED_RANGE[1]
                serial = FakeSerial(number_of_leds)

                brightness = 10

                led_strip = SerialLedStrip(LED_RANGE, group_led_ranges, serial, brightness)

                self.assertEqual(led_strip.number_of_groups, len(group_led_ranges))


class TestNumberOfLeds(unittest.TestCase):
    def test_number_of_leds(self):
        NUMBER_OF_LEDS = [0, 1, 15, 300]

        for number_of_leds in NUMBER_OF_LEDS:
            with self.subTest(f'number_of_leds={number_of_leds}'):

                led_range = (0, number_of_leds)
                group_led_ranges = []
                serial = FakeSerial(number_of_leds)
                brightness = 10

                led_strip = SerialLedStrip(led_range, group_led_ranges, serial, brightness)

                self.assertEqual(number_of_leds, led_strip.number_of_leds)


class TestEnqueueColor(unittest.TestCase):

    def setUp(self) -> None:
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = [(0, 10), (10, 20)]

        number_of_leds = LED_RANGE[1]
        serial = FakeSerial(number_of_leds)

        brightness = 10

        self.led_strip = SerialLedStrip(LED_RANGE, GROUP_LED_RANGES, serial, brightness)

        self.group_0 = 0
        self.group_1 = 1

    def test_enqueue_one_group_color(self):
        RGB = (10, 20, 30)

        self.led_strip.enqueue_rgb(self.group_0, RGB)

        self.assertFalse(self.led_strip.group_is_color(self.group_0, RGB))
        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB))

        self.led_strip.show_enqueued_colors()

        self.assertTrue(self.led_strip.group_is_color(self.group_0, RGB))
        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB))

    def test_enqueue_two_group_colors(self):
        RGB_0 = (10, 20, 30)
        RGB_1 = (100, 150, 200)

        self.led_strip.enqueue_rgb(self.group_0, RGB_0)
        self.led_strip.enqueue_rgb(self.group_1, RGB_1)

        self.assertFalse(self.led_strip.group_is_color(self.group_0, RGB_0))
        self.assertFalse(self.led_strip.group_is_color(self.group_0, RGB_1))

        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB_0))
        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB_1))

        self.led_strip.show_enqueued_colors()

        self.assertTrue(self.led_strip.group_is_color(self.group_0, RGB_0))
        self.assertFalse(self.led_strip.group_is_color(self.group_0, RGB_1))

        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB_0))
        self.assertTrue(self.led_strip.group_is_color(self.group_1, RGB_1))

    def test_overwrite_group_color(self):
        RGB_0 = (10, 20, 30)
        RGB_1 = (40, 50, 60)

        GROUP = self.group_0

        self.led_strip.enqueue_rgb(GROUP, RGB_0)
        self.led_strip.enqueue_rgb(GROUP, RGB_1)

        self.assertFalse(self.led_strip.group_is_color(GROUP, RGB_0))
        self.assertFalse(self.led_strip.group_is_color(GROUP, RGB_1))

        self.led_strip.show_enqueued_colors()

        self.assertFalse(self.led_strip.group_is_color(GROUP, RGB_0))
        self.assertTrue(self.led_strip.group_is_color(GROUP, RGB_1))

    def test_no_groups(self):
        GROUPS = [0, 1, 100]

        for group in GROUPS:
            with self.subTest(f'group={group}'):
                LED_RANGE = (0, 100)
                GROUP_LED_RANGES = []

                number_of_leds = LED_RANGE[1]
                serial = FakeSerial(number_of_leds)

                brightness = 10

                led_strip = SerialLedStrip(LED_RANGE, GROUP_LED_RANGES, serial, brightness)

                with self.assertRaises(IndexError) as error:
                    rbg = (1, 2, 3)

                    led_strip.enqueue_rgb(group, rbg)

                actual_error_message = str(error.exception)
                expected_error_message = f'Cannot enqueue RGB when GraphicLedStrip has 0 groups.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_group_does_not_exist(self):
        INVALID_GROUPS = [-6, -1, 1, 10]

        for invalid_group in INVALID_GROUPS:
            with self.subTest(f'group={invalid_group}'):
                led_range = (0, 100)
                group_led_ranges = [(0, 50)]

                number_of_leds = led_range[1]
                serial = FakeSerial(number_of_leds)

                brightness = 10

                led_strip = SerialLedStrip(led_range, group_led_ranges, serial, brightness)

                with self.assertRaises(IndexError) as error:
                    rgb = (1, 2, 3)

                    led_strip.enqueue_rgb(invalid_group, rgb)

                actual_error_message = str(error.exception)
                expected_error_message = f'Tried to enqueue an RGB color into group {invalid_group}, but group indices range from 0 (inclusive) to {len(group_led_ranges) - 1} (inclusive).'

                self.assertEqual(actual_error_message, expected_error_message)
