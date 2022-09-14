from typing import Union
from unittest import TestCase

from controller.__tests__.fake_widget_gui import FakeWidgetGui
from libraries.widget import Button, Combo
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from selection.selection import Selection
from selection.selection_gui import Element as SelectionGuiElement
from selection.selection_gui import Event as SelectionGuiEvent
from selection.settings_selection_gui import Element as SettingsSelectionElement
from selection.settings_selection_gui import SettingsSelectionGui
from settings import Settings


class SettingsSelectionGuiTestCase(TestCase):
    CURRENT_SETTINGS_NAME = 'current_settings'
    CURRENT_START_LED = 0
    CURRENT_END_LED = 100
    CURRENT_MILLISECONDS_PER_AUDIO_CHUNK = 50
    CURRENT_SERIAL_PORT = 'COM1'
    CURRENT_SERIAL_BAUDRATE = Settings.SERIAL_BAUDRATES[0]
    CURRENT_BRIGHTNESS = 20
    CURRENT_MINIMUM_FREQUENCY = 0
    CURRENT_MAXIMUM_FREQUENCY = 1000
    CURRENT_SHOULD_REVERSE_LEDS = False
    CURRENT_NUMBER_OF_GROUPS = 60

    NON_CURRENT_SETTINGS_NAME = 'non_current_settings'
    NON_CURRENT_START_LED = 60
    NON_CURRENT_END_LED = 600
    NON_CURRENT_MILLISECONDS_PER_AUDIO_CHUNK = 55
    NON_CURRENT_SERIAL_PORT = 'COM2'
    NON_CURRENT_SERIAL_BAUDRATE = Settings.SERIAL_BAUDRATES[1]
    NON_CURRENT_BRIGHTNESS = 50
    NON_CURRENT_MINIMUM_FREQUENCY = 20
    NON_CURRENT_MAXIMUM_FREQUENCY = 2000
    NON_CURRENT_SHOULD_REVERSE_LEDS = True
    NON_CURRENT_NUMBER_OF_GROUPS = 50

    NON_EXISTENT_SETTINGS_NAME = 'non_existent_settings_name'

    def setUp(self):
        self.current_settings = Settings(self.CURRENT_START_LED,
                                         self.CURRENT_END_LED,
                                         self.CURRENT_MILLISECONDS_PER_AUDIO_CHUNK,
                                         self.CURRENT_SERIAL_PORT,
                                         self.CURRENT_SERIAL_BAUDRATE,
                                         self.CURRENT_BRIGHTNESS,
                                         self.CURRENT_MINIMUM_FREQUENCY,
                                         self.CURRENT_MAXIMUM_FREQUENCY,
                                         self.CURRENT_SHOULD_REVERSE_LEDS,
                                         self.CURRENT_NUMBER_OF_GROUPS)

        self.non_current_settings = Settings(self.NON_CURRENT_START_LED,
                                             self.NON_CURRENT_END_LED,
                                             self.NON_CURRENT_MILLISECONDS_PER_AUDIO_CHUNK,
                                             self.NON_CURRENT_SERIAL_PORT,
                                             self.NON_CURRENT_SERIAL_BAUDRATE,
                                             self.NON_CURRENT_BRIGHTNESS,
                                             self.NON_CURRENT_MINIMUM_FREQUENCY,
                                             self.NON_CURRENT_MAXIMUM_FREQUENCY,
                                             self.NON_CURRENT_SHOULD_REVERSE_LEDS,
                                             self.NON_CURRENT_NUMBER_OF_GROUPS)

        self.settings_selection = Selection({self.CURRENT_SETTINGS_NAME: self.current_settings,
                                             self.NON_CURRENT_SETTINGS_NAME: self.non_current_settings})

        self.widget_gui = FakeWidgetGui()

        self.settings_selection_gui = SettingsSelectionGui(lambda: self.widget_gui)

    def clear_selection(self):
        NAMES = list(self.settings_selection.keys())

        for name in NAMES:
            del self.settings_selection[name]

    def clear_save_name_combo(self):
        EMPTY_SAVE_NAME_COMBO = Combo(SelectionGuiElement.SAVE_NAME_COMBO)
        self.widget_gui.update_widget(EMPTY_SAVE_NAME_COMBO)

    def check_widget_gui_matches_settings_selection(self, widget_gui: WidgetGui, settings_selection: Selection[Settings]):
        def get_widget_value(element: Union[SelectionGuiElement, SettingsSelectionElement]):
            WIDGET = widget_gui.get_widget(element)
            return WIDGET.value

        # Check the save names combo
        SAVE_NAME_COMBO: Combo = widget_gui.get_widget(SelectionGuiElement.SAVE_NAME_COMBO)

        EXPECTED_NAMES = list(settings_selection.keys())
        self.assertEqual(EXPECTED_NAMES, SAVE_NAME_COMBO.values)

        self.assertEqual(settings_selection.selected_key, SAVE_NAME_COMBO.value)

        # Check the Settings inputs
        SELECTED_SETTINGS = settings_selection.selected_value

        START_LED = str(SELECTED_SETTINGS.start_led)
        END_LED = str(SELECTED_SETTINGS.end_led)
        MILLISECONDS_PER_AUDIO_CHUNK = str(SELECTED_SETTINGS.milliseconds_per_audio_chunk)
        SERIAL_PORT = SELECTED_SETTINGS.serial_port
        SERIAL_BAUDRATE = str(SELECTED_SETTINGS.serial_baudrate)
        BRIGHTNESS = str(SELECTED_SETTINGS.brightness)
        MINIMUM_FREQUENCY = str(SELECTED_SETTINGS.minimum_frequency)
        MAXIMUM_FREQUENCY = str(SELECTED_SETTINGS.maximum_frequency)
        SHOULD_REVERSE_LEDS = SELECTED_SETTINGS.should_reverse_leds

        self.assertEqual(START_LED, get_widget_value(SettingsSelectionElement.START_LED_INPUT))
        self.assertEqual(END_LED, get_widget_value(SettingsSelectionElement.END_LED_INPUT))
        self.assertEqual(MILLISECONDS_PER_AUDIO_CHUNK, get_widget_value(SettingsSelectionElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT))
        self.assertEqual(SERIAL_PORT, get_widget_value(SettingsSelectionElement.SERIAL_PORT_INPUT))
        self.assertEqual(SERIAL_BAUDRATE, get_widget_value(SettingsSelectionElement.SERIAL_BAUDRATE_COMBO))
        self.assertEqual(BRIGHTNESS, get_widget_value(SettingsSelectionElement.BRIGHTNESS_INPUT))
        self.assertEqual(MINIMUM_FREQUENCY, get_widget_value(SettingsSelectionElement.MINIMUM_FREQUENCY_INPUT))
        self.assertEqual(MAXIMUM_FREQUENCY, get_widget_value(SettingsSelectionElement.MAXIMUM_FREQUENCY_INPUT))
        self.assertEqual(SHOULD_REVERSE_LEDS, get_widget_value(SettingsSelectionElement.REVERSE_LEDS_CHECK_BOX))


class TestDisplay(SettingsSelectionGuiTestCase):
    def test_display(self):
        self.assertFalse(self.widget_gui.open)

        self.settings_selection_gui.display(self.settings_selection)

        self.check_widget_gui_matches_settings_selection(self.widget_gui, self.settings_selection)

        self.assertTrue(self.widget_gui.open)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)


class DisplayedSettingsSelectionGuiTestCase(SettingsSelectionGuiTestCase):
    def setUp(self):
        super().setUp()

        self.settings_selection_gui.display(self.settings_selection)
        self.widget_gui.number_of_read_event_and_update_gui_calls = 0


class TestClose(DisplayedSettingsSelectionGuiTestCase):
    def test_close_displayed_gui(self):
        self.settings_selection_gui.close()
        self.assertTrue(not self.widget_gui.open)

    def test_close_non_displayed_gui(self):
        SETTINGS_SELECTION_GUI = SettingsSelectionGui(lambda: self.widget_gui)
        SETTINGS_SELECTION_GUI.close()
        self.assertTrue(not self.widget_gui.open)


class TestGetCurentSaveName(DisplayedSettingsSelectionGuiTestCase):
    def test_non_empty_save_name_combo(self):
        CURRENT_SAVE_NAME = self.settings_selection_gui.get_current_save_name()
        EXPECTED = self.settings_selection.selected_key
        self.assertEqual(CURRENT_SAVE_NAME, EXPECTED)

    def test_empty_save_name_combo(self):
        self.clear_save_name_combo()

        CURRENT_SAVE_NAME = self.settings_selection_gui.get_current_save_name()
        EXPECTED = ''
        self.assertEqual(CURRENT_SAVE_NAME, EXPECTED)


class TestGetSelection(DisplayedSettingsSelectionGuiTestCase):
    def test_get_selection(self):
        SELECTION = self.settings_selection_gui.get_selection()
        EXPECTED = Selection({self.CURRENT_SETTINGS_NAME: self.current_settings})

        self.assertEqual(SELECTION, EXPECTED)

    def test_get_selection_with_no_name(self):
        self.clear_save_name_combo()

        SELECTION = self.settings_selection_gui.get_selection()
        EXPECTED = Selection({'': self.current_settings})

        self.assertEqual(SELECTION, EXPECTED)


class TestUpdateWidgets(DisplayedSettingsSelectionGuiTestCase):
    def test_update_widgets(self):
        self.settings_selection.selected_key = self.NON_CURRENT_SETTINGS_NAME

        self.settings_selection_gui.update_widgets(self.settings_selection)

        self.check_widget_gui_matches_settings_selection(self.widget_gui, self.settings_selection)

        self.assertTrue(self.widget_gui.open)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(SelectionGuiElement.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)


class TestReadEventAndUpdateGui(DisplayedSettingsSelectionGuiTestCase):
    def test_read_an_event(self):
        EVENT = 'some event'

        self.widget_gui.event = EVENT

        event = self.settings_selection_gui.read_event_and_update_gui(self.settings_selection)

        self.assertEqual(event, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_select_current_save(self):
        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.settings_selection_gui.read_event_and_update_gui(self.settings_selection)

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
        SAVE_NAME_COMBO.value = self.NON_CURRENT_SETTINGS_NAME

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.settings_selection_gui.read_event_and_update_gui(self.settings_selection)

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

        EVENT = self.settings_selection_gui.read_event_and_update_gui(self.settings_selection)

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
        SAVE_NAME_COMBO.add_value(self.NON_EXISTENT_SETTINGS_NAME)
        SAVE_NAME_COMBO.value = self.NON_EXISTENT_SETTINGS_NAME

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.settings_selection_gui.read_event_and_update_gui(self.settings_selection)
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

        EVENT = self.settings_selection_gui.read_event_and_update_gui(self.settings_selection)
        self.assertEqual(WidgetGuiEvent.CLOSE_WINDOW, EVENT)

        self.assertFalse(self.widget_gui.open)
