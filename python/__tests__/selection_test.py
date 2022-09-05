import unittest

from color_palette import ColorPalette
from selection import Selection


class SelectionTestCase(unittest.TestCase):
    SELECTED_KEY = 'key_1'
    NON_SELECTED_KEY = 'key_2'
    KEY_NOT_IN_SELECTION = 'non_existent_key'

    def setUp(self):
        CURRENT_AMPLITUDE_RGBS = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
        self.selected_value = ColorPalette(CURRENT_AMPLITUDE_RGBS)

        NON_CURRENT_AMPLITUDE_RGBS = [(3, 3, 3), (4, 4, 4), (5, 5, 5)]
        self.non_selected_value = ColorPalette(NON_CURRENT_AMPLITUDE_RGBS)

        self.items = {self.SELECTED_KEY: self.selected_value,
                      self.NON_SELECTED_KEY: self.non_selected_value}

        self.selection = Selection(self.items)


class SelectionTest(SelectionTestCase):
    def test_constructor(self):
        self.assertEqual(self.selection.selected_key, self.SELECTED_KEY)
        self.assertIs(self.selection.selected_value, self.selected_value)

    def test_length(self):
        EXPECTED_LENGTH = len(self.items)

        self.assertEqual(len(self.selection), EXPECTED_LENGTH)

    def test_contains(self):
        self.assertTrue(self.SELECTED_KEY in self.selection)
        self.assertTrue(self.NON_SELECTED_KEY in self.selection)

        self.assertTrue(self.KEY_NOT_IN_SELECTION not in self.selection)

    def test_iter(self):
        EXPECTED_KEYS = {self.SELECTED_KEY, self.NON_SELECTED_KEY}
        ACTUAL_KEYS = {key for key in self.selection}

        self.assertEqual(EXPECTED_KEYS, ACTUAL_KEYS)


class TestSelectedKeyAndPalette(SelectionTestCase):
    def test_get_selected_key_with_no_values_in_selection(self):
        selection = Selection()

        with self.assertRaises(AttributeError):
            selection.selected_key

    def test_get_selected_value_with_no_values_in_selection(self):
        selection = Selection()

        with self.assertRaises(AttributeError):
            selection.selected_value

    def test_set_to_selected_key(self):
        self.selection.selected_key = self.SELECTED_KEY

        self.assertEqual(self.selection.selected_key, self.SELECTED_KEY)
        self.assertIs(self.selection.selected_value, self.selected_value)

    def test_set_to_non_selected_key(self):
        self.selection.selected_key = self.NON_SELECTED_KEY

        self.assertEqual(self.selection.selected_key, self.NON_SELECTED_KEY)
        self.assertIs(self.selection.selected_value, self.non_selected_value)

    def test_set_to_key_that_is_not_in_selection(self):
        with self.assertRaises(ValueError):
            self.selection.selected_key = self.KEY_NOT_IN_SELECTION

        self.assertEqual(self.selection.selected_key, self.SELECTED_KEY)
        self.assertIs(self.selection.selected_value, self.selected_value)


class TestKeysValuesAndItems(SelectionTestCase):
    def test_keys(self):
        keys = set(self.selection.keys())

        EXPECTED_KEYS = {self.SELECTED_KEY, self.NON_SELECTED_KEY}

        self.assertEqual(keys, EXPECTED_KEYS)

    def test_values(self):
        values = list(self.selection.values())

        EXPECTED_VALUES = [self.selected_value, self.non_selected_value]

        self.assertEqual(values, EXPECTED_VALUES)

    def test_items(self):
        items = [(key, value) for key, value in self.selection.items()]

        EXPECTED_VALUES = [(self.SELECTED_KEY, self.selected_value),
                           (self.NON_SELECTED_KEY, self.non_selected_value)]

        self.assertEqual(items, EXPECTED_VALUES)


class TestEqual(SelectionTestCase):
    def test_empty_selections_are_equal(self):
        selection_1 = Selection()
        selection_2 = Selection()

        self.assertEqual(selection_1, selection_2)

    def test_same_keys_and_selected_key_but_different_selected_value(self):
        ITEMS = {self.SELECTED_KEY: self.non_selected_value,
                 self.NON_SELECTED_KEY: self.selected_value}

        selection = Selection(ITEMS)
        selection.selected_key = self.SELECTED_KEY

        self.assertNotEqual(selection, self.selection)

    def test_same_keys_and_selected_key_and_selected_value_but_different_non_selected_value(self):
        SELECTED_VALUE = ColorPalette([(0, 0, 0)])
        NON_SELECTED_VALUE_1 = ColorPalette([(1, 1, 1)])
        NON_SELECTED_VALUE_2 = ColorPalette([(2, 2, 2)])

        ITEMS_1 = {'selected_key': SELECTED_VALUE,
                   'non_selected_key': NON_SELECTED_VALUE_1}

        ITEMS_2 = {'selected_key': SELECTED_VALUE,
                   'non_selected_key': NON_SELECTED_VALUE_2}

        SELECTION_1 = Selection(ITEMS_1)
        SELECTION_2 = Selection(ITEMS_2)

        self.assertNotEqual(SELECTION_1, SELECTION_2)

    def test_non_empty_selections_are_equal(self):
        items = {self.SELECTED_KEY: ColorPalette(self.selected_value.amplitude_rgbs),
                 self.NON_SELECTED_KEY: ColorPalette(self.non_selected_value.amplitude_rgbs)}

        selection = Selection(items)

        self.assertEqual(selection, self.selection)

    def test_swapped_keys(self):
        items = {self.NON_SELECTED_KEY: ColorPalette(self.selected_value.amplitude_rgbs),
                 self.SELECTED_KEY: ColorPalette(self.non_selected_value.amplitude_rgbs)}

        selection = Selection(items)

        self.assertNotEqual(selection, self.selection)

    def test_almost_equal_but_with_one_value_different(self):
        items = {self.SELECTED_KEY: ColorPalette(self.selected_value.amplitude_rgbs),
                 self.NON_SELECTED_KEY: ColorPalette(self.non_selected_value.amplitude_rgbs),
                 self.KEY_NOT_IN_SELECTION: ColorPalette()}

        selection = Selection(items)

        self.assertNotEqual(selection, self.selection)


class TestGetItem(SelectionTest):
    def test_get_selected_value(self):
        value = self.selection[self.SELECTED_KEY]

        self.assertIs(value, self.selected_value)

    def test_get_non_selected_value(self):
        value = self.selection[self.NON_SELECTED_KEY]

        self.assertIs(value, self.non_selected_value)

    def test_key_is_not_in_selection(self):
        with self.assertRaises(KeyError):
            self.selection[self.KEY_NOT_IN_SELECTION]


class TestSetItem(SelectionTest):
    def setUp(self):
        super().setUp()

        self.ORIGINAL_LENGTH = len(self.selection)

    def test_add_new_value(self):
        NEW_VALUE = ColorPalette()
        self.selection[self.KEY_NOT_IN_SELECTION] = NEW_VALUE

        EXPECTED_LENGTH = self.ORIGINAL_LENGTH + 1

        self.assertEqual(EXPECTED_LENGTH, len(self.selection))
        self.assertIs(NEW_VALUE, self.selection[self.KEY_NOT_IN_SELECTION])

    def test_overwrite_selected_value(self):
        NEW_VALUE = ColorPalette()
        self.selection[self.SELECTED_KEY] = NEW_VALUE

        self.assertEqual(self.ORIGINAL_LENGTH, len(self.selection))
        self.assertIs(NEW_VALUE, self.selection[self.SELECTED_KEY])
        self.assertIs(NEW_VALUE, self.selection.selected_value)

    def test_overwrite_non_selected_value(self):
        NEW_VALUE = ColorPalette()
        self.selection[self.NON_SELECTED_KEY] = NEW_VALUE

        self.assertEqual(self.ORIGINAL_LENGTH, len(self.selection))
        self.assertIs(NEW_VALUE, self.selection[self.NON_SELECTED_KEY])

    def test_set_value_on_empty_selection(self):
        selection = Selection()

        KEY = 'value_key'
        VALUE = ColorPalette()

        selection[KEY] = VALUE

        EXPECTED_LENGTH = 1
        self.assertEqual(EXPECTED_LENGTH, len(selection))

        self.assertEqual(selection.selected_key, KEY)
        self.assertIs(selection.selected_value, VALUE)


class TestDeleteItem(SelectionTest):
    def setUp(self):
        super().setUp()

        self.ORIGINAL_LENGTH = len(self.selection)

    def test_selection_is_empty(self):
        selection = Selection()

        with self.assertRaises(KeyError):
            del selection[self.SELECTED_KEY]

    def test_key_is_not_in_selection(self):
        with self.assertRaises(KeyError):
            del self.selection[self.KEY_NOT_IN_SELECTION]

        self.assertEqual(self.ORIGINAL_LENGTH, len(self.selection))

    def test_delete_last_value_in_selection(self):
        items = {self.SELECTED_KEY: self.selected_value}

        selection = Selection(items)

        del selection[self.SELECTED_KEY]

        EXPECTED_LENGTH = 0

        self.assertEqual(EXPECTED_LENGTH, len(selection))

        with self.assertRaises(AttributeError):
            selection.selected_key

        with self.assertRaises(AttributeError):
            selection.selected_value

    def test_more_than_one_value_in_selection_and_we_delete_selected_value(self):
        del self.selection[self.SELECTED_KEY]

        EXPECTED_LENGTH = self.ORIGINAL_LENGTH - 1

        self.assertEqual(EXPECTED_LENGTH, len(self.selection))

        self.assertEqual(self.NON_SELECTED_KEY, self.selection.selected_key)
        self.assertIs(self.non_selected_value, self.selection.selected_value)

    def test_more_than_one_value_in_selection_and_we_delete_non_selected_value(self):
        del self.selection[self.NON_SELECTED_KEY]

        EXPECTED_LENGTH = self.ORIGINAL_LENGTH - 1

        self.assertEqual(EXPECTED_LENGTH, len(self.selection))

        self.assertEqual(self.SELECTED_KEY, self.selection.selected_key)
        self.assertIs(self.selected_value, self.selection.selected_value)
