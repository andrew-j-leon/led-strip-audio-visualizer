from collections import Counter
from typing import Any, Dict, Hashable, List, Tuple
import unittest
from controller.settings_controller import SettingsController, Element

from libraries.widget_gui import Widget, WidgetGui, WidgetGuiEvent
from util import Settings, SettingsCollection


class FakeWidgetGui(WidgetGui):
    def __init__(self):
        self.queued_widgets: Dict[Hashable, Widget] = dict()
        self.displayed_widgets: Dict[Hashable, Widget] = dict()

        self.queued_layout: List[List[Widget]] = []
        self.displayed_layout = []

        self.event = WidgetGuiEvent.TIMEOUT

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

        self.closed = False

    def read_event_and_update_gui(self):
        for displayed_widget_key in self.displayed_widgets:
            try:
                self.displayed_widgets[displayed_widget_key] = self.queued_widgets[displayed_widget_key]

            except KeyError:
                continue

        return self.event

    def disable_widget(self, widget_key):
        self.queued_widgets[widget_key].disabled = True

    def enable_widget(self, widget_key):
        self.queued_widgets[widget_key].disabled = False

    def set_widget_value(self, widget_key, value):
        self.queued_widgets[widget_key].value = value

    def get_widget_value(self, widget_key):
        try:
            return self.displayed_widgets[widget_key].value

        except AttributeError:
            widget = self.displayed_widgets[widget_key]
            raise ValueError(f'The Widget for the key {widget_key} ({widget}) does not have a value.')

    def close(self):
        self.closed = True
        self.queued_layout.clear()
        self.displayed_layout.clear()

        self.queued_widgets.clear()
        self.displayed_widgets.clear()


def get_amplitude_rgbs(amplitude_rgbs: List[Tuple[int, int, int]]) -> str:
    COUNTER = Counter(amplitude_rgbs)

    result = ''
    for rgb, count in COUNTER.items():

        red, green, blue = rgb

        result += f'{red}, {green}, {blue}, {count}\n'

    return result.strip()


class SettingsControllerTestCase(unittest.TestCase):
    SETTINGS_1_NAME = 'settings_1_name'

    START_LED_1 = 0
    END_LED_1 = 100
    MILLISECONDS_PER_AUDIO_CHUNK_1 = 50
    SERIAL_PORT_1 = 'COM1'
    SERIAL_BAUDRATE_1 = Settings.SERIAL_BAUDRATES[0]
    BRIGHTNESS_1 = 20
    MINIMUM_FREQUENCY_1 = 0
    MAXIMUM_FREQUENCY_1 = 1000
    SHOULD_REVERSE_LEDS_1 = False
    NUMBER_OF_GROUPS_1 = 60
    AMPLITUDE_RGBS_1 = []

    SETTINGS_2_NAME = 'settings_2_name'

    START_LED_2 = 60
    END_LED_2 = 600
    MILLISECONDS_PER_AUDIO_CHUNK_2 = 55
    SERIAL_PORT_2 = 'COM2'
    SERIAL_BAUDRATE_2 = Settings.SERIAL_BAUDRATES[1]
    BRIGHTNESS_2 = 50
    MINIMUM_FREQUENCY_2 = 20
    MAXIMUM_FREQUENCY_2 = 2000
    SHOULD_REVERSE_LEDS_2 = True
    NUMBER_OF_GROUPS_2 = 50
    AMPLITUDE_RGBS_2 = [(10, 20, 30)]

    NON_EXISTENT_SETTINGS_NAME = 'I am not a Settings name in the SettingsCollection'

    def setUp(self):
        self.settings_1 = Settings(self.START_LED_1,
                                   self.END_LED_1,
                                   self.MILLISECONDS_PER_AUDIO_CHUNK_1,
                                   self.SERIAL_PORT_1,
                                   self.SERIAL_BAUDRATE_1,
                                   self.BRIGHTNESS_1,
                                   self.MINIMUM_FREQUENCY_1,
                                   self.MAXIMUM_FREQUENCY_1,
                                   self.SHOULD_REVERSE_LEDS_1,
                                   self.NUMBER_OF_GROUPS_1,
                                   self.AMPLITUDE_RGBS_1)

        self.settings_2 = Settings(self.START_LED_2,
                                   self.END_LED_2,
                                   self.MILLISECONDS_PER_AUDIO_CHUNK_2,
                                   self.SERIAL_PORT_2,
                                   self.SERIAL_BAUDRATE_2,
                                   self.BRIGHTNESS_2,
                                   self.MINIMUM_FREQUENCY_2,
                                   self.MAXIMUM_FREQUENCY_2,
                                   self.SHOULD_REVERSE_LEDS_2,
                                   self.NUMBER_OF_GROUPS_2,
                                   self.AMPLITUDE_RGBS_2)

        collection = {self.SETTINGS_1_NAME: self.settings_1,
                      self.SETTINGS_2_NAME: self.settings_2}

        self.settings_collection = SettingsCollection(collection)
        self.widget_gui = FakeWidgetGui()

        self.settings_controller = SettingsController(self.widget_gui, self.settings_collection)

    def check_widget_gui_does_not_match_settings(self, widget_gui: WidgetGui, settings: Settings):
        def get_widget_value(element: Element):
            return widget_gui.get_widget_value(element)

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

        AMPLITUDE_RGBS = get_amplitude_rgbs(settings.amplitude_rgbs)

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
            return widget_gui.get_widget_value(element)

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

        AMPLITUDE_RGBS = get_amplitude_rgbs(settings.amplitude_rgbs)

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


class TestConstructor(SettingsControllerTestCase):
    def test_with_empty_collection(self):
        widget_gui = FakeWidgetGui()

        collection = dict()
        settings_collection = SettingsCollection(collection)

        settings_controller = SettingsController(widget_gui, settings_collection)

        EXPECTED_SETTINGS = Settings()

        self.assertEqual(settings_controller.settings, EXPECTED_SETTINGS)

    def test_with_non_empty_collection(self):
        SETTINGS_1 = self.settings_collection[self.SETTINGS_1_NAME]

        self.assertEqual(self.settings_controller.settings, SETTINGS_1)


class TestDrawWidgetGui(SettingsControllerTestCase):
    def test_draw_widget_gui(self):
        self.settings_controller.draw_widget_gui()

        SETTINGS_1 = self.settings_collection[self.SETTINGS_1_NAME]
        SETTINGS_2 = self.settings_collection[self.SETTINGS_2_NAME]

        self.check_widget_gui_matches_settings(self.widget_gui, SETTINGS_1)
        self.check_widget_gui_does_not_match_settings(self.widget_gui, SETTINGS_2)

        self.assertFalse(self.widget_gui.closed)


class TestReadEventAndUpdateGui(SettingsControllerTestCase):
    def test_read_event(self):
        self.settings_controller.draw_widget_gui()

        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        event = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(event, WidgetGuiEvent.TIMEOUT)


class TestHandleEvent(SettingsControllerTestCase):
    def test_save(self):
        def set_widget_value(element: Element, value: Any):
            self.widget_gui.set_widget_value(element, value)

        self.settings_controller.draw_widget_gui()

        set_widget_value(Element.START_LED_INPUT, self.START_LED_2)
        set_widget_value(Element.END_LED_INPUT, self.END_LED_2)
        set_widget_value(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT, self.MILLISECONDS_PER_AUDIO_CHUNK_2)
        set_widget_value(Element.SERIAL_PORT_INPUT, self.SERIAL_PORT_2)

        set_widget_value(Element.SERIAL_BAUDRATE_COMBO, str(self.SERIAL_BAUDRATE_2))

        set_widget_value(Element.BRIGHTNESS_INPUT, self.BRIGHTNESS_2)
        set_widget_value(Element.MINIMUM_FREQUENCY_INPUT, self.MINIMUM_FREQUENCY_2)
        set_widget_value(Element.MAXIMUM_FREQUENCY_INPUT, self.MAXIMUM_FREQUENCY_2)
        set_widget_value(Element.REVERSE_LEDS_CHECK_BOX, self.SHOULD_REVERSE_LEDS_2)
        set_widget_value(Element.NUMBER_OF_GROUPS_INPUT, self.NUMBER_OF_GROUPS_2)

        AMPLITUDE_RGBS = get_amplitude_rgbs(self.AMPLITUDE_RGBS_2)
        set_widget_value(Element.AMPLITUDE_RGBS_MULTILINE, AMPLITUDE_RGBS)

        self.settings_controller.handle_event(Element.SAVE_BUTTON)

        SETTINGS_1 = self.settings_collection[self.SETTINGS_1_NAME]
        SETTINGS_2 = self.settings_collection[self.SETTINGS_2_NAME]

        self.check_widget_gui_matches_settings(self.widget_gui, SETTINGS_1)
        self.check_widget_gui_matches_settings(self.widget_gui, SETTINGS_2)
        self.assertEqual(SETTINGS_1, SETTINGS_2)

    def test_delete_once_with_two_settings_in_the_collection(self):
        def set_widget_value(element: Element, value: Any):
            self.widget_gui.set_widget_value(element, value)

        self.settings_controller.draw_widget_gui()

        set_widget_value(Element.SETTINGS_NAME_COMBO, self.SETTINGS_1_NAME)

        self.settings_controller.handle_event(Element.DELETE_BUTTON)

        self.assertEqual(set(self.settings_collection.names()), {self.SETTINGS_2_NAME})

        self.assertEqual(self.SETTINGS_2_NAME, self.settings_collection.current_name)

        SETTINGS_2 = self.settings_collection.current_settings

        self.assertEqual(self.settings_2, SETTINGS_2)

        self.check_widget_gui_matches_settings(self.widget_gui, SETTINGS_2)

    def test_delete_all_settings_in_the_collection(self):
        self.settings_controller.draw_widget_gui()

        self.settings_controller.handle_event(Element.DELETE_BUTTON)
        self.settings_controller.handle_event(Element.DELETE_BUTTON)

        self.assertTrue(len(self.settings_collection) == 0)

        SETTINGS = Settings()

        self.check_widget_gui_matches_settings(self.widget_gui, SETTINGS)

    def test_delete_when_there_are_no_settings_remaining(self):
        self.settings_controller.draw_widget_gui()

        self.settings_controller.handle_event(Element.DELETE_BUTTON)
        self.settings_controller.handle_event(Element.DELETE_BUTTON)

        with self.assertRaises(ValueError):
            self.settings_controller.handle_event(Element.DELETE_BUTTON)

        self.assertTrue(len(self.settings_collection) == 0)

        SETTINGS = Settings()

        self.check_widget_gui_matches_settings(self.widget_gui, SETTINGS)

    def test_close_window(self):
        self.settings_controller.draw_widget_gui()

        self.settings_controller.handle_event(WidgetGuiEvent.CLOSE_WINDOW)

        self.assertTrue(self.widget_gui.closed)

    def test_no_settings_name(self):
        self.settings_controller.draw_widget_gui()

        original_get_widget_value = self.widget_gui.get_widget_value

        def get_widget_value(widget: Hashable):
            if (widget == Element.SETTINGS_NAME_COMBO):
                return ''

            return original_get_widget_value(widget)

        self.widget_gui.get_widget_value = get_widget_value

        self.settings_controller.handle_event(WidgetGuiEvent.TIMEOUT)

        self.assertTrue(self.widget_gui.displayed_widgets[Element.SAVE_BUTTON].disabled)
        self.assertTrue(self.widget_gui.displayed_widgets[Element.DELETE_BUTTON].disabled)

    def test_settings_name_is_in_collection(self):
        self.settings_controller.draw_widget_gui()

        original_get_widget_value = self.widget_gui.get_widget_value

        def get_widget_value(widget: Hashable):
            if (widget == Element.SETTINGS_NAME_COMBO):
                return self.SETTINGS_1_NAME

            return original_get_widget_value(widget)

        self.widget_gui.get_widget_value = get_widget_value

        self.settings_controller.handle_event(WidgetGuiEvent.TIMEOUT)

        self.assertFalse(self.widget_gui.displayed_widgets[Element.SAVE_BUTTON].disabled)
        self.assertFalse(self.widget_gui.displayed_widgets[Element.DELETE_BUTTON].disabled)

    def test_settings_name_is_not_in_collection(self):
        self.settings_controller.draw_widget_gui()

        original_get_widget_value = self.widget_gui.get_widget_value

        def get_widget_value(widget: Hashable):
            if (widget == Element.SETTINGS_NAME_COMBO):
                return self.NON_EXISTENT_SETTINGS_NAME

            return original_get_widget_value(widget)

        self.widget_gui.get_widget_value = get_widget_value

        self.settings_controller.handle_event(WidgetGuiEvent.TIMEOUT)

        self.assertFalse(self.widget_gui.displayed_widgets[Element.SAVE_BUTTON].disabled)
        self.assertTrue(self.widget_gui.displayed_widgets[Element.DELETE_BUTTON].disabled)

    def test_settings_name_is_in_the_collection_but_not_the_current(self):
        self.settings_controller.draw_widget_gui()

        original_get_widget_value = self.widget_gui.get_widget_value

        def get_widget_value(widget: Hashable):
            if (widget == Element.SETTINGS_NAME_COMBO):
                return self.SETTINGS_2_NAME

            return original_get_widget_value(widget)

        self.widget_gui.get_widget_value = get_widget_value

        self.settings_controller.handle_event(WidgetGuiEvent.TIMEOUT)
        self.settings_controller.handle_event(WidgetGuiEvent.TIMEOUT)

        self.assertFalse(self.widget_gui.displayed_widgets[Element.SAVE_BUTTON].disabled)
        self.assertFalse(self.widget_gui.displayed_widgets[Element.DELETE_BUTTON].disabled)

        SETTINGS_2 = self.settings_collection[self.SETTINGS_2_NAME]

        self.assertEqual(SETTINGS_2, self.settings_2)

        self.check_widget_gui_matches_settings(self.widget_gui, SETTINGS_2)

        self.assertEqual(self.SETTINGS_2_NAME, self.settings_collection.current_name)
