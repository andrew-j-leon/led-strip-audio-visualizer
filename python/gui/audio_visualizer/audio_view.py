from typing import List, Tuple

import PySimpleGUI as sg

import util
import gui.view as view
from gui.window import Window
import gui.styling as styling
import gui.audio_visualizer.setting.setting_view as setting_view


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


class Element(view.Element):
    SELECT_VISUALIZER_TYPE_DROPDOWN = "select_visualizer_type_dropdown"
    SERIAL_LED_STRIP_CHECKBOX = "serial_led_strip_checkbox"
    GRAPHIC_LED_STRIP_CHECKBOX = "graphic_led_strip_checkbox"


class _Element(view._Element, Element):
    SELECT_VISUALIZER_TYPE_LABEL = "label_for_the_{}".format(Element.SELECT_VISUALIZER_TYPE_DROPDOWN)
    SETTINGS_BUTTON = "settings_button"


class Event(view.Event):
    OPEN_SETTINGS_MODAL = _Element.SETTINGS_BUTTON


class AudioView(view.View):
    def __init__(self):
        view.View.__init__(self)
        self.__setting_view: setting_view.SettingView = setting_view.SettingView()

    def _create_main_window(self) -> Window:
        VISUALIZER_DROPDOWN_VALUES: List[str] = [VisualizerType.NONE, VisualizerType.FREQUENCY]

        row_with_settings_button = [sg.Button(button_text="Settings", key=_Element.SETTINGS_BUTTON)]

        row_with_default_visualizer_and_led_selection = [sg.Text(text="Visualizer : ", key=_Element.SELECT_VISUALIZER_TYPE_LABEL, font=styling.INPUT_LABEL_FONT),
                                                         sg.Combo(values=VISUALIZER_DROPDOWN_VALUES,
                                                                  default_value=VisualizerType.FREQUENCY, key=_Element.SELECT_VISUALIZER_TYPE_DROPDOWN, font=styling.DROPDOWN_INPUT_FONT),
                                                         sg.Checkbox(text="Serial Led Strip", key=_Element.SERIAL_LED_STRIP_CHECKBOX, font=styling.CHECKBOX_INPUT_FONT),
                                                         sg.Checkbox(text="Graphic Led Strip", key=_Element.GRAPHIC_LED_STRIP_CHECKBOX, font=styling.CHECKBOX_INPUT_FONT)]

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
        elements = self._get_elements_to_the_left_of_default_visualizer_and_led_selection()

        if (not _gui_elements_are_valid(elements)):
            raise TypeError("elements are not valid PySimpleGui elements")
        return elements

    def __get_elements_to_the_right_of_default_visualizer_and_led_selection(self) -> List[sg.Element]:
        elements = self._get_elements_to_the_right_of_default_visualizer_and_led_selection()

        if (not _gui_elements_are_valid(elements)):
            raise TypeError("elements are not valid PySimpleGui elements")
        return elements

    def __get_rows_above_default_visualizer_and_led_selection(self) -> List[List[sg.Element]]:
        rows = self._get_rows_above_default_visualizer_and_led_selection()

        if (not _gui_rows_are_valid(rows)):
            raise TypeError("rows are not valid PySimpleGui rows")
        return rows

    def __get_rows_below_default_visualizer_and_led_selection(self) -> List[List[sg.Element]]:
        rows = self._get_rows_below_default_visualizer_and_led_selection()

        if (not _gui_rows_are_valid(rows)):
            raise TypeError("rows are not valid PySimpleGui rows")
        return rows

    def _get_elements_to_the_left_of_default_visualizer_and_led_selection(self) -> List[sg.Element]:
        return []

    def _get_elements_to_the_right_of_default_visualizer_and_led_selection(self) -> List[sg.Element]:
        return []

    def _get_rows_above_default_visualizer_and_led_selection(self) -> List[List[sg.Element]]:
        return []

    def _get_rows_below_default_visualizer_and_led_selection(self) -> List[List[sg.Element]]:
        return []

    def get_visualizer_type_dropdown_value(self) -> str:
        return self._get_element_value(_Element.SELECT_VISUALIZER_TYPE_DROPDOWN)

    def get_serial_led_strip_checkbox_value(self):
        return self._get_element_value(_Element.SERIAL_LED_STRIP_CHECKBOX)

    def get_graphic_led_strip_checkbox_value(self):
        return self._get_element_value(_Element.GRAPHIC_LED_STRIP_CHECKBOX)

    def _handle_event_before_client_on_event(self, event: str) -> str:
        if (event == Event.OPEN_SETTINGS_MODAL):
            self.__setting_view.run_concurrent()
        return event

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
