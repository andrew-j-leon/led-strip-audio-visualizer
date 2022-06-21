import shutil
from pathlib import Path

from pyfakefs import fake_filesystem_unittest
from settings import Settings, load, save


class TestSaveAndLoadSettings(fake_filesystem_unittest.TestCase):
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
        self.setUpPyfakefs()

        self.settings = Settings(self.START_LED, self.END_LED, self.MILLISECONDS_PER_AUDIO_CHUNK,
                                 self.SERIAL_PORT, self.SERIAL_BAUDRATE, self.BRIGHTNESS, self.MINIMUM_FREQUENCY,
                                 self.MAXIMUM_FREQUENCY, self.SHOULD_REVERSE_LEDS, self.NUMBER_OF_GROUPS)

        self.existent_directory = Path('existent_directory')
        self.existent_directory.mkdir()

        self.non_existent_directory = Path('non_existent_directory')

        self.existent_file = self.existent_directory.joinpath('existent_file')
        self.existent_file.touch()

    def tearDown(self):
        shutil.rmtree(str(self.existent_directory), ignore_errors=True)

    def test_saving_in_directory_that_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            save(self.settings, self.non_existent_directory)

    def test_saving_to_a_file(self):
        with self.assertRaises(NotADirectoryError):
            save(self.settings, self.existent_file)

    def test_saving_in_directory_with_insufficient_permissions(self):
        self.existent_directory.chmod(0o100)

        with self.assertRaises(PermissionError):
            save(self.settings, self.existent_directory)

    def test_loading_from_directory_that_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            load(self.non_existent_directory)

    def test_loading_from_a_file(self):
        with self.assertRaises(NotADirectoryError):
            load(self.existent_file)

    def test_loading_from_directory_with_no_save_data(self):
        with self.assertRaises(ValueError):
            load(self.existent_directory)

    def test_save_once_and_load(self):
        save(self.settings, self.existent_directory)

        SETTINGS = load(self.existent_directory)

        self.assertEqual(self.settings, SETTINGS)

    def test_overwrite_previous_save(self):
        save(self.settings, self.existent_directory)

        self.settings.start_led = self.START_LED + 1
        self.settings.end_led = self.END_LED + 1

        save(self.settings, self.existent_directory)

        settings = load(self.existent_directory)

        self.assertEqual(settings, self.settings)
