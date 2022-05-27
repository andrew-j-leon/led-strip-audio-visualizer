from enum import Enum, auto
from typing import List, Tuple

import pyaudio
from controller.settings_controller import SettingsController
from util import Settings, Font
from led_strip.grouped_leds import GraphicGroupedLeds, SerialGroupedLeds
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.widget_gui import Button, CheckBox, Combo, Font, Text, ProductionWidgetGui, WidgetGui, WidgetGuiEvent
from libraries.canvas_gui import ProductionCanvasGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial
from spectrogram import Spectrogram


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
    def __init__(self, widget_gui: WidgetGui = ProductionWidgetGui(),
                 settings_controller: SettingsController = SettingsController()):
        self.__widget_gui = widget_gui

        self.__settings_controller = settings_controller

        self._audio_player_generator = pyaudio.PyAudio()
        self.__audio_player: pyaudio.Stream = None
        self.__audio_chunk: bytes = b''
        self.__init_audio_player()

        self.__spectrogram: Spectrogram = None
        self.__led_strip: LedStrip = None

    @property
    def __settings(self) -> Settings:
        return self.__settings_controller.settings

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

    def run(self):
        CURRENT_INPUT_SOURCE_FONT = Font("Courier New", 20)
        BUTTON_FONT = Font("Courier New", 14)
        INPUT_LABEL_FONT = Font("Courier New", 14)
        DROPDOWN_INPUT_FONT = Font("Courier New", 14)
        CHECKBOX_INPUT_FONT = Font("Courier New", 14)

        VISUALIZER_DROPDOWN_VALUES = [VisualizerType.NONE, VisualizerType.FREQUENCY]
        VISUALIZER_DROPDOWN_WIDGET = Combo(Element.SELECT_VISUALIZER_TYPE_DROPDOWN, VISUALIZER_DROPDOWN_VALUES,
                                           DROPDOWN_INPUT_FONT)
        VISUALIZER_DROPDOWN_WIDGET.value = VisualizerType.FREQUENCY

        LAYOUT = [[Button(Element.SETTINGS_BUTTON, text="Settings")],

                  [Text(Element.CURRENT_INPUT_SOURCE_MESSAGE, text="No audio currently playing.", font=CURRENT_INPUT_SOURCE_FONT)],

                  [Button(Element.PAUSE_AUDIO_BUTTON, text="Stop ([])", font=BUTTON_FONT, disabled=True),
                   Button(Element.RESUME_AUDIO_BUTTON, text="Play (>)", font=BUTTON_FONT, disabled=False)],

                  [Text(Element.SELECT_VISUALIZER_TYPE_LABEL, text="Visualizer : ", font=INPUT_LABEL_FONT),
                   VISUALIZER_DROPDOWN_WIDGET,
                   CheckBox(Element.SERIAL_LED_STRIP_CHECKBOX, text="Serial Led Strip", font=CHECKBOX_INPUT_FONT),
                   CheckBox(Element.GRAPHIC_LED_STRIP_CHECKBOX, text="Graphic Led Strip", font=CHECKBOX_INPUT_FONT)]]

        self.__widget_gui.set_layout(LAYOUT)

        self.__widget_gui.display_layout()

        while True:
            event = self.__widget_gui.read_event_and_update_gui()

            if (event == Element.SETTINGS_BUTTON):
                self.__settings_controller.draw_widget_gui()
                settings_event = self.__settings_controller.read_event_and_update_gui()

                while (settings_event != WidgetGuiEvent.CLOSE_WINDOW):
                    self.__settings_controller.handle_event(settings_event)
                    settings_event = self.__settings_controller.read_event_and_update_gui()

                self.__settings_controller.handle_event(settings_event)

            if (self.__is_state(State.PLAYING)):
                MILLISECONDS_PER_SECOND = 1000
                frames_per_millisecond = self.__audio_player._rate / MILLISECONDS_PER_SECOND  # sample rate (frames / second) / 1000 ms/second = frames / millisecond

                number_of_frames = int(frames_per_millisecond * self.__settings.milliseconds_per_audio_chunk)  # frames / ms * ms = frames

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

        if (len(default_input_device_info) == 0):
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
                return self.__settings.end_led - self.__settings.start_led

            number_of_leds_per_group = max(1, get_number_of_leds() // self.__settings.number_of_groups)
            group_index_to_led_range = list()

            for group_index in range(self.__settings.number_of_groups):
                shifted_start_index = group_index * number_of_leds_per_group + self.__settings.start_led

                shifted_end_index = shifted_start_index + number_of_leds_per_group

                group_index_to_led_range.append((shifted_start_index, shifted_end_index))

            if (self.__settings.should_reverse_leds):
                group_index_to_led_range.reverse()

            return group_index_to_led_range

        def get_led_strip():
            use_serial_led_strip = self.__widget_gui.get_widget_value(Element.SERIAL_LED_STRIP_CHECKBOX)
            use_graphic_led_strip = self.__widget_gui.get_widget_value(Element.GRAPHIC_LED_STRIP_CHECKBOX)

            LED_RANGE = (self.__settings.start_led, self.__settings.end_led)

            if (use_serial_led_strip):
                PARITY = PARITY_NONE
                STOP_BITS = STOPBITS_ONE_POINT_FIVE
                BYTE_SIZE = EIGHTBITS
                READ_TIMEOUT = 1
                WRITE_TIMEOUT = 0

                serial = ProductionSerial(self.__settings.serial_port, self.__settings.serial_baudrate,
                                          PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)

                serial_grouped_leds = SerialGroupedLeds(LED_RANGE, get_group_index_to_led_range(),
                                                        serial, self.__settings.brightness)

                return ProductionLedStrip(serial_grouped_leds)

            if (use_graphic_led_strip):
                WIDTH = 1350
                HEIGHT = 600

                gui = ProductionCanvasGui(WIDTH, HEIGHT)
                gui.update()

                graphic_grouped_leds = GraphicGroupedLeds(LED_RANGE, get_group_index_to_led_range(), gui)

                return ProductionLedStrip(graphic_grouped_leds)

        def init_spectrogram():
            self.__delete_spectrogram()
            visualizer_dropdown_value = self.__widget_gui.get_widget_value(Element.SELECT_VISUALIZER_TYPE_DROPDOWN)

            if (visualizer_dropdown_value == VisualizerType.FREQUENCY):
                FREQUENCY_RANGE = (self.__settings.minimum_frequency,
                                   self.__settings.maximum_frequency)
                self.__led_strip = get_led_strip()

                self.__spectrogram = Spectrogram(FREQUENCY_RANGE, self.__settings.amplitude_rgbs)

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
