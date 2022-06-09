from enum import Enum, auto
from typing import List, Tuple, Union

import pyaudio
from controller.settings_controller import SettingsController
from led_strip.grouped_leds import GraphicGroupedLeds, SerialGroupedLeds
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.canvas_gui import ProductionCanvasGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial
from libraries.widget_gui import Font, WidgetGui, WidgetGuiEvent
from libraries.widget import Button, Combo, Text
from spectrogram import Spectrogram
from util import Font, Settings


class Element(Enum):
    LED_STRIP_COMBO = auto()

    PAUSE_AUDIO_BUTTON = auto()
    RESUME_AUDIO_BUTTON = auto()

    CURRENT_INPUT_SOURCE_MESSAGE = auto()
    SELECT_INPUT_SOURCE_DROPDOWN = auto()
    SELECT_INPUT_SOURCE_LABEL = auto()

    CONFIRMATION_MODAL_OK_BUTTON = auto()
    SELECT_VISUALIZER_TYPE_LABEL = auto()
    SETTINGS_BUTTON = auto()


class Event(Enum):
    PLAYING = auto()


class State(Enum):
    PLAYING = auto()
    PAUSED = auto()


class AudioInController:
    def __init__(self, widget_gui: WidgetGui, settings_controller: SettingsController):
        self.__widget_gui = widget_gui

        self.__settings_controller = settings_controller

        self._audio_player_generator = pyaudio.PyAudio()
        self.__audio_player: pyaudio.Stream = None
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

    def read_event_and_update_gui(self) -> Union[Element, WidgetGuiEvent]:
        EVENT = self.__widget_gui.read_event_and_update_gui()

        if (EVENT == WidgetGuiEvent.TIMEOUT and self.__is_state(State.PLAYING)):
            return Event.PLAYING

        return EVENT

    def handle_event(self, event: Union[Element, WidgetGuiEvent]):
        if (event == Element.SETTINGS_BUTTON):
            self.__settings_controller.display()
            settings_event = self.__settings_controller.read_event_and_update_gui()

            while (settings_event != WidgetGuiEvent.CLOSE_WINDOW):
                self.__settings_controller.handle_event(settings_event)
                settings_event = self.__settings_controller.read_event_and_update_gui()

            self.__settings_controller.handle_event(settings_event)

        elif (event == Event.PLAYING):
            MILLISECONDS_PER_SECOND = 1000
            frames_per_millisecond = self.__audio_player._rate / MILLISECONDS_PER_SECOND  # sample rate (frames / second) / 1000 ms/second = frames / millisecond

            number_of_frames = int(frames_per_millisecond * self.__settings.milliseconds_per_audio_chunk)  # frames / ms * ms = frames

            AUDIO_CHUNK = self.__audio_player.read(number_of_frames)

            self.__spectrogram.update_led_strips(self.__led_strip, AUDIO_CHUNK, number_of_frames,
                                                 self.__audio_player._rate)

        elif (event == Element.PAUSE_AUDIO_BUTTON):
            self.__audio_player.stop_stream()
            self.__delete_spectrogram()
            self.__set_audio_paused_state()

        elif (event == Element.RESUME_AUDIO_BUTTON):
            input_source = self._audio_player_generator.get_default_input_device_info()["name"]
            CURRENT_INPUT_SOURCE = f"Input Source : {input_source}"

            CURRENT_INPUT_SOURCE_TEXT = self.__widget_gui.get_widget(Element.CURRENT_INPUT_SOURCE_MESSAGE)
            CURRENT_INPUT_SOURCE_TEXT.value = CURRENT_INPUT_SOURCE
            self.__widget_gui.update_widget(CURRENT_INPUT_SOURCE_TEXT)

            self.__init_spectrogram()
            self.__audio_player.start_stream()
            self.__set_audio_playing_state()

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.__widget_gui.close()

        elif (event != WidgetGuiEvent.TIMEOUT):
            raise ValueError(f'The event {event} is not a recognized event.')

    def display(self):
        TITLE_TEXT = Font("Courier New", 20)
        FONT = Font("Courier New", 14)

        LED_STRIP_COMBO_VALUES = ['Graphic LED Strip', 'Serial LED Strip']
        LED_STRIP_COMBO = Combo(Element.LED_STRIP_COMBO, LED_STRIP_COMBO_VALUES)

        LAYOUT = [[Button(Element.SETTINGS_BUTTON, text="Settings")],

                  [Text(Element.CURRENT_INPUT_SOURCE_MESSAGE, text="No audio currently playing.", font=TITLE_TEXT)],

                  [Button(Element.PAUSE_AUDIO_BUTTON, text="Stop ([])", font=FONT, enabled=False),
                   Button(Element.RESUME_AUDIO_BUTTON, text="Play (>)", font=FONT, enabled=True)],

                  [Text(Element.SELECT_VISUALIZER_TYPE_LABEL, text="LED Strip Type : ", font=FONT),
                   LED_STRIP_COMBO]]

        self.__widget_gui.set_layout(LAYOUT)
        self.__widget_gui.display_layout()

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

    def __set_audio_paused_state(self):
        SETTINGS_BUTTON: Button = self.__widget_gui.get_widget(Element.SETTINGS_BUTTON)
        PAUSE_BUTTON: Button = self.__widget_gui.get_widget(Element.PAUSE_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.__widget_gui.get_widget(Element.RESUME_AUDIO_BUTTON)
        LED_STRIP_COMBO: Combo = self.__widget_gui.get_widget(Element.LED_STRIP_COMBO)

        SETTINGS_BUTTON.enabled = True
        PAUSE_BUTTON.enabled = False
        RESUME_BUTTON.enabled = True
        LED_STRIP_COMBO.enabled = True

        self.__widget_gui.update_widget(SETTINGS_BUTTON)
        self.__widget_gui.update_widget(PAUSE_BUTTON)
        self.__widget_gui.update_widget(RESUME_BUTTON)
        self.__widget_gui.update_widget(LED_STRIP_COMBO)

    def __set_audio_playing_state(self):
        SETTINGS_BUTTON: Button = self.__widget_gui.get_widget(Element.SETTINGS_BUTTON)
        PAUSE_BUTTON: Button = self.__widget_gui.get_widget(Element.PAUSE_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.__widget_gui.get_widget(Element.RESUME_AUDIO_BUTTON)
        LED_STRIP_COMBO: Combo = self.__widget_gui.get_widget(Element.LED_STRIP_COMBO)

        SETTINGS_BUTTON.enabled = False
        PAUSE_BUTTON.enabled = True
        RESUME_BUTTON.enabled = False
        LED_STRIP_COMBO.enabled = True

        self.__widget_gui.update_widget(SETTINGS_BUTTON)
        self.__widget_gui.update_widget(PAUSE_BUTTON)
        self.__widget_gui.update_widget(RESUME_BUTTON)
        self.__widget_gui.update_widget(LED_STRIP_COMBO)

    def __get_group_index_to_led_range(self) -> List[Tuple[int, int]]:
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

    def __get_led_strip(self):
        LED_STRIP_COMBO = self.__widget_gui.get_widget(Element.LED_STRIP_COMBO)

        LED_RANGE = (self.__settings.start_led, self.__settings.end_led)

        if (LED_STRIP_COMBO.value == 'Serial LED Strip'):
            PARITY = PARITY_NONE
            STOP_BITS = STOPBITS_ONE_POINT_FIVE
            BYTE_SIZE = EIGHTBITS
            READ_TIMEOUT = 1
            WRITE_TIMEOUT = 0

            serial = ProductionSerial(self.__settings.serial_port, self.__settings.serial_baudrate,
                                      PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)

            serial_grouped_leds = SerialGroupedLeds(LED_RANGE, self.__get_group_index_to_led_range(),
                                                    serial, self.__settings.brightness)

            return ProductionLedStrip(serial_grouped_leds)

        if (LED_STRIP_COMBO.value == 'Graphic LED Strip'):
            WIDTH = 1350
            HEIGHT = 600

            gui = ProductionCanvasGui(WIDTH, HEIGHT)
            gui.update()

            graphic_grouped_leds = GraphicGroupedLeds(LED_RANGE, self.__get_group_index_to_led_range(), gui)

            return ProductionLedStrip(graphic_grouped_leds)

    def __init_spectrogram(self):
        self.__delete_spectrogram()

        FREQUENCY_RANGE = (self.__settings.minimum_frequency,
                           self.__settings.maximum_frequency)
        self.__led_strip = self.__get_led_strip()

        self.__spectrogram = Spectrogram(FREQUENCY_RANGE, self.__settings.amplitude_rgbs)

    def __delete_spectrogram(self):
        if (self.__led_strip is not None):
            del self.__led_strip
            self.__led_strip = None

        if (self.__spectrogram is not None):
            del self.__spectrogram
            self.__spectrogram = None
