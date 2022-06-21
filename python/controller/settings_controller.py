from __future__ import annotations

from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, Hashable, Union

from controller.controller import Controller
from libraries.widget import Button, CheckBox, Combo, Input, Text, Widget
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from settings import Settings
from settings import save as save_settings
from util import Font


class Element(Enum):
    SAVE_BUTTON = auto()

    START_LED_INPUT = auto()
    END_LED_INPUT = auto()
    MILLISECONDS_PER_AUDIO_CHUNK_INPUT = auto()
    SERIAL_PORT_INPUT = auto()
    SERIAL_BAUDRATE_COMBO = auto()
    BRIGHTNESS_INPUT = auto()
    NUMBER_OF_GROUPS_INPUT = auto()
    MINIMUM_FREQUENCY_INPUT = auto()
    MAXIMUM_FREQUENCY_INPUT = auto()
    REVERSE_LEDS_CHECK_BOX = auto()


class SettingsController(Controller):
    def __init__(self, create_gui: Callable[[], WidgetGui],
                 save_directory: Path, settings=Settings()):
        self.__gui = create_gui()
        self.__gui.title = 'Settings'

        self.__save_directory = save_directory
        self.__settings = settings

    def close(self):
        self.__gui.close()

    def read_event_and_update_gui(self) -> Union[Element, WidgetGuiEvent]:
        EVENT = self.__gui.read_event_and_update_gui()

        return EVENT

    def handle_event(self, event: Union[Element, WidgetGuiEvent]):
        if (event == Element.SAVE_BUTTON):
            self.__save_settings()
            save_settings(self.__settings, self.__save_directory)
            self.__update_widgets()

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.__gui.close()

        elif (event != WidgetGuiEvent.TIMEOUT):
            raise ValueError(f'This SettingsController does not recognize the event {event}.')

    def display(self):
        def get_widget(widget_key: Element) -> Widget:
            return WIDGETS[widget_key]

        WIDGETS = self.__create_widgets()

        SAVE_BUTTON = get_widget(Element.SAVE_BUTTON)

        START_LED_INPUT = get_widget(Element.START_LED_INPUT)
        END_LED_INPUT = get_widget(Element.END_LED_INPUT)

        MILLISECONDS_PER_AUDIO_CHUNK_INPUT = get_widget(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT)

        SERIAL_PORT_INPUT = get_widget(Element.SERIAL_PORT_INPUT)

        BAUDRATES_COMBO = get_widget(Element.SERIAL_BAUDRATE_COMBO)

        BRIGHTNESS_INPUT = get_widget(Element.BRIGHTNESS_INPUT)

        NUMBER_OF_GROUPS_INPUT = get_widget(Element.NUMBER_OF_GROUPS_INPUT)

        MINIMUM_FREQUENCY_INPUT = get_widget(Element.MINIMUM_FREQUENCY_INPUT)

        MAXIMUM_FREQUENCY_INPUT = get_widget(Element.MAXIMUM_FREQUENCY_INPUT)

        REVERSE_LEDS_CHECK_BOX = get_widget(Element.REVERSE_LEDS_CHECK_BOX)

        FONT = Font("Courier New", 14)

        START_LED_LABEL = Text(text="Start LED (inclusive):", font=FONT)
        END_LED_LABEL = Text(text="End LED (exclusive):", font=FONT)
        MILLISECONDS_PER_AUDIO_CHUNK_LABEL = Text(text="Milliseconds per Audio Chunk:", font=FONT)
        SERIAL_PORT_LABEL = Text(text="Port:", font=FONT)
        BAUDRATES_LABEL = Text(text="Baudrate:", font=FONT)
        BRIGHTNESS_LABEL = Text(text="Brightness", font=FONT)
        NUMBER_OF_GROUPS_LABEL = Text(text="Number of Groups:", font=FONT)
        MINIMUM_FREQUENCY_LABEL = Text(text="Minimum Frequency:", font=FONT)
        MAXIMUM_FREQUENCY_LABEL = Text(text="Maximum Frequency:", font=FONT)

        LAYOUT = [[SAVE_BUTTON],

                  [START_LED_LABEL, START_LED_INPUT],
                  [END_LED_LABEL, END_LED_INPUT],

                  [MILLISECONDS_PER_AUDIO_CHUNK_LABEL, MILLISECONDS_PER_AUDIO_CHUNK_INPUT],

                  [SERIAL_PORT_LABEL, SERIAL_PORT_INPUT],

                  [BAUDRATES_LABEL, BAUDRATES_COMBO],

                  [BRIGHTNESS_LABEL, BRIGHTNESS_INPUT],

                  [NUMBER_OF_GROUPS_LABEL, NUMBER_OF_GROUPS_INPUT],

                  [MINIMUM_FREQUENCY_LABEL, MINIMUM_FREQUENCY_INPUT],
                  [MAXIMUM_FREQUENCY_LABEL, MAXIMUM_FREQUENCY_INPUT],

                  [REVERSE_LEDS_CHECK_BOX]]

        self.__gui.set_layout(LAYOUT)
        self.__gui.display_layout()

    def __update_widgets(self):
        WIDGETS = self.__create_widgets()

        for widget in WIDGETS.values():
            self.__gui.update_widget(widget)

    def __create_widgets(self) -> Dict[Element, Widget]:
        def create_baudrates_combo():
            BAUDRATES = [str(baudrate) for baudrate in Settings.SERIAL_BAUDRATES]

            combo = Combo(Element.SERIAL_BAUDRATE_COMBO, BAUDRATES)
            combo.value = str(SETTINGS.serial_baudrate)

            return combo

        FONT = Font("Courier New", 14)
        SETTINGS = self.__settings

        SAVE_BUTTON = Button(Element.SAVE_BUTTON, "Save", FONT, True)

        START_LED_INPUT = Input(Element.START_LED_INPUT, str(SETTINGS.start_led))
        END_LED_INPUT = Input(Element.END_LED_INPUT, str(SETTINGS.end_led))

        MILLISECONDS_PER_AUDIO_CHUNK_INPUT = Input(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                                                   str(SETTINGS.milliseconds_per_audio_chunk))

        SERIAL_PORT_INPUT = Input(Element.SERIAL_PORT_INPUT, SETTINGS.serial_port)

        BAUDRATES_COMBO = create_baudrates_combo()

        BRIGHTNESS_INPUT = Input(Element.BRIGHTNESS_INPUT, str(SETTINGS.brightness))

        NUMBER_OF_GROUPS_INPUT = Input(Element.NUMBER_OF_GROUPS_INPUT, str(SETTINGS.number_of_groups))

        MINIMUM_FREQUENCY_INPUT = Input(Element.MINIMUM_FREQUENCY_INPUT, str(SETTINGS.minimum_frequency))

        MAXIMUM_FREQUENCY_INPUT = Input(Element.MAXIMUM_FREQUENCY_INPUT, str(SETTINGS.maximum_frequency))

        REVERSE_LEDS_CHECK_BOX = CheckBox(Element.REVERSE_LEDS_CHECK_BOX,
                                          "Reverse LEDs", FONT, SETTINGS.should_reverse_leds)

        def create_widgets(*widgets: Widget) -> Dict[Hashable, Widget]:
            result = dict()

            for widget in widgets:
                result[widget.key] = widget

            return result

        return create_widgets(SAVE_BUTTON,
                              START_LED_INPUT,
                              END_LED_INPUT, MILLISECONDS_PER_AUDIO_CHUNK_INPUT, SERIAL_PORT_INPUT,
                              BAUDRATES_COMBO, BRIGHTNESS_INPUT, NUMBER_OF_GROUPS_INPUT,
                              MINIMUM_FREQUENCY_INPUT, MAXIMUM_FREQUENCY_INPUT, REVERSE_LEDS_CHECK_BOX)

    def __save_settings(self):
        START_LED = self.__get_setting_from_wiget_gui(Element.START_LED_INPUT)
        END_LED = self.__get_setting_from_wiget_gui(Element.END_LED_INPUT)
        MILLISECONDS_PER_AUDIO_CHUNK = self.__get_setting_from_wiget_gui(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT)
        SERIAL_PORT = self.__get_setting_from_wiget_gui(Element.SERIAL_PORT_INPUT)
        SERIAL_BAUDRATE = self.__get_setting_from_wiget_gui(Element.SERIAL_BAUDRATE_COMBO)
        BRIGHTNESS = self.__get_setting_from_wiget_gui(Element.BRIGHTNESS_INPUT)
        MINIMUM_FREQUENCY = self.__get_setting_from_wiget_gui(Element.MINIMUM_FREQUENCY_INPUT)
        MAXIMUM_FREQUENCY = self.__get_setting_from_wiget_gui(Element.MAXIMUM_FREQUENCY_INPUT)
        SHOULD_REVERSE_LEDS = self.__get_setting_from_wiget_gui(Element.REVERSE_LEDS_CHECK_BOX)
        NUMBER_OF_GROUPS = self.__get_setting_from_wiget_gui(Element.NUMBER_OF_GROUPS_INPUT)

        self.__settings.start_led = START_LED
        self.__settings.end_led = END_LED
        self.__settings.milliseconds_per_audio_chunk = MILLISECONDS_PER_AUDIO_CHUNK
        self.__settings.serial_port = SERIAL_PORT
        self.__settings.serial_baudrate = SERIAL_BAUDRATE
        self.__settings.brightness = BRIGHTNESS
        self.__settings.minimum_frequency = MINIMUM_FREQUENCY
        self.__settings.maximum_frequency = MAXIMUM_FREQUENCY
        self.__settings.should_reverse_leds = SHOULD_REVERSE_LEDS
        self.__settings.number_of_groups = NUMBER_OF_GROUPS

    def __get_setting_from_wiget_gui(self, setting_element: Element) -> Any:
        INTEGER_SETTINGS = {Element.START_LED_INPUT,
                            Element.END_LED_INPUT,
                            Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                            Element.SERIAL_BAUDRATE_COMBO,
                            Element.BRIGHTNESS_INPUT,
                            Element.MINIMUM_FREQUENCY_INPUT,
                            Element.MAXIMUM_FREQUENCY_INPUT,
                            Element.NUMBER_OF_GROUPS_INPUT}

        WIDGET = self.__gui.get_widget(setting_element)
        WIDGET_VALUE = WIDGET.value

        if (setting_element in INTEGER_SETTINGS):
            return int(WIDGET_VALUE)

        return WIDGET_VALUE
