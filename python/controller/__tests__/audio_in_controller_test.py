from typing import Hashable, List, Tuple
from unittest import TestCase

from color_palette import ColorPalette
from controller.__tests__.fake_widget_gui import FakeWidgetGui, WidgetGuiEvent
from controller.audio_in_controller import AudioInController, Element, Event, LedStripType, _create_groups, _create_mirrored_groups
from controller.controller import RunnableResource
from led_strip.led_strip import FakeLedStrip
from libraries.audio_in_stream import AudioInStream
from libraries.canvas_gui import CanvasGui
from libraries.serial import FakeSerial
from libraries.widget import Button, CheckBox, Combo, Input, Text, Widget
from selection.selection import Selection
from settings import Settings
from spectrogram import Spectrogram
from util import Font


class FakeCanvasGui(CanvasGui):
    def __init__(self):
        self.opened = False

    @property
    def width(self) -> int:
        return 1920

    @property
    def height(self) -> int:
        return 1080

    def open(self):
        self.opened = True

    def close(self):
        self.opened = False

    def create_oval(self, top_left_x, top_left_y, bottom_right_x, bottom_right_y, fill_color='#000000'):
        return 0

    def create_text(self, center_x, center_y, text, font=Font(), fill_color='#000000'):
        return 0

    def update(self):
        pass

    def set_element_fill_color(self, element_id, color):
        pass


class FakeRunnableResource(RunnableResource):
    def __init__(self):
        self.running = False

    def run(self):
        self.running = True

    def close(self):
        self.running = False


class FakeAudioInStream(AudioInStream):
    def __init__(self, input_source: str = ''):
        self.__input_source = input_source
        self.opened = False
        self.data = b''

    @property
    def input_source(self) -> str:
        return self.__input_source

    @input_source.setter
    def input_source(self, input_source: str):
        self.__input_source = input_source

    def is_open(self) -> bool:
        return self.opened

    @property
    def sample_rate(self) -> int:
        '''
            Returns:
                `int`: The audio sampling rate in frames per second.
        '''
        return 44100

    def open(self):
        self.opened = True

    def close(self):
        self.opened = False

    def read(self, number_of_frames: int) -> bytes:
        return self.data


class FakeSpectrogram(Spectrogram):
    def __init__(self):
        self.amplitude_rgbs = []
        self.start_frequency = 0
        self.end_frequency = 0

    def set_amplitude_rgbs(self, amplitude_rgbs):
        self.amplitude_rgbs = amplitude_rgbs

    def set_frequency_range(self, start_frequency: int, end_frequency: int):
        self.start_frequency = start_frequency
        self.end_frequency = end_frequency

    def update_led_strip(self, led_strip, audio_data, number_of_frames, sampling_rate):
        '''
            Args:
                `audio_data (bytes)`: WAV audio data.
                `number_of_frames (int)`: The number of frames `audio_data` represents.
                `sampling_rate (int)`: The number of samples per second.
                `format (numpy.signedinteger)`: The format of the audio (i.e. 16 bit, 32 bit, etc.).
        '''
        self.led_strip = led_strip
        self.audio_data = audio_data
        self.number_of_frames = number_of_frames
        self.sampling_rate = sampling_rate


class AudioInControllerTestCase(TestCase):

    def setUp(self):
        RGB_A0 = (10, 10, 10)
        RGB_A0_COUNT = 10

        RGB_A1 = (10, 6, 25)
        RGB_A1_COUNT = 5

        RGB_A2 = (5, 7, 8)
        RGB_A2_COUNT = 20

        AMPLITUDE_RGBS_A = ([RGB_A0] * RGB_A0_COUNT
                            + [RGB_A1] * RGB_A1_COUNT
                            + [RGB_A2] * RGB_A2_COUNT)

        RGB_B0 = (150, 100, 0)
        RGB_B0_COUNT = 4

        RGB_B1 = (0, 0, 0)
        RGB_B1_COUNT = 15

        RGB_B2 = (255, 255, 255)
        RGB_B2_COUNT = 30

        AMPLITUDE_RGBS_B = ([RGB_B0] * RGB_B0_COUNT
                            + [RGB_B1] * RGB_B1_COUNT
                            + [RGB_B2] * RGB_B2_COUNT)

        CURRENT_COLOR_PALETTE_NAME = 'current_color_palette'
        NON_CURRENT_COLOR_PALETTE_NAME = 'non_current_color_palette'

        self.current_color_palette = ColorPalette(AMPLITUDE_RGBS_A)
        self.non_current_color_palette = ColorPalette(AMPLITUDE_RGBS_B)

        COLOR_PALETTES = {CURRENT_COLOR_PALETTE_NAME: self.current_color_palette,
                          NON_CURRENT_COLOR_PALETTE_NAME: self.non_current_color_palette}

        CURRENT_SETTINGS_NAME = 'current_settings'
        START_LED_A = 0
        END_LED_A = 300
        MILLISECONDS_PER_AUDIO_CHUNK_A = 50
        SERIAL_PORT_A = '/dev/ttyACM0'
        SERIAL_BAUDRATE_A = 1000000
        BRIGHTNESS_A = 20
        START_FREQUENCY_A = 0
        END_FREQUENCY_A = 2000
        SHOULD_REVERSE_LEDS_A = True
        NUMBER_OF_GROUPS_A = 60

        NON_CURRENT_SETTINGS_NAME = 'non_current_settings'
        START_LED_B = 60
        END_LED_B = 600
        MILLISECONDS_PER_AUDIO_CHUNK_B = 55
        SERIAL_PORT_B = 'COM2'
        SERIAL_BAUDRATE_B = Settings.SERIAL_BAUDRATES[1]
        BRIGHTNESS_B = 50
        MINIMUM_FREQUENCY_B = 20
        MAXIMUM_FREQUENCY_B = 2000
        SHOULD_REVERSE_LEDS_B = True
        NUMBER_OF_GROUPS_B = 50

        self.settings_controller = FakeRunnableResource()
        self.current_settings = Settings(START_LED_A, END_LED_A, MILLISECONDS_PER_AUDIO_CHUNK_A, SERIAL_PORT_A,
                                         SERIAL_BAUDRATE_A, BRIGHTNESS_A, START_FREQUENCY_A, END_FREQUENCY_A,
                                         SHOULD_REVERSE_LEDS_A, NUMBER_OF_GROUPS_A)
        self.non_current_settings = Settings(START_LED_B, END_LED_B, MILLISECONDS_PER_AUDIO_CHUNK_B, SERIAL_PORT_B,
                                             SERIAL_BAUDRATE_B, BRIGHTNESS_B, MINIMUM_FREQUENCY_B, MAXIMUM_FREQUENCY_B,
                                             SHOULD_REVERSE_LEDS_B, NUMBER_OF_GROUPS_B)

        SETTINGS = {CURRENT_SETTINGS_NAME: self.current_settings,
                    NON_CURRENT_SETTINGS_NAME: self.non_current_settings}

        self.settings_selection = Selection(SETTINGS)

        self.color_palette_controller = FakeRunnableResource()
        self.color_palette_selection = Selection(COLOR_PALETTES)
        self.widget_gui = FakeWidgetGui()
        self.canvas_gui = FakeCanvasGui()
        self.serial = FakeSerial()
        self.audio_in_stream = FakeAudioInStream()
        self.led_strip = FakeLedStrip()
        self.spectrogram = FakeSpectrogram()

        def create_settings_controller(settings: Settings):
            return self.settings_controller

        def create_color_palette_controller(color_palette_selection: Selection[ColorPalette]):
            return self.color_palette_controller

        def create_widget_gui():
            return self.widget_gui

        def create_canvas_gui():
            return self.canvas_gui

        def create_serial():
            return self.serial

        def create_audio_in_stream():
            return self.audio_in_stream

        def create_led_strip():
            return self.led_strip

        def create_spectrogram():
            return self.spectrogram

        self.audio_in_controller = AudioInController(create_settings_controller, self.settings_selection,
                                                     create_color_palette_controller, self.color_palette_selection,
                                                     create_widget_gui, create_canvas_gui, create_serial,
                                                     create_audio_in_stream, create_led_strip, create_spectrogram)

    def get_widget(self, widget_key: Hashable) -> Widget:
        return self.widget_gui.get_widget(widget_key)

    def check_led_strip_is_off(self):
        BLACK_RGB = (0, 0, 0)
        for group in range(self.led_strip.number_of_groups):
            with self.subTest(group=group):
                self.assertTrue(self.led_strip.group_is_rgb(group, BLACK_RGB))

    def clear_color_palettes(self):
        COLOR_PALETTE_NAMES = list(self.color_palette_selection.keys())

        for name in COLOR_PALETTE_NAMES:
            del self.color_palette_selection[name]


class DisplayedAudioInControllerTestCase(AudioInControllerTestCase):
    def setUp(self):
        super().setUp()

        self.audio_in_controller.display()


class TestDisplay(AudioInControllerTestCase):
    def test_display(self):
        self.audio_in_controller.display()

        self.assertTrue(self.widget_gui.open)

        SETTINGS_BUTTON: Button = self.get_widget(Element.SETTINGS_BUTTON)
        COLOR_PALETTE_BUTTON: Button = self.get_widget(Element.COLOR_PALETTE_BUTTON)
        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)

        CURRENT_INPUT_SOURCE_TEXT: Text = self.get_widget(Element.CURRENT_INPUT_SOURCE_TEXT)

        STOP_AUDIO_BUTTON: Button = self.get_widget(Element.STOP_AUDIO_BUTTON)
        PLAY_AUDIO_BUTTON: Button = self.get_widget(Element.PLAY_AUDIO_BUTTON)
        NEXT_COLOR_PALETTE_BUTTON: Button = self.get_widget(Element.NEXT_COLOR_PALETTE_BUTTON)

        LED_STRIP_TYPE_COMBO: Combo = self.get_widget(Element.LED_STRIP_TYPE_COMBO)

        self.assertTrue(SETTINGS_BUTTON.enabled)
        self.assertTrue(COLOR_PALETTE_BUTTON.enabled)
        self.assertTrue(CYCLE_COLOR_PALETTES_CHECKBOX.enabled)
        self.assertFalse(CYCLE_COLOR_PALETTES_CHECKBOX.value)
        self.assertTrue(SECONDS_PER_COLOR_PALETTE_INPUT.enabled)
        self.assertEqual(SECONDS_PER_COLOR_PALETTE_INPUT.value, '90')

        self.assertTrue(self.audio_in_stream.input_source.casefold() in CURRENT_INPUT_SOURCE_TEXT.value.casefold())

        self.assertFalse(STOP_AUDIO_BUTTON.enabled)
        self.assertTrue(PLAY_AUDIO_BUTTON.enabled)
        self.assertFalse(NEXT_COLOR_PALETTE_BUTTON.enabled)

        self.assertTrue(LED_STRIP_TYPE_COMBO.enabled)


class TestClose(DisplayedAudioInControllerTestCase):
    def test_close(self):
        self.audio_in_controller.close()

        self.assertFalse(self.settings_controller.running)
        self.assertFalse(self.color_palette_controller.running)
        self.assertFalse(self.widget_gui.open)
        self.assertFalse(self.audio_in_stream.opened)
        self.assertFalse(self.serial.opened)
        self.assertFalse(self.canvas_gui.opened)
        self.check_led_strip_is_off()


class TestReadEventAndUpdateGui(DisplayedAudioInControllerTestCase):
    def test_read_an_event(self):
        EXPECTED_EVENT = 'some event'

        self.widget_gui.event = EXPECTED_EVENT

        EVENT = self.audio_in_controller.read_event_and_update_gui()

        self.assertEqual(EXPECTED_EVENT, EVENT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_playing(self):
        self.audio_in_stream.opened = True
        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.audio_in_controller.read_event_and_update_gui()

        self.assertEqual(EVENT, Event.PLAYING)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)

    def test_not_playing(self):
        self.audio_in_stream.opened = False
        self.widget_gui.event = WidgetGuiEvent.TIMEOUT

        EVENT = self.audio_in_controller.read_event_and_update_gui()

        self.assertEqual(EVENT, WidgetGuiEvent.TIMEOUT)

        EXPECTED_NUMBER_OF_CALLS = 1
        self.assertEqual(self.widget_gui.number_of_read_event_and_update_gui_calls,
                         EXPECTED_NUMBER_OF_CALLS)


class TestHandleEvent(DisplayedAudioInControllerTestCase):
    def test_settings_button(self):
        self.audio_in_controller.handle_event(Element.SETTINGS_BUTTON)

        self.assertTrue(self.settings_controller.running)

    def test_color_palette_button(self):
        self.audio_in_controller.handle_event(Element.COLOR_PALETTE_BUTTON)

        self.assertTrue(self.color_palette_controller.running)

    def test_playing(self):
        AUDIO_CHUNK = b'hello'
        self.audio_in_stream.data = AUDIO_CHUNK

        self.audio_in_controller.handle_event(Event.PLAYING)

        self.assertIs(self.spectrogram.led_strip, self.led_strip)
        self.assertEqual(self.spectrogram.audio_data, AUDIO_CHUNK)

        MILLISECONDS_PER_SECOND = 1000
        FRAMES_PER_MILLISECOND = self.audio_in_stream.sample_rate / MILLISECONDS_PER_SECOND
        NUMBER_OF_FRAMES = int(FRAMES_PER_MILLISECOND * self.settings_selection.selected_value.milliseconds_per_audio_chunk)
        self.assertEqual(self.spectrogram.number_of_frames, NUMBER_OF_FRAMES)

        self.assertEqual(self.spectrogram.sampling_rate, self.audio_in_stream.sample_rate)

    def test_color_palette_shuffles(self):
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)
        SECONDS_PER_COLOR_PALETTE_INPUT.value = 0

        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        CYCLE_COLOR_PALETTES_CHECKBOX.value = True

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertEqual(self.spectrogram.amplitude_rgbs, self.color_palette_selection.selected_value.amplitude_rgbs)

        self.audio_in_controller.handle_event(Event.PLAYING)
        self.assertEqual(self.spectrogram.amplitude_rgbs, self.non_current_color_palette.amplitude_rgbs)

    def test_color_palette_does_not_shuffle_because_not_enough_time_has_passed(self):
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)
        SECONDS_PER_COLOR_PALETTE_INPUT.value = 90

        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        CYCLE_COLOR_PALETTES_CHECKBOX.value = True

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)
        self.audio_in_controller.handle_event(Event.PLAYING)

        self.assertEqual(self.spectrogram.amplitude_rgbs, self.color_palette_selection.selected_value.amplitude_rgbs)

        self.audio_in_controller.handle_event(Event.PLAYING)

        self.assertEqual(self.spectrogram.amplitude_rgbs, self.color_palette_selection.selected_value.amplitude_rgbs)

    def test_color_palette_does_not_shuffle_because_there_are_no_color_palettes(self):
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)
        SECONDS_PER_COLOR_PALETTE_INPUT.value = 90

        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        CYCLE_COLOR_PALETTES_CHECKBOX.value = True

        self.clear_color_palettes()

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)
        self.audio_in_controller.handle_event(Event.PLAYING)

        self.assertEqual(self.spectrogram.amplitude_rgbs, [])

        self.audio_in_controller.handle_event(Event.PLAYING)

        self.assertEqual(self.spectrogram.amplitude_rgbs, [])

    def test_color_palette_does_not_shuffle_because_shuffling_was_disabled(self):
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)
        SECONDS_PER_COLOR_PALETTE_INPUT.value = 90

        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        CYCLE_COLOR_PALETTES_CHECKBOX.value = False

        self.clear_color_palettes()

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)
        self.audio_in_controller.handle_event(Event.PLAYING)

        self.assertEqual(self.spectrogram.amplitude_rgbs, [])

        self.audio_in_controller.handle_event(Event.PLAYING)

        self.assertEqual(self.spectrogram.amplitude_rgbs, [])

    def test_stop_audio_button(self):
        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)
        self.audio_in_controller.handle_event(Element.STOP_AUDIO_BUTTON)

        self.check_led_strip_is_off()
        self.assertFalse(self.canvas_gui.opened)
        self.assertFalse(self.serial.opened)
        self.assertFalse(self.audio_in_stream.opened)

        self.check_gui_state_after_clicking_stop_button()

    def test_next_color_palette_button(self):
        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertEqual(self.spectrogram.amplitude_rgbs, self.color_palette_selection.selected_value.amplitude_rgbs)

        self.audio_in_controller.handle_event(Element.NEXT_COLOR_PALETTE_BUTTON)

        self.assertEqual(self.spectrogram.amplitude_rgbs, self.non_current_color_palette.amplitude_rgbs)

    def test_next_color_palette_button_with_no_color_palettes(self):
        self.clear_color_palettes()

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertEqual(self.spectrogram.amplitude_rgbs, [])

        self.audio_in_controller.handle_event(Element.NEXT_COLOR_PALETTE_BUTTON)

        self.assertEqual(self.spectrogram.amplitude_rgbs, [])

    def test_play_audio_with_color_palettes(self):
        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertTrue(self.audio_in_stream.opened)

        self.check_spectrogram(self.color_palette_selection.selected_value.amplitude_rgbs,
                               self.current_settings.minimum_frequency,
                               self.current_settings.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_with_no_color_palettes(self):
        self.clear_color_palettes()

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertTrue(self.audio_in_stream.opened)

        EXPECTED_SPECTROGRAM_AMPLITUDE_RGBS = []
        self.check_spectrogram(EXPECTED_SPECTROGRAM_AMPLITUDE_RGBS,
                               self.settings_selection.selected_value.minimum_frequency,
                               self.settings_selection.selected_value.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_with_zero_groups(self):
        self.settings_selection.selected_value.number_of_groups = 0

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertTrue(self.audio_in_stream.opened)

        self.check_spectrogram(self.color_palette_selection.selected_value.amplitude_rgbs,
                               self.settings_selection.selected_value.minimum_frequency,
                               self.settings_selection.selected_value.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_graphic_led_strip_type(self):
        LED_STRIP_TYPE_COMBO: Combo = self.get_widget(Element.LED_STRIP_TYPE_COMBO)
        LED_STRIP_TYPE_COMBO.value = LedStripType.GRAPHIC

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertTrue(self.audio_in_stream.opened)

        self.check_spectrogram(self.color_palette_selection.selected_value.amplitude_rgbs,
                               self.settings_selection.selected_value.minimum_frequency,
                               self.settings_selection.selected_value.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_serial_led_strip_type(self):
        LED_STRIP_TYPE_COMBO: Combo = self.get_widget(Element.LED_STRIP_TYPE_COMBO)
        LED_STRIP_TYPE_COMBO.value = LedStripType.SERIAL

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertTrue(self.audio_in_stream.opened)

        self.check_spectrogram(self.color_palette_selection.selected_value.amplitude_rgbs,
                               self.settings_selection.selected_value.minimum_frequency,
                               self.settings_selection.selected_value.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_unrecognized_led_strip_type(self):
        LED_STRIP_TYPE_COMBO: Combo = self.get_widget(Element.LED_STRIP_TYPE_COMBO)

        UNRECOGNIZED_LED_STRIP_TYPE = 'unrecognized strip type'
        LED_STRIP_TYPE_COMBO.add_value(UNRECOGNIZED_LED_STRIP_TYPE)
        LED_STRIP_TYPE_COMBO.value = UNRECOGNIZED_LED_STRIP_TYPE

        with self.assertRaises(ValueError):
            self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertFalse(self.audio_in_stream.opened)

        self.check_spectrogram(self.color_palette_selection.selected_value.amplitude_rgbs,
                               self.settings_selection.selected_value.minimum_frequency,
                               self.settings_selection.selected_value.maximum_frequency)

        self.check_gui_state_after_clicking_stop_button()

    def test_close_window(self):
        self.audio_in_controller.handle_event(WidgetGuiEvent.CLOSE_WINDOW)

        self.assertFalse(self.widget_gui.open)

    def test_timeout_event(self):
        self.audio_in_controller.handle_event(WidgetGuiEvent.TIMEOUT)

    def test_unrecognized_event(self):
        EVENT = 'unrecognized event'

        with self.assertRaises(ValueError):
            self.audio_in_controller.handle_event(EVENT)

    def check_spectrogram(self, amplitude_rgbs: List[Tuple[int, int, int]], start_frequency, end_frequency):
        self.assertEqual(self.spectrogram.amplitude_rgbs, amplitude_rgbs)
        self.assertEqual(self.spectrogram.start_frequency, start_frequency)
        self.assertEqual(self.spectrogram.end_frequency, end_frequency)

    def check_gui_state_after_clicking_play_button(self):
        SETTINGS_BUTTON: Button = self.get_widget(Element.SETTINGS_BUTTON)
        COLOR_PALETTE_BUTTON: Button = self.get_widget(Element.COLOR_PALETTE_BUTTON)
        STOP_BUTTON: Button = self.get_widget(Element.STOP_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.get_widget(Element.PLAY_AUDIO_BUTTON)
        LED_STRIP_TYPE_COMBO: Combo = self.get_widget(Element.LED_STRIP_TYPE_COMBO)
        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)

        self.assertFalse(SETTINGS_BUTTON.enabled)
        self.assertFalse(COLOR_PALETTE_BUTTON.enabled)
        self.assertTrue(STOP_BUTTON.enabled)
        self.assertFalse(RESUME_BUTTON.enabled)
        self.assertFalse(LED_STRIP_TYPE_COMBO.enabled)
        self.assertFalse(CYCLE_COLOR_PALETTES_CHECKBOX.enabled)
        self.assertFalse(SECONDS_PER_COLOR_PALETTE_INPUT.enabled)

        CURRENT_INPUT_SOURCE_TEXT: Text = self.get_widget(Element.CURRENT_INPUT_SOURCE_TEXT)
        self.assertTrue(self.audio_in_stream.input_source.casefold() in CURRENT_INPUT_SOURCE_TEXT.value.casefold())

    def check_gui_state_after_clicking_stop_button(self):
        SETTINGS_BUTTON: Button = self.get_widget(Element.SETTINGS_BUTTON)
        COLOR_PALETTE_BUTTON: Button = self.get_widget(Element.COLOR_PALETTE_BUTTON)
        STOP_BUTTON: Button = self.get_widget(Element.STOP_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.get_widget(Element.PLAY_AUDIO_BUTTON)
        LED_STRIP_TYPE_COMBO: Combo = self.get_widget(Element.LED_STRIP_TYPE_COMBO)
        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)

        self.assertTrue(SETTINGS_BUTTON.enabled)
        self.assertTrue(COLOR_PALETTE_BUTTON.enabled)
        self.assertFalse(STOP_BUTTON.enabled)
        self.assertTrue(RESUME_BUTTON.enabled)
        self.assertTrue(LED_STRIP_TYPE_COMBO.enabled)
        self.assertTrue(CYCLE_COLOR_PALETTES_CHECKBOX.enabled)
        self.assertTrue(SECONDS_PER_COLOR_PALETTE_INPUT.enabled)

        CURRENT_INPUT_SOURCE_TEXT: Text = self.get_widget(Element.CURRENT_INPUT_SOURCE_TEXT)
        self.assertTrue(self.audio_in_stream.input_source.casefold() in CURRENT_INPUT_SOURCE_TEXT.value.casefold())


class TestCreateGroups(TestCase):
    def test_start_led_is_negative(self):
        START_LED = -1
        END_LED = 0
        NUMBER_OF_GROUPS = 1

        with self.assertRaises(ValueError):
            _create_groups(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_end_led_is_negative(self):
        START_LED = 0
        END_LED = -1
        NUMBER_OF_GROUPS = 1

        with self.assertRaises(ValueError):
            _create_groups(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_zero_leds(self):
        START_LED = 0
        END_LED = 0
        NUMBER_OF_GROUPS = 5

        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), [])

    def test_one_led(self):
        START_LED = 0
        END_LED = 1
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 1)}, set(), set(), set(), set()]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_ten_leds(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 2)}, {(2, 4)}, {(4, 6)}, {(6, 8)}, {(8, 10)}]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_six_hundred_leds(self):
        START_LED = 0
        END_LED = 600
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 120)}, {(120, 240)}, {(240, 360)}, {(360, 480)}, {(480, 600)}]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_negative_leds(self):
        START_LED = 1
        END_LED = 0
        NUMBER_OF_GROUPS = 5

        with self.assertRaises(ValueError):
            _create_groups(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_zero_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 0

        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), [])

    def test_one_group(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 1

        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), [{(0, 100)}])

    def test_ten_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 10

        EXPECTED = [{(start, start + 10)} for start in range(START_LED, 91, 10)]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_one_hundred_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 100

        EXPECTED = [{(start, start + 1)} for start in range(START_LED, 100)]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_one_led_per_group(self):
        START_LED = 0
        END_LED = 5
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 1)}, {(1, 2)}, {(2, 3)}, {(3, 4)}, {(4, 5)}]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_two_leds_per_group(self):
        START_LED = 0
        END_LED = 6
        NUMBER_OF_GROUPS = 3

        EXPECTED = [{(0, 2)}, {(2, 4)}, {(4, 6)}]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_ten_leds_per_group(self):
        START_LED = 0
        END_LED = 50
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 10)}, {(10, 20)}, {(20, 30)}, {(30, 40)}, {(40, 50)}]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_negative_number_of_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = -1

        with self.assertRaises(ValueError):
            _create_groups(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_number_of_groups_greater_than_number_of_leds(self):
        START_LED = 0
        END_LED = 3
        NUMBER_OF_GROUPS = 4

        EXPECTED = [{(0, 1)}, {(1, 2)}, {(2, 3)}, set()]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_cannot_evenly_divide_number_of_leds_by_number_of_groups(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 3

        EXPECTED = [{(0, 3)}, {(3, 6)}, {(6, 9)}]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_zero(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 2)}, {(2, 4)}, {(4, 6)}, {(6, 8)}, {(8, 10)}]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_one(self):
        START_LED = 1
        END_LED = 11
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(1, 3)}, {(3, 5)}, {(5, 7)}, {(7, 9)}, {(9, 11)}]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_one_hundred(self):
        START_LED = 100
        END_LED = 110
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(100, 102)}, {(102, 104)}, {(104, 106)}, {(106, 108)}, {(108, 110)}]
        self.assertEqual(_create_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)


class TestCreateMirroredGroups(TestCase):
    def test_start_led_is_negative(self):
        START_LED = -1
        END_LED = 0
        NUMBER_OF_GROUPS = 1

        with self.assertRaises(ValueError):
            _create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_end_led_is_negative(self):
        START_LED = 0
        END_LED = -1
        NUMBER_OF_GROUPS = 1

        with self.assertRaises(ValueError):
            _create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_zero_leds(self):
        START_LED = 0
        END_LED = 0
        NUMBER_OF_GROUPS = 5

        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), [])

    def test_one_led(self):
        START_LED = 0
        END_LED = 1
        NUMBER_OF_GROUPS = 5

        EXPECTED = [set(), set(), set(), set(), {(0, 1)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_ten_leds(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(4, 5), (5, 6)}, {(3, 4), (6, 7)}, {(2, 3), (7, 8)}, {(1, 2), (8, 9)}, {(0, 1), (9, 10)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_six_hundred_leds(self):
        START_LED = 0
        END_LED = 600
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(240, 300), (300, 360)}, {(180, 240), (360, 420)},
                    {(120, 180), (420, 480)}, {(60, 120), (480, 540)},
                    {(0, 60), (540, 600)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_negative_leds(self):
        START_LED = 1
        END_LED = 0
        NUMBER_OF_GROUPS = 5

        with self.assertRaises(ValueError):
            _create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_zero_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 0

        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), [])

    def test_one_group(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 1

        EXPECTED = [{(0, 50), (50, 100)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_five_groups(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(4, 5), (5, 6)}, {(3, 4), (6, 7)}, {(2, 3), (7, 8)}, {(1, 2), (8, 9)}, {(0, 1), (9, 10)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_negative_number_of_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = -1

        with self.assertRaises(ValueError):
            _create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_number_of_groups_greater_than_number_of_leds(self):
        START_LED = 0
        END_LED = 3
        NUMBER_OF_GROUPS = 4

        EXPECTED = [set(), {(2, 3)}, {(1, 2)}, {(0, 1)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_cannot_evenly_divide_number_of_leds_by_number_of_groups(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 3

        EXPECTED = [{(2, 3), (3, 4)}, {(1, 2), (4, 5)}, {(0, 1), (5, 6)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_zero(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(4, 5), (5, 6)}, {(3, 4), (6, 7)},
                    {(2, 3), (7, 8)}, {(1, 2), (8, 9)},
                    {(0, 1), (9, 10)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_one(self):
        START_LED = 1
        END_LED = 11
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(5, 6), (6, 7)}, {(4, 5), (7, 8)},
                    {(3, 4), (8, 9)}, {(2, 3), (9, 10)},
                    {(1, 2), (10, 11)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_one_hundred(self):
        START_LED = 100
        END_LED = 110
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(104, 105), (105, 106)}, {(103, 104), (106, 107)},
                    {(102, 103), (107, 108)}, {(101, 102), (108, 109)},
                    {(100, 101), (109, 110)}]
        self.assertEqual(_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)
