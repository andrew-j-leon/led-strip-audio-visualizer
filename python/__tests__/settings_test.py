from typing import List, Tuple
import unittest

from util import Settings


class SettingsTestCase(unittest.TestCase):
    START_LED = 0
    END_LED = 300
    MILLISECONDS_PER_AUDIO_CHUNK = 60
    SERIAL_PORT = 'COM4'
    SERIAL_BAUDRATE = 9600
    BRIGHTNESS = 50
    MINIMUM_FREQUENCY = 0
    MAXIMUM_FREQUENCY = 2000
    SHOULD_REVERSE_LEDS = True
    NUMBER_OF_GROUPS = 50
    AMPLITUDE_RGBS = [(0, 20, 30),
                      (40, 50, 60),
                      (100, 200, 255)]

    def setUp(self):
        self.settings = Settings(self.START_LED, self.END_LED, self.MILLISECONDS_PER_AUDIO_CHUNK,
                                 self.SERIAL_PORT, self.SERIAL_BAUDRATE, self.BRIGHTNESS, self.MINIMUM_FREQUENCY,
                                 self.MAXIMUM_FREQUENCY, self.SHOULD_REVERSE_LEDS, self.NUMBER_OF_GROUPS, self.AMPLITUDE_RGBS)


class TestConstructor(unittest.TestCase):
    def test_default_constructor(self):
        Settings()


class TestRepr(SettingsTestCase):
    def test_repr(self):
        actual = repr(self.settings)

        expected = (f'Settings(start_led = {self.settings.start_led}, end_led = {self.settings.end_led}, '
                    f'milliseconds_per_audio_chunk = {self.settings.milliseconds_per_audio_chunk}, '
                    f'serial_port = {self.settings.serial_port}, serial_baudrate = {self.settings.serial_baudrate}, '
                    f'brightness = {self.settings.brightness}, minimum_frequency = {self.settings.minimum_frequency}, '
                    f'maximum_frequency = {self.settings.maximum_frequency}, should_reverse_leds = {self.settings.should_reverse_leds}, '
                    f'number_of_groups = {self.settings.number_of_groups}, amplitude_rgbs = {self.settings.amplitude_rgbs})')

        self.assertEqual(actual, expected)


class TestStartLed(SettingsTestCase):
    def test_set_to_less_than_0(self):
        START_LEDS_LESS_THAN_0 = [-1, -100]

        for start_led in START_LEDS_LESS_THAN_0:

            with self.subTest(start_led=start_led):

                with self.assertRaises(ValueError) as error:
                    self.settings.start_led = start_led

                self.assertEqual(self.settings.start_led, self.START_LED)

                actual_error_message = str(error.exception)
                expected_error_message = f'start_led ({start_led}) must be >= 0.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_greater_than_end_led(self):
        START_LEDS_GREATER_THAN_END_LED = [self.END_LED + 1, self.END_LED + 100]

        for start_led in START_LEDS_GREATER_THAN_END_LED:

            with self.subTest(start_led=start_led):

                with self.assertRaises(ValueError) as error:
                    self.settings.start_led = start_led

                self.assertEqual(self.settings.start_led, self.START_LED)

                actual_error_message = str(error.exception)
                expected_error_message = f'start_led ({start_led}) must be <= end_led ({self.END_LED}).'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_valid_value(self):
        START_LEDS = [0, self.END_LED // 2, self.END_LED]

        for start_led in START_LEDS:

            with self.subTest(start_led=start_led):

                self.settings.start_led = start_led

                self.assertEqual(self.settings.start_led, start_led)


class TestEndLed(unittest.TestCase):
    START_LED = 20
    END_LED = 100

    def setUp(self):
        self.settings = Settings(self.START_LED, self.END_LED)

    def test_set_to_less_than_0(self):
        END_LEDS_LESS_THAN_0 = [-1, -100]

        for end_led in END_LEDS_LESS_THAN_0:

            with self.subTest(end_led=end_led):

                with self.assertRaises(ValueError) as error:
                    self.settings.end_led = end_led

                self.assertEqual(self.settings.end_led, self.END_LED)

                actual_error_message = str(error.exception)
                expected_error_message = f'end_led ({end_led}) must be >= 0.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_less_than_start_led(self):
        END_LEDS_LESS_THAN_START_LED = [self.START_LED - 1, 0]

        for end_led in END_LEDS_LESS_THAN_START_LED:

            with self.subTest(end_led=end_led):

                with self.assertRaises(ValueError) as error:
                    self.settings.end_led = end_led

                self.assertEqual(self.settings.end_led, self.END_LED)

                actual_error_message = str(error.exception)
                expected_error_message = f'end_led ({end_led}) must be >= start_led ({self.START_LED}).'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_valid_value(self):
        END_LEDS = [self.START_LED, self.START_LED + 1, self.START_LED + 100]

        for end_led in END_LEDS:

            with self.subTest(end_led=end_led):

                self.settings.end_led = end_led

                self.assertEqual(self.settings.end_led, end_led)


class TestMillisecondsPerAudioChunk(SettingsTestCase):
    def test_set_to_less_than_zero(self):
        MILLISECONDS_PER_AUDIO_CHUNKS_LESS_THAN_0 = [-1, -100]

        for milliseconds_per_audio_chunk in MILLISECONDS_PER_AUDIO_CHUNKS_LESS_THAN_0:

            with self.subTest(milliseconds_per_audio_chunk=milliseconds_per_audio_chunk):

                with self.assertRaises(ValueError) as error:
                    self.settings.milliseconds_per_audio_chunk = milliseconds_per_audio_chunk

                self.assertEqual(self.settings.milliseconds_per_audio_chunk, self.MILLISECONDS_PER_AUDIO_CHUNK)

                actual_error_message = str(error.exception)
                expected_error_message = f'milliseconds_per_audio_chunk ({milliseconds_per_audio_chunk}) must be >= 0.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_valid_value(self):
        MILLISECONDS_PER_AUDIO_CHUNKS = [0, 1, 100]

        for milliseconds_per_audio_chunk in MILLISECONDS_PER_AUDIO_CHUNKS:

            with self.subTest(milliseconds_per_audio_chunk=milliseconds_per_audio_chunk):

                self.settings.milliseconds_per_audio_chunk = milliseconds_per_audio_chunk

                self.assertEqual(self.settings.milliseconds_per_audio_chunk, milliseconds_per_audio_chunk)


class TestSerialBaudrate(SettingsTestCase):

    def test_set_to_invalid_value(self):
        INVALID_SERIAL_BAUDRATES = []
        for baudrate in Settings.SERIAL_BAUDRATES:
            INVALID_SERIAL_BAUDRATES.extend([baudrate - 1, baudrate - 100, baudrate + 1, baudrate + 100])

        for serial_baudrate in INVALID_SERIAL_BAUDRATES:
            with self.subTest(serial_baudrate=serial_baudrate):

                with self.assertRaises(ValueError) as error:
                    self.settings.serial_baudrate = serial_baudrate

                self.assertEqual(self.settings.serial_baudrate, self.SERIAL_BAUDRATE)

                actual_error_message = str(error.exception)
                expected_error_message = f'Invalid serial_baudrate. Valid serial baudrates include: {Settings.SERIAL_BAUDRATES}'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_valid_value(self):
        for serial_baudrate in Settings.SERIAL_BAUDRATES:
            with self.subTest(serial_baudrate=serial_baudrate):

                self.settings.serial_baudrate = serial_baudrate

                self.assertEqual(self.settings.serial_baudrate, serial_baudrate)


class TestBrightness(SettingsTestCase):

    def test_set_to_invalid_value(self):
        INVALID_BRIGHTNESSES = [-1, -100, 256, 300]

        for brightness in INVALID_BRIGHTNESSES:

            with self.subTest(brightness=brightness):

                with self.assertRaises(ValueError) as error:
                    self.settings.brightness = brightness

                self.assertEqual(self.settings.brightness, self.BRIGHTNESS)

                actual_error_message = str(error.exception)
                expected_error_message = f'brightness ({brightness}) must be >= 0 and <= 255.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_valid_value(self):
        VALID_BRIGHTNESSES = [0, 1, 100, 254, 255]

        for brightness in VALID_BRIGHTNESSES:

            with self.subTest(brightness=brightness):

                self.settings.brightness = brightness

            self.assertEqual(self.settings.brightness, brightness)


class TestMinimumFrequency(SettingsTestCase):

    def test_set_to_less_than_0(self):
        MINIMUM_FREQUENCIES_LESS_THAN_0 = [-1, -100]

        for minimum_frequency in MINIMUM_FREQUENCIES_LESS_THAN_0:

            with self.subTest(minimum_frequency=minimum_frequency):

                with self.assertRaises(ValueError) as error:
                    self.settings.minimum_frequency = minimum_frequency

                self.assertEqual(self.settings.minimum_frequency, self.MINIMUM_FREQUENCY)

                actual_error_message = str(error.exception)
                expected_error_message = f'minimum_frequency ({minimum_frequency}) must be >= 0.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_greater_than_maximum_frequency(self):
        MINIMUM_FREQUENCIES_GREATER_THAN_MAXIMUM_FREQUENCY = [self.MAXIMUM_FREQUENCY + 1, self.MAXIMUM_FREQUENCY + 100]

        for minimum_frequency in MINIMUM_FREQUENCIES_GREATER_THAN_MAXIMUM_FREQUENCY:

            with self.subTest(minimum_frequency=minimum_frequency):

                with self.assertRaises(ValueError) as error:
                    self.settings.minimum_frequency = minimum_frequency

                self.assertEqual(self.settings.minimum_frequency, self.MINIMUM_FREQUENCY)

                actual_error_message = str(error.exception)
                expected_error_message = f'minimum_frequency ({minimum_frequency}) must be <= maximum_frequency ({self.MAXIMUM_FREQUENCY}).'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_valid_value(self):
        MINIMUM_FREQUENCIES = [0, self.MAXIMUM_FREQUENCY // 2, self.MAXIMUM_FREQUENCY]

        for minimum_frequency in MINIMUM_FREQUENCIES:

            with self.subTest(minimum_frequency=minimum_frequency):

                self.settings.minimum_frequency = minimum_frequency

                self.assertEqual(self.settings.minimum_frequency, minimum_frequency)


class TestMaximumFrequency(unittest.TestCase):
    MINIMUM_FREQUENCY = 20
    MAXIMUM_FREQUENCY = 2000

    def setUp(self):
        self.settings = Settings(minimum_frequency=self.MINIMUM_FREQUENCY,
                                 maximum_frequency=self.MAXIMUM_FREQUENCY)

    def test_set_to_less_than_0(self):

        MAXIMUM_FREQUENCIES_LESS_THAN_0 = [-1, -100]

        for maximum_frequency in MAXIMUM_FREQUENCIES_LESS_THAN_0:

            with self.subTest(maximum_frequency=maximum_frequency):

                with self.assertRaises(ValueError) as error:

                    self.settings.maximum_frequency = maximum_frequency

                self.assertEqual(self.settings.maximum_frequency, self.MAXIMUM_FREQUENCY)

                actual_error_message = str(error.exception)
                expected_error_message = f'maximum_frequency ({maximum_frequency}) must be >= 0.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_less_than_minimum_frequency(self):
        MAXIMUM_FREQUENCIES_LESS_THAN_MINIMUM_FREQUENCY = [self.MINIMUM_FREQUENCY - 1, 0]

        for maximum_frequency in MAXIMUM_FREQUENCIES_LESS_THAN_MINIMUM_FREQUENCY:

            with self.subTest(maximum_frequency=maximum_frequency):

                with self.assertRaises(ValueError) as error:

                    self.settings.maximum_frequency = maximum_frequency

                self.assertEqual(self.settings.maximum_frequency, self.MAXIMUM_FREQUENCY)

                actual_error_message = str(error.exception)
                expected_error_message = f'maximum_frequency ({maximum_frequency}) must be >= minimum_frequency ({self.MINIMUM_FREQUENCY}).'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_valid_value(self):
        MAXIMUM_FREQUENCIES = [self.MINIMUM_FREQUENCY, self.MINIMUM_FREQUENCY + 1, self.MINIMUM_FREQUENCY + 100]

        for maximum_frequency in MAXIMUM_FREQUENCIES:

            with self.subTest(maximum_frequency=maximum_frequency):

                self.settings.maximum_frequency = maximum_frequency

                self.assertEqual(self.settings.maximum_frequency, maximum_frequency)


class TestNumberOfGroups(SettingsTestCase):

    def test_set_to_invalid_value(self):

        INVALID_NUMBER_OF_GROUPS = [-1, -100, 256, 300]

        for number_of_groups in INVALID_NUMBER_OF_GROUPS:
            with self.subTest(number_of_groups=number_of_groups):

                with self.assertRaises(ValueError) as error:
                    self.settings.number_of_groups = number_of_groups

                self.assertEqual(self.settings.number_of_groups, self.NUMBER_OF_GROUPS)

                actual_error_message = str(error.exception)
                expected_error_message = f'number_of_groups ({number_of_groups}) must be >= 0 and <= 255.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_set_to_valid_value(self):
        NUMBER_OF_GROUPS = [0, 1, 100, 254, 255]

        for number_of_groups in NUMBER_OF_GROUPS:
            with self.subTest(number_of_groups=number_of_groups):

                self.settings.number_of_groups = number_of_groups

                self.assertEqual(self.settings.number_of_groups, number_of_groups)


class TestAmplitudeRGBs(unittest.TestCase):

    AMPLITUDE_RGBS = []

    def setUp(self):
        self.settings = Settings(amplitude_rgbs=self.AMPLITUDE_RGBS)

    def test_invalid_red(self):

        AMPLITUDE_RGBS_WITH_INVALID_RED = [[(-1, 0, 0)],
                                           [(-100, 0, 0)],
                                           [(256, 0, 0)],
                                           [(300, 0, 0)]]

        for amplitude_rgbs in AMPLITUDE_RGBS_WITH_INVALID_RED:

            with self.subTest(amplitude_rgbs=amplitude_rgbs):

                with self.assertRaises(ValueError) as error:
                    self.settings.amplitude_rgbs = amplitude_rgbs

                self.assertEqual(self.settings.amplitude_rgbs, self.AMPLITUDE_RGBS)

                actual_error_message = str(error.exception)

                INDEX = 0
                expected_error_message = f'The red value for the rgb at index {INDEX}, {amplitude_rgbs[INDEX]}, was not >= 0 and <= 255.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_invalid_green(self):
        AMPLITUDE_RGBS_WITH_INVALID_GREEN = [[(0, -1, 0)],
                                             [(0, -100, 0)],
                                             [(0, 256, 0)],
                                             [(0, 300, 0)]]

        for amplitude_rgbs in AMPLITUDE_RGBS_WITH_INVALID_GREEN:

            with self.subTest(amplitude_rgbs=amplitude_rgbs):

                with self.assertRaises(ValueError) as error:
                    self.settings.amplitude_rgbs = amplitude_rgbs

                self.assertEqual(self.settings.amplitude_rgbs, self.AMPLITUDE_RGBS)

                actual_error_message = str(error.exception)

                INDEX = 0
                expected_error_message = f'The green value for the rgb at index {INDEX}, {amplitude_rgbs[INDEX]}, was not >= 0 and <= 255.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_invalid_blue(self):
        AMPLITUDE_RGBS_WITH_INVALID_BLUE = [[(0, 0, -1)],
                                            [(0, 0, -100)],
                                            [(0, 0, 256)],
                                            [(0, 0, 300)]]

        for amplitude_rgbs in AMPLITUDE_RGBS_WITH_INVALID_BLUE:

            with self.subTest(amplitude_rgbs=amplitude_rgbs):

                with self.assertRaises(ValueError) as error:
                    self.settings.amplitude_rgbs = amplitude_rgbs

                self.assertEqual(self.settings.amplitude_rgbs, self.AMPLITUDE_RGBS)

                actual_error_message = str(error.exception)

                INDEX = 0
                expected_error_message = f'The blue value for the rgb at index {INDEX}, {amplitude_rgbs[INDEX]}, was not >= 0 and <= 255.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_rgb_does_not_have_three_values(self):
        AMPLITUDE_RGBS_WITH_RGBS_WITHOUT_THREE_VALUES = [[tuple()],
                                                         [(0,)],
                                                         [(0, 0)],
                                                         [(0, 0, 0, 0)],
                                                         [tuple(0 for i in range(100))]]

        for amplitude_rgbs in AMPLITUDE_RGBS_WITH_RGBS_WITHOUT_THREE_VALUES:

            with self.subTest(amplitude_rgbs=amplitude_rgbs):

                with self.assertRaises(ValueError) as error:
                    self.settings.amplitude_rgbs = amplitude_rgbs

                self.assertEqual(self.settings.amplitude_rgbs, self.AMPLITUDE_RGBS)

                actual_error_message = str(error.exception)

                INDEX = 0
                expected_error_message = f'The rgb at index {INDEX}, {amplitude_rgbs[INDEX]}, was not an Iterable with three values.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_valid_value(self):
        def create_amplitude_rgbs(color: str) -> List[List[Tuple[int, int, int]]]:
            colors = {'red': 0, 'green': 0, 'blue': 0}

            VALUES = [1, 100, 254, 255]

            amplitude_rgbs = []

            for value in VALUES:

                colors[color] = value

                amplitude_rgbs.append([(colors['red'], colors['green'], colors['blue'])])

            return amplitude_rgbs

        AMPLITUDE_RGBS = [[(0, 0, 0)],
                          [(10, 20, 30), (0, 10, 30), (43, 145, 231)]]
        AMPLITUDE_RGBS.extend(create_amplitude_rgbs('red'))
        AMPLITUDE_RGBS.extend(create_amplitude_rgbs('green'))
        AMPLITUDE_RGBS.extend(create_amplitude_rgbs('blue'))

        for amplitude_rgbs in AMPLITUDE_RGBS:

            with self.subTest(amplitude_rgbs=amplitude_rgbs):

                self.settings.amplitude_rgbs = amplitude_rgbs

                self.assertEqual(self.settings.amplitude_rgbs, amplitude_rgbs)
