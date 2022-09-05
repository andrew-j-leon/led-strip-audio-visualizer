import shutil
from pathlib import Path

from color_palette import ColorPalette, load, save
from pyfakefs import fake_filesystem_unittest
from selection import Selection


class TestSaveAndLoadColorPaletteSelection(fake_filesystem_unittest.TestCase):
    SELECTED_NAME = 'palette_1'
    NON_SELECTED_NAME = 'palette_2'

    def setUp(self):
        self.setUpPyfakefs()

        CURRENT_AMPLITUDE_RGBS = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
        SELECTED_COLOR_PALETTE = ColorPalette(CURRENT_AMPLITUDE_RGBS)

        NON_CURRENT_AMPLITUDE_RGBS = [(3, 3, 3), (4, 4, 4), (5, 5, 5)]
        NON_SELECTED_COLOR_PALETTE = ColorPalette(NON_CURRENT_AMPLITUDE_RGBS)

        PALETTES = {self.SELECTED_NAME: SELECTED_COLOR_PALETTE,
                    self.NON_SELECTED_NAME: NON_SELECTED_COLOR_PALETTE}

        self.color_palette_selection = Selection(PALETTES)

        self.existent_directory = Path('existent_directory')
        self.existent_directory.mkdir()

        self.non_existent_directory = Path('non_existent_directory')

        self.existent_file = self.existent_directory.joinpath('existent_file')
        self.existent_file.touch()

    def tearDown(self):
        shutil.rmtree(str(self.existent_directory), ignore_errors=True)

    def test_saving_in_directory_that_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            save(self.color_palette_selection, self.non_existent_directory)

    def test_saving_to_a_file(self):
        with self.assertRaises(NotADirectoryError):
            save(self.color_palette_selection, self.existent_file)

    def test_saving_in_directory_with_insufficient_permissions(self):
        self.existent_directory.chmod(0o100)

        with self.assertRaises(PermissionError):
            save(self.color_palette_selection, self.existent_directory)

    def test_loading_from_directory_that_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            load(self.non_existent_directory)

    def test_loading_from_a_file(self):
        with self.assertRaises(NotADirectoryError):
            load(self.existent_file)

    def test_loading_from_an_empty_directory(self):
        selection = load(self.existent_directory)

        EXPECTED_SELECTION = Selection()

        self.assertEqual(selection, EXPECTED_SELECTION)

    def test_save_and_load_empty_selection(self):
        selection_1 = Selection()

        save(selection_1, self.existent_directory)

        selection_2 = load(self.existent_directory)

        self.assertEqual(selection_1, selection_2)

    def test_save_and_load_selection_with_default_selected_palette(self):
        save(self.color_palette_selection, self.existent_directory)

        loaded_selection = load(self.existent_directory)

        self.assertEqual(self.color_palette_selection, loaded_selection)

    def test_save_and_laod_selection_with_non_default_selected_palette(self):
        self.color_palette_selection.selected_key = self.NON_SELECTED_NAME

        save(self.color_palette_selection, self.existent_directory)

        loaded_selection = load(self.existent_directory)

        self.assertEqual(self.color_palette_selection, loaded_selection)
