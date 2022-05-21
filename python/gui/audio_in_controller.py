from enum import Enum, auto
from typing import List, Tuple

import pyaudio
import util.util as util
from gui.setting.setting_controller import SettingController
from led_strip.grouped_leds import GraphicGroupedLeds, SerialGroupedLeds
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.gui import Button, CheckBox, Combo, Font, ProductionCanvasGui, Text, WidgetGui, WidgetGuiEvent
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial
from visualizer.spectrogram import Spectrogram


class Element(Enum):
    SELECT_VISUALIZER_TYPE_DROPDOWN = auto()
    SERIAL_LED_STRIP_CHECKBOX = auto()
    GRAPHIC_LED_STRIP_CHECKBOX = auto()

    PAUSE_AUDIO_BUTTON = auto()
    RESUME_AUDIO_BUTTON = auto()

    CURRENT_INPUT_SOURCE_MESSAGE = auto()
    SELECT_INPUT_SOURCE_DROPDOWN = auto()
    SELECT_INPUT_SOURCE_LABEL = auto()

    CONFIRMATION_MODAL_OK_BUTTON = auto()
    SELECT_VISUALIZER_TYPE_LABEL = auto()
    SETTINGS_BUTTON = auto()


class VisualizerType:
    NONE = "None"
    FREQUENCY = "Frequency"


class State(Enum):
    PLAYING = auto()
    PAUSED = auto()


class AudioInController:
    def __init__(self, widget_gui: WidgetGui):
        self.__setting_controller = SettingController()
        self.__widget_gui = widget_gui

        self._audio_player_generator = pyaudio.PyAudio()
        self.__audio_player: pyaudio.Stream = None
        self.__audio_chunk: bytes = b''
        self.__init_audio_player()

        self.__spectrogram: Spectrogram = None
        self.__led_strip: LedStrip = None

    def __del__(self):
        self.__delete_spectrogram()

        if (self.__led_strip is not None):
            BLACK_RGB = (0, 0, 0)

            self.__led_strip.clear_queued_colors()

            for group in range(self.__led_strip.number_of_groups):
                self.__led_strip.enqueue_rgb(group, BLACK_RGB)

            self.__led_strip.show_queued_colors()

            del self.__led_strip
            self.__led_strip = None

        self.__close_audio_player()

        if (self._audio_player_generator is not None):
            self._audio_player_generator.terminate()

    def start(self):
        CURRENT_INPUT_SOURCE_FONT = Font("Courier New", 20)
        BUTTON_FONT = Font("Courier New", 14)
        INPUT_LABEL_FONT = Font("Courier New", 14)
        DROPDOWN_INPUT_FONT = Font("Courier New", 14)
        CHECKBOX_INPUT_FONT = Font("Courier New", 14)

        VISUALIZER_DROPDOWN_VALUES = [VisualizerType.NONE, VisualizerType.FREQUENCY]

        LAYOUT = [[Button(Element.SETTINGS_BUTTON, text="Settings")],

                  [Text(Element.CURRENT_INPUT_SOURCE_MESSAGE, text="No audio currently playing.", font=CURRENT_INPUT_SOURCE_FONT)],

                  [Button(Element.PAUSE_AUDIO_BUTTON, text="Pause (||)", font=BUTTON_FONT, disabled=True),
                   Button(Element.RESUME_AUDIO_BUTTON, text="Resume (>)", font=BUTTON_FONT, disabled=False)],

                  [Text(Element.SELECT_VISUALIZER_TYPE_LABEL, text="Visualizer : ", font=INPUT_LABEL_FONT),
                   Combo(Element.SELECT_VISUALIZER_TYPE_DROPDOWN, values=VISUALIZER_DROPDOWN_VALUES,
                         default_value=VisualizerType.FREQUENCY, font=DROPDOWN_INPUT_FONT),
                   CheckBox(Element.SERIAL_LED_STRIP_CHECKBOX, text="Serial Led Strip", font=CHECKBOX_INPUT_FONT),
                   CheckBox(Element.GRAPHIC_LED_STRIP_CHECKBOX, text="Graphic Led Strip", font=CHECKBOX_INPUT_FONT)]]

        self.__widget_gui.set_layout(LAYOUT)

        self.__widget_gui.update_display()

        while True:
            event = self.__widget_gui.read_event()

            if (event == Element.SETTINGS_BUTTON):
                self.__setting_controller.run_concurrent()

            if (self.__is_state(State.PLAYING)):
                MILLISECONDS_PER_SECOND = 1000
                frames_per_millisecond = self.__audio_player._rate / MILLISECONDS_PER_SECOND  # sample rate (frames / second) / 1000 ms/second = frames / millisecond

                milleseconds_per_audio_chunk = self.__setting_controller.get_milliseconds_per_audio_chunk()  # ms
                number_of_frames = int(frames_per_millisecond * milleseconds_per_audio_chunk)  # frames / ms * ms = frames

                self.__audio_chunk = self.__audio_player.read(number_of_frames)

                self.__spectrogram.update_led_strips(self.__led_strip, self.__audio_chunk, number_of_frames,
                                                     self.__audio_player._rate)

            if (event != WidgetGuiEvent.TIMEOUT):
                self.__handle_ui_event(event)

            if (event == WidgetGuiEvent.CLOSE_WINDOW):
                break

    def __is_state(self, state: str) -> bool:
        if (state == State.PLAYING):
            return (isinstance(self.__audio_player, pyaudio.Stream) and self.__audio_player.is_active())

        elif (state == State.PAUSED):
            return (isinstance(self.__audio_player, pyaudio.Stream) and self.__audio_player.is_stopped())

        return False

    def __init_audio_player(self):
        default_input_device_info: dict = self._audio_player_generator.get_default_input_device_info()

        if (util.is_empty(default_input_device_info)):
            raise ValueError("There is no default input device set on this machine.")

        self.__close_audio_player()

        self.__audio_player = self._audio_player_generator.open(format=pyaudio.paInt16, channels=default_input_device_info["maxInputChannels"],
                                                                rate=int(default_input_device_info["defaultSampleRate"]), input=True)

        self.__audio_player.stop_stream()

    def __close_audio_player(self):
        if (self.__audio_player):
            self.__audio_player.close()
            self.__audio_player = None

    def __handle_ui_event(self, event: str):
        def set_audio_paused_state():
            self.__widget_gui.enable_widget(Element.SETTINGS_BUTTON)
            self.__widget_gui.disable_widget(Element.PAUSE_AUDIO_BUTTON)
            self.__widget_gui.enable_widget(Element.RESUME_AUDIO_BUTTON)

            self.__widget_gui.enable_widget(Element.SELECT_VISUALIZER_TYPE_DROPDOWN)
            self.__widget_gui.enable_widget(Element.SERIAL_LED_STRIP_CHECKBOX)
            self.__widget_gui.enable_widget(Element.GRAPHIC_LED_STRIP_CHECKBOX)

        def set_audio_playing_state():
            self.__widget_gui.disable_widget(Element.SETTINGS_BUTTON)
            self.__widget_gui.enable_widget(Element.PAUSE_AUDIO_BUTTON)
            self.__widget_gui.disable_widget(Element.RESUME_AUDIO_BUTTON)

            self.__widget_gui.disable_widget(Element.SELECT_VISUALIZER_TYPE_DROPDOWN)
            self.__widget_gui.disable_widget(Element.SERIAL_LED_STRIP_CHECKBOX)
            self.__widget_gui.disable_widget(Element.GRAPHIC_LED_STRIP_CHECKBOX)

        def get_group_index_to_led_range() -> List[Tuple[int, int]]:
            def get_number_of_leds() -> int:
                start_led = self.__setting_controller.get_start_led_index()
                end_led = self.__setting_controller.get_end_led_index()

                return end_led - start_led

            number_of_groups = self.__setting_controller.get_number_of_groups()

            number_of_leds_per_group = max(1, get_number_of_leds() // number_of_groups)
            group_index_to_led_range = list()

            for group_index in range(number_of_groups):
                start_led = self.__setting_controller.get_start_led_index()
                shifted_start_index = group_index * number_of_leds_per_group + start_led

                shifted_end_index = shifted_start_index + number_of_leds_per_group

                group_index_to_led_range.append((shifted_start_index, shifted_end_index))

            if (self.__setting_controller.should_reverse_indicies()):
                group_index_to_led_range.reverse()

            return group_index_to_led_range

        def get_led_strip():
            use_serial_led_strip = self.__widget_gui.get_widget_value(Element.SERIAL_LED_STRIP_CHECKBOX)
            use_graphic_led_strip = self.__widget_gui.get_widget_value(Element.GRAPHIC_LED_STRIP_CHECKBOX)

            start_led = self.__setting_controller.get_start_led_index()
            end_led = self.__setting_controller.get_end_led_index()

            led_range = (start_led, end_led)

            if (use_serial_led_strip):
                PORT = self.__setting_controller.get_serial_port()
                BAUDRATE = self.__setting_controller.get_serial_baudrate()
                PARITY = PARITY_NONE
                STOP_BITS = STOPBITS_ONE_POINT_FIVE
                BYTE_SIZE = EIGHTBITS
                READ_TIMEOUT = 1
                WRITE_TIMEOUT = 0

                serial = ProductionSerial(PORT, BAUDRATE, PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)
                brightness = self.__setting_controller.get_brightness()

                serial_grouped_leds = SerialGroupedLeds(led_range, get_group_index_to_led_range(),
                                                        serial, brightness)

                return ProductionLedStrip(serial_grouped_leds)

            if (use_graphic_led_strip):
                WIDTH = 1350
                HEIGHT = 600

                gui = ProductionCanvasGui(WIDTH, HEIGHT)
                gui.update()

                graphic_grouped_leds = GraphicGroupedLeds(led_range, get_group_index_to_led_range(), gui)

                return ProductionLedStrip(graphic_grouped_leds)

        def init_spectrogram():
            self.__delete_spectrogram()
            visualizer_dropdown_value = self.__widget_gui.get_widget_value(Element.SELECT_VISUALIZER_TYPE_DROPDOWN)

            if (visualizer_dropdown_value == VisualizerType.FREQUENCY):
                start_frequency = self.__setting_controller.get_minimum_frequency()
                end_frequency = self.__setting_controller.get_maximum_frequency()

                FREQUENCY_RANGE = (start_frequency, end_frequency)
                AMPLITUDE_TO_RGB = self.__setting_controller.get_amplitude_to_rgb()
                self.__led_strip = get_led_strip()

                self.__spectrogram = Spectrogram(FREQUENCY_RANGE, AMPLITUDE_TO_RGB)

        if (event == Element.PAUSE_AUDIO_BUTTON):
            self.__audio_player.stop_stream()
            self.__delete_spectrogram()
            set_audio_paused_state()

        elif (event == Element.RESUME_AUDIO_BUTTON):
            input_source = self._audio_player_generator.get_default_input_device_info()["name"]
            CURRENT_INPUT_SOURCE = f"Input Source : {input_source}"
            self.__widget_gui.set_widget_value(Element.CURRENT_INPUT_SOURCE_MESSAGE, CURRENT_INPUT_SOURCE)

            init_spectrogram()
            self.__audio_player.start_stream()
            set_audio_playing_state()

    def __delete_spectrogram(self):
        if (self.__spectrogram is not None):
            del self.__spectrogram
            self.__spectrogram = None
