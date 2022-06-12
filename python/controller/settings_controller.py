from __future__ import annotations

from collections import Counter
from enum import Enum, auto
from typing import Any, Callable, Dict, Hashable, List, Tuple, Union

from libraries.widget import Button, CheckBox, ColorPicker, Combo, Input, Text, Widget
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from util import Font, Settings, SettingsCollection, convert_to_hex, convert_to_rgb


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

    DECIBEL_INPUT_1 = auto()
    COLOR_PICKER_1 = auto()

    DECIBEL_INPUT_2 = auto()
    COLOR_PICKER_2 = auto()

    DECIBEL_INPUT_3 = auto()
    COLOR_PICKER_3 = auto()

    DECIBEL_INPUT_4 = auto()
    COLOR_PICKER_4 = auto()

    DECIBEL_INPUT_5 = auto()
    COLOR_PICKER_5 = auto()


class Event(Enum):
    SELECT_CURRENT_SETTINGS_NAME = auto()
    SELECT_NON_CURRENT_SETTINGS_NAME = auto()
    CLEAR_SETTINGS_NAME = auto()
    ENTER_NEW_SETTINGS_NAME = auto()


class SettingsController:
    def __init__(self, create_gui: Callable[[], WidgetGui], settings_collection: SettingsCollection = SettingsCollection()):
        self.__gui = create_gui()
        self.__settings_collection = settings_collection

    @property
    def settings(self) -> Settings:
        try:
            return self.__settings_collection.current_settings

        except AttributeError:
            return Settings()

    def __enter__(self) -> SettingsController:
        return self

    def __exit__(self, *args):
        self.__gui.close()

    def run(self):
        self._display()
        settings_event = self._read_event_and_update_gui()

        while (settings_event != WidgetGuiEvent.CLOSE_WINDOW):
            self._handle_event(settings_event)
            settings_event = self._read_event_and_update_gui()

        self._handle_event(settings_event)

    def __get_selected_settings_name(self) -> str:
        try:
            COMBO = self.__gui.get_widget(Element.SETTINGS_NAME_COMBO)
            return COMBO.value

        except AttributeError:
            return ''

    def _read_event_and_update_gui(self) -> Union[Element, WidgetGuiEvent, Event]:
        EVENT = self.__gui.read_event_and_update_gui()

        if (EVENT == WidgetGuiEvent.TIMEOUT):
            SELECTED_SETTINGS_NAME = self.__get_selected_settings_name()

            if (self.__the_current_settings_name_is_selected(SELECTED_SETTINGS_NAME)):
                return Event.SELECT_CURRENT_SETTINGS_NAME

            elif (self.__a_non_current_settings_name_is_selected(SELECTED_SETTINGS_NAME)):
                return Event.SELECT_NON_CURRENT_SETTINGS_NAME

            elif (SELECTED_SETTINGS_NAME == ''):
                return Event.CLEAR_SETTINGS_NAME

            return Event.ENTER_NEW_SETTINGS_NAME

        return EVENT

    def __the_current_settings_name_is_selected(self, settings_name: str):
        try:
            return settings_name == self.__settings_collection.current_name

        except AttributeError:
            return False

    def __a_non_current_settings_name_is_selected(self, settings_name: str):
        try:
            return (settings_name != self.__settings_collection.current_name
                    and settings_name in self.__settings_collection)

        except AttributeError:
            return False

    def _handle_event(self, event: Union[Element, WidgetGuiEvent]):
        SELECTED_SETTINGS_NAME = self.__get_selected_settings_name()

        if (event == Element.SAVE_BUTTON):
            self.__save_settings()

            try:
                self.__settings_collection.save_to_files()

            except ValueError:
                pass

            self.__update_widgets()

        elif (event == Element.DELETE_BUTTON):
            try:
                del self.__settings_collection[SELECTED_SETTINGS_NAME]

                try:
                    self.__settings_collection.save_to_files()

                except ValueError:
                    pass

                self.__update_widgets()

            except KeyError:
                raise ValueError(f'There is no Settings with the name {SELECTED_SETTINGS_NAME} to delete.')

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.__gui.close()

        elif (event != WidgetGuiEvent.TIMEOUT):
            SAVE_BUTTON: Button = self.__gui.get_widget(Element.SAVE_BUTTON)
            DELETE_BUTTON: Button = self.__gui.get_widget(Element.DELETE_BUTTON)

            if (event == Event.SELECT_CURRENT_SETTINGS_NAME):
                SAVE_BUTTON.enabled = True
                DELETE_BUTTON.enabled = True

                self.__gui.update_widget(SAVE_BUTTON)
                self.__gui.update_widget(DELETE_BUTTON)

            elif (event == Event.SELECT_NON_CURRENT_SETTINGS_NAME):
                try:
                    self.__settings_collection.current_name = SELECTED_SETTINGS_NAME
                    self.__update_widgets()

                except ValueError as error:
                    if (SELECTED_SETTINGS_NAME not in self.__settings_collection):
                        raise ValueError(f"The selected settings name {SELECTED_SETTINGS_NAME} is not in this SettingsController's SettingsCollection.")

                    raise error

            elif (event == Event.CLEAR_SETTINGS_NAME):
                SAVE_BUTTON.enabled = False
                DELETE_BUTTON.enabled = False

                self.__gui.update_widget(SAVE_BUTTON)
                self.__gui.update_widget(DELETE_BUTTON)

            elif (event == Event.ENTER_NEW_SETTINGS_NAME):
                SAVE_BUTTON.enabled = True
                DELETE_BUTTON.enabled = False

                self.__gui.update_widget(SAVE_BUTTON)
                self.__gui.update_widget(DELETE_BUTTON)

            else:
                raise ValueError(f'This SettingsController does not recognize the event {event}.')

    def _display(self):
        def get_widget(widget_key: Element) -> Widget:
            return WIDGETS[widget_key]

        WIDGETS = self.__create_widgets()

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

        DECIBEL_INPUT_1 = get_widget(Element.DECIBEL_INPUT_1)
        COLOR_PICKER_1 = get_widget(Element.COLOR_PICKER_1)

        DECIBEL_INPUT_2 = get_widget(Element.DECIBEL_INPUT_2)
        COLOR_PICKER_2 = get_widget(Element.COLOR_PICKER_2)

        DECIBEL_INPUT_3 = get_widget(Element.DECIBEL_INPUT_3)
        COLOR_PICKER_3 = get_widget(Element.COLOR_PICKER_3)

        DECIBEL_INPUT_4 = get_widget(Element.DECIBEL_INPUT_4)
        COLOR_PICKER_4 = get_widget(Element.COLOR_PICKER_4)

        DECIBEL_INPUT_5 = get_widget(Element.DECIBEL_INPUT_5)
        COLOR_PICKER_5 = get_widget(Element.COLOR_PICKER_5)

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

        FIRST_TEXT = Text(text='First', font=FONT)
        NEXT_TEXT = Text(text='next', font=FONT)
        DECIBELS_TEXT = Text(text='decibels (dB) are')

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

                  [FIRST_TEXT, DECIBEL_INPUT_1, DECIBELS_TEXT, COLOR_PICKER_1],
                  [NEXT_TEXT, DECIBEL_INPUT_2, DECIBELS_TEXT, COLOR_PICKER_2],
                  [NEXT_TEXT, DECIBEL_INPUT_3, DECIBELS_TEXT, COLOR_PICKER_3],
                  [NEXT_TEXT, DECIBEL_INPUT_4, DECIBELS_TEXT, COLOR_PICKER_4],
                  [NEXT_TEXT, DECIBEL_INPUT_5, DECIBELS_TEXT, COLOR_PICKER_5]]

        self.__gui.set_layout(LAYOUT)
        self.__gui.display_layout()

    def __update_widgets(self):
        WIDGETS = self.__create_widgets()

        for widget in WIDGETS.values():
            self.__gui.update_widget(widget)

    def __create_widgets(self) -> Dict[Element, Widget]:
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

        def create_amplitude_rgbs_widgets() -> List[Widget]:
            COUNTER = Counter(SETTINGS.amplitude_rgbs)
            INPUT_KEYS = [Element.DECIBEL_INPUT_1, Element.DECIBEL_INPUT_2,
                          Element.DECIBEL_INPUT_3, Element.DECIBEL_INPUT_4,
                          Element.DECIBEL_INPUT_5]

            COLOR_PICKER_KEYS = [Element.COLOR_PICKER_1, Element.COLOR_PICKER_2,
                                 Element.COLOR_PICKER_3, Element.COLOR_PICKER_4,
                                 Element.COLOR_PICKER_5]

            widgets = []

            i = -1
            for rgb, count in COUNTER.items():
                i += 1

                input_key = INPUT_KEYS[i]
                color_picker_key = COLOR_PICKER_KEYS[i]

                red, green, blue = rgb
                widgets += [Input(input_key, count), ColorPicker(color_picker_key, convert_to_hex(red, green, blue))]

            for j in range(i + 1, len(INPUT_KEYS)):
                input_key = INPUT_KEYS[j]
                color_picker_key = COLOR_PICKER_KEYS[j]

                widgets += [Input(input_key, '0'), ColorPicker(color_picker_key)]

            return widgets

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

        def create_widgets(*widgets: Widget) -> Dict[Hashable, Widget]:
            result = dict()

            for widget in widgets:
                result[widget.key] = widget

            return result

        return create_widgets(SETTINGS_NAMES_COMBO, SAVE_BUTTON, DELETE_BUTTON, START_LED_INPUT,
                              END_LED_INPUT, MILLISECONDS_PER_AUDIO_CHUNK_INPUT, SERIAL_PORT_INPUT,
                              BAUDRATES_COMBO, BRIGHTNESS_INPUT, NUMBER_OF_GROUPS_INPUT,
                              MINIMUM_FREQUENCY_INPUT, MAXIMUM_FREQUENCY_INPUT, REVERSE_LEDS_CHECK_BOX,
                              *create_amplitude_rgbs_widgets())

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

        AMPLITUDE_RGBS = self.__get_amplitude_rgbs_from_gui()

        settings = Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK, SERIAL_PORT, SERIAL_BAUDRATE,
                            BRIGHTNESS, MINIMUM_FREQUENCY, MAXIMUM_FREQUENCY, SHOULD_REVERSE_LEDS,
                            NUMBER_OF_GROUPS, AMPLITUDE_RGBS)

        SETTINGS_NAME_COMBO = self.__gui.get_widget(Element.SETTINGS_NAME_COMBO)
        SETTINGS_NAME = SETTINGS_NAME_COMBO.value

        self.__settings_collection[SETTINGS_NAME] = settings
        self.__settings_collection.current_name = SETTINGS_NAME

    def __get_amplitude_rgbs_from_gui(self) -> List[Tuple[int, int, int]]:
        NUMBER_OF_DECIBELS_1 = self.__get_setting_from_wiget_gui(Element.DECIBEL_INPUT_1)
        NUMBER_OF_DECIBELS_2 = self.__get_setting_from_wiget_gui(Element.DECIBEL_INPUT_2)
        NUMBER_OF_DECIBELS_3 = self.__get_setting_from_wiget_gui(Element.DECIBEL_INPUT_3)
        NUMBER_OF_DECIBELS_4 = self.__get_setting_from_wiget_gui(Element.DECIBEL_INPUT_4)
        NUMBER_OF_DECIBELS_5 = self.__get_setting_from_wiget_gui(Element.DECIBEL_INPUT_5)

        COLOR_PICKER_1 = self.__get_setting_from_wiget_gui(Element.COLOR_PICKER_1)
        COLOR_PICKER_2 = self.__get_setting_from_wiget_gui(Element.COLOR_PICKER_2)
        COLOR_PICKER_3 = self.__get_setting_from_wiget_gui(Element.COLOR_PICKER_3)
        COLOR_PICKER_4 = self.__get_setting_from_wiget_gui(Element.COLOR_PICKER_4)
        COLOR_PICKER_5 = self.__get_setting_from_wiget_gui(Element.COLOR_PICKER_5)

        return ([convert_to_rgb(COLOR_PICKER_1)] * NUMBER_OF_DECIBELS_1
                + [convert_to_rgb(COLOR_PICKER_2)] * NUMBER_OF_DECIBELS_2
                + [convert_to_rgb(COLOR_PICKER_3)] * NUMBER_OF_DECIBELS_3
                + [convert_to_rgb(COLOR_PICKER_4)] * NUMBER_OF_DECIBELS_4
                + [convert_to_rgb(COLOR_PICKER_5)] * NUMBER_OF_DECIBELS_5)

    def __get_setting_from_wiget_gui(self, setting_element: Element) -> Any:
        INTEGER_SETTINGS = {Element.START_LED_INPUT,
                            Element.END_LED_INPUT,
                            Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                            Element.SERIAL_BAUDRATE_COMBO,
                            Element.BRIGHTNESS_INPUT,
                            Element.MINIMUM_FREQUENCY_INPUT,
                            Element.MAXIMUM_FREQUENCY_INPUT,
                            Element.NUMBER_OF_GROUPS_INPUT,
                            Element.DECIBEL_INPUT_1,
                            Element.DECIBEL_INPUT_2,
                            Element.DECIBEL_INPUT_3,
                            Element.DECIBEL_INPUT_4,
                            Element.DECIBEL_INPUT_5}

        WIDGET = self.__gui.get_widget(setting_element)
        WIDGET_VALUE = WIDGET.value

        if (setting_element in INTEGER_SETTINGS):
            return int(WIDGET_VALUE)

        return WIDGET_VALUE
