import unittest

from led_strip.serial_led_strip import SerialLedStrip
from libraries.serial import FakeSerial


class TestConstructor(unittest.TestCase):

    def test_led_ranges(self):
        VALID_LED_RANGES = [(0, 0), (3, 3), (0, 150), (1, 150)]
        GROUP_INDEX_TO_LED_RANGE = []

        NUMBER_OF_LEDS = 150
        SERIAL = FakeSerial(NUMBER_OF_LEDS)
        BRIGHTNESS = 10

        for VALID_LED_RANGE in VALID_LED_RANGES:
            with self.subTest(f'led_range={VALID_LED_RANGE}'):

                SerialLedStrip(VALID_LED_RANGE, GROUP_INDEX_TO_LED_RANGE, SERIAL, BRIGHTNESS)

        INVALID_LED_RANGES = [(-1, 0), (-2, -1), (-10, -1), (-1, -1),
                              (1, 0), (2, 0), (10, 0)]

        for INVALID_LED_RANGE in INVALID_LED_RANGES:

            with self.subTest(f'led_range={INVALID_LED_RANGE}'):

                with self.assertRaises(ValueError):
                    SerialLedStrip(INVALID_LED_RANGE, GROUP_INDEX_TO_LED_RANGE, SERIAL, BRIGHTNESS)

    def test_group_index_to_led_range(self):
        LED_RANGE = (10, 150)

        VALID_GROUP_LED_RANGES = [
            [(0, 0)], [(200, 200)],
            [(9, 9)],
            [(10, 10)],
            [(150, 150)],
            [(151, 151)],
            [(10, 11)],
            [(10, 20), (20, 30)],
            [(10, 20), (10, 30)],
            [(10, 50), (50, 100), (100, 150)],
            [(149, 150)], [(10, 11)]
        ]

        NUMBER_OF_LEDS = 150
        SERIAL = FakeSerial(NUMBER_OF_LEDS)
        BRIGHTNESS = 10

        for VALID_GROUP_LED_RANGE in VALID_GROUP_LED_RANGES:

            with self.subTest(f'group_led_ranges={VALID_GROUP_LED_RANGE}'):

                SerialLedStrip(LED_RANGE, VALID_GROUP_LED_RANGE, SERIAL, BRIGHTNESS)

        INVALID_GROUP_LED_RANGES = [
            [(9, 10)], [(0, 10)],
            [(150, 151)], [(149, 151)], [(150, 151)],
            [(10, 151)],
            [(-1, 0)], [(-2, -1)]
        ]

        for INVALID_GROUP_LED_RANGE in INVALID_GROUP_LED_RANGES:

            with self.subTest(f'group_led_ranges={INVALID_GROUP_LED_RANGE}'):

                with self.assertRaises(ValueError):
                    SerialLedStrip(LED_RANGE, INVALID_GROUP_LED_RANGE, SERIAL, BRIGHTNESS)

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
                expected_error_message = f'The serial connection stated that its led indicies range from 0 (inclusive) to {NUMBER_OF_LEDS} (exclusive), but this LedStrip has an (exclusive) end index of {LED_RANGE[1]}.'

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
