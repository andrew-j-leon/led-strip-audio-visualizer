from pathlib import Path
import unittest

from util import Settings, SettingsCollection


class SettingsCollectionTestCase(unittest.TestCase):
    CURRENT_NAME = 'settings_1_name'
    NON_CURRENT_NAME = 'settings_2_name'

    NEW_NAME = 'settings_new_name'
    NON_EXISTENT_NAME = 'non_existant_settings_name'

    def setUp(self):
        START_LED = 100
        END_LED = 300
        MILLISECONDS_PER_AUDIO_CHUNK = 55
        SERIAL_PORT = 'COM1'
        SERIAL_BAUDRATE = 9600
        BRIGHTNESS = 10
        MINIMUM_FREQUENCY = 100
        MAXIMUM_FREQUENCY = 1000
        SHOULD_REVERSE_LEDS = True
        NUMBER_OF_GROUPS = 50
        AMPLITUDE_RGBS = [(0, 0, 0), (1, 1, 1), (2, 3, 4)]

        self.current_settings = Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK,
                                         SERIAL_PORT, SERIAL_BAUDRATE, BRIGHTNESS, MINIMUM_FREQUENCY,
                                         MAXIMUM_FREQUENCY, SHOULD_REVERSE_LEDS, NUMBER_OF_GROUPS, AMPLITUDE_RGBS)

        self.non_current_settings = Settings()

        self.collection = {self.CURRENT_NAME: self.current_settings,
                           self.NON_CURRENT_NAME: self.non_current_settings}

        self.settings_collection = SettingsCollection(self.collection)


class TestMiscellaneous(SettingsCollectionTestCase):
    def test_length(self):
        SETTINGS_COLLECTION_LENGTH = len(self.settings_collection)
        EXPECTED_LENGTH = len(self.collection)

        self.assertEqual(SETTINGS_COLLECTION_LENGTH, EXPECTED_LENGTH)

    def test_contains(self):
        self.assertTrue(self.CURRENT_NAME in self.settings_collection)
        self.assertTrue(self.NON_CURRENT_NAME in self.settings_collection)
        self.assertTrue(self.NEW_NAME not in self.settings_collection)

    def test_iter(self):
        names = list()

        for name in self.settings_collection:
            names.append(name)

        expected_names = list()

        for name in self.collection:
            expected_names.append(name)

        self.assertEqual(names, expected_names)


class TestConstructor(unittest.TestCase):
    def test_empty_collection(self):
        settings_collection = SettingsCollection()

        with self.assertRaises(AttributeError):
            settings_collection.current_settings

        with self.assertRaises(AttributeError):
            settings_collection.current_name

        EXPECTED_LENGTH = 0
        self.assertEqual(len(settings_collection), EXPECTED_LENGTH)

        EXPECTED_NAMES = dict().keys()
        self.assertEqual(settings_collection.names(), EXPECTED_NAMES)

    def test_collection_with_one_settings(self):
        SETTINGS_NAME = 'current_settings'
        SETTINGS = Settings()

        COLLECTION = {SETTINGS_NAME: SETTINGS}

        settings_collection = SettingsCollection(COLLECTION)

        EXPECTED_LENGTH = len(COLLECTION)
        self.assertEqual(EXPECTED_LENGTH, len(settings_collection))

        EXPECTED_NAMES = COLLECTION.keys()
        self.assertEqual(settings_collection.names(), EXPECTED_NAMES)

        self.assertIs(settings_collection.current_settings, SETTINGS)

        self.assertEqual(settings_collection.current_name, SETTINGS_NAME)

    def test_collection_with_multiple_settings(self):
        CURRENT_NAME = 'current_settings'
        SETINGS_1 = Settings()

        NON_CURRENT_NAME = 'non_current_settings'
        SETTINGS_2 = Settings()

        COLLECTION = {CURRENT_NAME: SETINGS_1,
                      NON_CURRENT_NAME: SETTINGS_2}

        settings_collection = SettingsCollection(COLLECTION)

        EXPECTED_LENGTH = len(COLLECTION)
        self.assertEqual(EXPECTED_LENGTH, len(settings_collection))

        EXPECTED_NAMES = COLLECTION.keys()
        self.assertEqual(EXPECTED_NAMES, settings_collection.names())

        self.assertIs(settings_collection.current_settings, SETINGS_1)

        self.assertEqual(settings_collection.current_name, CURRENT_NAME)


class TestProperties(SettingsCollectionTestCase):
    def test_current_settings(self):
        self.assertIs(self.settings_collection.current_settings,
                      self.current_settings)

    def test_current_name(self):
        self.assertEqual(self.settings_collection.current_name,
                         self.CURRENT_NAME)


class TestSettingTheCurrentName(SettingsCollectionTestCase):
    def test_set_to_a_name_that_is_in_the_collection(self):
        self.settings_collection.current_name = self.NON_CURRENT_NAME

        self.assertEqual(self.settings_collection.current_name, self.NON_CURRENT_NAME)
        self.assertIs(self.settings_collection.current_settings, self.non_current_settings)

    def test_set_to_a_name_that_is_NOT_in_the_collection(self):
        with self.assertRaises(ValueError):
            self.settings_collection.current_name = self.NEW_NAME

        self.assertEqual(self.settings_collection.current_name, self.CURRENT_NAME)
        self.assertIs(self.settings_collection.current_settings, self.current_settings)


class TestGetSettings(SettingsCollectionTestCase):
    def test_using_names_that_are_in_the_collection(self):
        CURRENT_SETTINGS = self.settings_collection[self.CURRENT_NAME]
        NON_CURRENT_SETTINGS = self.settings_collection[self.NON_CURRENT_NAME]

        self.assertIs(CURRENT_SETTINGS, self.current_settings)
        self.assertIs(NON_CURRENT_SETTINGS, self.non_current_settings)

    def test_using_a_name_that_is_NOT_in_the_collection(self):
        with self.assertRaises(KeyError):
            self.settings_collection[self.NEW_NAME]


class TestSetSettings(SettingsCollectionTestCase):
    def test_overwrite_current_settings(self):
        NEW_SETTINGS = Settings()

        self.settings_collection[self.CURRENT_NAME] = NEW_SETTINGS

        self.assertIs(self.settings_collection[self.CURRENT_NAME],
                      NEW_SETTINGS)

        self.assertIs(self.settings_collection.current_settings,
                      NEW_SETTINGS)

        EXPECTED_LENGTH = 2
        self.assertEqual(len(self.settings_collection), EXPECTED_LENGTH)

    def test_overwite_a_settings_in_the_collection_that_is_NOT_current_settings(self):
        NEW_SETTINGS = Settings()

        self.settings_collection[self.NON_CURRENT_NAME] = NEW_SETTINGS

        self.assertIs(self.settings_collection[self.NON_CURRENT_NAME],
                      NEW_SETTINGS)

        self.assertIs(self.settings_collection.current_settings,
                      self.current_settings)

        EXPECTED_LENGTH = 2
        self.assertEqual(len(self.settings_collection), EXPECTED_LENGTH)

    def test_add_a_new_settings_to_the_collection(self):
        NEW_SETTINGS = Settings()

        self.settings_collection[self.NEW_NAME] = NEW_SETTINGS

        self.assertIs(self.settings_collection[self.NEW_NAME],
                      NEW_SETTINGS)

        self.assertIs(self.settings_collection.current_settings,
                      self.current_settings)

        EXPECTED_LENGTH = 3
        self.assertEqual(len(self.settings_collection), EXPECTED_LENGTH)

    def test_add_a_non_settings_object(self):
        NEW_SETTINGS = 'not a Settings'

        with self.assertRaises(TypeError):
            self.settings_collection[self.NEW_NAME] = NEW_SETTINGS

        with self.assertRaises(KeyError):
            self.settings_collection[self.NEW_NAME]

        self.assertIs(self.settings_collection.current_settings,
                      self.current_settings)

        EXPECTED_LENGTH = 2
        self.assertEqual(len(self.settings_collection), EXPECTED_LENGTH)


class TestDeleteSettings(SettingsCollectionTestCase):
    def test_delete_current_settings(self):
        del self.settings_collection[self.CURRENT_NAME]

        with self.assertRaises(KeyError):
            self.settings_collection[self.CURRENT_NAME]

        self.assertIs(self.settings_collection.current_settings,
                      self.non_current_settings)

        self.assertEqual(self.settings_collection.current_name,
                         self.NON_CURRENT_NAME)

        EXPECTED_LENGTH = 1
        self.assertEqual(len(self.settings_collection), EXPECTED_LENGTH)

    def test_delete_non_current_settings(self):
        del self.settings_collection[self.NON_CURRENT_NAME]

        with self.assertRaises(KeyError):
            self.settings_collection[self.NON_CURRENT_NAME]

        self.assertIs(self.settings_collection.current_settings,
                      self.current_settings)

        self.assertEqual(self.settings_collection.current_name,
                         self.CURRENT_NAME)

        EXPECTED_LENGTH = 1
        self.assertEqual(len(self.settings_collection), EXPECTED_LENGTH)

    def test_delete_settings_that_is_NOT_in_the_collection(self):
        with self.assertRaises(KeyError):
            del self.settings_collection[self.NEW_NAME]

        self.assertIs(self.settings_collection.current_settings,
                      self.current_settings)

        self.assertEqual(self.settings_collection.current_name,
                         self.CURRENT_NAME)

        EXPECTED_LENGTH = 2
        self.assertEqual(len(self.settings_collection), EXPECTED_LENGTH)

    def test_delete_ALL_settings_in_the_collection(self):
        NAMES = list(self.settings_collection.names())

        for name in NAMES:
            del self.settings_collection[name]

        with self.assertRaises(AttributeError):
            self.settings_collection.current_settings

        with self.assertRaises(AttributeError):
            self.settings_collection.current_name

        EXPECTED_LENGTH = 0
        self.assertEqual(len(self.settings_collection), EXPECTED_LENGTH)


class TestSavingAndLoadingFromFile(SettingsCollectionTestCase):
    def setUp(self):
        super().setUp()

        self.save_directory = Path('./test_saves')

        self.save_directory.mkdir(exist_ok=True)

        self.settings_collection.set_save_directory(self.save_directory)

    def tearDown(self):
        super().tearDown()

        for file in self.save_directory.iterdir():
            file.unlink()

        self.save_directory.rmdir()

    def test_can_load_the_same_collection_after_saving(self):
        START_LED = 20
        END_LED = 200

        NEW_NAME = 'new_name'
        NEW_SETTINGS = Settings(START_LED, END_LED)

        self.settings_collection[NEW_NAME] = NEW_SETTINGS
        self.settings_collection.current_name = NEW_NAME

        self.settings_collection.save_to_files()

        new_settings_collection = SettingsCollection()
        new_settings_collection.load_from_directory(self.save_directory)

        self.assertEqual(self.settings_collection, new_settings_collection)

    def test_save_when_no_save_directory_set(self):
        settings_collection = SettingsCollection()

        with self.assertRaises(ValueError):
            settings_collection.save_to_files()
