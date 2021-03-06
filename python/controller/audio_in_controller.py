from __future__ import annotations

from enum import Enum, auto
from typing import Callable, List, Tuple, Union

from color_palette import ColorPalette, ColorPaletteSelection
from controller.controller import Controller, RunnableResource
from led_strip.grouped_leds import GraphicGroupedLeds, GroupedLeds, SerialGroupedLeds
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.audio_in_stream import AudioInStream
from libraries.canvas_gui import CanvasGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, Serial
from libraries.widget import Button, CheckBox, Combo, Input, Text
from libraries.widget_gui import Font, WidgetGui, WidgetGuiEvent
from settings import Settings
from spectrogram import Spectrogram
from util import TimedCircularQueue


class Element(Enum):
    SETTINGS_BUTTON = auto()
    COLOR_PALETTE_BUTTON = auto()
    CYCLE_COLOR_PALETTES_CHECKBOX = auto()
    SECONDS_PER_COLOR_PALETTE_INPUT = auto()

    CURRENT_INPUT_SOURCE_TEXT = auto()

    STOP_AUDIO_BUTTON = auto()
    PLAY_AUDIO_BUTTON = auto()

    LED_STRIP_TYPE_COMBO = auto()


class Event(Enum):
    PLAYING = auto()


class State(Enum):
    PLAYING = auto()
    PAUSED = auto()


class LedStripType:
    GRAPHIC = 'Graphic LED Strip'
    SERIAL = 'Serial LED Strip'


class AudioInController(Controller):
    def __init__(self, create_settings_controller: Callable[[Settings], RunnableResource], settings: Settings,
                 create_color_palette_controller: Callable[[ColorPaletteSelection], RunnableResource],
                 color_palette_selection: ColorPaletteSelection,
                 create_widget_gui: Callable[[], WidgetGui], create_canvas_gui: Callable[[], CanvasGui],
                 create_serial: Callable[[], Serial], create_audio_in_stream: Callable[[], AudioInStream],
                 create_led_strip: Callable[[], LedStrip], create_spectrogram: Callable[[], Spectrogram]):

        self.__gui = create_widget_gui()
        self.__gui.title = 'Audio In Music Visualizer'

        self.__settings = settings
        self.__color_palette_selection = color_palette_selection

        self.__settings_controller = create_settings_controller(self.__settings)
        self.__color_palette_controller = create_color_palette_controller(self.__color_palette_selection)
        self.__led_strip = create_led_strip()
        self.__spectrogram = create_spectrogram()

        self.__serial = create_serial()
        self.__led_strip_gui = create_canvas_gui()
        self.__audio_in_stream = create_audio_in_stream()

        self.__timed_circular_palette_queue = TimedCircularQueue(self.__color_palette_selection.palettes())

    def close(self):
        self.__settings_controller.close()
        self.__color_palette_controller.close()
        self.__gui.close()
        self.__audio_in_stream.close()
        self.__serial.close()
        self.__led_strip_gui.close()

        try:
            self.__led_strip.turn_off()
        except ValueError:
            pass

    def read_event_and_update_gui(self) -> Union[Element, WidgetGuiEvent]:
        EVENT = self.__gui.read_event_and_update_gui()

        if (EVENT == WidgetGuiEvent.TIMEOUT and self.__audio_in_stream.is_open()):
            return Event.PLAYING

        return EVENT

    def handle_event(self, event: Union[Element, WidgetGuiEvent]):
        if (event == Element.SETTINGS_BUTTON):
            self.__settings_controller.run()

        elif (event == Element.COLOR_PALETTE_BUTTON):
            self.__color_palette_controller.run()

        elif (event == Event.PLAYING):
            SHOULD_SHUFFLE_PALETTES = self.__gui.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX).value

            if (SHOULD_SHUFFLE_PALETTES):
                try:
                    palette: ColorPalette = self.__timed_circular_palette_queue.dequeue()
                    self.__spectrogram.set_amplitude_rgbs(palette.amplitude_rgbs)

                except ValueError:
                    pass

            MILLISECONDS_PER_SECOND = 1000
            FRAMES_PER_MILLISECOND = self.__audio_in_stream.sample_rate / MILLISECONDS_PER_SECOND
            NUMBER_OF_FRAMES = int(FRAMES_PER_MILLISECOND * self.__settings.milliseconds_per_audio_chunk)

            AUDIO_CHUNK = self.__audio_in_stream.read(NUMBER_OF_FRAMES)

            self.__spectrogram.update_led_strip(self.__led_strip, AUDIO_CHUNK, NUMBER_OF_FRAMES, self.__audio_in_stream.sample_rate)

        elif (event == Element.STOP_AUDIO_BUTTON):
            self.__led_strip.turn_off()

            self.__led_strip_gui.close()
            self.__serial.close()
            self.__audio_in_stream.close()

            self.__set_audio_paused_gui_state()

        elif (event == Element.PLAY_AUDIO_BUTTON):
            self.__audio_in_stream.open()

            CURRENT_INPUT_SOURCE = f"Input Source : {self.__audio_in_stream.input_source}"

            CURRENT_INPUT_SOURCE_TEXT = self.__gui.get_widget(Element.CURRENT_INPUT_SOURCE_TEXT)
            CURRENT_INPUT_SOURCE_TEXT.value = CURRENT_INPUT_SOURCE
            self.__gui.update_widget(CURRENT_INPUT_SOURCE_TEXT)

            try:
                PALETTE = self.__color_palette_selection.selected_palette
                self.__spectrogram.set_amplitude_rgbs(PALETTE.amplitude_rgbs)

            except AttributeError:
                self.__spectrogram.set_amplitude_rgbs([])

            self.__spectrogram.set_frequency_range(self.__settings.minimum_frequency,
                                                   self.__settings.maximum_frequency)

            try:
                GROUPED_LEDS = self.__create_grouped_leds()
                self.__led_strip = ProductionLedStrip(GROUPED_LEDS)

            except ValueError as error:
                self.__audio_in_stream.close()
                raise error

            self.__set_audio_playing_gui_state()

            SECONDS_PER_PALETTE = int(self.__gui.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT).value)
            self.__timed_circular_palette_queue = TimedCircularQueue(self.__color_palette_selection.palettes(),
                                                                     SECONDS_PER_PALETTE)

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.__gui.close()

        elif (event != WidgetGuiEvent.TIMEOUT):
            raise ValueError(f'The event {event} is not a recognized event.')

    def display(self):
        TITLE_TEXT = Font("Courier New", 20)
        FONT = Font("Courier New", 14)

        LED_STRIP_COMBO_VALUES = [LedStripType.GRAPHIC, LedStripType.SERIAL]
        LED_STRIP_TYPE_COMBO = Combo(Element.LED_STRIP_TYPE_COMBO, LED_STRIP_COMBO_VALUES)

        SECONDS_PER_CYCLE_LABEL = Text(text='Seconds Per Palette:')

        LAYOUT = [[Button(Element.SETTINGS_BUTTON, text="Settings"),
                   Button(Element.COLOR_PALETTE_BUTTON, text='Color Palettes'),
                   CheckBox(Element.CYCLE_COLOR_PALETTES_CHECKBOX, 'Cycle Color Palettes'),
                   SECONDS_PER_CYCLE_LABEL, Input(Element.SECONDS_PER_COLOR_PALETTE_INPUT, '90')],

                  [Text(Element.CURRENT_INPUT_SOURCE_TEXT, text="No audio currently playing.", font=TITLE_TEXT)],

                  [Button(Element.STOP_AUDIO_BUTTON, text="Stop ([])", font=FONT, enabled=False),
                   Button(Element.PLAY_AUDIO_BUTTON, text="Play (>)", font=FONT, enabled=True)],

                  [Text(text="LED Strip Type : ", font=FONT),
                   LED_STRIP_TYPE_COMBO]]

        self.__gui.set_layout(LAYOUT)
        self.__gui.display_layout()

    def __set_audio_paused_gui_state(self):
        SETTINGS_BUTTON: Button = self.__gui.get_widget(Element.SETTINGS_BUTTON)
        COLOR_PALETTE_BUTTON: Button = self.__gui.get_widget(Element.COLOR_PALETTE_BUTTON)
        STOP_BUTTON: Button = self.__gui.get_widget(Element.STOP_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.__gui.get_widget(Element.PLAY_AUDIO_BUTTON)
        LED_STRIP_TYPE_COMBO: Combo = self.__gui.get_widget(Element.LED_STRIP_TYPE_COMBO)
        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.__gui.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.__gui.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)

        SETTINGS_BUTTON.enabled = True
        COLOR_PALETTE_BUTTON.enabled = True
        STOP_BUTTON.enabled = False
        RESUME_BUTTON.enabled = True
        LED_STRIP_TYPE_COMBO.enabled = True
        CYCLE_COLOR_PALETTES_CHECKBOX.enabled = True
        SECONDS_PER_COLOR_PALETTE_INPUT.enabled = True

        self.__gui.update_widget(COLOR_PALETTE_BUTTON)
        self.__gui.update_widget(SETTINGS_BUTTON)
        self.__gui.update_widget(STOP_BUTTON)
        self.__gui.update_widget(RESUME_BUTTON)
        self.__gui.update_widget(LED_STRIP_TYPE_COMBO)
        self.__gui.update_widget(CYCLE_COLOR_PALETTES_CHECKBOX)
        self.__gui.update_widget(SECONDS_PER_COLOR_PALETTE_INPUT)

    def __set_audio_playing_gui_state(self):
        SETTINGS_BUTTON: Button = self.__gui.get_widget(Element.SETTINGS_BUTTON)
        COLOR_PALETTE_BUTTON: Button = self.__gui.get_widget(Element.COLOR_PALETTE_BUTTON)
        STOP_BUTTON: Button = self.__gui.get_widget(Element.STOP_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.__gui.get_widget(Element.PLAY_AUDIO_BUTTON)
        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.__gui.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.__gui.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)
        LED_STRIP_TYPE_COMBO: Combo = self.__gui.get_widget(Element.LED_STRIP_TYPE_COMBO)

        LED_STRIP_TYPE_COMBO.enabled = False
        COLOR_PALETTE_BUTTON.enabled = False
        SETTINGS_BUTTON.enabled = False
        STOP_BUTTON.enabled = True
        RESUME_BUTTON.enabled = False
        CYCLE_COLOR_PALETTES_CHECKBOX.enabled = False
        SECONDS_PER_COLOR_PALETTE_INPUT.enabled = False

        self.__gui.update_widget(COLOR_PALETTE_BUTTON)
        self.__gui.update_widget(SETTINGS_BUTTON)
        self.__gui.update_widget(STOP_BUTTON)
        self.__gui.update_widget(RESUME_BUTTON)
        self.__gui.update_widget(LED_STRIP_TYPE_COMBO)
        self.__gui.update_widget(CYCLE_COLOR_PALETTES_CHECKBOX)
        self.__gui.update_widget(SECONDS_PER_COLOR_PALETTE_INPUT)

    def __get_group_index_to_led_range(self) -> List[Tuple[int, int]]:
        def get_number_of_leds() -> int:
            return self.__settings.end_led - self.__settings.start_led

        try:
            number_of_leds_per_group = max(1, get_number_of_leds() // self.__settings.number_of_groups)
            group_index_to_led_range = list()

            for group_index in range(self.__settings.number_of_groups):
                shifted_start_index = group_index * number_of_leds_per_group + self.__settings.start_led

                shifted_end_index = shifted_start_index + number_of_leds_per_group

                group_index_to_led_range.append((shifted_start_index, shifted_end_index))

            if (self.__settings.should_reverse_leds):
                group_index_to_led_range.reverse()

            return group_index_to_led_range

        except ZeroDivisionError:
            return []

    def __create_grouped_leds(self) -> GroupedLeds:
        LED_STRIP_TYPE_COMBO: Combo = self.__gui.get_widget(Element.LED_STRIP_TYPE_COMBO)
        LED_RANGE = (self.__settings.start_led, self.__settings.end_led)

        if (LED_STRIP_TYPE_COMBO.value == LedStripType.GRAPHIC):
            self.__led_strip_gui.open()

            return GraphicGroupedLeds(LED_RANGE, self.__get_group_index_to_led_range(),
                                      self.__led_strip_gui)

        elif (LED_STRIP_TYPE_COMBO.value == LedStripType.SERIAL):
            PARITY = PARITY_NONE
            STOP_BITS = STOPBITS_ONE_POINT_FIVE
            BYTE_SIZE = EIGHTBITS
            READ_TIMEOUT = 10
            WRITE_TIMEOUT = 10

            self.__serial.open(self.__settings.serial_port, self.__settings.serial_baudrate,
                               PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)

            return SerialGroupedLeds(LED_RANGE, self.__get_group_index_to_led_range(),
                                     self.__serial, self.__settings.brightness)

        raise ValueError(f'The selected LedStripType {LED_STRIP_TYPE_COMBO.value} is an unrecognized LedStripType. '
                         + f'Recognized LedStripTypes include: {LED_STRIP_TYPE_COMBO.values}.')
