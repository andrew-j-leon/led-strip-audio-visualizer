from __future__ import annotations

from enum import Enum, auto
from queue import Empty
from typing import Callable, List, Set, Tuple, Union

from color_palette import ColorPalette
from controller.controller import Controller, RunnableResource
from led_strip.grouped_leds import GraphicGroupedLeds, GroupedLeds, SerialGroupedLeds
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.audio_in_stream import AudioInStream
from libraries.canvas_gui import CanvasGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE, Serial
from libraries.widget import Button, CheckBox, Combo, Input, Text
from libraries.widget_gui import Font, WidgetGui, WidgetGuiEvent
from selection.selection import Selection
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
    NEXT_COLOR_PALETTE_BUTTON = auto()

    LED_STRIP_TYPE_COMBO = auto()


class Event(Enum):
    PLAYING = auto()


class State(Enum):
    PLAYING = auto()
    PAUSED = auto()


class LedStripType:
    GRAPHIC = 'Graphic LED Strip'
    SERIAL = 'Serial LED Strip'


def _create_groups(start_led: int, end_led: int, number_of_groups: int) -> List[Set[Tuple[int, int]]]:
    if (start_led < 0):
        raise ValueError(f'start_led must be >= 0, but was {start_led}.')

    if (end_led < 0):
        raise ValueError(f'end_led must be >= 0, but was {end_led}.')

    if (number_of_groups < 0):
        raise ValueError(f'number_of_groups ({number_of_groups}) must be >= 0.')

    NUMBER_OF_LEDS = end_led - start_led

    if (NUMBER_OF_LEDS < 0):
        raise ValueError(f'start_led ({start_led}) must be <= end_led ({end_led}).')

    if (NUMBER_OF_LEDS == 0 or number_of_groups == 0):
        return []

    # NUMBER_OF_LEDS_PER_GROUP = 0 if (number_of_groups == 0) else max(1, NUMBER_OF_LEDS // number_of_groups)
    NUMBER_OF_LEDS_PER_GROUP = 0 if (number_of_groups == 0) else max(1, round(NUMBER_OF_LEDS / number_of_groups))

    group_number = 0
    group_start_led = start_led
    group_end_led = group_start_led + NUMBER_OF_LEDS_PER_GROUP

    group_led_ranges: List[Set[Tuple[int, int]]] = [set() for group_number in range(number_of_groups)]

    while (group_number < number_of_groups and group_start_led < end_led):
        group_led_ranges[group_number].add((group_start_led, group_end_led))

        group_start_led += NUMBER_OF_LEDS_PER_GROUP
        group_end_led += NUMBER_OF_LEDS_PER_GROUP
        group_number += 1

    try:
        LAST_GROUP_LED_RANGE = group_led_ranges[-1].pop()
        LAST_GROUP_START_LED = LAST_GROUP_LED_RANGE[0]
        group_led_ranges[-1].add((LAST_GROUP_START_LED, end_led))

    except IndexError as err:
        if (not len(group_led_ranges) == 0):
            raise err

    except KeyError as err:
        if (not len(group_led_ranges[-1]) == 0):
            raise err

    return group_led_ranges


def _create_mirrored_groups(start_led: int, end_led: int, number_of_groups: int) -> List[Set[Tuple[int, int]]]:
    if (start_led < 0):
        raise ValueError(f'start_led must be >= 0, but was {start_led}.')

    if (end_led < 0):
        raise ValueError(f'end_led must be >= 0, but was {end_led}.')

    if (number_of_groups < 0):
        raise ValueError(f'number_of_groups ({number_of_groups}) must be >= 0.')

    NUMBER_OF_LEDS = end_led - start_led

    if (NUMBER_OF_LEDS < 0):
        raise ValueError(f'start_led ({start_led}) must be <= end_led ({end_led}).')

    if (NUMBER_OF_LEDS == 0 or number_of_groups == 0):
        return []

    NUMBER_OF_LEDS_PER_GROUP = max(1, NUMBER_OF_LEDS // number_of_groups)
    NUMBER_OF_LEDS_PER_LED_RANGE = max(1, NUMBER_OF_LEDS_PER_GROUP // 2)

    group_led_ranges: List[Set[Tuple[int, int]]] = [set() for group_number in range(number_of_groups)]

    led_range_start = start_led
    led_range_end = led_range_start + NUMBER_OF_LEDS_PER_LED_RANGE

    group_number = number_of_groups - 1

    while (group_number >= 0 and led_range_end <= end_led):
        group_led_ranges[group_number].add((led_range_start, led_range_end))

        led_range_start += NUMBER_OF_LEDS_PER_LED_RANGE
        led_range_end += NUMBER_OF_LEDS_PER_LED_RANGE
        group_number -= 1

    NUMBER_OF_LED_RANGES = NUMBER_OF_LEDS // NUMBER_OF_LEDS_PER_LED_RANGE
    group_number = 0 if (NUMBER_OF_LED_RANGES % 2 == 0) else 1

    while (group_number < number_of_groups and led_range_end <= end_led):
        group_led_ranges[group_number].add((led_range_start, led_range_end))

        led_range_start += NUMBER_OF_LEDS_PER_LED_RANGE
        led_range_end += NUMBER_OF_LEDS_PER_LED_RANGE
        group_number += 1

    return group_led_ranges


class AudioInController(Controller):
    def __init__(self, create_settings_controller: Callable[[Selection[Settings]], RunnableResource],
                 settings_selection: Selection[Settings],
                 create_color_palette_controller: Callable[[Selection[ColorPalette]], RunnableResource],
                 color_palette_selection: Selection[ColorPalette],
                 create_widget_gui: Callable[[], WidgetGui], create_canvas_gui: Callable[[], CanvasGui],
                 create_serial: Callable[[], Serial], create_audio_in_stream: Callable[[], AudioInStream],
                 create_led_strip: Callable[[], LedStrip], create_spectrogram: Callable[[], Spectrogram]):

        self.__gui = create_widget_gui()
        self.__gui.title = 'Audio In Music Visualizer'

        self.__settings_selection = settings_selection
        self.__color_palette_selection = color_palette_selection

        self.__settings_controller = create_settings_controller(self.__settings_selection)
        self.__color_palette_controller = create_color_palette_controller(self.__color_palette_selection)
        self.__led_strip = create_led_strip()
        self.__spectrogram = create_spectrogram()

        self.__serial = create_serial()
        self.__led_strip_gui = create_canvas_gui()
        self.__audio_in_stream = create_audio_in_stream()

        self.__timed_circular_palette_queue = TimedCircularQueue(self.__color_palette_selection.values())

    @property
    def __settings(self) -> Settings:
        try:
            return self.__settings_selection.selected_value

        except AttributeError:
            return Settings()

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

    def __cycle_color_palettes(self):
        try:
            palette: ColorPalette = self.__timed_circular_palette_queue.dequeue()
            self.__spectrogram.set_amplitude_rgbs(palette.amplitude_rgbs)

        except Empty:
            pass

    def handle_event(self, event: Union[Element, WidgetGuiEvent]):
        if (event == Element.SETTINGS_BUTTON):
            self.__settings_controller.run()

        elif (event == Element.COLOR_PALETTE_BUTTON):
            self.__color_palette_controller.run()

        elif (event == Event.PLAYING):
            SHOULD_CYCLE_PALETTES = self.__gui.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX).value

            if (SHOULD_CYCLE_PALETTES):
                try:
                    self.__cycle_color_palettes()

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
                SELECTED_PALETTE = self.__color_palette_selection.selected_value
                SECONDS_PER_PALETTE = int(self.__gui.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT).value)
                COLOR_PALETTES = list(self.__color_palette_selection.values())
                INDEX_OF_SELECTED_PALETTE = COLOR_PALETTES.index(SELECTED_PALETTE)
                COLOR_PALETTE_QUEUE = COLOR_PALETTES[INDEX_OF_SELECTED_PALETTE:] + COLOR_PALETTES[0:INDEX_OF_SELECTED_PALETTE]
                self.__timed_circular_palette_queue = TimedCircularQueue(COLOR_PALETTE_QUEUE, SECONDS_PER_PALETTE)

                palette: ColorPalette = self.__timed_circular_palette_queue.dequeue()
                self.__spectrogram.set_amplitude_rgbs(palette.amplitude_rgbs)

            except AttributeError:
                self.__spectrogram.set_amplitude_rgbs([])

                SECONDS_PER_PALETTE = int(self.__gui.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT).value)
                self.__timed_circular_palette_queue = TimedCircularQueue([], SECONDS_PER_PALETTE)

            self.__spectrogram.set_frequency_range(self.__settings.minimum_frequency,
                                                   self.__settings.maximum_frequency)

            try:
                GROUPED_LEDS = self.__create_grouped_leds()
                self.__led_strip = ProductionLedStrip(GROUPED_LEDS)

            except ValueError as error:
                self.__audio_in_stream.close()
                raise error

            self.__set_audio_playing_gui_state()

        elif (event == Element.NEXT_COLOR_PALETTE_BUTTON):
            ORIGINAL_SECONDS_BETWEEN_DEQUEUES = self.__timed_circular_palette_queue.seconds_between_dequeues
            self.__timed_circular_palette_queue.seconds_between_dequeues = 0
            self.__cycle_color_palettes()
            self.__timed_circular_palette_queue.seconds_between_dequeues = ORIGINAL_SECONDS_BETWEEN_DEQUEUES

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

        SECONDS_PER_COLOR_PALETTE_INPUT_WIDTH = 5

        LAYOUT = [[Button(Element.SETTINGS_BUTTON, text="Settings"),
                   Button(Element.COLOR_PALETTE_BUTTON, text='Color Palettes'),
                   SECONDS_PER_CYCLE_LABEL, Input(Element.SECONDS_PER_COLOR_PALETTE_INPUT, '90', width=SECONDS_PER_COLOR_PALETTE_INPUT_WIDTH),
                   CheckBox(Element.CYCLE_COLOR_PALETTES_CHECKBOX, 'Cycle Color Palettes')],

                  [Text(Element.CURRENT_INPUT_SOURCE_TEXT, text="No audio currently playing.", font=TITLE_TEXT)],

                  [Button(Element.STOP_AUDIO_BUTTON, text="Stop ([])", font=FONT, enabled=False),
                   Button(Element.PLAY_AUDIO_BUTTON, text="Play (>)", font=FONT, enabled=True),
                   Button(Element.NEXT_COLOR_PALETTE_BUTTON, text='Next Color Palette', enabled=False)],

                  [Text(text="LED Strip Type : ", font=FONT),
                   LED_STRIP_TYPE_COMBO]]

        self.__gui.set_layout(LAYOUT)
        self.__gui.display_layout()

    def __set_audio_paused_gui_state(self):
        SETTINGS_BUTTON: Button = self.__gui.get_widget(Element.SETTINGS_BUTTON)
        COLOR_PALETTE_BUTTON: Button = self.__gui.get_widget(Element.COLOR_PALETTE_BUTTON)
        STOP_BUTTON: Button = self.__gui.get_widget(Element.STOP_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.__gui.get_widget(Element.PLAY_AUDIO_BUTTON)
        NEXT_COLOR_PALETTE_BUTTON: Button = self.__gui.get_widget(Element.NEXT_COLOR_PALETTE_BUTTON)
        LED_STRIP_TYPE_COMBO: Combo = self.__gui.get_widget(Element.LED_STRIP_TYPE_COMBO)
        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.__gui.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.__gui.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)

        SETTINGS_BUTTON.enabled = True
        COLOR_PALETTE_BUTTON.enabled = True
        STOP_BUTTON.enabled = False
        RESUME_BUTTON.enabled = True
        NEXT_COLOR_PALETTE_BUTTON.enabled = False
        LED_STRIP_TYPE_COMBO.enabled = True
        CYCLE_COLOR_PALETTES_CHECKBOX.enabled = True
        SECONDS_PER_COLOR_PALETTE_INPUT.enabled = True

        self.__gui.update_widgets(COLOR_PALETTE_BUTTON, SETTINGS_BUTTON, STOP_BUTTON,
                                  RESUME_BUTTON, NEXT_COLOR_PALETTE_BUTTON, LED_STRIP_TYPE_COMBO,
                                  CYCLE_COLOR_PALETTES_CHECKBOX, SECONDS_PER_COLOR_PALETTE_INPUT)

    def __set_audio_playing_gui_state(self):
        SETTINGS_BUTTON: Button = self.__gui.get_widget(Element.SETTINGS_BUTTON)
        COLOR_PALETTE_BUTTON: Button = self.__gui.get_widget(Element.COLOR_PALETTE_BUTTON)
        STOP_BUTTON: Button = self.__gui.get_widget(Element.STOP_AUDIO_BUTTON)
        RESUME_BUTTON: Button = self.__gui.get_widget(Element.PLAY_AUDIO_BUTTON)
        NEXT_COLOR_PALETTE_BUTTON: Button = self.__gui.get_widget(Element.NEXT_COLOR_PALETTE_BUTTON)
        CYCLE_COLOR_PALETTES_CHECKBOX: CheckBox = self.__gui.get_widget(Element.CYCLE_COLOR_PALETTES_CHECKBOX)
        SECONDS_PER_COLOR_PALETTE_INPUT: Input = self.__gui.get_widget(Element.SECONDS_PER_COLOR_PALETTE_INPUT)
        LED_STRIP_TYPE_COMBO: Combo = self.__gui.get_widget(Element.LED_STRIP_TYPE_COMBO)

        LED_STRIP_TYPE_COMBO.enabled = False
        COLOR_PALETTE_BUTTON.enabled = False
        SETTINGS_BUTTON.enabled = False
        STOP_BUTTON.enabled = True
        RESUME_BUTTON.enabled = False
        NEXT_COLOR_PALETTE_BUTTON.enabled = True
        CYCLE_COLOR_PALETTES_CHECKBOX.enabled = False
        SECONDS_PER_COLOR_PALETTE_INPUT.enabled = False

        self.__gui.update_widgets(COLOR_PALETTE_BUTTON, SETTINGS_BUTTON, STOP_BUTTON, RESUME_BUTTON,
                                  NEXT_COLOR_PALETTE_BUTTON, LED_STRIP_TYPE_COMBO,
                                  CYCLE_COLOR_PALETTES_CHECKBOX, SECONDS_PER_COLOR_PALETTE_INPUT)

    def __create_groups(self) -> List[Set[Tuple[int, int]]]:
        try:
            START_LED = self.__settings.start_led
            END_LED = self.__settings.end_led
            NUMBER_OF_GROUPS = self.__settings.number_of_groups

            group_led_ranges = (_create_mirrored_groups(START_LED, END_LED, NUMBER_OF_GROUPS)
                                if (self.__settings.should_mirror_groups)
                                else _create_groups(START_LED, END_LED, NUMBER_OF_GROUPS))

            if (self.__settings.should_reverse_groups):
                group_led_ranges.reverse()

            return group_led_ranges

        except ZeroDivisionError:
            return []

    def __create_grouped_leds(self) -> GroupedLeds:
        LED_STRIP_TYPE_COMBO: Combo = self.__gui.get_widget(Element.LED_STRIP_TYPE_COMBO)
        LED_RANGE = (self.__settings.start_led, self.__settings.end_led)

        if (LED_STRIP_TYPE_COMBO.value == LedStripType.GRAPHIC):
            self.__led_strip_gui.open()

            return GraphicGroupedLeds(LED_RANGE, self.__create_groups(),
                                      self.__led_strip_gui)

        elif (LED_STRIP_TYPE_COMBO.value == LedStripType.SERIAL):
            PARITY = PARITY_NONE
            STOP_BITS = STOPBITS_ONE
            BYTE_SIZE = EIGHTBITS
            READ_TIMEOUT = 10
            WRITE_TIMEOUT = 10

            self.__serial.open(self.__settings.serial_port, self.__settings.serial_baudrate,
                               PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)

            return SerialGroupedLeds(LED_RANGE, self.__create_groups(),
                                     self.__serial, self.__settings.brightness)

        raise ValueError(f'The selected LedStripType {LED_STRIP_TYPE_COMBO.value} is an unrecognized LedStripType. '
                         + f'Recognized LedStripTypes include: {LED_STRIP_TYPE_COMBO.values}.')
