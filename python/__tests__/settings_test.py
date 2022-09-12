import unittest

from settings import Settings


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

    def setUp(self):
        self.settings = Settings(self.START_LED, self.END_LED, self.MILLISECONDS_PER_AUDIO_CHUNK,
                                 self.SERIAL_PORT, self.SERIAL_BAUDRATE, self.BRIGHTNESS, self.MINIMUM_FREQUENCY,
                                 self.MAXIMUM_FREQUENCY, self.SHOULD_REVERSE_LEDS, self.NUMBER_OF_GROUPS)


class TestEquals(SettingsTestCase):
    def test_does_equal(self):
        settings = Settings(self.START_LED, self.END_LED, self.MILLISECONDS_PER_AUDIO_CHUNK,
                            self.SERIAL_PORT, self.SERIAL_BAUDRATE, self.BRIGHTNESS, self.MINIMUM_FREQUENCY,
                            self.MAXIMUM_FREQUENCY, self.SHOULD_REVERSE_LEDS, self.NUMBER_OF_GROUPS)

        self.assertEqual(settings, self.settings)

    def test_does_not_equal(self):
        self.assertNotEqual(self.settings, Settings())
        self.assertNotEqual(self.settings, None)


class TestRepr(SettingsTestCase):
    def test_repr(self):
        actual = repr(self.settings)

        expected = (f'Settings(start_led = {self.settings.start_led}, end_led = {self.settings.end_led}, '
                    f'milliseconds_per_audio_chunk = {self.settings.milliseconds_per_audio_chunk}, '
                    f'serial_port = {self.settings.serial_port}, serial_baudrate = {self.settings.serial_baudrate}, '
                    f'brightness = {self.settings.brightness}, minimum_frequency = {self.settings.minimum_frequency}, '
                    f'maximum_frequency = {self.settings.maximum_frequency}, should_reverse_leds = {self.settings.should_reverse_leds}, '
                    f'number_of_groups = {self.settings.number_of_groups})')

        self.assertEqual(actual, expected)


class TestStartLed(SettingsTestCase):
    def test_set_to_less_than_0(self):
        START_LEDS_LESS_THAN_0 = [-1, -100]

        for start_led in START_LEDS_LESS_THAN_0:

            with self.subTest(start_led=start_led):

                with self.assertRaises(ValueError):
                    self.settings.start_led = start_led

                self.assertEqual(self.settings.start_led, self.START_LED)

    def test_set_to_greater_than_end_led(self):
        START_LEDS_GREATER_THAN_END_LED = [self.END_LED + 1, self.END_LED + 100]

        for start_led in START_LEDS_GREATER_THAN_END_LED:

            with self.subTest(start_led=start_led):

                with self.assertRaises(ValueError):
                    self.settings.start_led = start_led

                self.assertEqual(self.settings.start_led, self.START_LED)

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

                with self.assertRaises(ValueError):
                    self.settings.end_led = end_led

                self.assertEqual(self.settings.end_led, self.END_LED)

    def test_set_to_less_than_start_led(self):
        END_LEDS_LESS_THAN_START_LED = [self.START_LED - 1, 0]

        for end_led in END_LEDS_LESS_THAN_START_LED:

            with self.subTest(end_led=end_led):

                with self.assertRaises(ValueError):
                    self.settings.end_led = end_led

                self.assertEqual(self.settings.end_led, self.END_LED)

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

                with self.assertRaises(ValueError):
                    self.settings.milliseconds_per_audio_chunk = milliseconds_per_audio_chunk

                self.assertEqual(self.settings.milliseconds_per_audio_chunk, self.MILLISECONDS_PER_AUDIO_CHUNK)

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

                with self.assertRaises(ValueError):
                    self.settings.serial_baudrate = serial_baudrate

                self.assertEqual(self.settings.serial_baudrate, self.SERIAL_BAUDRATE)

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

                with self.assertRaises(ValueError):
                    self.settings.brightness = brightness

                self.assertEqual(self.settings.brightness, self.BRIGHTNESS)

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

                with self.assertRaises(ValueError):
                    self.settings.minimum_frequency = minimum_frequency

                self.assertEqual(self.settings.minimum_frequency, self.MINIMUM_FREQUENCY)

    def test_set_to_greater_than_maximum_frequency(self):
        MINIMUM_FREQUENCIES_GREATER_THAN_MAXIMUM_FREQUENCY = [self.MAXIMUM_FREQUENCY + 1, self.MAXIMUM_FREQUENCY + 100]

        for minimum_frequency in MINIMUM_FREQUENCIES_GREATER_THAN_MAXIMUM_FREQUENCY:

            with self.subTest(minimum_frequency=minimum_frequency):

                with self.assertRaises(ValueError):
                    self.settings.minimum_frequency = minimum_frequency

                self.assertEqual(self.settings.minimum_frequency, self.MINIMUM_FREQUENCY)

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

                with self.assertRaises(ValueError):

                    self.settings.maximum_frequency = maximum_frequency

                self.assertEqual(self.settings.maximum_frequency, self.MAXIMUM_FREQUENCY)

    def test_set_to_less_than_minimum_frequency(self):
        MAXIMUM_FREQUENCIES_LESS_THAN_MINIMUM_FREQUENCY = [self.MINIMUM_FREQUENCY - 1, 0]

        for maximum_frequency in MAXIMUM_FREQUENCIES_LESS_THAN_MINIMUM_FREQUENCY:

            with self.subTest(maximum_frequency=maximum_frequency):

                with self.assertRaises(ValueError):

                    self.settings.maximum_frequency = maximum_frequency

                self.assertEqual(self.settings.maximum_frequency, self.MAXIMUM_FREQUENCY)

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

                with self.assertRaises(ValueError):
                    self.settings.number_of_groups = number_of_groups

                self.assertEqual(self.settings.number_of_groups, self.NUMBER_OF_GROUPS)

    def test_set_to_valid_value(self):
        NUMBER_OF_GROUPS = [0, 1, 100, 254, 255]

        for number_of_groups in NUMBER_OF_GROUPS:
            with self.subTest(number_of_groups=number_of_groups):

                self.settings.number_of_groups = number_of_groups

                self.assertEqual(self.settings.number_of_groups, number_of_groups)


class TestToJSON(SettingsTestCase):
    def test_empty(self):
        SETTINGS = Settings()

        EXPECTED = {'start_led': SETTINGS.start_led, 'end_led': SETTINGS.end_led,
                    'milliseconds_per_audio_chunk': SETTINGS.milliseconds_per_audio_chunk,
                    'serial_port': SETTINGS.serial_port, 'serial_baudrate': SETTINGS.serial_baudrate,
                    'brightness': SETTINGS.brightness, 'minimum_frequency': SETTINGS.minimum_frequency,
                    'maximum_frequency': SETTINGS.maximum_frequency,
                    'should_reverse_leds': SETTINGS.should_reverse_leds, 'number_of_groups': SETTINGS.number_of_groups}

        ACTUAL = SETTINGS.to_json()

        self.assertEqual(EXPECTED, ACTUAL)

    def test_not_empty(self):
        SETTINGS = self.settings

        EXPECTED = {'start_led': SETTINGS.start_led, 'end_led': SETTINGS.end_led,
                    'milliseconds_per_audio_chunk': SETTINGS.milliseconds_per_audio_chunk,
                    'serial_port': SETTINGS.serial_port, 'serial_baudrate': SETTINGS.serial_baudrate,
                    'brightness': SETTINGS.brightness, 'minimum_frequency': SETTINGS.minimum_frequency,
                    'maximum_frequency': SETTINGS.maximum_frequency,
                    'should_reverse_leds': SETTINGS.should_reverse_leds, 'number_of_groups': SETTINGS.number_of_groups}

        ACTUAL = self.settings.to_json()

        self.assertEqual(EXPECTED, ACTUAL)
