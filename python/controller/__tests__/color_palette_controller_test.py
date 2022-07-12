import shutil
from pathlib import Path
from typing import Any, Hashable
from unittest import TestCase

import pyfakefs.fake_filesystem_unittest as fake_filesystem_unittest
from color_palette import ColorPalette, ColorPaletteSelection
from color_palette import save as save_color_palette_selection
from controller.__tests__.fake_widget_gui import FakeWidgetGui
from controller.color_palette_controller import ColorPaletteController, Element, Event, create_color_palette_gui_values
from libraries.widget import Button, Combo
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from util import rgb_to_hex


class SaveColorPaletteSelection:
    def __init__(self, save_directory: Path):
        self.number_of_calls = 0
        self.__save_directory = save_directory

    def __call__(self, color_palette_selection: ColorPaletteSelection):
        self.number_of_calls += 1
        save_color_palette_selection(color_palette_selection, self.__save_directory)


class TestCreateColorPaletteGuiValues(TestCase):
    RGB_0 = (10, 10, 10)
    RGB_0_COUNT = 10

    RGB_1 = (10, 6, 25)
    RGB_1_COUNT = 5

    RGB_2 = (5, 7, 8)
    RGB_2_COUNT = 20

    AMPLITUDE_RGBS = ([RGB_0] * RGB_0_COUNT
                      + [RGB_1] * RGB_1_COUNT
                      + [RGB_2] * RGB_2_COUNT)

    def test_no_amplitude_rgbs(self):
        AMPLITUDE_RGBS = []
        NUMBER_OF_COLORS = 5

        GUI_VALUES = create_color_palette_gui_values(AMPLITUDE_RGBS, NUMBER_OF_COLORS)
        EXPECTED_GUI_VALUES = [(0, '#000000')] * NUMBER_OF_COLORS

        self.assertEqual(GUI_VALUES, EXPECTED_GUI_VALUES)

    def test_zero_number_of_colors(self):
        AMPLITUDE_RGBS = []
        NUMBER_OF_COLORS = 0

        GUI_VALUES = create_color_palette_gui_values(AMPLITUDE_RGBS, NUMBER_OF_COLORS)
        EXPECTED_GUI_VALUES = []

        self.assertEqual(GUI_VALUES, EXPECTED_GUI_VALUES)

    def test_more_colors_in_amplitude_rgbs_than_number_of_colors(self):
        EXPECTED_GUI_VALUES = [(self.RGB_0_COUNT, rgb_to_hex(*self.RGB_0)),
                               (self.RGB_1_COUNT, rgb_to_hex(*self.RGB_1))]

        NUMBER_OF_COLORS = len(EXPECTED_GUI_VALUES)
        NUMBER_OF_COLORS_IN_AMPLITUDE_RGBS = len(set(self.AMPLITUDE_RGBS))

        self.assertTrue(NUMBER_OF_COLORS < NUMBER_OF_COLORS_IN_AMPLITUDE_RGBS)

        GUI_VALUES = create_color_palette_gui_values(self.AMPLITUDE_RGBS, NUMBER_OF_COLORS)

        self.assertEqual(GUI_VALUES, EXPECTED_GUI_VALUES)

    def test_less_colors_in_amplitude_rgbs_than_number_of_colors(self):
        ZERO_COUNT = 0
        BLACK_HEX = '#000000'
        EXPECTED_GUI_VALUES = [(self.RGB_0_COUNT, rgb_to_hex(*self.RGB_0)),
                               (self.RGB_1_COUNT, rgb_to_hex(*self.RGB_1)),
                               (self.RGB_2_COUNT, rgb_to_hex(*self.RGB_2)),
                               (ZERO_COUNT, BLACK_HEX),
                               (ZERO_COUNT, BLACK_HEX)]

        NUMBER_OF_COLORS = len(EXPECTED_GUI_VALUES)
        NUMBER_OF_COLORS_IN_AMPLITUDE_RGBS = len(set(self.AMPLITUDE_RGBS))

        self.assertTrue(NUMBER_OF_COLORS > NUMBER_OF_COLORS_IN_AMPLITUDE_RGBS)

        GUI_VALUES = create_color_palette_gui_values(self.AMPLITUDE_RGBS, NUMBER_OF_COLORS)

        self.assertEqual(GUI_VALUES, EXPECTED_GUI_VALUES)

    def test_equal_number_of_colors(self):
        EXPECTED_GUI_VALUES = [(self.RGB_0_COUNT, rgb_to_hex(*self.RGB_0)),
                               (self.RGB_1_COUNT, rgb_to_hex(*self.RGB_1)),
                               (self.RGB_2_COUNT, rgb_to_hex(*self.RGB_2))]

        NUMBER_OF_COLORS = len(EXPECTED_GUI_VALUES)
        NUMBER_OF_COLORS_IN_AMPLITUDE_RGBS = len(set(self.AMPLITUDE_RGBS))

        self.assertEqual(NUMBER_OF_COLORS, NUMBER_OF_COLORS_IN_AMPLITUDE_RGBS)

        GUI_VALUES = create_color_palette_gui_values(self.AMPLITUDE_RGBS, NUMBER_OF_COLORS)

        self.assertEqual(GUI_VALUES, EXPECTED_GUI_VALUES)


class ColorPaletteControllerTestCase(fake_filesystem_unittest.TestCase):
    CURRENT_COLOR_PALETTE_NAME = 'current_color_palette'
    CURRENT_COLOR_PALETTE_AMPLITUDE_RGBS = ([(10, 10, 10)] * 10 +
                                            [(20, 20, 20)] * 5 +
                                            [(30, 30, 30)] * 15)

    NON_CURRENT_COLOR_PALETTE_NAME = 'non_current_color_palette'
    NON_CURRENT_COLOR_PALETTE_AMPLITUDE_RGBS = []

    NON_EXISTENT_COLOR_PALETTE_NAME = 'non_existent_color_palette_name'

    def setUp(self):
        self.setUpPyfakefs()

        self.current_color_palette = ColorPalette(self.CURRENT_COLOR_PALETTE_AMPLITUDE_RGBS)
        self.non_current_color_palette = ColorPalette(self.NON_CURRENT_COLOR_PALETTE_AMPLITUDE_RGBS)

        self.color_palette_selection = ColorPaletteSelection({self.CURRENT_COLOR_PALETTE_NAME: self.current_color_palette,
                                                              self.NON_CURRENT_COLOR_PALETTE_NAME: self.non_current_color_palette})

        self.widget_gui = FakeWidgetGui()

        def create_gui():
            return self.widget_gui

        self.save_directory = Path('save_directory')
        self.save_directory.mkdir()

        self.save_color_palette_selection = SaveColorPaletteSelection(self.save_directory)

        self.color_palette_controller = ColorPaletteController(create_gui, self.save_color_palette_selection,
                                                               self.color_palette_selection)

    def tearDown(self):
        shutil.rmtree(str(self.save_directory), ignore_errors=True)

    def clear_color_palette_selection(self):
        NAMES = list(self.color_palette_selection.names())

        for name in NAMES:
            del self.color_palette_selection[name]

    def check_widget_gui_matches_color_palette_selection(self, widget_gui: WidgetGui,
                                                         color_palette_selection: ColorPaletteSelection):
        def get_widget_value(element: Element):
            WIDGET = widget_gui.get_widget(element)
            return WIDGET.value

        # Check the combo
        NAME_COMBO: Combo = widget_gui.get_widget(Element.NAME_COMBO)

        EXPECTED_NAMES = list(color_palette_selection.names())
        self.assertEqual(EXPECTED_NAMES, NAME_COMBO.values)

        self.assertEqual(color_palette_selection.selected_name, NAME_COMBO.value)

        # Check the colors of the selected color palette
        SELECTED_COLOR_PALETTE = color_palette_selection.selected_palette

        NUMBER_OF_COLORS = 5
        COLOR_PALETTE_GUI_VALUES = create_color_palette_gui_values(SELECTED_COLOR_PALETTE.amplitude_rgbs,
                                                                   NUMBER_OF_COLORS)

        KEYS = [(Element.DECIBEL_INPUT_0, Element.COLOR_PICKER_0),
                (Element.DECIBEL_INPUT_1, Element.COLOR_PICKER_1),
                (Element.DECIBEL_INPUT_2, Element.COLOR_PICKER_2),
                (Element.DECIBEL_INPUT_3, Element.COLOR_PICKER_3),
                (Element.DECIBEL_INPUT_4, Element.COLOR_PICKER_4)]

        for i in range(len(KEYS)):
            with self.subTest(color_row=i):
                expected_decibel_count, expected_color = COLOR_PALETTE_GUI_VALUES[i]
                decibel_input_key, color_picker_key = KEYS[i]

                gui_decibel_count = get_widget_value(decibel_input_key)
                gui_color = get_widget_value(color_picker_key)

                self.assertEqual(expected_decibel_count, gui_decibel_count)
                self.assertEqual(expected_color, gui_color)


class TestDisplay(ColorPaletteControllerTestCase):
    def test_display(self):
        self.color_palette_controller.display()

        self.check_widget_gui_matches_color_palette_selection(self.widget_gui, self.color_palette_selection)

        self.assertTrue(self.widget_gui.open)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)


class DisplayedColorPaletteControllerTestCase(ColorPaletteControllerTestCase):
    def setUp(self):
        super().setUp()

        self.color_palette_controller.display()
        self.widget_gui.number_of_read_event_and_update_gui_calls = 0


class TestClose(DisplayedColorPaletteControllerTestCase):

    def test_close(self):
        self.color_palette_controller.close()

        self.assertTrue(not self.widget_gui.open)


class TestReadEventAndUpdateGui(DisplayedColorPaletteControllerTestCase):

    def test_read_an_event(self):
        EXPECTED_EVENT = 'some event'

        self.widget_gui.event = EXPECTED_EVENT

        EVENT = self.color_palette_controller.read_event_and_update_gui()

        self.assertEqual(EVENT, EXPECTED_EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_select_current_color_palette_name_event(self):
        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.color_palette_controller.read_event_and_update_gui()

        self.assertEqual(Event.SELECT_CURRENT_COLOR_PALETTE_NAME, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_select_non_current_color_palette_name_event(self):
        NAME_COMBO: Combo = self.widget_gui.get_widget(Element.NAME_COMBO)
        NAME_COMBO.value = self.NON_CURRENT_COLOR_PALETTE_NAME

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.color_palette_controller.read_event_and_update_gui()

        self.assertEqual(Event.SELECT_NON_CURRENT_COLOR_PALETTE_NAME, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_delete_color_palette_name_event(self):
        self.clear_color_palette_selection()

        NEW_NAME_COMBO = Combo(Element.NAME_COMBO)
        self.widget_gui.update_widget(NEW_NAME_COMBO)

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.color_palette_controller.read_event_and_update_gui()

        self.assertEqual(Event.DELETE_COLOR_PALETTE_NAME, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_new_color_palette_name_event(self):
        NAME_COMBO: Combo = self.widget_gui.get_widget(Element.NAME_COMBO)
        NAME_COMBO.add_value(self.NON_EXISTENT_COLOR_PALETTE_NAME)
        NAME_COMBO.value = self.NON_EXISTENT_COLOR_PALETTE_NAME

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.color_palette_controller.read_event_and_update_gui()

        self.assertEqual(Event.ENTER_NEW_COLOR_PALETTE_NAME, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)


class TestHandleEvent(DisplayedColorPaletteControllerTestCase):
    def test_save_new_color_palette(self):
        NAME_COMBO: Combo = self.widget_gui.get_widget(Element.NAME_COMBO)
        NAME_COMBO.add_value(self.NON_EXISTENT_COLOR_PALETTE_NAME)
        NAME_COMBO.value = self.NON_EXISTENT_COLOR_PALETTE_NAME

        self.color_palette_controller.handle_event(Element.SAVE_BUTTON)

        EXPECTED_NEW_COLOR_PALETTE = ColorPalette(self.current_color_palette.amplitude_rgbs)

        EXPECTED_COLOR_PALETTES = {self.CURRENT_COLOR_PALETTE_NAME: self.current_color_palette,
                                   self.NON_CURRENT_COLOR_PALETTE_NAME: self.non_current_color_palette,
                                   self.NON_EXISTENT_COLOR_PALETTE_NAME: EXPECTED_NEW_COLOR_PALETTE}
        EXPECTED_COLOR_PALETTE_SELECTION = ColorPaletteSelection(EXPECTED_COLOR_PALETTES)
        EXPECTED_COLOR_PALETTE_SELECTION.selected_name = self.NON_EXISTENT_COLOR_PALETTE_NAME

        self.assertEqual(self.color_palette_selection, EXPECTED_COLOR_PALETTE_SELECTION)

        EXPECTED_NUMBER_OF_SAVES = 1
        self.assertEqual(self.save_color_palette_selection.number_of_calls, EXPECTED_NUMBER_OF_SAVES)

    def test_overwrite_saved_color_palette(self):
        def set_widget_value(widget_key: Hashable, value: Any):
            WIDGET = self.widget_gui.get_widget(widget_key)
            WIDGET.value = value

        RGB_0 = (50, 20, 10)
        HEX_0 = rgb_to_hex(*RGB_0)
        DECIBEL_COUNT_0 = 10
        RGB_1 = (0, 100, 150)
        HEX_1 = rgb_to_hex(*RGB_1)
        DECIBEL_COUNT_1 = 5
        RGB_2 = (200, 100, 60)
        HEX_2 = rgb_to_hex(*RGB_2)
        DECIBEL_COUNT_2 = 15
        RGB_3 = (1, 2, 3)
        HEX_3 = rgb_to_hex(*RGB_3)
        DECIBEL_COUNT_3 = 20
        RGB_4 = (80, 90, 100)
        HEX_4 = rgb_to_hex(*RGB_4)
        DECIBEL_COUNT_4 = 0

        set_widget_value(Element.DECIBEL_INPUT_0, DECIBEL_COUNT_0)
        set_widget_value(Element.COLOR_PICKER_0, HEX_0)
        set_widget_value(Element.DECIBEL_INPUT_1, DECIBEL_COUNT_1)
        set_widget_value(Element.COLOR_PICKER_1, HEX_1)
        set_widget_value(Element.DECIBEL_INPUT_2, DECIBEL_COUNT_2)
        set_widget_value(Element.COLOR_PICKER_2, HEX_2)
        set_widget_value(Element.DECIBEL_INPUT_3, DECIBEL_COUNT_3)
        set_widget_value(Element.COLOR_PICKER_3, HEX_3)
        set_widget_value(Element.DECIBEL_INPUT_4, DECIBEL_COUNT_4)
        set_widget_value(Element.COLOR_PICKER_4, HEX_4)

        self.color_palette_controller.handle_event(Element.SAVE_BUTTON)

        AMPLITUDE_RGBS = ([RGB_0] * DECIBEL_COUNT_0
                          + [RGB_1] * DECIBEL_COUNT_1
                          + [RGB_2] * DECIBEL_COUNT_2
                          + [RGB_3] * DECIBEL_COUNT_3
                          + [RGB_4] * DECIBEL_COUNT_4)
        EXPECTED_CURRENT_COLOR_PALETTE = ColorPalette(AMPLITUDE_RGBS)

        EXPECTED_COLOR_PALETTES = {self.CURRENT_COLOR_PALETTE_NAME: EXPECTED_CURRENT_COLOR_PALETTE,
                                   self.NON_CURRENT_COLOR_PALETTE_NAME: self.non_current_color_palette}
        EXPECTED_COLOR_PALETTE_SELECTION = ColorPaletteSelection(EXPECTED_COLOR_PALETTES)
        EXPECTED_COLOR_PALETTE_SELECTION.selected_name = self.CURRENT_COLOR_PALETTE_NAME

        self.assertEqual(self.color_palette_selection, EXPECTED_COLOR_PALETTE_SELECTION)

        EXPECTED_NUMBER_OF_SAVES = 1
        self.assertEqual(self.save_color_palette_selection.number_of_calls, EXPECTED_NUMBER_OF_SAVES)

    def test_delete_non_existent_color_palette_name(self):
        NAME_COMBO: Combo = self.widget_gui.get_widget(Element.NAME_COMBO)
        NAME_COMBO.add_value(self.NON_EXISTENT_COLOR_PALETTE_NAME)
        NAME_COMBO.value = self.NON_EXISTENT_COLOR_PALETTE_NAME

        with self.assertRaises(ValueError):
            self.color_palette_controller.handle_event(Element.DELETE_BUTTON)

        EXPECTED_COLOR_PALETTES = {self.CURRENT_COLOR_PALETTE_NAME: self.current_color_palette,
                                   self.NON_CURRENT_COLOR_PALETTE_NAME: self.non_current_color_palette}
        EXPECTED_COLOR_PALETTE_SELECTION = ColorPaletteSelection(EXPECTED_COLOR_PALETTES)
        EXPECTED_COLOR_PALETTE_SELECTION.selected_name = self.CURRENT_COLOR_PALETTE_NAME

        self.assertEqual(self.color_palette_selection, EXPECTED_COLOR_PALETTE_SELECTION)

    def test_delete_existent_color_palette_name(self):
        NAME_COMBO: Combo = self.widget_gui.get_widget(Element.NAME_COMBO)
        NAME_COMBO.value = self.CURRENT_COLOR_PALETTE_NAME

        self.color_palette_controller.handle_event(Element.DELETE_BUTTON)

        EXPECTED_COLOR_PALETTES = {self.NON_CURRENT_COLOR_PALETTE_NAME: self.non_current_color_palette}
        EXPECTED_COLOR_PALETTE_SELECTION = ColorPaletteSelection(EXPECTED_COLOR_PALETTES)

        self.assertEqual(self.color_palette_selection, EXPECTED_COLOR_PALETTE_SELECTION)

    def test_close_window(self):
        self.color_palette_controller.handle_event(WidgetGuiEvent.CLOSE_WINDOW)

        self.assertFalse(self.widget_gui.open)

    def test_select_current_color_palette_name(self):
        NAME_COMBO: Combo = self.widget_gui.get_widget(Element.NAME_COMBO)
        NAME_COMBO.value = self.CURRENT_COLOR_PALETTE_NAME

        self.color_palette_controller.handle_event(Event.SELECT_CURRENT_COLOR_PALETTE_NAME)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)

        self.color_palette_selection.selected_name = self.CURRENT_COLOR_PALETTE_NAME
        self.check_widget_gui_matches_color_palette_selection(self.widget_gui, self.color_palette_selection)

    def test_select_non_current_color_palette_name(self):
        NAME_COMBO: Combo = self.widget_gui.get_widget(Element.NAME_COMBO)
        NAME_COMBO.value = self.NON_CURRENT_COLOR_PALETTE_NAME

        self.color_palette_controller.handle_event(Event.SELECT_NON_CURRENT_COLOR_PALETTE_NAME)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)

        self.color_palette_selection.selected_name = self.NON_CURRENT_COLOR_PALETTE_NAME
        self.check_widget_gui_matches_color_palette_selection(self.widget_gui, self.color_palette_selection)

    def test_select_non_current_color_palette_name_when_combo_name_not_in_color_palette_selection(self):
        NAME_COMBO: Combo = self.widget_gui.get_widget(Element.NAME_COMBO)
        NAME_COMBO.add_value(self.NON_EXISTENT_COLOR_PALETTE_NAME)
        NAME_COMBO.value = self.NON_EXISTENT_COLOR_PALETTE_NAME

        with self.assertRaises(ValueError):
            self.color_palette_controller.handle_event(Event.SELECT_NON_CURRENT_COLOR_PALETTE_NAME)

    def test_delete_color_palette_name(self):
        self.color_palette_controller.handle_event(Event.DELETE_COLOR_PALETTE_NAME)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertFalse(SAVE_BUTTON.enabled)
        self.assertFalse(DELETE_BUTTON.enabled)

    def test_enter_new_color_palette_name(self):
        self.color_palette_controller.handle_event(Event.ENTER_NEW_COLOR_PALETTE_NAME)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertFalse(DELETE_BUTTON.enabled)

    def test_unrecognized_event(self):
        EVENT = 'unrecognized event'

        with self.assertRaises(ValueError):
            self.color_palette_controller.handle_event(EVENT)
