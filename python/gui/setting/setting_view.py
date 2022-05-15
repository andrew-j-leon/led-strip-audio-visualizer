import os
from typing import Any, Callable, Dict, List, Tuple, Union

import PySimpleGUI as sg
import util.util as util
from gui.setting.error_message import *
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED

BUTTON_FONT = ("Courier New", 14)
INPUT_LABEL_FONT = ("Courier New", 14)
DROPDOWN_INPUT_FONT = ("Courier New", 14)
CHECKBOX_INPUT_FONT = ("Courier New", 14)
H1 = ("Courier New", 18)


class Element:
    CONFIRMATION_MODAL_OK_BUTTON = "error_modal_ok_button"
    LOAD_BUTTON = "load_setting_button"
    SAVE_BUTTON = "save_settings_button"
    DELETE_BUTTON = "delete_setting_button"
    RESET_SETTING_BUTTON = "reset_setting_button"


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


class Event:
    WINDOW_CLOSED = WINDOW_CLOSED
    TIMEOUT_EVENT = TIMEOUT_EVENT
    CONFIRMATION_MODAL_OK = Element.CONFIRMATION_MODAL_OK_BUTTON
    FILE_NAME_COMBO_CHANGE = SettingElement.SETTING_FILE_NAME_COMBO
    LOAD = Element.LOAD_BUTTON
    SAVE = Element.SAVE_BUTTON
    DELETE = Element.DELETE_BUTTON
    RESET = Element.RESET_SETTING_BUTTON


_BAUDRATES = ["115200", "57600", "38400", "31250", "28800", "19200", "14400", "9600", "4800", "2400", "1200", "600", "300"]


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


class SettingView:
    def __init__(self):
        self.__main_window: sg.Window = None

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

    def __del__(self):
        self.__close_main_window()

    def get_value(self, element: str) -> Any:
        if (element not in self.__element_to_value_method):
            raise ValueError("Element {} is not a value that can be retrieved. Valid elements are : {}".format(element, util.get_non_builtin_items(SettingElement)))

        return self.__element_to_value_method[element]()

    def display_confirmation_modal(self, title: str, error_message: str):
        '''
            Display a modal that blocks input from all other windows until said modal's
            "Ok" button or upper-right "X" button is clicked.

            Args:
                `title (str)`: The title of the modal.
                `error_message (str)`: The modal's message to the user.
        '''
        LAYOUT = [[sg.Text(text=error_message)], [sg.Button(button_text="Ok")]]

        modal = sg.Window(title=title, layout=LAYOUT, modal=True)

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
        self.__main_window = self._create_main_window()
        self.__main_window.read(timeout=0)

        while (self.__main_window):
            event: str = self.__main_window.read(timeout=0)
            event: str = self._handle_event_before_client_on_event(event)

            on_event(event)

            if (event == Event.WINDOW_CLOSED):
                self.__close_main_window()

    def __close_main_window(self):
        if (self.__main_window):
            self.__main_window.close()
            self.__main_window = None

    # Helper methods for child classes

    def _update_element(self, element: str, *update_args, **update_kwargs):
        self.__main_window[element].update(*update_args, **update_kwargs)

    def _create_gui_rows(self, *rows: Tuple[List[sg.Element]]) -> List[List[sg.Element]]:
        gui_rows: List[List[sg.Element]] = []
        util.foreach(rows, lambda row: gui_rows.append(row))
        return gui_rows

    def _get_element_value(self, element: str) -> Any:
        return self.__main_window[element].get()

    def _fill_input_fields(self, values: Dict[str, Any]):
        self.__main_window.fill(values)

    # Methods the child class can/shold override

    def _create_main_window(self) -> sg.Window:
        LAYOUT = [[sg.Combo(values=_get_user_setting_file_names(),
                            default_value=("" if (_get_current_setting_file_name() == _get_default_setting_file_name())
                                           else _get_current_setting_file_name()),
                            key=SettingElement.SETTING_FILE_NAME_COMBO, size=(50, 1)),
                   sg.Button(button_text="Load", key=Element.LOAD_BUTTON, font=BUTTON_FONT, disabled=True),
                   sg.Button(button_text="Save", key=Element.SAVE_BUTTON, font=BUTTON_FONT, disabled=True),
                   sg.Button(button_text="Delete", key=Element.DELETE_BUTTON, font=BUTTON_FONT, disabled=True),
                   sg.Button(button_text="Reset", key=Element.RESET_SETTING_BUTTON, font=BUTTON_FONT)],

                  [sg.Text(text="General", font=H1)],
                  [sg.Text(text="Led Index Range:", font=INPUT_LABEL_FONT),
                   sg.Text(text="start_index (inclusive):", font=INPUT_LABEL_FONT), sg.Input(key=SettingElement.START_LED_INDEX_INPUT,
                                                                                             default_text=self.__settings[SettingElement.START_LED_INDEX_INPUT]),
                   sg.Text(text="end_index (exclusive):", font=INPUT_LABEL_FONT), sg.Input(key=SettingElement.END_LED_INDEX_INPUT,
                                                                                           default_text=self.__settings[SettingElement.END_LED_INDEX_INPUT])],
                  [sg.Text(text="Milliseconds per Audio Chunk:", font=INPUT_LABEL_FONT), sg.Input(key=SettingElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                                                                                                  default_text=self.__settings[SettingElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT])],

                  [sg.Text(text="Serial", font=H1)],
                  [sg.Text(text="Port:", font=INPUT_LABEL_FONT), sg.Input(key=SettingElement.SERIAL_PORT_INPUT, default_text=self.__settings[SettingElement.SERIAL_PORT_INPUT])],
                  [sg.Text(text="Baudrate:", font=INPUT_LABEL_FONT), sg.DropDown(key=SettingElement.SERIAL_BAUDRATE_DROPDOWN, values=_BAUDRATES, default_value=self.__settings[SettingElement.SERIAL_BAUDRATE_DROPDOWN])],
                  [sg.Text(text="Brightness", font=INPUT_LABEL_FONT), sg.Input(key=SettingElement.BRIGHTNESS_INPUT, default_text=self.__settings[SettingElement.BRIGHTNESS_INPUT])],

                  [sg.Text(text="Frequency Visualizer", font=H1)],
                  [sg.Text(text="Number of Groups:", font=INPUT_LABEL_FONT), sg.Input(key=SettingElement.NUMBER_OF_GROUPS_INPUT, default_text=self.__settings[SettingElement.NUMBER_OF_GROUPS_INPUT])],

                  [sg.Text(text="Frequency Range:", font=INPUT_LABEL_FONT),
                   sg.Text("minimum:", font=INPUT_LABEL_FONT), sg.Input(key=SettingElement.MINIMUM_FREQUENCY_INPUT, default_text=self.__settings[SettingElement.MINIMUM_FREQUENCY_INPUT]),
                   sg.Text("maximum", font=INPUT_LABEL_FONT), sg.Input(key=SettingElement.MAXIMUM_FREQUENCY_INPUT, default_text=self.__settings[SettingElement.MAXIMUM_FREQUENCY_INPUT])],

                  [sg.Checkbox(text="Should Reverse Led Indicies", key=SettingElement.SHOULD_REVERSE_LED_INDICIES_CHECKBOX, font=CHECKBOX_INPUT_FONT)],

                  [sg.Text(text="Amplitude to RGB", font=INPUT_LABEL_FONT),
                   sg.Multiline(key=SettingElement.AMPLITUDE_TO_RGB_INPUT, default_text=self.__settings[SettingElement.AMPLITUDE_TO_RGB_INPUT])],

                  [sg.ColorChooserButton(button_text="Pick Color")]]

        return sg.Window(title="Settings", layout=LAYOUT, modal=True)

    def _handle_event_before_client_on_event(self, event: str) -> str:
        if (event in self.__event_to_method):
            self.__event_to_method[event]()
        self.__handle_setting_file_name_combo_event()
        return event

    def __get_start_led_index(self) -> int:
        return int(self.__settings[SettingElement.START_LED_INDEX_INPUT])

    def __get_end_led_index(self) -> int:
        return int(self.__settings[SettingElement.END_LED_INDEX_INPUT])

    def __get_milliseconds_per_audio_chunk(self) -> int:
        return int(self.__settings[SettingElement.MILLISECONDS_PER_AUDIO_CHUNK_INPUT])

    def __get_serial_port(self) -> str:
        return self.__settings[SettingElement.SERIAL_PORT_INPUT]

    def __get_serial_baudrate(self) -> int:
        return int(self.__settings[SettingElement.SERIAL_BAUDRATE_DROPDOWN])

    def __get_brightness(self) -> int:
        return int(self.__settings[SettingElement.BRIGHTNESS_INPUT])

    def __get_minimum_frequency(self) -> int:
        return int(self.__settings[SettingElement.MINIMUM_FREQUENCY_INPUT])

    def __get_maximum_frequency(self) -> int:
        return int(self.__settings[SettingElement.MAXIMUM_FREQUENCY_INPUT])

    def __should_reverse_indicies(self) -> bool:
        return self.__settings[SettingElement.SHOULD_REVERSE_LED_INDICIES_CHECKBOX]

    def __get_number_of_groups(self) -> int:
        return int(self.__settings[SettingElement.NUMBER_OF_GROUPS_INPUT])

    def __get_amplitude_to_rgb(self) -> List[Tuple[int, int, int]]:
        if (self.__settings[SettingElement.AMPLITUDE_TO_RGB_INPUT] == ""):
            return _create_default_amplitude_to_rgb()

        else:
            amplitude_rgbs: List[str] = self.__settings[SettingElement.AMPLITUDE_TO_RGB_INPUT].split("\n")
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
        file_name: str = self.__get_setting_modal_element_value(SettingElement.SETTING_FILE_NAME_COMBO)
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
        file_name: str = self.__get_setting_modal_element_value(SettingElement.SETTING_FILE_NAME_COMBO)

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
        file_name: str = self.__get_setting_modal_element_value(SettingElement.SETTING_FILE_NAME_COMBO)
        if (not _is_user_setting_file_name(file_name)):
            self.display_confirmation_modal("File not found", "The file {} could not be found.".format(file_name))

        else:
            sg.user_settings_filename(filename=file_name, path=_get_setting_directory_path())
            self.__settings = sg.user_settings()
            _save_current_setting_file_name(file_name)

            self._fill_input_fields(self.__settings)

    def __handle_setting_file_name_combo_event(self):
        file_name: str = self.__get_setting_modal_element_value(SettingElement.SETTING_FILE_NAME_COMBO)

        if (file_name == ""):
            self._update_element(Element.LOAD_BUTTON, disabled=True)
            self._update_element(Element.SAVE_BUTTON, disabled=True)
            self._update_element(Element.DELETE_BUTTON, disabled=True)

        elif (_is_user_setting_file_name(file_name)):
            self._update_element(Element.LOAD_BUTTON, disabled=False)
            self._update_element(Element.SAVE_BUTTON, disabled=False)
            self._update_element(Element.DELETE_BUTTON, disabled=False)

        elif (file_name != None):
            self._update_element(Element.LOAD_BUTTON, disabled=True)
            self._update_element(Element.SAVE_BUTTON, disabled=False)
            self._update_element(Element.DELETE_BUTTON, disabled=True)

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
