import shutil
from pathlib import Path
from typing import Any, Hashable

import pyfakefs.fake_filesystem_unittest as fake_filesystem_unittest
from controller.__tests__.fake_widget_gui import FakeWidgetGui
from controller.settings_controller import Element, Event, SettingsController
from libraries.widget import Button, Combo
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from selection import Selection, save
from settings import Settings


class SaveSelection:
    def __init__(self, save_directory: Path):
        self.number_of_calls = 0
        self.__save_directory = save_directory

    def __call__(self, settings: Settings):
        self.number_of_calls += 1
        save(settings, self.__save_directory)


class SettingsControllerTestCase(fake_filesystem_unittest.TestCase):
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
        self.setUpPyfakefs()

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

        def create_gui():
            return self.widget_gui

        self.save_directory = Path('save_directory')
        self.save_directory.mkdir()

        self.save = SaveSelection(self.save_directory)

        self.settings_controller = SettingsController(create_gui, self.save, self.settings_selection)

    def tearDown(self):
        shutil.rmtree(str(self.save_directory), ignore_errors=True)

    def clear_selection(self):
        NAMES = list(self.settings_selection.keys())

        for name in NAMES:
            del self.settings_selection[name]

    def check_widget_gui_matches_settings_selection(self, widget_gui: WidgetGui, settings_selection: Selection[Settings]):
        def get_widget_value(element: Element):
            WIDGET = widget_gui.get_widget(element)
            return WIDGET.value

        # Check the save names combo
        SAVE_NAME_COMBO: Combo = widget_gui.get_widget(Element.SAVE_NAME_COMBO)

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

        self.assertEqual(START_LED, get_widget_value(Element.START_LED_INPUT))
        self.assertEqual(END_LED, get_widget_value(Element.END_LED_INPUT))
        self.assertEqual(MILLISECONDS_PER_AUDIO_CHUNK, get_widget_value(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT))
        self.assertEqual(SERIAL_PORT, get_widget_value(Element.SERIAL_PORT_INPUT))
        self.assertEqual(SERIAL_BAUDRATE, get_widget_value(Element.SERIAL_BAUDRATE_COMBO))
        self.assertEqual(BRIGHTNESS, get_widget_value(Element.BRIGHTNESS_INPUT))
        self.assertEqual(MINIMUM_FREQUENCY, get_widget_value(Element.MINIMUM_FREQUENCY_INPUT))
        self.assertEqual(MAXIMUM_FREQUENCY, get_widget_value(Element.MAXIMUM_FREQUENCY_INPUT))
        self.assertEqual(SHOULD_REVERSE_LEDS, get_widget_value(Element.REVERSE_LEDS_CHECK_BOX))


class TestDisplay(SettingsControllerTestCase):
    def test_display(self):
        self.settings_controller.display()

        self.check_widget_gui_matches_settings_selection(self.widget_gui, self.settings_selection)

        self.assertTrue(self.widget_gui.open)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)


class DisplayedSettingsControllerTestCase(SettingsControllerTestCase):
    def setUp(self):
        super().setUp()

        self.settings_controller.display()
        self.widget_gui.number_of_read_event_and_update_gui_calls = 0


class TestClose(DisplayedSettingsControllerTestCase):
    def test_close(self):
        self.settings_controller.close()

        self.assertTrue(not self.widget_gui.open)


class TestReadEventAndUpdateGui(DisplayedSettingsControllerTestCase):
    def test_read_an_event(self):
        EVENT = 'some event'

        self.widget_gui.event = EVENT

        event = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(event, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_select_current_save_event(self):
        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(Event.SELECT_CURRENT_SAVE, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_select_non_current_save_event(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(Element.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.value = self.NON_CURRENT_SETTINGS_NAME

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(Event.SELECT_NON_CURRENT_SAVE, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_delete_save_name_event(self):
        self.clear_selection()

        NEW_NAME_COMBO = Combo(Element.SAVE_NAME_COMBO)
        self.widget_gui.update_widget(NEW_NAME_COMBO)

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(Event.DELETE_SAVE_NAME, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_new_color_palette_name_event(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(Element.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.add_value(self.NON_EXISTENT_SETTINGS_NAME)
        SAVE_NAME_COMBO.value = self.NON_EXISTENT_SETTINGS_NAME

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(Event.ENTER_NEW_SAVE_NAME, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)


class TestHandleEvent(DisplayedSettingsControllerTestCase):

    def test_save_new_color_palette(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(Element.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.add_value(self.NON_EXISTENT_SETTINGS_NAME)
        SAVE_NAME_COMBO.value = self.NON_EXISTENT_SETTINGS_NAME

        self.settings_controller.handle_event(Element.SAVE_BUTTON)

        EXPECTED_SETTINGS = {self.CURRENT_SETTINGS_NAME: self.current_settings,
                             self.NON_CURRENT_SETTINGS_NAME: self.non_current_settings,
                             self.NON_EXISTENT_SETTINGS_NAME: self.current_settings}
        EXPECTED_SETTINGS_SELECTION = Selection(EXPECTED_SETTINGS)
        EXPECTED_SETTINGS_SELECTION.selected_key = self.NON_EXISTENT_SETTINGS_NAME

        self.assertEqual(self.settings_selection, EXPECTED_SETTINGS_SELECTION)

        EXPECTED_NUMBER_OF_SAVES = 1
        self.assertEqual(self.save.number_of_calls, EXPECTED_NUMBER_OF_SAVES)

    def test_overwrite_saved_color_palette(self):
        def set_widget_value(widget_key: Hashable, value: Any):
            WIDGET = self.widget_gui.get_widget(widget_key)
            WIDGET.value = value

        START_LED = 100
        END_LED = 500
        MILLISECONDS_PER_AUDIO_CHUNK = 100
        SERIAL_PORT = "COM100"
        SERIAL_BAUDRATE = 115200
        BRIGHTNESS = 100
        NUMBER_OF_GROUPS = 60
        MINIMUM_FREQUENCY = 0
        MAXIMUM_FREQUENCY = 20000
        REVERSE_LEDS = True

        set_widget_value(Element.START_LED_INPUT, str(START_LED))
        set_widget_value(Element.END_LED_INPUT, str(END_LED))
        set_widget_value(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT, str(MILLISECONDS_PER_AUDIO_CHUNK))
        set_widget_value(Element.SERIAL_PORT_INPUT, str(SERIAL_PORT))
        set_widget_value(Element.SERIAL_BAUDRATE_COMBO, str(SERIAL_BAUDRATE))
        set_widget_value(Element.BRIGHTNESS_INPUT, str(BRIGHTNESS))
        set_widget_value(Element.NUMBER_OF_GROUPS_INPUT, str(NUMBER_OF_GROUPS))
        set_widget_value(Element.MINIMUM_FREQUENCY_INPUT, str(MINIMUM_FREQUENCY))
        set_widget_value(Element.MAXIMUM_FREQUENCY_INPUT, str(MAXIMUM_FREQUENCY))
        set_widget_value(Element.REVERSE_LEDS_CHECK_BOX, REVERSE_LEDS)

        self.settings_controller.handle_event(Element.SAVE_BUTTON)

        EXPECTED_CURRENT_SETTINGS = Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK,
                                             SERIAL_PORT, SERIAL_BAUDRATE, BRIGHTNESS,
                                             MINIMUM_FREQUENCY, MAXIMUM_FREQUENCY, REVERSE_LEDS,
                                             NUMBER_OF_GROUPS)

        EXPECTED_COLOR_PALETTES = {self.CURRENT_SETTINGS_NAME: EXPECTED_CURRENT_SETTINGS,
                                   self.NON_CURRENT_SETTINGS_NAME: self.non_current_settings}
        EXPECTED_COLOR_PALETTE_SELECTION = Selection(EXPECTED_COLOR_PALETTES)
        EXPECTED_COLOR_PALETTE_SELECTION.selected_key = self.CURRENT_SETTINGS_NAME

        self.assertEqual(self.settings_selection, EXPECTED_COLOR_PALETTE_SELECTION)

        EXPECTED_NUMBER_OF_SAVES = 1
        self.assertEqual(self.save.number_of_calls, EXPECTED_NUMBER_OF_SAVES)

    def test_delete_non_existent_color_palette_name(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(Element.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.add_value(self.NON_EXISTENT_SETTINGS_NAME)
        SAVE_NAME_COMBO.value = self.NON_EXISTENT_SETTINGS_NAME

        with self.assertRaises(ValueError):
            self.settings_controller.handle_event(Element.DELETE_BUTTON)

        EXPECTED_COLOR_PALETTES = {self.CURRENT_SETTINGS_NAME: self.current_settings,
                                   self.NON_CURRENT_SETTINGS_NAME: self.non_current_settings}
        EXPECTED_COLOR_PALETTE_SELECTION = Selection(EXPECTED_COLOR_PALETTES)
        EXPECTED_COLOR_PALETTE_SELECTION.selected_key = self.CURRENT_SETTINGS_NAME

        self.assertEqual(self.settings_selection, EXPECTED_COLOR_PALETTE_SELECTION)

    def test_delete_existent_color_palette_name(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(Element.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.value = self.CURRENT_SETTINGS_NAME

        self.settings_controller.handle_event(Element.DELETE_BUTTON)

        EXPECTED_COLOR_PALETTES = {self.NON_CURRENT_SETTINGS_NAME: self.non_current_settings}
        EXPECTED_COLOR_PALETTE_SELECTION = Selection(EXPECTED_COLOR_PALETTES)

        self.assertEqual(self.settings_selection, EXPECTED_COLOR_PALETTE_SELECTION)

    def test_select_current_color_palette_name(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(Element.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.value = self.CURRENT_SETTINGS_NAME

        self.settings_controller.handle_event(Event.SELECT_CURRENT_SAVE)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)

        self.settings_selection.selected_key = self.CURRENT_SETTINGS_NAME
        self.check_widget_gui_matches_settings_selection(self.widget_gui, self.settings_selection)

    def test_select_non_current_color_palette_name(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(Element.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.value = self.NON_CURRENT_SETTINGS_NAME

        self.settings_controller.handle_event(Event.SELECT_NON_CURRENT_SAVE)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)

        self.settings_selection.selected_key = self.NON_CURRENT_SETTINGS_NAME
        self.check_widget_gui_matches_settings_selection(self.widget_gui, self.settings_selection)

    def test_select_non_current_color_palette_name_when_combo_name_not_in_color_palette_selection(self):
        SAVE_NAME_COMBO: Combo = self.widget_gui.get_widget(Element.SAVE_NAME_COMBO)
        SAVE_NAME_COMBO.add_value(self.NON_EXISTENT_SETTINGS_NAME)
        SAVE_NAME_COMBO.value = self.NON_EXISTENT_SETTINGS_NAME

        with self.assertRaises(ValueError):
            self.settings_controller.handle_event(Event.SELECT_NON_CURRENT_SAVE)

    def test_delete_color_palette_name(self):
        self.settings_controller.handle_event(Event.DELETE_SAVE_NAME)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertFalse(SAVE_BUTTON.enabled)
        self.assertFalse(DELETE_BUTTON.enabled)

    def test_enter_new_color_palette_name(self):
        self.settings_controller.handle_event(Event.ENTER_NEW_SAVE_NAME)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertFalse(DELETE_BUTTON.enabled)

    def test_close_window(self):
        self.settings_controller.handle_event(WidgetGuiEvent.CLOSE_WINDOW)

        self.assertFalse(self.widget_gui.open)

    def test_unrecognized_event(self):
        UNRECOGNIZED_EVENT = 'unrecognized event'

        with self.assertRaises(ValueError):
            self.settings_controller.handle_event(UNRECOGNIZED_EVENT)
