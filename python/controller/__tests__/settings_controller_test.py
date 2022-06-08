import unittest
from collections import Counter
from typing import Any, Dict, Hashable, List, Tuple

from controller.settings_controller import Element, Event, SettingsController
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from libraries.widget import Widget, Button, Combo
from util import Settings, SettingsCollection


class FakeWidgetGui(WidgetGui):
    def __init__(self):
        self.queued_widgets: Dict[Hashable, Widget] = dict()
        self.displayed_widgets: Dict[Hashable, Widget] = dict()

        self.queued_layout: List[List[Widget]] = []
        self.displayed_layout = []

        self.event = WidgetGuiEvent.TIMEOUT
        self.number_of_read_event_and_update_gui_calls = 0

    def close(self):
        self.open = False

        self.queued_layout.clear()
        self.displayed_layout.clear()

        self.queued_widgets.clear()
        self.displayed_widgets.clear()

    def set_layout(self, layout: List[List[Widget]]):
        self.queued_layout = layout

        for row in layout:
            for widget in row:
                try:
                    self.queued_widgets[widget.key] = widget

                except AttributeError:
                    pass

    def display_layout(self):
        self.displayed_layout = self.queued_layout

        for row in self.displayed_layout:
            for widget in row:
                try:
                    self.displayed_widgets[widget.key] = widget

                except AttributeError:
                    pass

        self.open = True

    def read_event_and_update_gui(self):
        self.number_of_read_event_and_update_gui_calls += 1
        for displayed_widget_key in self.displayed_widgets:
            try:
                self.displayed_widgets[displayed_widget_key] = self.queued_widgets[displayed_widget_key]

            except KeyError:
                continue

        return self.event

    def get_widget(self, widget_key):
        return self.displayed_widgets[widget_key]

    def update_widget(self, widget: Widget):
        WIDGET_KEY = widget.key

        if (WIDGET_KEY not in self.queued_widgets):
            raise KeyError(f'There is no Widget with the key {WIDGET_KEY}.')

        self.queued_widgets[WIDGET_KEY] = widget
        self.displayed_widgets = self.queued_widgets


def create_amplitude_rgbs_widget_value(amplitude_rgbs: List[Tuple[int, int, int]]) -> str:
    COUNTER = Counter(amplitude_rgbs)

    result = ''
    for rgb, count in COUNTER.items():

        red, green, blue = rgb

        result += f'{red}, {green}, {blue}, {count}\n'

    return result.strip()


class SettingsControllerTestCase(unittest.TestCase):
    CURRENT_SETTINGS_NAME = 'current_settings_name'

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
    CURRENT_AMPLITUDE_RGBS = []

    NON_CURRENT_SETTINGS_NAME = 'non_current_settings_name'

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
    NON_CURRENT_AMPLITUDE_RGBS = [(10, 20, 30)]

    NON_EXISTENT_SETTINGS_NAME = 'I am not a Settings name in the SettingsCollection'

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
                                         self.CURRENT_NUMBER_OF_GROUPS,
                                         self.CURRENT_AMPLITUDE_RGBS)

        self.non_current_settings = Settings(self.NON_CURRENT_START_LED,
                                             self.NON_CURRENT_END_LED,
                                             self.NON_CURRENT_MILLISECONDS_PER_AUDIO_CHUNK,
                                             self.NON_CURRENT_SERIAL_PORT,
                                             self.NON_CURRENT_SERIAL_BAUDRATE,
                                             self.NON_CURRENT_BRIGHTNESS,
                                             self.NON_CURRENT_MINIMUM_FREQUENCY,
                                             self.NON_CURRENT_MAXIMUM_FREQUENCY,
                                             self.NON_CURRENT_SHOULD_REVERSE_LEDS,
                                             self.NON_CURRENT_NUMBER_OF_GROUPS,
                                             self.NON_CURRENT_AMPLITUDE_RGBS)

        collection = {self.CURRENT_SETTINGS_NAME: self.current_settings,
                      self.NON_CURRENT_SETTINGS_NAME: self.non_current_settings}

        self.settings_collection = SettingsCollection(collection)
        self.widget_gui = FakeWidgetGui()

        self.settings_controller = SettingsController(self.widget_gui, self.settings_collection)

    def check_widget_gui_does_not_match_settings(self, widget_gui: WidgetGui, settings: Settings):
        def get_widget_value(element: Element):
            WIDGET = widget_gui.get_widget(element)
            return WIDGET.value

        START_LED = str(settings.start_led)
        END_LED = str(settings.end_led)
        MILLISECONDS_PER_AUDIO_CHUNK = str(settings.milliseconds_per_audio_chunk)
        SERIAL_PORT = settings.serial_port
        SERIAL_BAUDRATE = str(settings.serial_baudrate)
        BRIGHTNESS = str(settings.brightness)
        MINIMUM_FREQUENCY = str(settings.minimum_frequency)
        MAXIMUM_FREQUENCY = str(settings.maximum_frequency)
        SHOULD_REVERSE_LEDS = settings.should_reverse_leds
        NUMBER_OF_GROUPS = str(settings.number_of_groups)

        AMPLITUDE_RGBS = create_amplitude_rgbs_widget_value(settings.amplitude_rgbs)

        self.assertNotEqual(START_LED, get_widget_value(Element.START_LED_INPUT))
        self.assertNotEqual(END_LED, get_widget_value(Element.END_LED_INPUT))
        self.assertNotEqual(MILLISECONDS_PER_AUDIO_CHUNK, get_widget_value(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT))
        self.assertNotEqual(SERIAL_PORT, get_widget_value(Element.SERIAL_PORT_INPUT))
        self.assertNotEqual(SERIAL_BAUDRATE, get_widget_value(Element.SERIAL_BAUDRATE_COMBO))
        self.assertNotEqual(BRIGHTNESS, get_widget_value(Element.BRIGHTNESS_INPUT))
        self.assertNotEqual(MINIMUM_FREQUENCY, get_widget_value(Element.MINIMUM_FREQUENCY_INPUT))
        self.assertNotEqual(MAXIMUM_FREQUENCY, get_widget_value(Element.MAXIMUM_FREQUENCY_INPUT))
        self.assertNotEqual(SHOULD_REVERSE_LEDS, get_widget_value(Element.REVERSE_LEDS_CHECK_BOX))
        self.assertNotEqual(NUMBER_OF_GROUPS, get_widget_value(Element.NUMBER_OF_GROUPS_INPUT))
        self.assertNotEqual(AMPLITUDE_RGBS, get_widget_value(Element.AMPLITUDE_RGBS_MULTILINE))

    def check_widget_gui_matches_settings(self, widget_gui: WidgetGui, settings: Settings):
        def get_widget_value(element: Element):
            WIDGET = widget_gui.get_widget(element)
            return WIDGET.value

        START_LED = str(settings.start_led)
        END_LED = str(settings.end_led)
        MILLISECONDS_PER_AUDIO_CHUNK = str(settings.milliseconds_per_audio_chunk)
        SERIAL_PORT = settings.serial_port
        SERIAL_BAUDRATE = str(settings.serial_baudrate)
        BRIGHTNESS = str(settings.brightness)
        MINIMUM_FREQUENCY = str(settings.minimum_frequency)
        MAXIMUM_FREQUENCY = str(settings.maximum_frequency)
        SHOULD_REVERSE_LEDS = settings.should_reverse_leds
        NUMBER_OF_GROUPS = str(settings.number_of_groups)

        AMPLITUDE_RGBS = create_amplitude_rgbs_widget_value(settings.amplitude_rgbs)

        self.assertEqual(START_LED, get_widget_value(Element.START_LED_INPUT))
        self.assertEqual(END_LED, get_widget_value(Element.END_LED_INPUT))
        self.assertEqual(MILLISECONDS_PER_AUDIO_CHUNK, get_widget_value(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT))
        self.assertEqual(SERIAL_PORT, get_widget_value(Element.SERIAL_PORT_INPUT))
        self.assertEqual(SERIAL_BAUDRATE, get_widget_value(Element.SERIAL_BAUDRATE_COMBO))
        self.assertEqual(BRIGHTNESS, get_widget_value(Element.BRIGHTNESS_INPUT))
        self.assertEqual(MINIMUM_FREQUENCY, get_widget_value(Element.MINIMUM_FREQUENCY_INPUT))
        self.assertEqual(MAXIMUM_FREQUENCY, get_widget_value(Element.MAXIMUM_FREQUENCY_INPUT))
        self.assertEqual(SHOULD_REVERSE_LEDS, get_widget_value(Element.REVERSE_LEDS_CHECK_BOX))
        self.assertEqual(NUMBER_OF_GROUPS, get_widget_value(Element.NUMBER_OF_GROUPS_INPUT))
        self.assertEqual(AMPLITUDE_RGBS, get_widget_value(Element.AMPLITUDE_RGBS_MULTILINE))

    def set_settings_name_combo_values(self, values: List[str]):
        OLD_QUEUED_COMBO: Combo = self.widget_gui.queued_widgets[Element.SETTINGS_NAME_COMBO]
        NEW_QUEUED_COMBO = Combo(Element.SETTINGS_NAME_COMBO, values, OLD_QUEUED_COMBO.font,
                                 OLD_QUEUED_COMBO.size, OLD_QUEUED_COMBO.enabled)

        OLD_DISPLAYED_COMBO: Combo = self.widget_gui.displayed_widgets[Element.SETTINGS_NAME_COMBO]
        NEW_DISPLAYED_COMBO = Combo(Element.SETTINGS_NAME_COMBO, values, OLD_DISPLAYED_COMBO.font,
                                    OLD_DISPLAYED_COMBO.size, OLD_DISPLAYED_COMBO.enabled)

        self.widget_gui.queued_widgets[Element.SETTINGS_NAME_COMBO] = NEW_QUEUED_COMBO
        self.widget_gui.displayed_widgets[Element.SETTINGS_NAME_COMBO] = NEW_DISPLAYED_COMBO


class TestConstructor(SettingsControllerTestCase):
    def test_with_empty_collection(self):
        widget_gui = FakeWidgetGui()

        collection = dict()
        settings_collection = SettingsCollection(collection)

        settings_controller = SettingsController(widget_gui, settings_collection)

        EXPECTED_SETTINGS = Settings()

        self.assertEqual(settings_controller.settings, EXPECTED_SETTINGS)

    def test_with_non_empty_collection(self):
        SETTINGS_1 = self.settings_collection[self.CURRENT_SETTINGS_NAME]

        self.assertEqual(self.settings_controller.settings, SETTINGS_1)


class TestDisplay(SettingsControllerTestCase):
    def test_display(self):
        self.settings_controller.display()

        SETTINGS_1 = self.settings_collection[self.CURRENT_SETTINGS_NAME]
        SETTINGS_2 = self.settings_collection[self.NON_CURRENT_SETTINGS_NAME]

        self.check_widget_gui_matches_settings(self.widget_gui, SETTINGS_1)
        self.check_widget_gui_does_not_match_settings(self.widget_gui, SETTINGS_2)

        self.assertTrue(self.widget_gui.open)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertTrue(DELETE_BUTTON.enabled)


class TestReadEventAndUpdateGui(SettingsControllerTestCase):
    def setUp(self):
        super().setUp()

        self.settings_controller.display()
        self.widget_gui.number_of_read_event_and_update_gui_calls = 0

    def test_read_an_event(self):
        EVENT = 'some event'

        self.widget_gui.event = EVENT

        event = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(event, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_read_select_current_settings_name_event(self):
        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        event = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(event, Event.SELECT_CURRENT_SETTINGS_NAME)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_read_clear_settings_name_event(self):
        VALUES = ['']
        self.set_settings_name_combo_values(VALUES)

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        event = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(event, Event.CLEAR_SETTINGS_NAME)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_read_enter_new_settings_name_event(self):
        VALUES = [self.NON_EXISTENT_SETTINGS_NAME]
        self.set_settings_name_combo_values(VALUES)

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        event = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(event, Event.ENTER_NEW_SETTINGS_NAME)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_read_select_non_current_settings_name_event(self):
        VALUES = [self.NON_CURRENT_SETTINGS_NAME]
        self.set_settings_name_combo_values(VALUES)

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        event = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(event, Event.SELECT_NON_CURRENT_SETTINGS_NAME)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)


class TestHandleEvent(SettingsControllerTestCase):
    def setUp(self):
        super().setUp()

        self.settings_controller.display()

        self.widget_gui.number_of_read_event_and_update_gui_calls = 0

    def set_widget_value(self, element: Element, value: Any):
        widget = self.widget_gui.get_widget(element)
        widget.value = value
        self.widget_gui.update_widget(widget)

    def test_save(self):
        self.set_widget_value(Element.START_LED_INPUT, self.NON_CURRENT_START_LED)
        self.set_widget_value(Element.END_LED_INPUT, self.NON_CURRENT_END_LED)
        self.set_widget_value(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT, self.NON_CURRENT_MILLISECONDS_PER_AUDIO_CHUNK)
        self.set_widget_value(Element.SERIAL_PORT_INPUT, self.NON_CURRENT_SERIAL_PORT)

        self.set_widget_value(Element.SERIAL_BAUDRATE_COMBO, str(self.NON_CURRENT_SERIAL_BAUDRATE))

        self.set_widget_value(Element.BRIGHTNESS_INPUT, self.NON_CURRENT_BRIGHTNESS)
        self.set_widget_value(Element.MINIMUM_FREQUENCY_INPUT, self.NON_CURRENT_MINIMUM_FREQUENCY)
        self.set_widget_value(Element.MAXIMUM_FREQUENCY_INPUT, self.NON_CURRENT_MAXIMUM_FREQUENCY)
        self.set_widget_value(Element.REVERSE_LEDS_CHECK_BOX, self.NON_CURRENT_SHOULD_REVERSE_LEDS)
        self.set_widget_value(Element.NUMBER_OF_GROUPS_INPUT, self.NON_CURRENT_NUMBER_OF_GROUPS)

        AMPLITUDE_RGBS = create_amplitude_rgbs_widget_value(self.NON_CURRENT_AMPLITUDE_RGBS)
        self.set_widget_value(Element.AMPLITUDE_RGBS_MULTILINE, AMPLITUDE_RGBS)

        self.settings_controller.handle_event(Element.SAVE_BUTTON)

        PREVIOUS_SETTINGS = self.settings_collection[self.CURRENT_SETTINGS_NAME]
        CURRENT_SETTINGS = self.settings_collection[self.NON_CURRENT_SETTINGS_NAME]

        self.check_widget_gui_matches_settings(self.widget_gui, PREVIOUS_SETTINGS)
        self.check_widget_gui_matches_settings(self.widget_gui, CURRENT_SETTINGS)
        self.assertEqual(PREVIOUS_SETTINGS, CURRENT_SETTINGS)

    def test_delete_a_settings_when_there_are_two_settings_in_the_collection(self):
        self.set_widget_value(Element.SETTINGS_NAME_COMBO, self.CURRENT_SETTINGS_NAME)

        self.settings_controller.handle_event(Element.DELETE_BUTTON)

        SETTINGS_NAMES = list(self.settings_collection.names())
        EXPECTED_SETTINGS_NAMES = [self.NON_CURRENT_SETTINGS_NAME]
        self.assertEqual(SETTINGS_NAMES, EXPECTED_SETTINGS_NAMES)

        self.assertEqual(self.NON_CURRENT_SETTINGS_NAME, self.settings_collection.current_name)

        SETTINGS_2 = self.settings_collection.current_settings

        self.assertEqual(self.non_current_settings, SETTINGS_2)
        self.check_widget_gui_matches_settings(self.widget_gui, SETTINGS_2)

    def test_delete_all_settings_in_the_collection(self):
        self.settings_controller.handle_event(Element.DELETE_BUTTON)
        self.settings_controller.handle_event(Element.DELETE_BUTTON)

        self.assertTrue(len(self.settings_collection) == 0)

        DEFAULT_SETTINGS = Settings()

        self.check_widget_gui_matches_settings(self.widget_gui, DEFAULT_SETTINGS)
        self.assertEqual(DEFAULT_SETTINGS, self.settings_controller.settings)

    def test_delete_when_there_are_no_settings_remaining(self):
        self.settings_controller.handle_event(Element.DELETE_BUTTON)
        self.settings_controller.handle_event(Element.DELETE_BUTTON)

        with self.assertRaises(ValueError):
            self.settings_controller.handle_event(Element.DELETE_BUTTON)

        self.assertTrue(len(self.settings_collection) == 0)

        DEFAULT_SETTINGS = Settings()

        self.check_widget_gui_matches_settings(self.widget_gui, DEFAULT_SETTINGS)
        self.assertEqual(DEFAULT_SETTINGS, self.settings_controller.settings)

    def test_close_window(self):
        self.settings_controller.handle_event(WidgetGuiEvent.CLOSE_WINDOW)

        self.assertFalse(self.widget_gui.open)

        self.assertEqual(self.widget_gui.displayed_layout, list())
        self.assertEqual(self.widget_gui.queued_layout, list())

        self.assertEqual(self.widget_gui.displayed_widgets, dict())
        self.assertEqual(self.widget_gui.queued_widgets, dict())

    def test_select_non_current_settings_name_valid(self):
        VALUES = [self.NON_CURRENT_SETTINGS_NAME]
        self.set_settings_name_combo_values(VALUES)

        self.settings_controller.handle_event(Event.SELECT_NON_CURRENT_SETTINGS_NAME)

        EXPECTED_SETTINGS = self.settings_collection[self.NON_CURRENT_SETTINGS_NAME]

        self.assertIs(self.settings_controller.settings, EXPECTED_SETTINGS)
        self.check_widget_gui_matches_settings(self.widget_gui, EXPECTED_SETTINGS)

    def test_select_non_current_settings_name_not_valid(self):
        VALUES = [self.NON_EXISTENT_SETTINGS_NAME]
        self.set_settings_name_combo_values(VALUES)

        with self.assertRaises(ValueError):
            self.settings_controller.handle_event(Event.SELECT_NON_CURRENT_SETTINGS_NAME)

        EXPECTED_SETTINGS = self.settings_collection[self.CURRENT_SETTINGS_NAME]

        self.assertIs(self.settings_controller.settings, EXPECTED_SETTINGS)
        self.check_widget_gui_matches_settings(self.widget_gui, EXPECTED_SETTINGS)

    def test_clear_settings_name(self):
        self.settings_controller.handle_event(Event.CLEAR_SETTINGS_NAME)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertFalse(SAVE_BUTTON.enabled)
        self.assertFalse(DELETE_BUTTON.enabled)

    def test_enter_new_settings_name(self):
        self.settings_controller.handle_event(Event.ENTER_NEW_SETTINGS_NAME)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON: Button = self.widget_gui.get_widget(Element.DELETE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)
        self.assertFalse(DELETE_BUTTON.enabled)

    def test_unrecognized_event(self):
        UNRECOGNIZED_EVENT = 'unrecognized event'

        with self.assertRaises(ValueError):
            self.settings_controller.handle_event(UNRECOGNIZED_EVENT)

        EXPECTED_SETTINGS = self.settings_collection[self.CURRENT_SETTINGS_NAME]

        self.assertIs(self.settings_controller.settings, EXPECTED_SETTINGS)
        self.check_widget_gui_matches_settings(self.widget_gui, EXPECTED_SETTINGS)
