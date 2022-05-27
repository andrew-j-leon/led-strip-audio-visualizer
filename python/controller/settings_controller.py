
from collections import Counter
from enum import Enum, auto
from typing import Any, Union
from libraries.widget_gui import Button, CheckBox, Combo, Input, Multiline, Text, WidgetGui, WidgetGuiEvent
from util import Settings, SettingsCollection, Font


class Element(Enum):
    SAVE_BUTTON = auto()
    DELETE_BUTTON = auto()
    SETTINGS_NAME_COMBO = auto()
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
    AMPLITUDE_RGBS_MULTILINE = auto()


class SettingsController:
    def __init__(self, widget_gui: WidgetGui, settings_collection: SettingsCollection = SettingsCollection()):
        self.__widget_gui = widget_gui
        self.__settings_collection = settings_collection

    @property
    def settings(self) -> Settings:
        try:
            return self.__settings_collection.current_settings

        except AttributeError:
            return Settings()

    def read_event_and_update_gui(self) -> Union[Element, WidgetGuiEvent]:
        return self.__widget_gui.read_event_and_update_gui()

    def handle_event(self, event: Union[Element, WidgetGuiEvent]):

        def get_widget_gui_settings_name() -> str:
            try:
                return self.__widget_gui.get_widget_value(Element.SETTINGS_NAME_COMBO)

            except ValueError:
                return ''

        WIDGET_GUI_SETTINGS_NAME = get_widget_gui_settings_name()

        def a_new_settings_name_from_the_dropdown_was_selected():
            try:
                return (WIDGET_GUI_SETTINGS_NAME != self.__settings_collection.current_name
                        and WIDGET_GUI_SETTINGS_NAME in self.__settings_collection)

            except AttributeError:
                return False

        if (a_new_settings_name_from_the_dropdown_was_selected()):
            self.__settings_collection.current_name = WIDGET_GUI_SETTINGS_NAME
            self.draw_widget_gui()

        elif (event == Element.SAVE_BUTTON):
            self.__save_settings()
            self.draw_widget_gui()

        elif (event == Element.DELETE_BUTTON):
            try:
                del self.__settings_collection[WIDGET_GUI_SETTINGS_NAME]
                self.draw_widget_gui()

            except KeyError:
                raise ValueError(f'There is no Settings with the name {WIDGET_GUI_SETTINGS_NAME} to delete.')

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.__widget_gui.close()

        elif (WIDGET_GUI_SETTINGS_NAME == ''):
            self.__widget_gui.disable_widget(Element.SAVE_BUTTON)
            self.__widget_gui.disable_widget(Element.DELETE_BUTTON)

        elif (WIDGET_GUI_SETTINGS_NAME in self.__settings_collection):
            self.__widget_gui.enable_widget(Element.SAVE_BUTTON)
            self.__widget_gui.enable_widget(Element.DELETE_BUTTON)

        else:
            self.__widget_gui.enable_widget(Element.SAVE_BUTTON)
            self.__widget_gui.disable_widget(Element.DELETE_BUTTON)

        return event

    def draw_widget_gui(self):
        FONT = Font("Courier New", 14)

        SETTINGS = self.settings

        def create_settings_names_combo():
            SETTINGS_NAMES = list(self.__settings_collection.names())
            SETTINGS_NAMES_COMBO_SIZE = (50, 1)

            combo = Combo(Element.SETTINGS_NAME_COMBO, SETTINGS_NAMES, size=SETTINGS_NAMES_COMBO_SIZE)

            try:
                combo.value = self.__settings_collection.current_name
                return combo

            except AttributeError:
                return combo

        def create_baudrates_combo():
            BAUDRATES = [str(baudrate) for baudrate in Settings.SERIAL_BAUDRATES]

            combo = Combo(Element.SERIAL_BAUDRATE_COMBO, BAUDRATES)
            combo.value = str(SETTINGS.serial_baudrate)

            return combo

        def create_amplitude_rgbs_multiline():
            COUNTER = Counter(SETTINGS.amplitude_rgbs)

            text = ''
            for rgb, count in COUNTER.items():

                red, green, blue = rgb

                text += f'{red}, {green}, {blue}, {count}\n'

            return Multiline(Element.AMPLITUDE_RGBS_MULTILINE, text.strip())

        SETTINGS_NAMES_COMBO = create_settings_names_combo()
        SAVE_BUTTON = Button(Element.SAVE_BUTTON, "Save", FONT, True)
        DELETE_BUTTON = Button(Element.DELETE_BUTTON, "Delete", FONT, True)

        START_LED_LABEL = Text(text="Start LED (inclusive):", font=FONT)
        START_LED_INPUT = Input(Element.START_LED_INPUT, str(SETTINGS.start_led))

        END_LED_LABEL = Text(text="End LED (exclusive):", font=FONT)
        END_LED_INPUT = Input(Element.END_LED_INPUT, str(SETTINGS.end_led))

        MILLISECONDS_PER_AUDIO_CHUNK_LABEL = Text(text="Milliseconds per Audio Chunk:", font=FONT)
        MILLISECONDS_PER_AUDIO_CHUNK_INPUT = Input(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                                                   str(SETTINGS.milliseconds_per_audio_chunk))

        SERIAL_PORT_LABEL = Text(text="Port:", font=FONT)
        SERIAL_PORT_INPUT = Input(Element.SERIAL_PORT_INPUT, SETTINGS.serial_port)

        BAUDRATES_LABEL = Text(text="Baudrate:", font=FONT)
        BAUDRATES_COMBO = create_baudrates_combo()

        BRIGHTNESS_LABEL = Text(text="Brightness", font=FONT)
        BRIGHTNESS_INPUT = Input(Element.BRIGHTNESS_INPUT, str(SETTINGS.brightness))

        NUMBER_OF_GROUPS_LABEL = Text(text="Number of Groups:", font=FONT)
        NUMBER_OF_GROUPS_INPUT = Input(Element.NUMBER_OF_GROUPS_INPUT, str(SETTINGS.number_of_groups))

        MINIMUM_FREQUENCY_LABEL = Text(text="Minimum Frequency:", font=FONT)
        MINIMUM_FREQUENCY_INPUT = Input(Element.MINIMUM_FREQUENCY_INPUT, str(SETTINGS.minimum_frequency))

        MAXIMUM_FREQUENCY_LABEL = Text(text="Maximum Frequency:", font=FONT)
        MAXIMUM_FREQUENCY_INPUT = Input(Element.MAXIMUM_FREQUENCY_INPUT, str(SETTINGS.maximum_frequency))

        REVERSE_LEDS_CHECK_BOX = CheckBox(Element.REVERSE_LEDS_CHECK_BOX,
                                          "Reverse LEDs", FONT, SETTINGS.should_reverse_leds)

        AMPLITUDE_RGBS = create_amplitude_rgbs_multiline()

        LAYOUT = [[SETTINGS_NAMES_COMBO, SAVE_BUTTON, DELETE_BUTTON],

                  [START_LED_LABEL, START_LED_INPUT],
                  [END_LED_LABEL, END_LED_INPUT],

                  [MILLISECONDS_PER_AUDIO_CHUNK_LABEL, MILLISECONDS_PER_AUDIO_CHUNK_INPUT],

                  [SERIAL_PORT_LABEL, SERIAL_PORT_INPUT],

                  [BAUDRATES_LABEL, BAUDRATES_COMBO],

                  [BRIGHTNESS_LABEL, BRIGHTNESS_INPUT],

                  [NUMBER_OF_GROUPS_LABEL, NUMBER_OF_GROUPS_INPUT],

                  [MINIMUM_FREQUENCY_LABEL, MINIMUM_FREQUENCY_INPUT],
                  [MAXIMUM_FREQUENCY_LABEL, MAXIMUM_FREQUENCY_INPUT],

                  [REVERSE_LEDS_CHECK_BOX],

                  [AMPLITUDE_RGBS]]

        self.__widget_gui.set_layout(LAYOUT)
        self.__widget_gui.display_layout()

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
        AMPLITUDE_RGBS = self.__get_setting_from_wiget_gui(Element.AMPLITUDE_RGBS_MULTILINE)

        settings = Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK, SERIAL_PORT, SERIAL_BAUDRATE,
                            BRIGHTNESS, MINIMUM_FREQUENCY, MAXIMUM_FREQUENCY, SHOULD_REVERSE_LEDS,
                            NUMBER_OF_GROUPS, AMPLITUDE_RGBS)

        SETTINGS_NAME = self.__widget_gui.get_widget_value(Element.SETTINGS_NAME_COMBO)

        self.__settings_collection[SETTINGS_NAME] = settings
        self.__settings_collection.current_name = SETTINGS_NAME

    def __get_setting_from_wiget_gui(self, setting_element: Element) -> Any:
        INTEGER_SETTINGS = {Element.START_LED_INPUT,
                            Element.END_LED_INPUT,
                            Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                            Element.SERIAL_BAUDRATE_COMBO,
                            Element.BRIGHTNESS_INPUT,
                            Element.MINIMUM_FREQUENCY_INPUT,
                            Element.MAXIMUM_FREQUENCY_INPUT,
                            Element.NUMBER_OF_GROUPS_INPUT}

        WIDGET_VALUE = self.__widget_gui.get_widget_value(setting_element)

        if (setting_element in INTEGER_SETTINGS):
            return int(WIDGET_VALUE)

        elif (setting_element == Element.AMPLITUDE_RGBS_MULTILINE):
            rgb_counts = WIDGET_VALUE.strip().split('\n')

            amplitude_rgbs = list()

            for i in range(len(rgb_counts)):

                rgb_count = rgb_counts[i]

                try:
                    red, green, blue, count = (int(string) for string in rgb_count.split(','))
                    amplitude_rgbs += [(red, green, blue)] * count

                except ValueError:
                    if (rgb_count != ''):
                        raise ValueError(f'Line {i} of the amplitude rgbs multiline ({rgb_count}) '
                                         'was not formatted correctly. The expected formatting was : red, '
                                         'green, blue, next_n_amplitude_values. For example: 10, 20, '
                                         '30, 8 would specify the RGB color (10, 20, 30) for the next 8 '
                                         'amplitude integers.')

            return amplitude_rgbs

        return WIDGET_VALUE
