import unittest

from color_palette import ColorPalette, ColorPaletteSelection


class ColorPaletteTestCase(unittest.TestCase):
    SELECTED_NAME = 'palette_1'
    NON_SELECTED_NAME = 'palette_2'

    NAME_NOT_IN_SELECTION = 'non_palette_name'

    def setUp(self):
        CURRENT_AMPLITUDE_RGBS = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
        self.selected_color_palette = ColorPalette(CURRENT_AMPLITUDE_RGBS)

        NON_CURRENT_AMPLITUDE_RGBS = [(3, 3, 3), (4, 4, 4), (5, 5, 5)]
        self.non_selected_color_palette = ColorPalette(NON_CURRENT_AMPLITUDE_RGBS)

        self.palettes = {self.SELECTED_NAME: self.selected_color_palette,
                         self.NON_SELECTED_NAME: self.non_selected_color_palette}

        self.color_palette_selection = ColorPaletteSelection(self.palettes)


class ColorPaletteSelectionTest(ColorPaletteTestCase):
    def test_constructor(self):
        self.assertEqual(self.color_palette_selection.selected_name, self.SELECTED_NAME)
        self.assertIs(self.color_palette_selection.selected_palette, self.selected_color_palette)

    def test_length(self):
        EXPECTED_LENGTH = len(self.palettes)

        self.assertEqual(len(self.color_palette_selection), EXPECTED_LENGTH)

    def test_contains(self):
        self.assertTrue(self.SELECTED_NAME in self.color_palette_selection)
        self.assertTrue(self.NON_SELECTED_NAME in self.color_palette_selection)

        self.assertTrue(self.NAME_NOT_IN_SELECTION not in self.color_palette_selection)

    def test_iter(self):
        EXPECTED_NAMES = {self.SELECTED_NAME, self.NON_SELECTED_NAME}
        ACTUAL_NAMES = {name for name in self.color_palette_selection}

        self.assertEqual(EXPECTED_NAMES, ACTUAL_NAMES)


class TestSelectedNameAndPalette(ColorPaletteTestCase):
    def test_get_selected_name_with_no_palettes_in_selection(self):
        selection = ColorPaletteSelection()

        with self.assertRaises(AttributeError):
            selection.selected_name

    def test_get_selected_palette_with_no_palettes_in_selection(self):
        selection = ColorPaletteSelection()

        with self.assertRaises(AttributeError):
            selection.selected_palette

    def test_set_to_selected_name(self):
        self.color_palette_selection.selected_name = self.SELECTED_NAME

        self.assertEqual(self.color_palette_selection.selected_name, self.SELECTED_NAME)
        self.assertIs(self.color_palette_selection.selected_palette, self.selected_color_palette)

    def test_set_to_non_selected_name(self):
        self.color_palette_selection.selected_name = self.NON_SELECTED_NAME

        self.assertEqual(self.color_palette_selection.selected_name, self.NON_SELECTED_NAME)
        self.assertIs(self.color_palette_selection.selected_palette, self.non_selected_color_palette)

    def test_set_to_name_that_is_not_in_selection(self):
        with self.assertRaises(ValueError):
            self.color_palette_selection.selected_name = self.NAME_NOT_IN_SELECTION

        self.assertEqual(self.color_palette_selection.selected_name, self.SELECTED_NAME)
        self.assertIs(self.color_palette_selection.selected_palette, self.selected_color_palette)


class TestNamesPalettesAndItems(ColorPaletteTestCase):
    def test_names(self):
        names = set(self.color_palette_selection.names())

        EXPECTED_NAMES = {self.SELECTED_NAME, self.NON_SELECTED_NAME}

        self.assertEqual(names, EXPECTED_NAMES)

    def test_palettes(self):
        palettes = list(self.color_palette_selection.palettes())

        EXPECTED_PALETTES = [self.selected_color_palette, self.non_selected_color_palette]

        self.assertEqual(palettes, EXPECTED_PALETTES)

    def test_values(self):
        values = [(name, palette) for name, palette in self.color_palette_selection.items()]

        EXPECTED_VALUES = [(self.SELECTED_NAME, self.selected_color_palette),
                           (self.NON_SELECTED_NAME, self.non_selected_color_palette)]

        self.assertEqual(values, EXPECTED_VALUES)


class TestEqual(ColorPaletteTestCase):
    def test_empty_selections_are_equal(self):
        selection_1 = ColorPaletteSelection()
        selection_2 = ColorPaletteSelection()

        self.assertEqual(selection_1, selection_2)

    def test_same_names_and_selected_name_but_different_selected_palette(self):
        PALETTES = {self.SELECTED_NAME: self.non_selected_color_palette,
                    self.NON_SELECTED_NAME: self.selected_color_palette}

        selection = ColorPaletteSelection(PALETTES)
        selection.selected_name = self.SELECTED_NAME

        self.assertNotEqual(selection, self.color_palette_selection)

    def test_same_names_and_selected_name_and_selected_palette_but_different_non_selected_palette(self):
        SELECTED_PALETTE = ColorPalette([(0, 0, 0)])
        NON_SELECTED_PALETTE_1 = ColorPalette([(1, 1, 1)])
        NON_SELECTED_PALETTE_2 = ColorPalette([(2, 2, 2)])

        PALETTES_1 = {'selected_name': SELECTED_PALETTE,
                      'non_selected_name': NON_SELECTED_PALETTE_1}

        PALETTES_2 = {'selected_name': SELECTED_PALETTE,
                      'non_selected_name': NON_SELECTED_PALETTE_2}

        SELECTION_1 = ColorPaletteSelection(PALETTES_1)
        SELECTION_2 = ColorPaletteSelection(PALETTES_2)

        self.assertNotEqual(SELECTION_1, SELECTION_2)

    def test_non_empty_selections_are_equal(self):
        palettes = {self.SELECTED_NAME: ColorPalette(self.selected_color_palette.amplitude_rgbs),
                    self.NON_SELECTED_NAME: ColorPalette(self.non_selected_color_palette.amplitude_rgbs)}

        palette_selection = ColorPaletteSelection(palettes)

        self.assertEqual(palette_selection, self.color_palette_selection)

    def test_swapped_names(self):
        palettes = {self.NON_SELECTED_NAME: ColorPalette(self.selected_color_palette.amplitude_rgbs),
                    self.SELECTED_NAME: ColorPalette(self.non_selected_color_palette.amplitude_rgbs)}

        palette_selection = ColorPaletteSelection(palettes)

        self.assertNotEqual(palette_selection, self.color_palette_selection)

    def test_almost_equal_but_with_one_palette_different(self):
        palettes = {self.SELECTED_NAME: ColorPalette(self.selected_color_palette.amplitude_rgbs),
                    self.NON_SELECTED_NAME: ColorPalette(self.non_selected_color_palette.amplitude_rgbs),
                    self.NAME_NOT_IN_SELECTION: ColorPalette()}

        palette_selection = ColorPaletteSelection(palettes)

        self.assertNotEqual(palette_selection, self.color_palette_selection)

    def test_not_a_palette(self):
        self.assertNotEqual(self.color_palette_selection, None)


class TestGetItem(ColorPaletteSelectionTest):
    def test_get_selected_palette(self):
        palette = self.color_palette_selection[self.SELECTED_NAME]

        self.assertIs(palette, self.selected_color_palette)

    def test_get_non_selected_palette(self):
        palette = self.color_palette_selection[self.NON_SELECTED_NAME]

        self.assertIs(palette, self.non_selected_color_palette)

    def test_name_is_not_in_selection(self):
        with self.assertRaises(KeyError):
            self.color_palette_selection[self.NAME_NOT_IN_SELECTION]


class TestSetItem(ColorPaletteSelectionTest):
    def setUp(self):
        super().setUp()

        self.ORIGINAL_LENGTH = len(self.color_palette_selection)

    def test_add_new_palette(self):
        NEW_PALETTE = ColorPalette()
        self.color_palette_selection[self.NAME_NOT_IN_SELECTION] = NEW_PALETTE

        EXPECTED_LENGTH = self.ORIGINAL_LENGTH + 1

        self.assertEqual(EXPECTED_LENGTH, len(self.color_palette_selection))
        self.assertIs(NEW_PALETTE, self.color_palette_selection[self.NAME_NOT_IN_SELECTION])

    def test_overwrite_selected_palette(self):
        NEW_PALETTE = ColorPalette()
        self.color_palette_selection[self.SELECTED_NAME] = NEW_PALETTE

        self.assertEqual(self.ORIGINAL_LENGTH, len(self.color_palette_selection))
        self.assertIs(NEW_PALETTE, self.color_palette_selection[self.SELECTED_NAME])
        self.assertIs(NEW_PALETTE, self.color_palette_selection.selected_palette)

    def test_overwrite_non_selected_palette(self):
        NEW_PALETTE = ColorPalette()
        self.color_palette_selection[self.NON_SELECTED_NAME] = NEW_PALETTE

        self.assertEqual(self.ORIGINAL_LENGTH, len(self.color_palette_selection))
        self.assertIs(NEW_PALETTE, self.color_palette_selection[self.NON_SELECTED_NAME])

    def test_set_palette_on_empty_selection(self):
        palette_selection = ColorPaletteSelection()

        NAME = 'palette_name'
        PALETTE = ColorPalette()

        palette_selection[NAME] = PALETTE

        EXPECTED_LENGTH = 1
        self.assertEqual(EXPECTED_LENGTH, len(palette_selection))

        self.assertEqual(palette_selection.selected_name, NAME)
        self.assertIs(palette_selection.selected_palette, PALETTE)

    def test_set_non_palette(self):
        with self.assertRaises(TypeError):
            self.color_palette_selection[self.SELECTED_NAME] = None

        self.assertEqual(self.ORIGINAL_LENGTH, len(self.color_palette_selection))

        self.assertEqual(self.SELECTED_NAME, self.color_palette_selection.selected_name)
        self.assertIs(self.selected_color_palette, self.color_palette_selection.selected_palette)


class TestDeleteItem(ColorPaletteSelectionTest):
    def setUp(self):
        super().setUp()

        self.ORIGINAL_LENGTH = len(self.color_palette_selection)

    def test_selection_is_empty(self):
        selection = ColorPaletteSelection()

        with self.assertRaises(KeyError):
            del selection[self.SELECTED_NAME]

    def test_name_is_not_in_selection(self):
        with self.assertRaises(KeyError):
            del self.color_palette_selection[self.NAME_NOT_IN_SELECTION]

        self.assertEqual(self.ORIGINAL_LENGTH, len(self.color_palette_selection))

    def test_delete_last_palette_in_selection(self):
        palettes = {self.SELECTED_NAME: self.selected_color_palette}

        selection = ColorPaletteSelection(palettes)

        del selection[self.SELECTED_NAME]

        EXPECTED_LENGTH = 0

        self.assertEqual(EXPECTED_LENGTH, len(selection))

        with self.assertRaises(AttributeError):
            selection.selected_name

        with self.assertRaises(AttributeError):
            selection.selected_palette

    def test_more_than_one_palette_in_selection_and_we_delete_selected_palette(self):
        del self.color_palette_selection[self.SELECTED_NAME]

        EXPECTED_LENGTH = self.ORIGINAL_LENGTH - 1

        self.assertEqual(EXPECTED_LENGTH, len(self.color_palette_selection))

        self.assertEqual(self.NON_SELECTED_NAME, self.color_palette_selection.selected_name)
        self.assertIs(self.non_selected_color_palette, self.color_palette_selection.selected_palette)

    def test_more_than_one_palette_in_selection_and_we_delete_non_selected_palette(self):
        del self.color_palette_selection[self.NON_SELECTED_NAME]

        EXPECTED_LENGTH = self.ORIGINAL_LENGTH - 1

        self.assertEqual(EXPECTED_LENGTH, len(self.color_palette_selection))

        self.assertEqual(self.SELECTED_NAME, self.color_palette_selection.selected_name)
        self.assertIs(self.selected_color_palette, self.color_palette_selection.selected_palette)
