from typing import Any, Callable, Dict, List, Tuple

import gui.audio_visualizer.setting.setting_view as setting_view
import gui.styling as styling
import PySimpleGUI as sg
import util.util as util
from gui.window import Window
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED


class Element:
    SELECT_VISUALIZER_TYPE_DROPDOWN = "select_visualizer_type_dropdown"
    SERIAL_LED_STRIP_CHECKBOX = "serial_led_strip_checkbox"
    GRAPHIC_LED_STRIP_CHECKBOX = "graphic_led_strip_checkbox"

    PAUSE_AUDIO_BUTTON = "pause_audio_button"
    RESUME_AUDIO_BUTTON = "resume_audio_button"

    CURRENT_INPUT_SOURCE_MESSAGE = "current_input_source_message"
    SELECT_INPUT_SOURCE_DROPDOWN = "select_input_source_dropdown"
    SELECT_INPUT_SOURCE_LABEL = "select_input_source_label"

    CONFIRMATION_MODAL_OK_BUTTON = "error_modal_ok_button"
    SELECT_VISUALIZER_TYPE_LABEL = "label_for_the_select_visualizer_type_dropdown"
    SETTINGS_BUTTON = "settings_button"


class Event:
    WINDOW_CLOSED = WINDOW_CLOSED
    TIMEOUT_EVENT = TIMEOUT_EVENT
    CONFIRMATION_MODAL_OK = Element.CONFIRMATION_MODAL_OK_BUTTON
    OPEN_SETTINGS_MODAL = Element.SETTINGS_BUTTON
    PAUSE_AUDIO = Element.PAUSE_AUDIO_BUTTON
    RESUME_AUDIO = Element.RESUME_AUDIO_BUTTON


class VisualizerType:
    NONE = "None"
    FREQUENCY = "Frequency"
    CENTER_AMPLITUDE = "Center_Amplitude"


def _gui_rows_are_valid(rows: List[List[sg.Element]]) -> bool:
    if (not isinstance(rows, list)):
        return False
    for elements in rows:
        if (not _gui_elements_are_valid(elements)):
            return False
    return True


def _gui_elements_are_valid(elements: List[sg.Element]) -> bool:
    if (not isinstance(elements, list)):
        return False
    for element in elements:
        if (not isinstance(element, sg.Element)):
            return False
    return True


class AudioInView:
    def __init__(self):
        self.__setting_view = setting_view.SettingView()
        self.__main_window: Window = None

    def __del__(self):
        self.__close_main_window()

    def display_confirmation_modal(self, title: str, error_message: str):
        '''
            Display a modal that blocks input from all other windows until said modal's
            "Ok" button or upper-right "X" button is clicked.

            Args:
                `title (str)`: The title of the modal.
                `error_message (str)`: The modal's message to the user.
        '''
        LAYOUT = [[sg.Text(text=error_message)], [sg.Button(button_text="Ok")]]

        modal: Window = Window(title=title, layout=LAYOUT, modal=True)

        while True:
            event = modal.read(timeout=0)
            if (event == Event.WINDOW_CLOSED, Event.CONFIRMATION_MODAL_OK):
                modal.close()
                break

    def run_concurrent(self, on_event: Callable[[str], None] = lambda event: None):
        '''
            Args:
                `on_event (Callable[[str], None], optional)`: Called with the name of the event whenever an event occurs.
        '''
        self.__main_window: Window = self._create_main_window()
        self.__main_window.read(timeout=0)

        while (self.__main_window):
            event: str = self.__main_window.read(timeout=0)
            event: str = self._handle_event_before_client_on_event(event)

            on_event(event)

            if (event == Event.WINDOW_CLOSED):
                self.__close_main_window()

    def get_visualizer_type_dropdown_value(self) -> str:
        return self._get_element_value(Element.SELECT_VISUALIZER_TYPE_DROPDOWN)

    def get_serial_led_strip_checkbox_value(self):
        return self._get_element_value(Element.SERIAL_LED_STRIP_CHECKBOX)

    def get_graphic_led_strip_checkbox_value(self):
        return self._get_element_value(Element.GRAPHIC_LED_STRIP_CHECKBOX)

    def get_led_index_range(self) -> Tuple[int, int]:
        return (self.__setting_view.get_value(setting_view.SettingElement.START_LED_INDEX_INPUT),
                self.__setting_view.get_value(setting_view.SettingElement.END_LED_INDEX_INPUT))

    def get_milliseconds_per_audio_chunk(self) -> int:
        return self.__setting_view.get_value(setting_view.SettingElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT)

    def get_serial_port(self) -> str:
        return self.__setting_view.get_value(setting_view.SettingElement.SERIAL_PORT_INPUT)

    def get_serial_baudrate(self) -> int:
        return self.__setting_view.get_value(setting_view.SettingElement.SERIAL_BAUDRATE_DROPDOWN)

    def get_brightness(self) -> int:
        return self.__setting_view.get_value(setting_view.SettingElement.BRIGHTNESS_INPUT)

    def get_frequency_range(self) -> Tuple[int, int]:
        return (self.__setting_view.get_value(setting_view.SettingElement.MINIMUM_FREQUENCY_INPUT),
                self.__setting_view.get_value(setting_view.SettingElement.MAXIMUM_FREQUENCY_INPUT))

    def should_reverse_indicies(self) -> bool:
        return self.__setting_view.get_value(setting_view.SettingElement.SHOULD_REVERSE_LED_INDICIES_CHECKBOX)

    def get_number_of_groups(self) -> int:
        return self.__setting_view.get_value(setting_view.SettingElement.NUMBER_OF_GROUPS_INPUT)

    def get_amplitude_to_rgb(self) -> List[Tuple[int, int, int]]:
        return self.__setting_view.get_value(setting_view.SettingElement.AMPLITUDE_TO_RGB_INPUT)

    def set_current_input_source_message(self, message: str):
        self.__update_element(Element.CURRENT_INPUT_SOURCE_MESSAGE, message)

    def set_audio_paused_state(self):
        self.__update_element(Element.SETTINGS_BUTTON, disabled=False)
        self.__update_element(Element.PAUSE_AUDIO_BUTTON, disabled=True)
        self.__update_element(Element.RESUME_AUDIO_BUTTON, disabled=False)

        self.__update_element(Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=False)
        self.__update_element(Element.SERIAL_LED_STRIP_CHECKBOX, disabled=False)
        self.__update_element(Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=False)

    def set_audio_playing_state(self):
        self.__update_element(Element.SETTINGS_BUTTON, disabled=True)
        self.__update_element(Element.PAUSE_AUDIO_BUTTON, disabled=False)
        self.__update_element(Element.RESUME_AUDIO_BUTTON, disabled=True)

        self.__update_element(Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=True)
        self.__update_element(Element.SERIAL_LED_STRIP_CHECKBOX, disabled=True)
        self.__update_element(Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=True)

    def __close_main_window(self):
        if (self.__main_window):
            self.__main_window.close()
            self.__main_window = None

    def __update_element(self, element: str, *update_args, **update_kwargs):
        self.__main_window[element].update(*update_args, **update_kwargs)

    def _create_gui_rows(self, *rows: Tuple[List[sg.Element]]) -> List[List[sg.Element]]:
        gui_rows: List[List[sg.Element]] = []
        util.foreach(rows, lambda row: gui_rows.append(row))
        return gui_rows

    def _element_is_enabled(self, element: str) -> bool:
        return not self.__main_window[element].Disabled

    def _get_element_value(self, element: str) -> Any:
        return self.__main_window[element].get()

    def _fill_input_fields(self, values: Dict[str, Any]):
        self.__main_window.fill(values)

    def _handle_event_before_client_on_event(self, event: str) -> str:
        return event

    def _create_main_window(self) -> Window:
        VISUALIZER_DROPDOWN_VALUES: List[str] = [VisualizerType.NONE, VisualizerType.FREQUENCY]

        row_with_settings_button = [sg.Button(button_text="Settings", key=Element.SETTINGS_BUTTON)]

        row_with_default_visualizer_and_led_selection = [sg.Text(text="Visualizer : ", key=Element.SELECT_VISUALIZER_TYPE_LABEL, font=styling.INPUT_LABEL_FONT),
                                                         sg.Combo(values=VISUALIZER_DROPDOWN_VALUES,
                                                                  default_value=VisualizerType.FREQUENCY, key=Element.SELECT_VISUALIZER_TYPE_DROPDOWN, font=styling.DROPDOWN_INPUT_FONT),
                                                         sg.Checkbox(text="Serial Led Strip", key=Element.SERIAL_LED_STRIP_CHECKBOX, font=styling.CHECKBOX_INPUT_FONT),
                                                         sg.Checkbox(text="Graphic Led Strip", key=Element.GRAPHIC_LED_STRIP_CHECKBOX, font=styling.CHECKBOX_INPUT_FONT)]

        row_with_default_visualizer_and_led_selection = (self.__get_elements_to_the_left_of_default_visualizer_and_led_selection()
                                                         + row_with_default_visualizer_and_led_selection
                                                         + self.__get_elements_to_the_right_of_default_visualizer_and_led_selection())

        layout = [row_with_settings_button]
        util.foreach(self.__get_rows_above_default_visualizer_and_led_selection(), lambda row: layout.append(row))
        layout.append(row_with_default_visualizer_and_led_selection)
        util.foreach(self.__get_rows_below_default_visualizer_and_led_selection(), lambda row: layout.append(row))

        return Window('Led Strip Music Visualizer', layout=layout, resizable=True, element_padding=(0, 0),
                      margins=(0, 0), titlebar_background_color="#000917", titlebar_text_color="#8a8a8a")

    def __get_elements_to_the_left_of_default_visualizer_and_led_selection(self) -> List[sg.Element]:
        elements = []

        if (not _gui_elements_are_valid(elements)):
            raise TypeError("elements are not valid PySimpleGui elements")
        return elements

    def __get_elements_to_the_right_of_default_visualizer_and_led_selection(self) -> List[sg.Element]:
        elements = []

        if (not _gui_elements_are_valid(elements)):
            raise TypeError("elements are not valid PySimpleGui elements")
        return elements

    def __get_rows_above_default_visualizer_and_led_selection(self) -> List[List[sg.Element]]:
        CURRENT_INPUT_SOURCE_FONT = ("Courier New", 20)

        return self._create_gui_rows([sg.Text(text="No audio currently playing.", key=Element.CURRENT_INPUT_SOURCE_MESSAGE, font=CURRENT_INPUT_SOURCE_FONT)],
                                     [sg.Button(button_text="Pause (||)", disabled=True, key=Element.PAUSE_AUDIO_BUTTON, font=styling.BUTTON_FONT),
                                      sg.Button(button_text="Resume (>)", disabled=False, key=Element.RESUME_AUDIO_BUTTON, font=styling.BUTTON_FONT)])

    def __get_rows_below_default_visualizer_and_led_selection(self) -> List[List[sg.Element]]:
        rows = []

        if (not _gui_rows_are_valid(rows)):
            raise TypeError("rows are not valid PySimpleGui rows")
        return rows

    def _handle_event_before_client_on_event(self, event: str) -> str:
        if (event == Event.OPEN_SETTINGS_MODAL):
            self.__setting_view.run_concurrent()
        return event
