import shutil
from pathlib import Path
from typing import Any

import pyfakefs.fake_filesystem_unittest as fake_filesystem_unittest
from controller.__tests__.fake_widget_gui import FakeWidgetGui
from controller.settings_controller import Element, SettingsController
from libraries.widget import Button
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from settings import Settings
from settings import save as save_settings


class SaveSettings:
    def __init__(self, save_directory: Path):
        self.number_of_calls = 0
        self.__save_directory = save_directory

    def __call__(self, settings: Settings):
        self.number_of_calls += 1
        save_settings(settings, self.__save_directory)


class SettingsControllerTestCase(fake_filesystem_unittest.TestCase):
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

        self.widget_gui = FakeWidgetGui()

        def create_gui():
            return self.widget_gui

        self.save_directory = Path('save_directory')
        self.save_directory.mkdir()

        self.save_settings = SaveSettings(self.save_directory)

        self.settings_controller = SettingsController(create_gui, self.save_settings, self.current_settings)

    def tearDown(self):
        shutil.rmtree(str(self.save_directory), ignore_errors=True)
        self.save_settings.number_of_calls = 0

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

        self.check_widget_gui_matches_settings(self.widget_gui, self.current_settings)

        self.assertTrue(self.widget_gui.open)

        SAVE_BUTTON: Button = self.widget_gui.get_widget(Element.SAVE_BUTTON)

        self.assertTrue(SAVE_BUTTON.enabled)


class TestSettingsController(SettingsControllerTestCase):
    def setUp(self):
        super().setUp()

        self.settings_controller.display()
        self.widget_gui.number_of_read_event_and_update_gui_calls = 0

    def test_close(self):
        self.settings_controller.close()

        self.assertTrue(not self.widget_gui.open)

    def test_read_an_event(self):
        EVENT = 'some event'

        self.widget_gui.event = EVENT

        event = self.settings_controller.read_event_and_update_gui()

        self.assertEqual(event, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_save(self):
        def set_widget_value(element: Element, value: Any):
            widget = self.widget_gui.get_widget(element)
            widget.value = value
            self.widget_gui.update_widget(widget)

        set_widget_value(Element.START_LED_INPUT, self.NON_CURRENT_START_LED)
        set_widget_value(Element.END_LED_INPUT, self.NON_CURRENT_END_LED)
        set_widget_value(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT, self.NON_CURRENT_MILLISECONDS_PER_AUDIO_CHUNK)
        set_widget_value(Element.SERIAL_PORT_INPUT, self.NON_CURRENT_SERIAL_PORT)

        set_widget_value(Element.SERIAL_BAUDRATE_COMBO, str(self.NON_CURRENT_SERIAL_BAUDRATE))

        set_widget_value(Element.BRIGHTNESS_INPUT, self.NON_CURRENT_BRIGHTNESS)
        set_widget_value(Element.MINIMUM_FREQUENCY_INPUT, self.NON_CURRENT_MINIMUM_FREQUENCY)
        set_widget_value(Element.MAXIMUM_FREQUENCY_INPUT, self.NON_CURRENT_MAXIMUM_FREQUENCY)
        set_widget_value(Element.REVERSE_LEDS_CHECK_BOX, self.NON_CURRENT_SHOULD_REVERSE_LEDS)
        set_widget_value(Element.NUMBER_OF_GROUPS_INPUT, self.NON_CURRENT_NUMBER_OF_GROUPS)

        self.settings_controller.handle_event(Element.SAVE_BUTTON)

        self.check_widget_gui_matches_settings(self.widget_gui, self.non_current_settings)
        self.check_widget_gui_matches_settings(self.widget_gui, self.current_settings)

        EXPECTED_NUMBER_OF_SAVES = 1
        self.assertEqual(self.save_settings.number_of_calls, EXPECTED_NUMBER_OF_SAVES)

    def test_close_window(self):
        self.settings_controller.handle_event(WidgetGuiEvent.CLOSE_WINDOW)

        self.assertFalse(self.widget_gui.open)

    def test_unrecognized_event(self):
        UNRECOGNIZED_EVENT = 'unrecognized event'

        with self.assertRaises(ValueError):
            self.settings_controller.handle_event(UNRECOGNIZED_EVENT)
