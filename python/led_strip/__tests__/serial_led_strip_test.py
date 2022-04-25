import unittest
from typing import Any

from led_strip.led_strip import GroupedLeds
from led_strip.serial_led_strip import SerialLedStrip
from libraries.serial import Serial


class FakeSerial(Serial):
    def __init__(self, number_of_leds: int):
        self.__number_of_leds = int(number_of_leds)

    @property
    def number_of_bytes_in_buffer(self) -> int:
        return 1

    def read(self, number_of_bytes: int) -> Any:
        LENGTH = 2
        BYTE_ORDER = 'big'

        return self.__number_of_leds.to_bytes(LENGTH, BYTE_ORDER)

    def write(self, data: bytes):
        pass

    def close(self):
        pass


class TestConstructor(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 50), (50, 100)]

    LEDS = GroupedLeds(LED_RANGE, GROUP_LED_RANGES)
    SERIAL = FakeSerial(LEDS.number_of_leds)

    def test_valid(self):
        BRIGHTNESS = 10

        SerialLedStrip(self.LEDS, self.SERIAL, BRIGHTNESS)

    def test_serial_reports_fewer_leds_than_led_range_implies(self):
        SERIAL_NUMBER_OF_LEDS = [self.LEDS.number_of_leds - 1,
                                 self.LEDS.number_of_leds // 2,
                                 0]

        for serial_number_of_leds in SERIAL_NUMBER_OF_LEDS:
            with self.subTest(serial_number_of_leds=serial_number_of_leds):

                with self.assertRaises(ValueError) as error:
                    brightness = 10

                    serial = FakeSerial(serial_number_of_leds)

                    SerialLedStrip(self.LEDS, serial, brightness)

                actual_error_message = str(error.exception)
                expected_error_message = f'The serial connection stated that there are {serial_number_of_leds} leds, but this LedStrip object is set for {self.LEDS.number_of_leds} leds.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_strip_led_range_outside_of_serial_led_range(self):
        STRIP_LED_RANGES = [(self.LEDS.start_led + 1, self.LEDS.end_led + 1),
                            (self.LEDS.start_led + 100, self.LEDS.end_led + 100), ]

        for strip_led_range in STRIP_LED_RANGES:
            with self.subTest(serial_led_range=(self.LEDS.start_led, self.LEDS.end_led), strip_led_range=strip_led_range):

                with self.assertRaises(ValueError) as error:
                    brightness = 10

                    group_led_ranges = []
                    leds = GroupedLeds(strip_led_range, group_led_ranges)

                    SerialLedStrip(leds, self.SERIAL, brightness)

                actual_error_message = str(error.exception)
                expected_error_message = f"The serial connection stated that its led indicies range from 0 (inclusive) to {self.LEDS.number_of_leds} (exclusive), but this LedStrip ranges from {leds.start_led} (inclusive) to {leds.end_led} (exclusive)."

                self.assertEqual(actual_error_message, expected_error_message)

    def test_brightness(self):
        VALID_BRIGHTNESSES = [0, 1, 10, 255]

        for valid_brightness in VALID_BRIGHTNESSES:
            with self.subTest(brightness=valid_brightness):

                SerialLedStrip(self.LEDS, self.SERIAL, valid_brightness)

        INVALID_BRIGHTNESSES = [-10, -2, -1, 256, 846]

        for invalid_brightness in INVALID_BRIGHTNESSES:
            with self.subTest(brightness=invalid_brightness):

                with self.assertRaises(ValueError) as error:
                    SerialLedStrip(self.LEDS, self.SERIAL, invalid_brightness)

                actual_error_message = str(error.exception)

                expected_error_message = f'brightness must be within the range [0,255], but was {invalid_brightness}.'

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
            with self.subTest(number_of_groups=len(group_led_ranges)):

                leds = GroupedLeds(LED_RANGE, group_led_ranges)
                serial = FakeSerial(leds.number_of_leds)
                brightness = 10

                led_strip = SerialLedStrip(leds, serial, brightness)

                self.assertEqual(led_strip.number_of_groups, len(group_led_ranges))


class TestEnqueueColor(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 10), (10, 20)]

    GROUP_0 = 0
    GROUP_1 = 1

    def setUp(self):
        leds = GroupedLeds(self.LED_RANGE, self.GROUP_LED_RANGES)

        serial = FakeSerial(leds.number_of_leds)
        BRIGHTNESS = 10

        self.led_strip = SerialLedStrip(leds, serial, BRIGHTNESS)

    def test_enqueue_one_group_color(self):
        RGB = (10, 20, 30)

        self.led_strip.enqueue_rgb(self.GROUP_0, RGB)

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, RGB))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB))

        self.led_strip.show_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, RGB))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB))

    def test_enqueue_multiple_group_colors(self):
        RGB_0 = (10, 20, 30)
        RGB_1 = (100, 150, 200)

        self.led_strip.enqueue_rgb(self.GROUP_0, RGB_0)
        self.led_strip.enqueue_rgb(self.GROUP_1, RGB_1)

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, RGB_0))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, RGB_1))

        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB_0))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB_1))

        self.led_strip.show_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, RGB_0))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, RGB_1))

        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB_0))
        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_1, RGB_1))

    def test_overwrite_group_color(self):
        RGB_0 = (10, 20, 30)
        RGB_1 = (40, 50, 60)

        GROUP = self.GROUP_0

        self.led_strip.enqueue_rgb(GROUP, RGB_0)
        self.led_strip.enqueue_rgb(GROUP, RGB_1)

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertFalse(self.led_strip.group_is_rgb(GROUP, RGB_0))
        self.assertFalse(self.led_strip.group_is_rgb(GROUP, RGB_1))

        self.led_strip.show_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertFalse(self.led_strip.group_is_rgb(GROUP, RGB_0))
        self.assertTrue(self.led_strip.group_is_rgb(GROUP, RGB_1))

    def test_no_groups(self):
        GROUPS = [0, 1, 100]

        for group in GROUPS:
            with self.subTest(group=group):
                led_range = (0, 100)
                group_led_ranges = []

                leds = GroupedLeds(led_range, group_led_ranges)
                serial = FakeSerial(leds.number_of_leds)

                brightness = 10

                led_strip = SerialLedStrip(leds, serial, brightness)

                with self.assertRaises(IndexError) as error:
                    rbg = (1, 2, 3)

                    led_strip.enqueue_rgb(group, rbg)

                actual_error_message = str(error.exception)
                expected_error_message = f'Cannot enqueue RGB when GraphicLedStrip has 0 groups.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_group_does_not_exist(self):
        INVALID_GROUPS = [-6, -1, 1, 10]

        for invalid_group in INVALID_GROUPS:
            with self.subTest(group=invalid_group):
                led_range = (0, 100)
                group_led_ranges = [(0, 100)]

                leds = GroupedLeds(led_range, group_led_ranges)
                serial = FakeSerial(leds.number_of_leds)

                brightness = 10

                led_strip = SerialLedStrip(leds, serial, brightness)

                with self.assertRaises(IndexError) as error:
                    rbg = (1, 2, 3)

                    led_strip.enqueue_rgb(invalid_group, rbg)

                actual_error_message = str(error.exception)
                expected_error_message = f'Tried to enqueue an RGB color into group {invalid_group}, but group indices range from 0 (inclusive) to {len(group_led_ranges) - 1} (inclusive).'

                self.assertEqual(actual_error_message, expected_error_message)


class TestClearQueuedColors(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 50), (50, 100)]

    GROUP_0 = 0
    GROUP_1 = 1

    def setUp(self):
        leds = GroupedLeds(self.LED_RANGE, self.GROUP_LED_RANGES)

        serial = FakeSerial(leds.number_of_leds)
        BRIGHTNESS = 10

        self.led_strip = SerialLedStrip(leds, serial, BRIGHTNESS)

    def test_clear_empty_queue(self):
        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

        self.led_strip.clear_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

    def test_clear_one_element_queue(self):
        self.led_strip.enqueue_rgb(self.GROUP_0, (1, 1, 1))

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

        self.led_strip.clear_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

    def test_clear_multi_element_queue(self):
        self.led_strip.enqueue_rgb(self.GROUP_0, (1, 1, 1))
        self.led_strip.enqueue_rgb(self.GROUP_1, (1, 1, 1))
        self.led_strip.enqueue_rgb(self.GROUP_0, (1, 1, 1))

        self.assertEqual(self.led_strip.number_of_queued_colors, 3)

        self.led_strip.clear_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)
