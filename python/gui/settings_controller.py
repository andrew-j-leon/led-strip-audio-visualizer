
from collections import Counter
from enum import Enum, auto
from typing import Any, List, Tuple
from libraries.gui import Button, CheckBox, Combo, Font, Input, Multiline, Text, WidgetGui, WidgetGuiEvent
from util import Settings, SettingsCollection


class Element(Enum):
    SAVE_BUTTON = auto()
    DELETE_BUTTON = auto()
    SETTINGS_NAME_COMBO = auto()


class SettingElement(Enum):
    START_LED_INDEX_INPUT = auto()
    END_LED_INDEX_INPUT = auto()
    MILLISECONDS_PER_AUDIO_CHUNK_INPUT = auto()

    SERIAL_PORT_INPUT = auto()
    SERIAL_BAUDRATE_DROPDOWN = auto()
    BRIGHTNESS_INPUT = auto()

    NUMBER_OF_GROUPS_INPUT = auto()
    MINIMUM_FREQUENCY_INPUT = auto()
    MAXIMUM_FREQUENCY_INPUT = auto()
    SHOULD_REVERSE_LED_INDICIES_CHECKBOX = auto()
    AMPLITUDE_RGBS = auto()


class SettingsController:
    def __init__(self, widget_gui: WidgetGui = WidgetGui(),
                 settings_collection: SettingsCollection = SettingsCollection()):
        self.__widget_gui = widget_gui

        self.__settings_collection = settings_collection

    @property
    def settings(self) -> Settings:
        try:
            return self.__settings_collection.current_settings

        except AttributeError:
            return Settings()

    def start(self):
        self.__update_widget_gui()

        while True:
            widget_gui_settings_name = self.__widget_gui.get_widget_value(Element.SETTINGS_NAME_COMBO)

            if (widget_gui_settings_name == ""):
                self.__widget_gui.disable_widget(Element.SAVE_BUTTON)
                self.__widget_gui.disable_widget(Element.DELETE_BUTTON)

            elif (widget_gui_settings_name in self.__settings_collection.settings_names):
                self.__widget_gui.enable_widget(Element.SAVE_BUTTON)
                self.__widget_gui.enable_widget(Element.DELETE_BUTTON)

            else:
                self.__widget_gui.enable_widget(Element.SAVE_BUTTON)
                self.__widget_gui.disable_widget(Element.DELETE_BUTTON)

            try:
                if (widget_gui_settings_name != self.__settings_collection.current_settings_name):
                    self.__settings_collection.current_settings_name = widget_gui_settings_name
                    self.__update_widget_gui()

            except (AttributeError, ValueError):
                pass

            event = self.__widget_gui.read_event()

            if (event == Element.SAVE_BUTTON):
                self.__save_settings()
                self.__update_widget_gui()

            elif (event == Element.DELETE_BUTTON):
                self.__settings_collection.delete_settings(widget_gui_settings_name)
                self.__update_widget_gui()

            elif (event == WidgetGuiEvent.CLOSE_WINDOW):
                break

    def __update_widget_gui(self):
        BUTTON_FONT = Font("Courier New", 14)
        INPUT_LABEL_FONT = Font("Courier New", 14)
        CHECKBOX_INPUT_FONT = Font("Courier New", 14)
        H1 = Font("Courier New", 18)

        BAUDRATES = [str(baudrate) for baudrate in Settings.SERIAL_BAUDRATES]

        SETTINGS_NAME_COMBO_VALUES = list(self.__settings_collection.settings_names)

        def get_settings_name_combo_default_value() -> str:
            try:
                return str(self.__settings_collection.current_settings_name)

            except AttributeError:
                return ''

        SETTINGS_NAME_COMBO_DEFAULT_VALUE = get_settings_name_combo_default_value()

        SETTINGS_NAME_COMBO_SIZE = (50, 1)

        def get_settings() -> Settings:
            try:
                return self.__settings_collection.current_settings

            except AttributeError:
                return Settings()

        SETTINGS = get_settings()

        START_LED = str(SETTINGS.start_led)
        END_LED = str(SETTINGS.end_led)
        MILLISECONDS_PER_AUDIO_CHUNK = str(SETTINGS.milliseconds_per_audio_chunk)
        SERIAL_PORT = SETTINGS.serial_port
        SERIAL_BAUDRATE = str(SETTINGS.serial_baudrate)
        BRIGHTNESS = str(SETTINGS.brightness)
        MINIMUM_FREQUENCY = str(SETTINGS.minimum_frequency)
        MAXIMUM_FREQUENCY = str(SETTINGS.maximum_frequency)
        SHOULD_REVERSE_LEDS = SETTINGS.should_reverse_leds
        NUMBER_OF_GROUPS = str(SETTINGS.number_of_groups)

        def get_amplitude_rgbs(amplitude_rgbs: List[Tuple[int, int, int]]) -> str:
            COUNTER = Counter(amplitude_rgbs)

            result = ''
            for rgb, count in COUNTER.items():

                red, green, blue = rgb

                result += f'{red}, {green}, {blue}, {count}\n'

            return result.strip()

        AMPLITUDE_RGBS = get_amplitude_rgbs(SETTINGS.amplitude_rgbs)

        LAYOUT = [[Combo(Element.SETTINGS_NAME_COMBO, SETTINGS_NAME_COMBO_VALUES,
                         SETTINGS_NAME_COMBO_DEFAULT_VALUE, size=SETTINGS_NAME_COMBO_SIZE),
                   Button(Element.SAVE_BUTTON, "Save", BUTTON_FONT, True),
                   Button(Element.DELETE_BUTTON, "Delete", BUTTON_FONT, True)],

                  [Text(text="General", font=H1)],

                  [Text(text="Led Index Range:", font=INPUT_LABEL_FONT),
                   Text(text="start_index (inclusive):", font=INPUT_LABEL_FONT),
                   Input(SettingElement.START_LED_INDEX_INPUT, START_LED),
                   Text(text="end_index (exclusive):", font=INPUT_LABEL_FONT),
                   Input(SettingElement.END_LED_INDEX_INPUT, END_LED)],

                  [Text(text="Milliseconds per Audio Chunk:", font=INPUT_LABEL_FONT),
                   Input(SettingElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                         MILLISECONDS_PER_AUDIO_CHUNK)],

                  [Text(text="Serial", font=H1)],

                  [Text(text="Port:", font=INPUT_LABEL_FONT),
                   Input(SettingElement.SERIAL_PORT_INPUT, SERIAL_PORT)],

                  [Text(text="Baudrate:", font=INPUT_LABEL_FONT),
                   Combo(SettingElement.SERIAL_BAUDRATE_DROPDOWN, BAUDRATES, SERIAL_BAUDRATE)],

                  [Text(text="Brightness", font=INPUT_LABEL_FONT),
                   Input(SettingElement.BRIGHTNESS_INPUT, BRIGHTNESS)],

                  [Text(text="Frequency Visualizer", font=H1)],

                  [Text(text="Number of Groups:", font=INPUT_LABEL_FONT),
                   Input(SettingElement.NUMBER_OF_GROUPS_INPUT,
                         NUMBER_OF_GROUPS)],

                  [Text(text="Frequency Range:", font=INPUT_LABEL_FONT),
                   Text(text="minimum:", font=INPUT_LABEL_FONT),
                   Input(SettingElement.MINIMUM_FREQUENCY_INPUT, MINIMUM_FREQUENCY),
                   Text("maximum", font=INPUT_LABEL_FONT),
                   Input(SettingElement.MAXIMUM_FREQUENCY_INPUT, MAXIMUM_FREQUENCY)],

                  [CheckBox(SettingElement.SHOULD_REVERSE_LED_INDICIES_CHECKBOX,
                            "Should Reverse Led Indicies", CHECKBOX_INPUT_FONT, SHOULD_REVERSE_LEDS)],

                  [Text(text="Amplitude RGBs", font=INPUT_LABEL_FONT),
                   Multiline(SettingElement.AMPLITUDE_RGBS, AMPLITUDE_RGBS)]]

        self.__widget_gui.set_layout(LAYOUT)
        self.__widget_gui.update_display()

    def __save_settings(self):
        START_LED = self.__get_setting_from_wiget_gui(SettingElement.START_LED_INDEX_INPUT)
        END_LED = self.__get_setting_from_wiget_gui(SettingElement.END_LED_INDEX_INPUT)
        MILLISECONDS_PER_AUDIO_CHUNK = self.__get_setting_from_wiget_gui(SettingElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT)
        SERIAL_PORT = self.__get_setting_from_wiget_gui(SettingElement.SERIAL_PORT_INPUT)
        SERIAL_BAUDRATE = self.__get_setting_from_wiget_gui(SettingElement.SERIAL_BAUDRATE_DROPDOWN)
        BRIGHTNESS = self.__get_setting_from_wiget_gui(SettingElement.BRIGHTNESS_INPUT)
        MINIMUM_FREQUENCY = self.__get_setting_from_wiget_gui(SettingElement.MINIMUM_FREQUENCY_INPUT)
        MAXIMUM_FREQUENCY = self.__get_setting_from_wiget_gui(SettingElement.MAXIMUM_FREQUENCY_INPUT)
        SHOULD_REVERSE_LEDS = self.__get_setting_from_wiget_gui(SettingElement.SHOULD_REVERSE_LED_INDICIES_CHECKBOX)
        NUMBER_OF_GROUPS = self.__get_setting_from_wiget_gui(SettingElement.NUMBER_OF_GROUPS_INPUT)
        AMPLITUDE_RGBS = self.__get_setting_from_wiget_gui(SettingElement.AMPLITUDE_RGBS)

        settings = Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK, SERIAL_PORT, SERIAL_BAUDRATE,
                            BRIGHTNESS, MINIMUM_FREQUENCY, MAXIMUM_FREQUENCY, SHOULD_REVERSE_LEDS,
                            NUMBER_OF_GROUPS, AMPLITUDE_RGBS)

        settings_name = self.__widget_gui.get_widget_value(Element.SETTINGS_NAME_COMBO)

        self.__settings_collection.update_collection(settings_name, settings)

        self.__settings_collection.current_settings_name = settings_name

    def __get_setting_from_wiget_gui(self, setting_element: SettingElement) -> Any:
        INTEGER_SETTINGS = {SettingElement.START_LED_INDEX_INPUT,
                            SettingElement.END_LED_INDEX_INPUT,
                            SettingElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                            SettingElement.SERIAL_BAUDRATE_DROPDOWN,
                            SettingElement.BRIGHTNESS_INPUT,
                            SettingElement.MINIMUM_FREQUENCY_INPUT,
                            SettingElement.MAXIMUM_FREQUENCY_INPUT,
                            SettingElement.NUMBER_OF_GROUPS_INPUT}

        widget_value = self.__widget_gui.get_widget_value(setting_element)

        if (setting_element in INTEGER_SETTINGS):
            return int(widget_value)

        elif (setting_element == SettingElement.AMPLITUDE_RGBS):
            rgb_counts = widget_value.strip().split('\n')

            amplitude_rgbs = list()

            for rgb_count in rgb_counts:
                try:
                    red, green, blue, count = (int(string) for string in rgb_count.split(','))

                    amplitude_rgbs += [(red, green, blue)] * count

                except ValueError as error:
                    if (rgb_count != ''):
                        raise error

            return amplitude_rgbs

        return self.__widget_gui.get_widget_value(setting_element)
