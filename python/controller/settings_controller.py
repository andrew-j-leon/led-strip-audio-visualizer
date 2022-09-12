from __future__ import annotations

from enum import Enum, auto
from typing import Any, Callable, Dict, Hashable, Union

from controller.controller import Controller
from libraries.widget import Button, CheckBox, Combo, Input, Text, Widget
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from selection import Selection
from settings import Settings
from util import Font


class Element(Enum):
    SAVE_NAME_COMBO = auto()
    SAVE_BUTTON = auto()
    DELETE_BUTTON = auto()

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


class Event(Enum):
    SELECT_CURRENT_SAVE = auto()
    SELECT_NON_CURRENT_SAVE = auto()
    DELETE_SAVE_NAME = auto()
    ENTER_NEW_SAVE_NAME = auto()


class SettingsController(Controller):
    def __init__(self, create_gui: Callable[[], WidgetGui],
                 save_selection: Callable[[Selection[Settings]], None],
                 selection: Selection[Settings] = Selection()):
        self.__gui = create_gui()
        self.__gui.title = 'Settings'

        self.__save_selection = save_selection
        self.__selection = selection

    def close(self):
        self.__gui.close()

    def read_event_and_update_gui(self) -> Union[Element, WidgetGuiEvent]:
        EVENT = self.__gui.read_event_and_update_gui()

        if (EVENT == WidgetGuiEvent.TIMEOUT):
            CURRENT_SAVE_NAME = self.__get_current_save_name()

            if (self.__current_save_is_selected(CURRENT_SAVE_NAME)):
                return Event.SELECT_CURRENT_SAVE

            elif (self.__a_non_current_save_is_selected(CURRENT_SAVE_NAME)):
                return Event.SELECT_NON_CURRENT_SAVE

            elif (CURRENT_SAVE_NAME == ''):
                return Event.DELETE_SAVE_NAME

            return Event.ENTER_NEW_SAVE_NAME

        return EVENT

    def handle_event(self, event: Union[Element, WidgetGuiEvent]):
        CURRENT_SAVE_NAME = self.__get_current_save_name()

        if (event == Element.SAVE_BUTTON):
            self.__set_settings()
            self.__save_selection(self.__selection)
            self.__update_widgets()

        elif (event == Element.DELETE_BUTTON):
            try:
                del self.__selection[CURRENT_SAVE_NAME]
                self.__save_selection(self.__selection)
                self.__update_widgets()

            except KeyError:
                raise ValueError(f'There is no Settings with the name {CURRENT_SAVE_NAME} to delete.')

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.__gui.close()

        elif (event != WidgetGuiEvent.TIMEOUT):
            SAVE_BUTTON: Button = self.__gui.get_widget(Element.SAVE_BUTTON)
            DELETE_BUTTON: Button = self.__gui.get_widget(Element.DELETE_BUTTON)

            if (event == Event.SELECT_CURRENT_SAVE):
                SAVE_BUTTON.enabled = True
                DELETE_BUTTON.enabled = True

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

            elif (event == Event.SELECT_NON_CURRENT_SAVE):
                try:
                    self.__selection.selected_key = CURRENT_SAVE_NAME
                    self.__update_widgets()

                except ValueError:
                    raise ValueError(f"The selected Settings name {CURRENT_SAVE_NAME} is not in "
                                     "this SettingsController's Settings Selection.")

            elif (event == Event.DELETE_SAVE_NAME):
                SAVE_BUTTON.enabled = False
                DELETE_BUTTON.enabled = False

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

            elif (event == Event.ENTER_NEW_SAVE_NAME):
                SAVE_BUTTON.enabled = True
                DELETE_BUTTON.enabled = False

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

            else:
                raise ValueError(f'This SettingsController does not recognize the event {event}.')

    def display(self):
        WIDGETS = self.__create_widgets()

        def get_widget(widget_key: Element) -> Widget:
            return WIDGETS[widget_key]

        SAVE_NAME_COMBO = get_widget(Element.SAVE_NAME_COMBO)
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

        LAYOUT = [[SAVE_NAME_COMBO, SAVE_BUTTON, DELETE_BUTTON],
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

    def __get_current_save_name(self) -> str:
        try:
            COMBO = self.__gui.get_widget(Element.SAVE_NAME_COMBO)
            return COMBO.value

        except AttributeError:
            return ''

    def __current_save_is_selected(self, name: str) -> bool:
        try:
            return name == self.__selection.selected_key

        except AttributeError:
            return False

    def __a_non_current_save_is_selected(self, name: str) -> bool:
        return (name in self.__selection
                and name != self.__selection.selected_key)

    def __update_widgets(self):
        WIDGETS = self.__create_widgets()

        for widget in WIDGETS.values():
            self.__gui.update_widget(widget)

    def __create_widgets(self) -> Dict[Element, Widget]:
        def create_save_name_combo():
            SAVE_NAMES = list(self.__selection.keys())
            COMBO_SIZE = (40, 7)

            combo = Combo(Element.SAVE_NAME_COMBO, SAVE_NAMES, size=COMBO_SIZE)

            try:
                combo.value = self.__selection.selected_key
                return combo

            except AttributeError:
                return combo

        SETTINGS = (Settings() if (not hasattr(self.__selection, 'selected_value'))
                    else self.__selection.selected_value)

        def create_baudrates_combo():
            BAUDRATES = [str(baudrate) for baudrate in Settings.SERIAL_BAUDRATES]

            combo = Combo(Element.SERIAL_BAUDRATE_COMBO, BAUDRATES)
            combo.value = str(SETTINGS.serial_baudrate)

            return combo

        FONT = Font("Courier New", 14)

        SAVE_NAME_COMBO = create_save_name_combo()
        SAVE_BUTTON = Button(Element.SAVE_BUTTON, "Save", FONT, True)
        DELETE_BUTTON = Button(Element.DELETE_BUTTON, 'Delete', FONT, True)

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

        return create_widgets(SAVE_NAME_COMBO, SAVE_BUTTON, DELETE_BUTTON,
                              START_LED_INPUT, END_LED_INPUT, MILLISECONDS_PER_AUDIO_CHUNK_INPUT, SERIAL_PORT_INPUT,
                              BAUDRATES_COMBO, BRIGHTNESS_INPUT, NUMBER_OF_GROUPS_INPUT,
                              MINIMUM_FREQUENCY_INPUT, MAXIMUM_FREQUENCY_INPUT, REVERSE_LEDS_CHECK_BOX)

    def __set_settings(self):
        SETTINGS = self.__create_settings_from_widget_gui()

        SAVE_NAME_COMBO = self.__gui.get_widget(Element.SAVE_NAME_COMBO)
        SAVE_NAME = SAVE_NAME_COMBO.value

        self.__selection[SAVE_NAME] = SETTINGS
        self.__selection.selected_key = SAVE_NAME

    def __create_settings_from_widget_gui(self) -> Settings:
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

        return Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK, SERIAL_PORT,
                        SERIAL_BAUDRATE, BRIGHTNESS, MINIMUM_FREQUENCY, MAXIMUM_FREQUENCY,
                        SHOULD_REVERSE_LEDS, NUMBER_OF_GROUPS)

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
