from typing import Hashable, List, Tuple
from unittest import TestCase

from color_palette import ColorPalette, ColorPaletteSelection
from controller.__tests__.fake_widget_gui import FakeWidgetGui, WidgetGuiEvent
from controller.audio_in_controller import AudioInController, Element, Event, LedStripType
from controller.controller import RunnableResource
from led_strip.led_strip import FakeLedStrip
from libraries.audio_in_stream import AudioInStream
from libraries.canvas_gui import CanvasGui
from libraries.serial import FakeSerial
from libraries.widget import Button, CheckBox, Combo, Input, Text, Widget
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

        CURRENT_COLOR_PALETTE_NAME = 'color_palette_A'
        NON_CURRENT_COLOR_PALETTE_NAME = 'color_palette_B'

        self.current_color_palette = ColorPalette(AMPLITUDE_RGBS_A)
        self.non_current_color_palette = ColorPalette(AMPLITUDE_RGBS_B)

        COLOR_PALETTES = {CURRENT_COLOR_PALETTE_NAME: self.current_color_palette,
                          NON_CURRENT_COLOR_PALETTE_NAME: self.non_current_color_palette}

        START_LED = 0
        END_LED = 300
        MILLISECONDS_PER_AUDIO_CHUNK = 50
        SERIAL_PORT = '/dev/ttyACM0'
        SERIAL_BAUDRATE = 1000000
        BRIGHTNESS = 20
        START_FREQUENCY = 0
        END_FREQUENCY = 2000
        SHOULD_REVERSE_LEDS = True
        NUMBER_OF_GROUPS = 60

        self.settings_controller = FakeRunnableResource()
        self.settings = Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK, SERIAL_PORT,
                                 SERIAL_BAUDRATE, BRIGHTNESS, START_FREQUENCY, END_FREQUENCY,
                                 SHOULD_REVERSE_LEDS, NUMBER_OF_GROUPS)
        self.color_palette_controller = FakeRunnableResource()
        self.color_palette_selection = ColorPaletteSelection(COLOR_PALETTES)
        self.widget_gui = FakeWidgetGui()
        self.canvas_gui = FakeCanvasGui()
        self.serial = FakeSerial()
        self.audio_in_stream = FakeAudioInStream()
        self.led_strip = FakeLedStrip()
        self.spectrogram = FakeSpectrogram()

        def create_settings_controller(settings: Settings):
            return self.settings_controller

        def create_color_palette_controller(color_palette_selection: ColorPaletteSelection):
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

        self.audio_in_controller = AudioInController(create_settings_controller, self.settings,
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
        COLOR_PALETTE_NAMES = list(self.color_palette_selection.names())

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
        NUMBER_OF_FRAMES = int(FRAMES_PER_MILLISECOND * self.settings.milliseconds_per_audio_chunk)
        self.assertEqual(self.spectrogram.number_of_frames, NUMBER_OF_FRAMES)

        self.assertEqual(self.spectrogram.sampling_rate, self.audio_in_stream.sample_rate)

    def test_color_palette_shuffles(self):
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)
        SECONDS_PER_COLOR_PALETTE_INPUT.value = 0

        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        CYCLE_COLOR_PALETTES_CHECKBOX.value = True

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertEqual(self.spectrogram.amplitude_rgbs, self.current_color_palette.amplitude_rgbs)

        self.audio_in_controller.handle_event(Event.PLAYING)
        self.assertEqual(self.spectrogram.amplitude_rgbs, self.non_current_color_palette.amplitude_rgbs)

    def test_color_palette_does_not_shuffle_because_not_enough_time_has_passed(self):
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)
        SECONDS_PER_COLOR_PALETTE_INPUT.value = 90

        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        CYCLE_COLOR_PALETTES_CHECKBOX.value = True

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)
        self.audio_in_controller.handle_event(Event.PLAYING)

        self.assertEqual(self.spectrogram.amplitude_rgbs, self.current_color_palette.amplitude_rgbs)

        self.audio_in_controller.handle_event(Event.PLAYING)

        self.assertEqual(self.spectrogram.amplitude_rgbs, self.current_color_palette.amplitude_rgbs)

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

        self.assertEqual(self.spectrogram.amplitude_rgbs, self.current_color_palette.amplitude_rgbs)

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

        self.check_spectrogram(self.current_color_palette.amplitude_rgbs,
                               self.settings.minimum_frequency,
                               self.settings.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_with_no_color_palettes(self):
        self.clear_color_palettes()

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertTrue(self.audio_in_stream.opened)

        EXPECTED_SPECTROGRAM_AMPLITUDE_RGBS = []
        self.check_spectrogram(EXPECTED_SPECTROGRAM_AMPLITUDE_RGBS,
                               self.settings.minimum_frequency,
                               self.settings.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_with_zero_groups(self):
        self.settings.number_of_groups = 0

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertTrue(self.audio_in_stream.opened)

        self.check_spectrogram(self.current_color_palette.amplitude_rgbs,
                               self.settings.minimum_frequency,
                               self.settings.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_graphic_led_strip_type(self):
        LED_STRIP_TYPE_COMBO: Combo = self.get_widget(Element.LED_STRIP_TYPE_COMBO)
        LED_STRIP_TYPE_COMBO.value = LedStripType.GRAPHIC

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertTrue(self.audio_in_stream.opened)

        self.check_spectrogram(self.current_color_palette.amplitude_rgbs,
                               self.settings.minimum_frequency,
                               self.settings.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_serial_led_strip_type(self):
        LED_STRIP_TYPE_COMBO: Combo = self.get_widget(Element.LED_STRIP_TYPE_COMBO)
        LED_STRIP_TYPE_COMBO.value = LedStripType.SERIAL

        self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertTrue(self.audio_in_stream.opened)

        self.check_spectrogram(self.current_color_palette.amplitude_rgbs,
                               self.settings.minimum_frequency,
                               self.settings.maximum_frequency)

        self.check_gui_state_after_clicking_play_button()

    def test_play_audio_unrecognized_led_strip_type(self):
        LED_STRIP_TYPE_COMBO: Combo = self.get_widget(Element.LED_STRIP_TYPE_COMBO)

        UNRECOGNIZED_LED_STRIP_TYPE = 'unrecognized strip type'
        LED_STRIP_TYPE_COMBO.add_value(UNRECOGNIZED_LED_STRIP_TYPE)
        LED_STRIP_TYPE_COMBO.value = UNRECOGNIZED_LED_STRIP_TYPE

        with self.assertRaises(ValueError):
            self.audio_in_controller.handle_event(Element.PLAY_AUDIO_BUTTON)

        self.assertFalse(self.audio_in_stream.opened)

        self.check_spectrogram(self.current_color_palette.amplitude_rgbs,
                               self.settings.minimum_frequency,
                               self.settings.maximum_frequency)

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
