
from collections import Counter
from enum import Enum, auto
from typing import Any, Dict, Union

from libraries.widget_gui import Button, CheckBox, Combo, Input, Multiline, Text, Widget, WidgetGui, WidgetGuiEvent
from util import Font, Settings, SettingsCollection


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


class Event(Enum):
    SELECT_CURRENT_SETTINGS_NAME = auto()
    SELECT_NON_CURRENT_SETTINGS_NAME = auto()
    CLEAR_SETTINGS_NAME = auto()
    ENTER_NEW_SETTINGS_NAME = auto()


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

    def __get_selected_settings_name(self) -> str:
        try:
            COMBO = self.__widget_gui.get_widget(Element.SETTINGS_NAME_COMBO)
            return COMBO.value

        except AttributeError:
            return ''

    def read_event_and_update_gui(self) -> Union[Element, WidgetGuiEvent, Event]:
        def the_current_settings_name_is_selected(settings_name: str):
            try:
                return settings_name == self.__settings_collection.current_name

            except AttributeError:
                return False

        def a_non_current_settings_name_is_selected(settings_name: str):
            try:
                return (settings_name != self.__settings_collection.current_name
                        and settings_name in self.__settings_collection)

            except AttributeError:
                return False

        EVENT = self.__widget_gui.read_event_and_update_gui()

        if (EVENT == WidgetGuiEvent.TIMEOUT):
            SELECTED_SETTINGS_NAME = self.__get_selected_settings_name()

            if (the_current_settings_name_is_selected(SELECTED_SETTINGS_NAME)):
                return Event.SELECT_CURRENT_SETTINGS_NAME

            elif (a_non_current_settings_name_is_selected(SELECTED_SETTINGS_NAME)):
                return Event.SELECT_NON_CURRENT_SETTINGS_NAME

            elif (SELECTED_SETTINGS_NAME == ''):
                return Event.CLEAR_SETTINGS_NAME

            return Event.ENTER_NEW_SETTINGS_NAME

        return EVENT

    def handle_event(self, event: Union[Element, WidgetGuiEvent]):
        SELECTED_SETTINGS_NAME = self.__get_selected_settings_name()

        if (event == Element.SAVE_BUTTON):
            self.__save_settings()
            self.__update_widgets()

        elif (event == Element.DELETE_BUTTON):
            try:
                del self.__settings_collection[SELECTED_SETTINGS_NAME]
                self.__update_widgets()

            except KeyError:
                raise ValueError(f'There is no Settings with the name {SELECTED_SETTINGS_NAME} to delete.')

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.__widget_gui.close()

        elif (event != WidgetGuiEvent.TIMEOUT):
            save_button: Button = self.__widget_gui.get_widget(Element.SAVE_BUTTON)
            delete_button: Button = self.__widget_gui.get_widget(Element.DELETE_BUTTON)

            if (event == Event.SELECT_CURRENT_SETTINGS_NAME):
                save_button.enabled = True
                delete_button.enabled = True

                self.__widget_gui.update_widget(save_button)
                self.__widget_gui.update_widget(delete_button)

            elif (event == Event.SELECT_NON_CURRENT_SETTINGS_NAME):
                try:
                    self.__settings_collection.current_name = SELECTED_SETTINGS_NAME
                    self.__update_widgets()

                except ValueError as error:
                    if (SELECTED_SETTINGS_NAME not in self.__settings_collection):
                        raise ValueError(f"The selected settings name {SELECTED_SETTINGS_NAME} is not in this SettingsController's SettingsCollection.")

                    raise error

            elif (event == Event.CLEAR_SETTINGS_NAME):
                save_button.enabled = False
                delete_button.enabled = False

                self.__widget_gui.update_widget(save_button)
                self.__widget_gui.update_widget(delete_button)

            elif (event == Event.ENTER_NEW_SETTINGS_NAME):
                save_button.enabled = True
                delete_button.enabled = False

                self.__widget_gui.update_widget(save_button)
                self.__widget_gui.update_widget(delete_button)

            else:
                raise ValueError(f'This SettingsController does not recognize the event {event}.')

    def display(self):
        def get_widget(widget_key: Element) -> Widget:
            return WIDGETS[widget_key]

        WIDGETS = self.__create_widgets_with_keys()

        SETTINGS_NAMES_COMBO = get_widget(Element.SETTINGS_NAME_COMBO)
        SAVE_BUTTON = get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON = get_widget(Element.DELETE_BUTTON)

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

        AMPLITUDE_RGBS_MULTILINE = get_widget(Element.AMPLITUDE_RGBS_MULTILINE)

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

                  [AMPLITUDE_RGBS_MULTILINE]]

        self.__widget_gui.set_layout(LAYOUT)
        self.__widget_gui.display_layout()

    def __update_widgets(self):
        WIDGETS = self.__create_widgets_with_keys()

        for widget in WIDGETS.values():
            self.__widget_gui.update_widget(widget)

    def __create_widgets_with_keys(self) -> Dict[Element, Widget]:
        def create_settings_names_combo():
            SETTINGS_NAMES = list(self.__settings_collection.names())
            SETTINGS_NAMES_COMBO_SIZE = (40, 7)

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

        FONT = Font("Courier New", 14)
        SETTINGS = self.settings

        SETTINGS_NAMES_COMBO = create_settings_names_combo()
        SAVE_BUTTON = Button(Element.SAVE_BUTTON, "Save", FONT, True)
        DELETE_BUTTON = Button(Element.DELETE_BUTTON, "Delete", FONT, True)

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

        AMPLITUDE_RGBS_MULTILINE = create_amplitude_rgbs_multiline()

        widgets = dict()

        def add_widget(widget: Widget):
            widgets[widget.key] = widget

        add_widget(SETTINGS_NAMES_COMBO)
        add_widget(SAVE_BUTTON)
        add_widget(DELETE_BUTTON)
        add_widget(START_LED_INPUT)
        add_widget(END_LED_INPUT)
        add_widget(MILLISECONDS_PER_AUDIO_CHUNK_INPUT)
        add_widget(SERIAL_PORT_INPUT)
        add_widget(BAUDRATES_COMBO)
        add_widget(BRIGHTNESS_INPUT)
        add_widget(NUMBER_OF_GROUPS_INPUT)
        add_widget(MINIMUM_FREQUENCY_INPUT)
        add_widget(MAXIMUM_FREQUENCY_INPUT)
        add_widget(REVERSE_LEDS_CHECK_BOX)
        add_widget(AMPLITUDE_RGBS_MULTILINE)

        return widgets

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

        SETTINGS_NAME_COMBO = self.__widget_gui.get_widget(Element.SETTINGS_NAME_COMBO)
        SETTINGS_NAME = SETTINGS_NAME_COMBO.value

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

        WIDGET = self.__widget_gui.get_widget(setting_element)
        WIDGET_VALUE = WIDGET.value

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
