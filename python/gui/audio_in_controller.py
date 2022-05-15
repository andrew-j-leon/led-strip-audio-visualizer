from typing import Any, Callable, Dict, List, Tuple

import gui.setting.setting_view as setting_view
import numpy
import pyaudio
import PySimpleGUI as sg
import util.util as util
from led_strip.grouped_leds import GraphicGroupedLeds, SerialGroupedLeds
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.gui import ProductionGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED
from visualizer.spectrogram import Spectrogram

# View
BUTTON_FONT = ("Courier New", 14)
INPUT_LABEL_FONT = ("Courier New", 14)
DROPDOWN_INPUT_FONT = ("Courier New", 14)
CHECKBOX_INPUT_FONT = ("Courier New", 14)

H1 = ("Courier New", 18)


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
        self.__main_window: sg.Window = None

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

        modal = sg.Window(title=title, layout=LAYOUT, modal=True)

        while True:
            event = modal.read(timeout=0)[0]
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
            event: str = self.__main_window.read(timeout=0)[0]
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

    def _create_main_window(self) -> sg.Window:
        VISUALIZER_DROPDOWN_VALUES: List[str] = [VisualizerType.NONE, VisualizerType.FREQUENCY]

        row_with_settings_button = [sg.Button(button_text="Settings", key=Element.SETTINGS_BUTTON)]

        row_with_default_visualizer_and_led_selection = [sg.Text(text="Visualizer : ", key=Element.SELECT_VISUALIZER_TYPE_LABEL, font=INPUT_LABEL_FONT),
                                                         sg.Combo(values=VISUALIZER_DROPDOWN_VALUES,
                                                                  default_value=VisualizerType.FREQUENCY, key=Element.SELECT_VISUALIZER_TYPE_DROPDOWN, font=DROPDOWN_INPUT_FONT),
                                                         sg.Checkbox(text="Serial Led Strip", key=Element.SERIAL_LED_STRIP_CHECKBOX, font=CHECKBOX_INPUT_FONT),
                                                         sg.Checkbox(text="Graphic Led Strip", key=Element.GRAPHIC_LED_STRIP_CHECKBOX, font=CHECKBOX_INPUT_FONT)]

        row_with_default_visualizer_and_led_selection = (self.__get_elements_to_the_left_of_default_visualizer_and_led_selection()
                                                         + row_with_default_visualizer_and_led_selection
                                                         + self.__get_elements_to_the_right_of_default_visualizer_and_led_selection())

        layout = [row_with_settings_button]
        util.foreach(self.__get_rows_above_default_visualizer_and_led_selection(), lambda row: layout.append(row))
        layout.append(row_with_default_visualizer_and_led_selection)
        util.foreach(self.__get_rows_below_default_visualizer_and_led_selection(), lambda row: layout.append(row))

        return sg.Window('Led Strip Music Visualizer', layout=layout, resizable=True, element_padding=(0, 0),
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
                                     [sg.Button(button_text="Pause (||)", disabled=True, key=Element.PAUSE_AUDIO_BUTTON, font=BUTTON_FONT),
                                      sg.Button(button_text="Resume (>)", disabled=False, key=Element.RESUME_AUDIO_BUTTON, font=BUTTON_FONT)])

    def __get_rows_below_default_visualizer_and_led_selection(self) -> List[List[sg.Element]]:
        rows = []

        if (not _gui_rows_are_valid(rows)):
            raise TypeError("rows are not valid PySimpleGui rows")
        return rows

    def _handle_event_before_client_on_event(self, event: str) -> str:
        if (event == Event.OPEN_SETTINGS_MODAL):
            self.__setting_view.run_concurrent()
        return event


# Model
class State:
    PLAYING = "playing"
    PAUSED = "paused"


class NoDefaultInputDeviceDetectedError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class AudioInModel:
    def __init__(self):
        self._audio_player_maker = pyaudio.PyAudio()
        self._audio_player: pyaudio.Stream = None
        self._audio_chunk: bytes = b''

        self.__set_default_input_device()

    def __del__(self):
        self.__close_audio_player()

        if (self._audio_player_maker is not None):
            self._audio_player_maker.terminate()

    def update(self, milliseconds_of_audio_to_read: int, on_audio_read: Callable):
        if (self.is_state(State.PLAYING)):
            number_of_frames = self.milliseconds_to_number_of_frames(milliseconds_of_audio_to_read)

            self._audio_chunk: bytes = self._audio_player.read(number_of_frames)
            on_audio_read(self._audio_chunk)

    def is_state(self, state: str) -> bool:
        if (state == State.PLAYING):
            return (isinstance(self._audio_player, pyaudio.Stream) and self._audio_player.is_active())

        elif (state == State.PAUSED):
            return (isinstance(self._audio_player, pyaudio.Stream) and self._audio_player.is_stopped())

        return False

    def milliseconds_to_number_of_frames(self, milliseconds: int) -> int:
        return int(self.__get_number_of_frames_per_millisecond() * milliseconds)

    def pause(self):
        if (self._audio_player):
            self._audio_player.stop_stream()

    def resume(self):
        if (self._audio_player):
            self._audio_player.start_stream()

    def number_of_frames_to_milliseconds(self, number_of_frames: int) -> int:
        return int((1 / self.__get_number_of_frames_per_millisecond()) * number_of_frames)

    def get_framerate(self) -> int:
        return self._audio_player._rate

    def get_current_input_device_name(self) -> str:
        return self._audio_player_maker.get_default_input_device_info()["name"]

    def __get_number_of_frames_per_millisecond(self) -> int:
        number_of_milliseconds_per_second = 1000
        return self.get_framerate() / number_of_milliseconds_per_second

    def __set_default_input_device(self):
        def init_audio_player(*stream_args, **stream_kwargs):
            self.__close_audio_player()
            self._audio_player = self._audio_player_maker.open(*stream_args, **stream_kwargs)

        default_input_device_info: dict = self._audio_player_maker.get_default_input_device_info()

        if (util.is_empty(default_input_device_info)):
            raise NoDefaultInputDeviceDetectedError("There is no default input device set on this machine.")

        init_audio_player(format=pyaudio.paInt16, channels=default_input_device_info["maxInputChannels"],
                          rate=int(default_input_device_info["defaultSampleRate"]), input=True)

        self._audio_player.stop_stream()

    def __close_audio_player(self):
        if (self._audio_player):
            self._audio_player.close()
            self._audio_player = None


# Controller
_START_LED_INDEX = 0
_END_LED_INDEX = 1


class AudioInController:
    def __init__(self):
        self.view = AudioInView()
        self.audio_player = AudioInModel()
        self.spectrogram: Spectrogram = None
        self.led_strip: LedStrip = None

    def __del__(self):
        self.__delete_spectrogram()

        if (self.led_strip is not None):
            BLACK_RGB = (0, 0, 0)

            self.led_strip.clear_queued_colors()

            for group in range(self.led_strip.number_of_groups):
                self.led_strip.enqueue_rgb(group, BLACK_RGB)

            self.led_strip.show_queued_colors()

            del self.led_strip
            self.led_strip = None

        del self.view
        del self.audio_player

    def start(self):
        def on_audio_player_update(audio_chunk: bytes):
            if (self.spectrogram):
                if (isinstance(self.spectrogram, Spectrogram)):

                    number_of_frames = self.audio_player.milliseconds_to_number_of_frames(self.view.get_milliseconds_per_audio_chunk())
                    self.spectrogram.update_led_strips(self.led_strip, audio_chunk, number_of_frames, self.audio_player.get_framerate(),
                                                       numpy.int16)

        def on_gui_event(event: str):
            self.audio_player.update(self.view.get_milliseconds_per_audio_chunk(),
                                     on_audio_player_update)

            if (event != Event.TIMEOUT_EVENT):
                if (self.__ui_event_is_valid(event)):
                    self.__handle_valid_ui_event(event)
                else:
                    self.__handle_invalid_ui_event(event)

        self.view.run_concurrent(on_gui_event)

    def __ui_event_is_valid(self, event: str) -> bool:
        if (event == Event.PAUSE_AUDIO):
            return self.audio_player.is_state(State.PLAYING)

        elif (event == Event.RESUME_AUDIO):
            return self.audio_player.is_state(State.PAUSED)

        return event in (Event.WINDOW_CLOSED, Event.TIMEOUT_EVENT, Event.OPEN_SETTINGS_MODAL)

    def __handle_valid_ui_event(self, event: str):

        def get_group_index_to_led_range() -> List[Tuple[int, int]]:
            def shift_index_up_by_start_index(index: int) -> int:
                return index + get_start_led_index()

            def get_number_of_leds() -> int:
                return get_end_led_index() - get_start_led_index()

            def get_start_led_index() -> int:
                return self.view.get_led_index_range()[_START_LED_INDEX]

            def get_end_led_index() -> int:
                return self.view.get_led_index_range()[_END_LED_INDEX]

            number_of_leds_per_group = max(1, get_number_of_leds() // self.view.get_number_of_groups())
            group_index_to_led_range = list()

            for group_index in range(self.view.get_number_of_groups()):
                shifted_start_index = shift_index_up_by_start_index(group_index * number_of_leds_per_group)
                shifted_end_index = shifted_start_index + number_of_leds_per_group

                group_index_to_led_range.append((shifted_start_index, shifted_end_index))

            if (self.view.should_reverse_indicies()):
                group_index_to_led_range.reverse()

            return group_index_to_led_range

        def get_led_strip():
            if (self.view.get_serial_led_strip_checkbox_value()):

                PORT = self.view.get_serial_port()
                BAUDRATE = self.view.get_serial_baudrate()
                PARITY = PARITY_NONE
                STOP_BITS = STOPBITS_ONE_POINT_FIVE
                BYTE_SIZE = EIGHTBITS
                READ_TIMEOUT = 1
                WRITE_TIMEOUT = 0

                serial = ProductionSerial(PORT, BAUDRATE, PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)

                serial_grouped_leds = SerialGroupedLeds(self.view.get_led_index_range(), get_group_index_to_led_range(),
                                                        serial, self.view.get_brightness())

                return ProductionLedStrip(serial_grouped_leds)

            if (self.view.get_graphic_led_strip_checkbox_value()):
                WIDTH = 1350
                HEIGHT = 600

                gui = ProductionGui(WIDTH, HEIGHT)
                gui.update()

                graphic_grouped_leds = GraphicGroupedLeds(self.view.get_led_index_range(),
                                                          get_group_index_to_led_range(),
                                                          gui)

                return ProductionLedStrip(graphic_grouped_leds)

        def init_spectrogram():
            self.__delete_spectrogram()
            if (self.view.get_visualizer_type_dropdown_value() == VisualizerType.FREQUENCY):
                FREQUENCY_RANGE = self.view.get_frequency_range()
                AMPLITUDE_TO_RGB = self.view.get_amplitude_to_rgb()
                self.led_strip = get_led_strip()

                self.spectrogram = Spectrogram(FREQUENCY_RANGE, AMPLITUDE_TO_RGB)

        if (event == Event.PAUSE_AUDIO):
            self.audio_player.pause()
            self.__delete_spectrogram()
            self.view.set_audio_paused_state()

        elif (event == Event.RESUME_AUDIO):
            current_input_source_message = f"Input Source : {self.audio_player.get_current_input_device_name()}"
            self.view.set_current_input_source_message(current_input_source_message)

            init_spectrogram()
            self.audio_player.resume()
            self.view.set_audio_playing_state()

    def __handle_invalid_ui_event(self, event: str):
        if (event not in (Event.PAUSE_AUDIO, Event.RESUME_AUDIO)):
            self.view.display_confirmation_modal("Error", "Did not recognize the event {}.".format(event))

    def __delete_spectrogram(self):
        if (self.spectrogram is not None):
            del self.spectrogram
            self.spectrogram = None
