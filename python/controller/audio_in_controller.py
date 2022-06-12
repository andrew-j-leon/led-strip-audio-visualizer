from __future__ import annotations

from enum import Enum, auto
from typing import Callable, List, Tuple, Union

from controller.settings_controller import SettingsController
from led_strip.grouped_leds import GraphicGroupedLeds, GroupedLeds, SerialGroupedLeds
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.audio_in_stream import AudioInStream
from libraries.canvas_gui import CanvasGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, Serial
from libraries.widget import Button, Combo, Text
from libraries.widget_gui import Font, WidgetGui, WidgetGuiEvent
from spectrogram import Spectrogram
from util import Font, Settings


class Element(Enum):
    LED_STRIP_COMBO = auto()

    STOP_AUDIO_BUTTON = auto()
    PLAY_AUDIO_BUTTON = auto()

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
    def __init__(self, create_gui: Callable[[], WidgetGui], settings_controller: SettingsController,
                 create_serial_connection: Callable[[], Serial],
                 create_led_strip_gui: Callable[[], CanvasGui],
                 create_audio_in_stream: Callable[[], AudioInStream]):
        self.__gui = create_gui()

        self.__settings_controller = settings_controller

        self.__led_strip: LedStrip = ProductionLedStrip()
        self.__spectrogram = Spectrogram(self.__led_strip)

        self.__serial = create_serial_connection()
        self.__led_strip_gui = create_led_strip_gui()
        self.__audio_in_stream = create_audio_in_stream()

    @property
    def __settings(self) -> Settings:
        return self.__settings_controller.settings

    def __enter__(self) -> AudioInController:
        return self

    def __exit__(self, *args):
        try:
            self.__led_strip.turn_off()

        except ValueError:
            pass

        self.__audio_in_stream.close()
        self.__serial.close()
        self.__led_strip_gui.close()

    def run(self):
        self._display()

        event = self._read_event_and_update_gui()

        while (event != WidgetGuiEvent.CLOSE_WINDOW):
            self._handle_event(event)
            event = self._read_event_and_update_gui()

        self._handle_event(event)

    def _read_event_and_update_gui(self) -> Union[Element, WidgetGuiEvent]:
        EVENT = self.__gui.read_event_and_update_gui()

        if (EVENT == WidgetGuiEvent.TIMEOUT and self.__audio_in_stream.is_open()):
            return Event.PLAYING

        return EVENT

    def _handle_event(self, event: Union[Element, WidgetGuiEvent]):
        if (event == Element.SETTINGS_BUTTON):
            self.__settings_controller.run()

        elif (event == Event.PLAYING):
            MILLISECONDS_PER_SECOND = 1000
            FRAMES_PER_MILLISECOND = self.__audio_in_stream.sample_rate / MILLISECONDS_PER_SECOND
            NUMBER_OF_FRAMES = int(FRAMES_PER_MILLISECOND * self.__settings.milliseconds_per_audio_chunk)

            AUDIO_CHUNK = self.__audio_in_stream.read(NUMBER_OF_FRAMES)

            self.__spectrogram.update_led_strip(AUDIO_CHUNK, NUMBER_OF_FRAMES, self.__audio_in_stream.sample_rate)

        elif (event == Element.STOP_AUDIO_BUTTON):
            self.__led_strip.turn_off()

            self.__led_strip_gui.close()
            self.__serial.close()
            self.__audio_in_stream.close()

            self.__set_audio_paused_gui_state()

        elif (event == Element.PLAY_AUDIO_BUTTON):
            self.__audio_in_stream.open()

            CURRENT_INPUT_SOURCE = f"Input Source : {self.__audio_in_stream.input_source}"

            CURRENT_INPUT_SOURCE_TEXT = self.__gui.get_widget(Element.CURRENT_INPUT_SOURCE_MESSAGE)
            CURRENT_INPUT_SOURCE_TEXT.value = CURRENT_INPUT_SOURCE
            self.__gui.update_widget(CURRENT_INPUT_SOURCE_TEXT)

            self.__spectrogram.set_amplitude_rgbs(self.__settings.amplitude_rgbs)
            self.__spectrogram.set_frequency_range(self.__settings.minimum_frequency,
                                                   self.__settings.maximum_frequency)

            GROUPED_LEDS = self.__create_grouped_leds()
            self.__led_strip = ProductionLedStrip(GROUPED_LEDS)

            self.__spectrogram.set_led_strip(self.__led_strip)

            self.__set_audio_playing_gui_state()

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.__gui.close()

        elif (event != WidgetGuiEvent.TIMEOUT):
            raise ValueError(f'The event {event} is not a recognized event.')

    def _display(self):
        TITLE_TEXT = Font("Courier New", 20)
        FONT = Font("Courier New", 14)

        LED_STRIP_COMBO_VALUES = ['Graphic LED Strip', 'Serial LED Strip']
        LED_STRIP_COMBO = Combo(Element.LED_STRIP_COMBO, LED_STRIP_COMBO_VALUES)

        LAYOUT = [[Button(Element.SETTINGS_BUTTON, text="Settings")],

                  [Text(Element.CURRENT_INPUT_SOURCE_MESSAGE, text="No audio currently playing.", font=TITLE_TEXT)],

                  [Button(Element.STOP_AUDIO_BUTTON, text="Stop ([])", font=FONT, enabled=False),
                   Button(Element.PLAY_AUDIO_BUTTON, text="Play (>)", font=FONT, enabled=True)],

                  [Text(Element.SELECT_VISUALIZER_TYPE_LABEL, text="LED Strip Type : ", font=FONT),
                   LED_STRIP_COMBO]]

        self.__gui.set_layout(LAYOUT)
        self.__gui.display_layout()

    def __set_audio_paused_gui_state(self):
        SETTINGS_BUTTON: Button = self.__gui.get_widget(Element.SETTINGS_BUTTON)
        PAUSE_BUTTON: Button = self.__gui.get_widget(Element.STOP_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.__gui.get_widget(Element.PLAY_AUDIO_BUTTON)
        LED_STRIP_COMBO: Combo = self.__gui.get_widget(Element.LED_STRIP_COMBO)

        SETTINGS_BUTTON.enabled = True
        PAUSE_BUTTON.enabled = False
        RESUME_BUTTON.enabled = True
        LED_STRIP_COMBO.enabled = True

        self.__gui.update_widget(SETTINGS_BUTTON)
        self.__gui.update_widget(PAUSE_BUTTON)
        self.__gui.update_widget(RESUME_BUTTON)
        self.__gui.update_widget(LED_STRIP_COMBO)

    def __set_audio_playing_gui_state(self):
        SETTINGS_BUTTON: Button = self.__gui.get_widget(Element.SETTINGS_BUTTON)
        PAUSE_BUTTON: Button = self.__gui.get_widget(Element.STOP_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.__gui.get_widget(Element.PLAY_AUDIO_BUTTON)
        LED_STRIP_COMBO: Combo = self.__gui.get_widget(Element.LED_STRIP_COMBO)

        SETTINGS_BUTTON.enabled = False
        PAUSE_BUTTON.enabled = True
        RESUME_BUTTON.enabled = False
        LED_STRIP_COMBO.enabled = True

        self.__gui.update_widget(SETTINGS_BUTTON)
        self.__gui.update_widget(PAUSE_BUTTON)
        self.__gui.update_widget(RESUME_BUTTON)
        self.__gui.update_widget(LED_STRIP_COMBO)

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

    def __create_grouped_leds(self) -> GroupedLeds:
        LED_STRIP_COMBO = self.__gui.get_widget(Element.LED_STRIP_COMBO)
        LED_RANGE = (self.__settings.start_led, self.__settings.end_led)

        if (LED_STRIP_COMBO.value == 'Serial LED Strip'):
            PARITY = PARITY_NONE
            STOP_BITS = STOPBITS_ONE_POINT_FIVE
            BYTE_SIZE = EIGHTBITS
            READ_TIMEOUT = 1
            WRITE_TIMEOUT = 0

            self.__serial.open(self.__settings.serial_port, self.__settings.serial_baudrate,
                               PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)

            return SerialGroupedLeds(LED_RANGE, self.__get_group_index_to_led_range(),
                                     self.__serial, self.__settings.brightness)

        self.__led_strip_gui.open()

        return GraphicGroupedLeds(LED_RANGE, self.__get_group_index_to_led_range(),
                                  self.__led_strip_gui)
