from typing import Union
from unittest import TestCase

from color_palette import ColorPalette
from controller.__tests__.fake_widget_gui import FakeWidgetGui
from libraries.widget import Button, Combo
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from selection.color_palette_selection_gui import ColorPaletteSelectionGui
from selection.color_palette_selection_gui import Element as ColorPaletteSelectionElement
from selection.color_palette_selection_gui import create_color_palette_gui_values
from selection.selection import Selection
from selection.selection_gui import Element as SelectionGuiElement
from selection.selection_gui import Event as SelectionGuiEvent
from util import rgb_to_hex


class ColorPaletteControllerTestCase(TestCase):
    CURRENT_COLOR_PALETTE_NAME = 'current_color_palette'
    CURRENT_COLOR_PALETTE_AMPLITUDE_RGBS = ([(10, 10, 10)] * 10 +
                                            [(20, 20, 20)] * 5 +
                                            [(30, 30, 30)] * 15)

    NON_CURRENT_COLOR_PALETTE_NAME = 'non_current_color_palette'
    NON_CURRENT_COLOR_PALETTE_AMPLITUDE_RGBS = []

    NON_EXISTENT_COLOR_PALETTE_NAME = 'non_existent_color_palette_name'

    def setUp(self):
        self.current_color_palette = ColorPalette(self.CURRENT_COLOR_PALETTE_AMPLITUDE_RGBS)
        self.non_current_color_palette = ColorPalette(self.NON_CURRENT_COLOR_PALETTE_AMPLITUDE_RGBS)

        self.color_palette_selection = Selection({self.CURRENT_COLOR_PALETTE_NAME: self.current_color_palette,
                                                  self.NON_CURRENT_COLOR_PALETTE_NAME: self.non_current_color_palette})

        self.widget_gui = FakeWidgetGui()

        self.color_palette_selection_gui = ColorPaletteSelectionGui(lambda: self.widget_gui)

    def clear_selection(self):
        NAMES = list(self.color_palette_selection.keys())

        for name in NAMES:
            del self.color_palette_selection[name]

    def clear_save_name_combo(self):
        EMPTY_SAVE_NAME_COMBO = Combo(SelectionGuiElement.SAVE_NAME_COMBO)
        self.widget_gui.update_widget(EMPTY_SAVE_NAME_COMBO)

    def check_widget_gui_matches_color_palette_selection(self, widget_gui: WidgetGui,
                                                         color_palette_selection: Selection[ColorPalette]):
        def get_widget_value(element: Union[SelectionGuiElement, ColorPaletteSelectionElement]):
            WIDGET = widget_gui.get_widget(element)
            return WIDGET.value

        # Check the save names combo
        SAVE_NAME_COMBO: Combo = widget_gui.get_widget(SelectionGuiElement.SAVE_NAME_COMBO)

        EXPECTED_NAMES = list(color_palette_selection.keys())
        self.assertEqual(EXPECTED_NAMES, SAVE_NAME_COMBO.values)

        self.assertEqual(color_palette_selection.selected_key, SAVE_NAME_COMBO.value)

        # Check ColorPalette inputs
        SELECTED_COLOR_PALETTE = color_palette_selection.selected_value

        NUMBER_OF_COLORS = 5
        COLOR_PALETTE_GUI_VALUES = create_color_palette_gui_values(SELECTED_COLOR_PALETTE.amplitude_rgbs,
                                                                   NUMBER_OF_COLORS)

        KEYS = [(ColorPaletteSelectionElement.DECIBEL_INPUT_0, ColorPaletteSelectionElement.COLOR_PICKER_0),
                (ColorPaletteSelectionElement.DECIBEL_INPUT_1, ColorPaletteSelectionElement.COLOR_PICKER_1),
                (ColorPaletteSelectionElement.DECIBEL_INPUT_2, ColorPaletteSelectionElement.COLOR_PICKER_2),
                (ColorPaletteSelectionElement.DECIBEL_INPUT_3, ColorPaletteSelectionElement.COLOR_PICKER_3),
                (ColorPaletteSelectionElement.DECIBEL_INPUT_4, ColorPaletteSelectionElement.COLOR_PICKER_4)]

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
        self.assertFalse(self.widget_gui.open)

        self.color_palette_selection_gui.display(self.color_palette_selection)

        self.check_widget_gui_matches_color_palette_selection(self.widget_gui, self.color_palette_selection)

        self.assertTrue(self.widget_gui.open)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)


class DisplayedSettingsSelectionGuiTestCase(ColorPaletteControllerTestCase):
    def setUp(self):
        super().setUp()

        self.color_palette_selection_gui.display(self.color_palette_selection)
        self.widget_gui.number_of_read_event_and_update_gui_calls = 0


class TestClose(DisplayedSettingsSelectionGuiTestCase):
    def test_close_displayed_gui(self):
        self.color_palette_selection_gui.close()
        self.assertTrue(not self.widget_gui.open)

    def test_close_non_displayed_gui(self):
        SETTINGS_SELECTION_GUI = ColorPaletteSelectionGui(lambda: self.widget_gui)
        SETTINGS_SELECTION_GUI.close()
        self.assertTrue(not self.widget_gui.open)


class TestGetCurentSaveName(DisplayedSettingsSelectionGuiTestCase):
    def test_non_empty_save_name_combo(self):
        CURRENT_SAVE_NAME = self.color_palette_selection_gui.get_current_save_name()
        EXPECTED = self.color_palette_selection.selected_key
        self.assertEqual(CURRENT_SAVE_NAME, EXPECTED)

    def test_empty_save_name_combo(self):
        self.clear_save_name_combo()

        CURRENT_SAVE_NAME = self.color_palette_selection_gui.get_current_save_name()
        EXPECTED = ''
        self.assertEqual(CURRENT_SAVE_NAME, EXPECTED)


class TestGetSelection(DisplayedSettingsSelectionGuiTestCase):
    def test_get_selection(self):
        SELECTION = self.color_palette_selection_gui.get_selection()
        EXPECTED = Selection({self.CURRENT_COLOR_PALETTE_NAME: self.current_color_palette})

        self.assertEqual(SELECTION, EXPECTED)

    def test_get_selection_with_no_name(self):
        self.clear_save_name_combo()

        SELECTION = self.color_palette_selection_gui.get_selection()
        EXPECTED = Selection({'': self.current_color_palette})

        self.assertEqual(SELECTION, EXPECTED)


class TestUpdateWidgets(DisplayedSettingsSelectionGuiTestCase):
    def test_update_widgets(self):
        self.color_palette_selection.selected_key = self.NON_CURRENT_COLOR_PALETTE_NAME

        self.color_palette_selection_gui.update_widgets(self.color_palette_selection)

        self.check_widget_gui_matches_color_palette_selection(self.widget_gui, self.color_palette_selection)

        self.assertTrue(self.widget_gui.open)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)


class TestReadEventAndUpdateGui(DisplayedSettingsSelectionGuiTestCase):
    def test_read_an_event(self):
        EVENT = 'some event'

        self.widget_gui.event = EVENT

        event = self.color_palette_selection_gui.read_event_and_update_gui(self.color_palette_selection)

        self.assertEqual(event, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_select_current_save(self):
        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.color_palette_selection_gui.read_event_and_update_gui(self.color_palette_selection)

        self.assertEqual(SelectionGuiEvent.SELECT_CURRENT_SAVE, EVENT)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_select_non_current_save(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(SelectionGuiElement.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.value = self.NON_CURRENT_COLOR_PALETTE_NAME

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.color_palette_selection_gui.read_event_and_update_gui(self.color_palette_selection)

        self.assertEqual(SelectionGuiEvent.SELECT_NON_CURRENT_SAVE, EVENT)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_clear_save_name_event(self):
        self.clear_save_name_combo()

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.color_palette_selection_gui.read_event_and_update_gui(self.color_palette_selection)

        self.assertEqual(SelectionGuiEvent.CLEAR_SAVE_NAME, EVENT)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.DELETE_BUTTON)

        self.assertFalse(SAVE_BUTTON.enabled)
        self.assertFalse(DELETE_BUTTON.enabled)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_new_save_name(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(SelectionGuiElement.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.add_value(self.NON_EXISTENT_COLOR_PALETTE_NAME)
        SAVE_NAME_COMBO.value = self.NON_EXISTENT_COLOR_PALETTE_NAME

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.color_palette_selection_gui.read_event_and_update_gui(self.color_palette_selection)
        self.assertEqual(SelectionGuiEvent.ENTER_NEW_SAVE_NAME, EVENT)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertFalse(DELETE_BUTTON.enabled)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_close_window(self):
        self.widget_gui.event = WidgetGuiEvent.CLOSE_WINDOW

        EVENT = self.color_palette_selection_gui.read_event_and_update_gui(self.color_palette_selection)
        self.assertEqual(WidgetGuiEvent.CLOSE_WINDOW, EVENT)

        self.assertFalse(self.widget_gui.open)


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
