import unittest
from util import Settings, SettingsCollection


class SettingsCollectionTestCase(unittest.TestCase):

    SETTINGS_1_NAME = 'settings_1_name'
    SETTINGS_2_NAME = 'settings_2_name'
    NON_EXISTENT_SETTINGS_NAME = 'I am not a Settings name in the SettingsCollection'
    UNUSED_SETTINGS_NAME = 'settings_new_name'

    def setUp(self):
        self.settings_1 = Settings()
        self.settings_2 = Settings()

        collection = {self.SETTINGS_1_NAME: self.settings_1,
                      self.SETTINGS_2_NAME: self.settings_2}

        self.settings_collection = SettingsCollection(collection)


class TestConstructor(unittest.TestCase):

    def test_default(self):
        SettingsCollection()

    def test_empty_collection(self):
        COLLECTION = dict()

        settings_collection = SettingsCollection(COLLECTION)

        EXPECTED_SETTINGS_NAMES = set()

        self.assertEqual(settings_collection.settings_names, EXPECTED_SETTINGS_NAMES)

        with self.assertRaises(AttributeError) as error:
            settings_collection.current_settings

        actual_error_message = str(error.exception)
        expected_error_message = 'There are no Settings in this SettingsCollection. Call update_collection to add a Setting.'

        self.assertEqual(actual_error_message, expected_error_message)

        with self.assertRaises(AttributeError) as error:
            settings_collection.current_settings_name

        actual_error_message = str(error.exception)
        expected_error_message = 'There are no Settings in this SettingsCollection. Call update_collection to add a Setting.'

        self.assertEqual(actual_error_message, expected_error_message)

    def test_collection_with_one_settings(self):
        SETTINGS_NAME = 'settings_1'
        SETTINGS = Settings()

        COLLETION = {SETTINGS_NAME: SETTINGS}

        settings_collection = SettingsCollection(COLLETION)

        EXPECTED_SETTINGS_NAMES = {SETTINGS_NAME}

        self.assertEqual(settings_collection.settings_names, EXPECTED_SETTINGS_NAMES)

        self.assertIs(settings_collection.current_settings, SETTINGS)

        self.assertEqual(settings_collection.current_settings_name, SETTINGS_NAME)

    def test_collection_with_two_settings(self):
        SETTINGS_1_NAME = 'settings_1'
        SETINGS_1 = Settings()

        SETTINGS_2_NAME = 'settings_2'
        SETTINGS_2 = Settings()

        COLLETION = {SETTINGS_1_NAME: SETINGS_1,
                     SETTINGS_2_NAME: SETTINGS_2}

        settings_collection = SettingsCollection(COLLETION)

        EXPECTED_SETTINGS_NAMES = {SETTINGS_1_NAME, SETTINGS_2_NAME}

        self.assertEqual(settings_collection.settings_names, EXPECTED_SETTINGS_NAMES)

        self.assertIs(settings_collection.current_settings, SETINGS_1)

        self.assertEqual(settings_collection.current_settings_name, SETTINGS_1_NAME)


class TestProperties(SettingsCollectionTestCase):
    def test_settings_names(self):
        EXPECTED_SETTINGS_NAMES = {self.SETTINGS_1_NAME, self.SETTINGS_2_NAME}

        self.assertEqual(self.settings_collection.settings_names, EXPECTED_SETTINGS_NAMES)

    def test_current_settings(self):
        self.assertIs(self.settings_collection.current_settings, self.settings_1)

    def test_current_settings_name(self):
        self.assertEqual(self.settings_collection.current_settings_name, self.SETTINGS_1_NAME)


class TestSetCurrentSettingsName(SettingsCollectionTestCase):
    def test_set_to_settings_name_that_is_in_the_collection(self):

        self.settings_collection.current_settings_name = self.SETTINGS_2_NAME

        self.assertEqual(self.settings_collection.current_settings_name, self.SETTINGS_2_NAME)

    def test_set_to_settings_name_that_is_not_in_the_collection(self):

        with self.assertRaises(ValueError) as error:
            self.settings_collection.current_settings_name = self.NON_EXISTENT_SETTINGS_NAME

        actual_error_message = str(error.exception)
        expected_error_message = (f'There is no Settings in this SettingsCollection with the name {self.NON_EXISTENT_SETTINGS_NAME}. '
                                  f'Recognized Settings names include: {self.settings_collection.settings_names}')

        self.assertEqual(actual_error_message, expected_error_message)


class TestGetSettings(SettingsCollectionTestCase):
    def test_get_settings_with_name_that_is_in_the_collection(self):

        settings_1 = self.settings_collection.get_settings(self.SETTINGS_1_NAME)
        settings_2 = self.settings_collection.get_settings(self.SETTINGS_2_NAME)

        self.assertIs(settings_1, self.settings_1)
        self.assertIs(settings_2, self.settings_2)

    def test_get_settings_with_name_that_is_not_in_the_collection(self):
        with self.assertRaises(KeyError):
            self.settings_collection.get_settings(self.NON_EXISTENT_SETTINGS_NAME)


class TestUpdateCollection(SettingsCollectionTestCase):
    def test_update_collection_with_other_elements_already_in_the_collection(self):
        SETTINGS = Settings()

        self.settings_collection.update_collection(self.UNUSED_SETTINGS_NAME, SETTINGS)

        settings = self.settings_collection.get_settings(self.UNUSED_SETTINGS_NAME)
        self.assertIs(settings, SETTINGS)

        self.assertEqual(self.settings_collection.current_settings_name, self.SETTINGS_1_NAME)
        self.assertIs(self.settings_collection.current_settings, self.settings_1)

        EXPECTED_SETTINGS_NAMES = {self.UNUSED_SETTINGS_NAME, self.SETTINGS_1_NAME, self.SETTINGS_2_NAME}

        self.assertEqual(self.settings_collection.settings_names, EXPECTED_SETTINGS_NAMES)

    def test_update_collection_with_no_other_elements_in_the_collection(self):
        COLLECTION = dict()

        settings_collection = SettingsCollection(COLLECTION)

        SETTINGS = Settings()

        settings_collection.update_collection(self.UNUSED_SETTINGS_NAME, SETTINGS)

        EXPECTED_SETTINGS_NAMES = {self.UNUSED_SETTINGS_NAME}

        self.assertEqual(settings_collection.settings_names, EXPECTED_SETTINGS_NAMES)

        self.assertIs(settings_collection.current_settings, SETTINGS)

        self.assertEqual(settings_collection.current_settings_name, self.UNUSED_SETTINGS_NAME)


class TestDeleteSettings(SettingsCollectionTestCase):

    def test_delete_non_current_setting_with_multiple_settings_in_collection(self):
        self.settings_collection.delete_settings(self.SETTINGS_2_NAME)

        EXPECTED_SETTINGS_NAMES = {self.SETTINGS_1_NAME}

        self.assertEqual(self.settings_collection.settings_names, EXPECTED_SETTINGS_NAMES)

        self.assertIs(self.settings_collection.current_settings, self.settings_1)

        self.assertEqual(self.settings_collection.current_settings_name, self.SETTINGS_1_NAME)

    def test_delete_current_setting_with_multiple_settings_in_collection(self):
        self.settings_collection.delete_settings(self.SETTINGS_1_NAME)

        EXPECTED_SETTINGS_NAMES = {self.SETTINGS_2_NAME}

        self.assertEqual(self.settings_collection.settings_names, EXPECTED_SETTINGS_NAMES)

        self.assertIs(self.settings_collection.current_settings, self.settings_2)

        self.assertEqual(self.settings_collection.current_settings_name, self.SETTINGS_2_NAME)

    def test_delete_with_no_settings_in_collection(self):
        COLLECTION = dict()

        settings_collection = SettingsCollection(COLLECTION)

        settings_collection.delete_settings(self.NON_EXISTENT_SETTINGS_NAME)

    def test_delete_non_existent_setting_with_settings_in_collection(self):
        self.settings_collection.delete_settings(self.NON_EXISTENT_SETTINGS_NAME)

        EXPECTED_SETTINGS_NAMES = {self.SETTINGS_1_NAME, self.SETTINGS_2_NAME}

        self.assertEqual(self.settings_collection.settings_names, EXPECTED_SETTINGS_NAMES)

        self.assertIs(self.settings_collection.current_settings, self.settings_1)

        self.assertEqual(self.settings_collection.current_settings_name, self.SETTINGS_1_NAME)
