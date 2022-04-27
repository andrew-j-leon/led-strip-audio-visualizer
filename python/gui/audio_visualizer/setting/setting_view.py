import os
from typing import Any, Callable, Dict, List, Tuple, Union

import gui.styling as styling
import gui.view as view
import PySimpleGUI as sg
import util.util as util
from gui.audio_visualizer.setting.error_message import *
from gui.window import Window


def _create_default_amplitude_to_rgb() -> List[Tuple[int, int, int]]:
    SATURATION = 85
    LIGHTNESS = 35

    MINIMUM_AMPLITUDE = 0  # dB
    MAXIMUM_AMPLITUDE = 200  # dB

    amplitude_rgbs: List[Tuple[int, int, int]] = []
    for amplitude in range(MINIMUM_AMPLITUDE, MAXIMUM_AMPLITUDE + 1):
        amplitude_rgbs.append(util.hsl_to_rgb(__get_hue(amplitude), SATURATION, LIGHTNESS))
    return amplitude_rgbs


def __get_hue(amplitude: Union[int, float]) -> int:
    if (amplitude < 41):
        return 240

    amp = min(57.5, max(0, amplitude))

    step_strength = 5.5

    # Try graphing this equation. The x-axis is the amplitude & the y-axis the hue.
    hue = round(step_strength * (-120 / 11) * round((amp - 5.25) / step_strength) + 600)
    return hue if (hue >= 0) else 0


_BAUDRATES = ["115200", "57600", "38400", "31250", "28800", "19200", "14400", "9600", "4800", "2400", "1200", "600", "300"]


class SettingElement:
    SETTING_FILE_NAME_COMBO = "setting_file_name_combo"

    START_LED_INDEX_INPUT = "start_led_index_input"
    END_LED_INDEX_INPUT = "end_led_index_input"
    MILLISECONDS_PER_AUDIO_CHUNK_INPUT = "milliseconds_per_audio_chunk_input"

    SERIAL_PORT_INPUT = "serial_port_input"
    SERIAL_BAUDRATE_DROPDOWN = "serial_baudrate_dropdown"
    BRIGHTNESS_INPUT = "brightness_input"

    NUMBER_OF_GROUPS_INPUT = "number_of_groups_input"
    MINIMUM_FREQUENCY_INPUT = "minimum_frequency_input"
    MAXIMUM_FREQUENCY_INPUT = "maximum_frequency_input"
    SHOULD_REVERSE_LED_INDICIES_CHECKBOX = "should_reverse_led_indicies_checkbox"
    AMPLITUDE_TO_RGB_INPUT = "amplitude_to_rgb_input"


class Element(SettingElement, view.Element):
    pass


class _Element(Element, view._Element):
    LOAD_BUTTON = "load_setting_button"
    SAVE_BUTTON = "save_settings_button"
    DELETE_BUTTON = "delete_setting_button"
    RESET_SETTING_BUTTON = "reset_setting_button"


class Event(view.Event):
    FILE_NAME_COMBO_CHANGE = _Element.SETTING_FILE_NAME_COMBO
    LOAD = _Element.LOAD_BUTTON
    SAVE = _Element.SAVE_BUTTON
    DELETE = _Element.DELETE_BUTTON
    RESET = _Element.RESET_SETTING_BUTTON


class SettingView(view.View):
    def __init__(self):
        view.View.__init__(self)

        sg.user_settings_filename(filename=_get_current_setting_file_name(), path=_get_setting_directory_path())

        self.__settings: Dict[str, Any] = sg.user_settings()  # For faster retrieval
        self.__event_to_method: Dict[str, Callable[[], None]] = {Event.LOAD: self.__load, Event.SAVE: self.__save,
                                                                 Event.DELETE: self.__delete, Event.RESET: self.__reset}

        self.__element_to_value_method: Dict[str, Callable[[], None]] = {SettingElement.START_LED_INDEX_INPUT: self.__get_start_led_index,
                                                                         SettingElement.END_LED_INDEX_INPUT: self.__get_end_led_index,
                                                                         SettingElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT: self.__get_milliseconds_per_audio_chunk,
                                                                         SettingElement.SERIAL_PORT_INPUT: self.__get_serial_port,
                                                                         SettingElement.SERIAL_BAUDRATE_DROPDOWN: self.__get_serial_baudrate,
                                                                         SettingElement.BRIGHTNESS_INPUT: self.__get_brightness,
                                                                         SettingElement.NUMBER_OF_GROUPS_INPUT: self.__get_number_of_groups,
                                                                         SettingElement.MINIMUM_FREQUENCY_INPUT: self.__get_minimum_frequency,
                                                                         SettingElement.MAXIMUM_FREQUENCY_INPUT: self.__get_maximum_frequency,
                                                                         SettingElement.SHOULD_REVERSE_LED_INDICIES_CHECKBOX: self.__should_reverse_indicies,
                                                                         SettingElement.AMPLITUDE_TO_RGB_INPUT: self.__get_amplitude_to_rgb}

    def _create_main_window(self):
        LAYOUT = [[sg.Combo(values=_get_user_setting_file_names(),
                            default_value=("" if (_get_current_setting_file_name() == _get_default_setting_file_name())
                                           else _get_current_setting_file_name()),
                            key=_Element.SETTING_FILE_NAME_COMBO, size=(50, 1)),
                   sg.Button(button_text="Load", key=_Element.LOAD_BUTTON, font=styling.BUTTON_FONT, disabled=True),
                   sg.Button(button_text="Save", key=_Element.SAVE_BUTTON, font=styling.BUTTON_FONT, disabled=True),
                   sg.Button(button_text="Delete", key=_Element.DELETE_BUTTON, font=styling.BUTTON_FONT, disabled=True),
                   sg.Button(button_text="Reset", key=_Element.RESET_SETTING_BUTTON, font=styling.BUTTON_FONT)],

                  [sg.Text(text="General", font=styling.H1)],
                  [sg.Text(text="Led Index Range:", font=styling.INPUT_LABEL_FONT),
                   sg.Text(text="start_index (inclusive):", font=styling.INPUT_LABEL_FONT), sg.Input(key=_Element.START_LED_INDEX_INPUT,
                                                                                                     default_text=self.__settings[_Element.START_LED_INDEX_INPUT]),
                   sg.Text(text="end_index (exclusive):", font=styling.INPUT_LABEL_FONT), sg.Input(key=_Element.END_LED_INDEX_INPUT,
                                                                                                   default_text=self.__settings[_Element.END_LED_INDEX_INPUT])],
                  [sg.Text(text="Milliseconds per Audio Chunk:", font=styling.INPUT_LABEL_FONT), sg.Input(key=_Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                                                                                                          default_text=self.__settings[_Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT])],

                  [sg.Text(text="Serial", font=styling.H1)],
                  [sg.Text(text="Port:", font=styling.INPUT_LABEL_FONT), sg.Input(key=_Element.SERIAL_PORT_INPUT, default_text=self.__settings[_Element.SERIAL_PORT_INPUT])],
                  [sg.Text(text="Baudrate:", font=styling.INPUT_LABEL_FONT), sg.DropDown(key=_Element.SERIAL_BAUDRATE_DROPDOWN, values=_BAUDRATES, default_value=self.__settings[_Element.SERIAL_BAUDRATE_DROPDOWN])],
                  [sg.Text(text="Brightness", font=styling.INPUT_LABEL_FONT), sg.Input(key=_Element.BRIGHTNESS_INPUT, default_text=self.__settings[_Element.BRIGHTNESS_INPUT])],

                  [sg.Text(text="Frequency Visualizer", font=styling.H1)],
                  [sg.Text(text="Number of Groups:", font=styling.INPUT_LABEL_FONT), sg.Input(key=_Element.NUMBER_OF_GROUPS_INPUT, default_text=self.__settings[_Element.NUMBER_OF_GROUPS_INPUT])],

                  [sg.Text(text="Frequency Range:", font=styling.INPUT_LABEL_FONT),
                   sg.Text("minimum:", font=styling.INPUT_LABEL_FONT), sg.Input(key=_Element.MINIMUM_FREQUENCY_INPUT, default_text=self.__settings[_Element.MINIMUM_FREQUENCY_INPUT]),
                   sg.Text("maximum", font=styling.INPUT_LABEL_FONT), sg.Input(key=_Element.MAXIMUM_FREQUENCY_INPUT, default_text=self.__settings[_Element.MAXIMUM_FREQUENCY_INPUT])],

                  [sg.Checkbox(text="Should Reverse Led Indicies", key=_Element.SHOULD_REVERSE_LED_INDICIES_CHECKBOX, font=styling.CHECKBOX_INPUT_FONT)],

                  [sg.Text(text="Amplitude to RGB", font=styling.INPUT_LABEL_FONT),
                   sg.Multiline(key=_Element.AMPLITUDE_TO_RGB_INPUT, default_text=self.__settings[_Element.AMPLITUDE_TO_RGB_INPUT])],

                  [sg.ColorChooserButton(button_text="Pick Color")]]

        return Window(title="Settings", layout=LAYOUT, modal=True)

    def _handle_event_before_client_on_event(self, event: str) -> str:
        if (event in self.__event_to_method):
            self.__event_to_method[event]()
        self.__handle_setting_file_name_combo_event()
        return event

    def get_value(self, element: str) -> Any:
        if (element not in self.__element_to_value_method):
            raise ValueError("Element {} is not a value that can be retrieved. Valid elements are : {}".format(element, util.get_non_builtin_items(SettingElement)))

        return self.__element_to_value_method[element]()

    def __get_start_led_index(self) -> int:
        return int(self.__settings[_Element.START_LED_INDEX_INPUT])

    def __get_end_led_index(self) -> int:
        return int(self.__settings[_Element.END_LED_INDEX_INPUT])

    def __get_milliseconds_per_audio_chunk(self) -> int:
        return int(self.__settings[_Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT])

    def __get_serial_port(self) -> str:
        return self.__settings[_Element.SERIAL_PORT_INPUT]

    def __get_serial_baudrate(self) -> int:
        return int(self.__settings[_Element.SERIAL_BAUDRATE_DROPDOWN])

    def __get_brightness(self) -> int:
        return int(self.__settings[_Element.BRIGHTNESS_INPUT])

    def __get_minimum_frequency(self) -> int:
        return int(self.__settings[_Element.MINIMUM_FREQUENCY_INPUT])

    def __get_maximum_frequency(self) -> int:
        return int(self.__settings[_Element.MAXIMUM_FREQUENCY_INPUT])

    def __should_reverse_indicies(self) -> bool:
        return self.__settings[_Element.SHOULD_REVERSE_LED_INDICIES_CHECKBOX]

    def __get_number_of_groups(self) -> int:
        return int(self.__settings[_Element.NUMBER_OF_GROUPS_INPUT])

    def __get_amplitude_to_rgb(self) -> List[Tuple[int, int, int]]:
        if (self.__settings[_Element.AMPLITUDE_TO_RGB_INPUT] == ""):
            return _create_default_amplitude_to_rgb()

        else:
            amplitude_rgbs: List[str] = self.__settings[_Element.AMPLITUDE_TO_RGB_INPUT].split("\n")
            for amplitude in range(len(amplitude_rgbs)):
                amplitude_rgbs[amplitude] = tuple(map(lambda rgb_str: int(rgb_str), amplitude_rgbs[amplitude].split(",")))
            return amplitude_rgbs

    def __reset(self):
        sg.user_settings_filename(filename=_get_default_setting_file_name(), path=_get_setting_directory_path())
        self.__settings = sg.user_settings()
        _save_current_setting_file_name(_get_default_setting_file_name())
        self._fill_input_fields(self.__settings)

    def __get_setting_modal_element_value(self, element: str) -> Any:
        return self._get_element_value(element)

    def __delete(self):
        file_name: str = self.__get_setting_modal_element_value(_Element.SETTING_FILE_NAME_COMBO)
        if (not _is_user_setting_file_name(file_name)):
            self.display_confirmation_modal("File not found", "The file {} could not be found.".format(file_name))
        else:
            os.remove(os.path.join(_get_setting_directory_path(), file_name))
            self.__reset()

    def __get_input_settings(self) -> dict:
        values: dict = dict()
        for setting_element in util.get_non_builtin_items(SettingElement).values():
            values[setting_element] = self.__get_setting_modal_element_value(setting_element)
        return values

    def __save(self):
        file_name: str = self.__get_setting_modal_element_value(_Element.SETTING_FILE_NAME_COMBO)

        if (not _is_valid_user_setting_file_name(file_name)):
            self.display_confirmation_modal("Invalid file name", "The file name {} is invalid.")

        else:
            if (self.__check_settings()):
                sg.user_settings_save(file_name, _get_setting_directory_path())
                sg.user_settings_filename(filename=file_name, path=_get_setting_directory_path())
                sg.user_settings_write_new_dictionary(self.__get_input_settings())
                self.__settings = sg.user_settings()
                _save_current_setting_file_name(file_name)

                self._fill_input_fields(self.__settings)

    def __load(self):
        file_name: str = self.__get_setting_modal_element_value(_Element.SETTING_FILE_NAME_COMBO)
        if (not _is_user_setting_file_name(file_name)):
            self.display_confirmation_modal("File not found", "The file {} could not be found.".format(file_name))

        else:
            sg.user_settings_filename(filename=file_name, path=_get_setting_directory_path())
            self.__settings = sg.user_settings()
            _save_current_setting_file_name(file_name)

            self._fill_input_fields(self.__settings)

    def __handle_setting_file_name_combo_event(self):
        file_name: str = self.__get_setting_modal_element_value(_Element.SETTING_FILE_NAME_COMBO)

        if (file_name == ""):
            self._update_element(_Element.LOAD_BUTTON, disabled=True)
            self._update_element(_Element.SAVE_BUTTON, disabled=True)
            self._update_element(_Element.DELETE_BUTTON, disabled=True)

        elif (_is_user_setting_file_name(file_name)):
            self._update_element(_Element.LOAD_BUTTON, disabled=False)
            self._update_element(_Element.SAVE_BUTTON, disabled=False)
            self._update_element(_Element.DELETE_BUTTON, disabled=False)

        elif (file_name != None):
            self._update_element(_Element.LOAD_BUTTON, disabled=True)
            self._update_element(_Element.SAVE_BUTTON, disabled=False)
            self._update_element(_Element.DELETE_BUTTON, disabled=True)

    def __check_settings(self) -> bool:
        error_messages: List[str] = [get_led_index_range_error_message(self._get_element_value(SettingElement.START_LED_INDEX_INPUT),
                                                                       self._get_element_value(SettingElement.END_LED_INDEX_INPUT)),
                                     get_milliseconds_per_audio_chunk_error_message(self._get_element_value(SettingElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT)),
                                     get_serial_baudrate_error_message(self._get_element_value(SettingElement.SERIAL_BAUDRATE_DROPDOWN), _BAUDRATES),
                                     get_brightness_error_message(self._get_element_value(SettingElement.BRIGHTNESS_INPUT)),
                                     get_frequency_range_error_message(self._get_element_value(SettingElement.MINIMUM_FREQUENCY_INPUT),
                                                                       self._get_element_value(SettingElement.MAXIMUM_FREQUENCY_INPUT)),
                                     get_should_reverse_indicies_error_message(self._get_element_value(SettingElement.SHOULD_REVERSE_LED_INDICIES_CHECKBOX)),
                                     get_number_of_groups_error_message(self._get_element_value(SettingElement.NUMBER_OF_GROUPS_INPUT)),
                                     get_amplitude_to_rgb_error_message(self._get_element_value(SettingElement.AMPLITUDE_TO_RGB_INPUT))]

        message = ""
        for error_message in error_messages:
            message += error_message

        if (message.strip() != ""):
            self.display_confirmation_modal(title="Invalid Input(s)", error_message="The following settings were invalid:\n\n{}".format(message))
            return False
        return True


def _is_valid_user_setting_file_name(file_name: str) -> bool:
    for substring in [".", "/", "\\"]:
        if substring in file_name:
            return False

    return not util.is_empty(file_name)


def _get_setting_directory_path() -> str:
    return (util.join_paths(__file__, "../../.settings"))


def _get_default_setting_file_name() -> str:
    return ".default"


def _get_user_setting_file_names() -> List[str]:
    return [file_name for file_name in os.listdir(_get_setting_directory_path())
            if (file_name not in (_get_default_setting_file_name(), _get_current_setting_container_file_name()))]


def _get_current_setting_container_file_name() -> str:
    return ".current_setting"


def _get_current_setting_container_file_path() -> str:
    return os.path.join(_get_setting_directory_path(), _get_current_setting_container_file_name())


def _get_current_setting_file_name() -> str:
    with open(_get_current_setting_container_file_path(), "r") as file:
        return file.readline()


def _save_current_setting_file_name(file_name: str) -> str:
    with open(_get_current_setting_container_file_path(), "w") as file:
        file.write(file_name)


def _is_user_setting_file_name(file_name) -> bool:
    return file_name in _get_user_setting_file_names()
