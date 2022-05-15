from typing import Any, Callable, List, Tuple

import numpy
import pyaudio
import PySimpleGUI as sg
import util.util as util
from gui.setting.setting_view import SettingView
from led_strip.grouped_leds import GraphicGroupedLeds, SerialGroupedLeds
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.gui import ProductionGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED
from visualizer.spectrogram import Spectrogram

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


class State:
    PLAYING = "playing"
    PAUSED = "paused"


class NoDefaultInputDeviceDetectedError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


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


class AudioInController:
    def __init__(self):
        self.__setting_view = SettingView()
        self.__main_window: sg.Window = None

        self._audio_player_maker = pyaudio.PyAudio()
        self.__audio_player: pyaudio.Stream = None
        self.__audio_chunk: bytes = b''
        self.__set_default_input_device()

        self.__spectrogram: Spectrogram = None
        self.__led_strip: LedStrip = None

    def __del__(self):
        self.__delete_spectrogram()

        if (self.__led_strip is not None):
            BLACK_RGB = (0, 0, 0)

            self.__led_strip.clear_queued_colors()

            for group in range(self.__led_strip.number_of_groups):
                self.__led_strip.enqueue_rgb(group, BLACK_RGB)

            self.__led_strip.show_queued_colors()

            del self.__led_strip
            self.__led_strip = None

        self.__close_main_window()

        self.__close_audio_player()

        if (self._audio_player_maker is not None):
            self._audio_player_maker.terminate()

    def start(self):
        def on_audio_player_update(audio_chunk: bytes):
            if (self.__spectrogram):
                if (isinstance(self.__spectrogram, Spectrogram)):

                    milleseconds_per_audio_chunk = self.__setting_view.get_milliseconds_per_audio_chunk()
                    number_of_frames = self.milliseconds_to_number_of_frames(milleseconds_per_audio_chunk)
                    self.__spectrogram.update_led_strips(self.__led_strip, audio_chunk, number_of_frames, self.__audio_player._rate, numpy.int16)

        self.__main_window = self.__create_main_window()
        self.__main_window.read(timeout=0)

        while (self.__main_window):
            event: str = self.__main_window.read(timeout=0)[0]
            event: str = self.__handle_event_before_client_on_event(event)

            milleseconds_per_audio_chunk = self.__setting_view.get_milliseconds_per_audio_chunk()
            self.update(milleseconds_per_audio_chunk, on_audio_player_update)

            if (event != Event.TIMEOUT_EVENT):
                if (self.__ui_event_is_valid(event)):
                    self.__handle_valid_ui_event(event)
                else:
                    self.__handle_invalid_ui_event(event)

            if (event == Event.WINDOW_CLOSED):
                self.__close_main_window()

    def update(self, milliseconds_of_audio_to_read: int, on_audio_read: Callable):
        if (self.is_state(State.PLAYING)):
            number_of_frames = self.milliseconds_to_number_of_frames(milliseconds_of_audio_to_read)

            self.__audio_chunk: bytes = self.__audio_player.read(number_of_frames)
            on_audio_read(self.__audio_chunk)

    def is_state(self, state: str) -> bool:
        if (state == State.PLAYING):
            return (isinstance(self.__audio_player, pyaudio.Stream) and self.__audio_player.is_active())

        elif (state == State.PAUSED):
            return (isinstance(self.__audio_player, pyaudio.Stream) and self.__audio_player.is_stopped())

        return False

    def milliseconds_to_number_of_frames(self, milliseconds: int) -> int:
        return int(self.__get_number_of_frames_per_millisecond() * milliseconds)

    def __get_number_of_frames_per_millisecond(self) -> int:
        number_of_milliseconds_per_second = 1000
        return self.__audio_player._rate / number_of_milliseconds_per_second

    def __set_default_input_device(self):
        def init_audio_player(*stream_args, **stream_kwargs):
            self.__close_audio_player()
            self.__audio_player = self._audio_player_maker.open(*stream_args, **stream_kwargs)

        default_input_device_info: dict = self._audio_player_maker.get_default_input_device_info()

        if (util.is_empty(default_input_device_info)):
            raise NoDefaultInputDeviceDetectedError("There is no default input device set on this machine.")

        init_audio_player(format=pyaudio.paInt16, channels=default_input_device_info["maxInputChannels"],
                          rate=int(default_input_device_info["defaultSampleRate"]), input=True)

        self.__audio_player.stop_stream()

    def __close_audio_player(self):
        if (self.__audio_player):
            self.__audio_player.close()
            self.__audio_player = None

    def __close_main_window(self):
        if (self.__main_window):
            self.__main_window.close()
            self.__main_window = None

    def __update_element(self, element: str, *update_args, **update_kwargs):
        self.__main_window[element].update(*update_args, **update_kwargs)

    def __create_gui_rows(self, *rows: Tuple[List[sg.Element]]) -> List[List[sg.Element]]:
        gui_rows: List[List[sg.Element]] = []
        util.foreach(rows, lambda row: gui_rows.append(row))
        return gui_rows

    def __get_element_value(self, element: str) -> Any:
        return self.__main_window[element].get()

    def __create_main_window(self) -> sg.Window:
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

        return self.__create_gui_rows([sg.Text(text="No audio currently playing.", key=Element.CURRENT_INPUT_SOURCE_MESSAGE, font=CURRENT_INPUT_SOURCE_FONT)],
                                      [sg.Button(button_text="Pause (||)", disabled=True, key=Element.PAUSE_AUDIO_BUTTON, font=BUTTON_FONT),
                                      sg.Button(button_text="Resume (>)", disabled=False, key=Element.RESUME_AUDIO_BUTTON, font=BUTTON_FONT)])

    def __get_rows_below_default_visualizer_and_led_selection(self) -> List[List[sg.Element]]:
        rows = []

        if (not _gui_rows_are_valid(rows)):
            raise TypeError("rows are not valid PySimpleGui rows")
        return rows

    def __handle_event_before_client_on_event(self, event: str) -> str:
        if (event == Event.OPEN_SETTINGS_MODAL):
            self.__setting_view.run_concurrent()
        return event

    def __ui_event_is_valid(self, event: str) -> bool:
        if (event == Event.PAUSE_AUDIO):
            return self.is_state(State.PLAYING)

        elif (event == Event.RESUME_AUDIO):
            return self.is_state(State.PAUSED)

        return event in (Event.WINDOW_CLOSED, Event.TIMEOUT_EVENT, Event.OPEN_SETTINGS_MODAL)

    def __handle_valid_ui_event(self, event: str):

        def set_audio_paused_state():
            self.__update_element(Element.SETTINGS_BUTTON, disabled=False)
            self.__update_element(Element.PAUSE_AUDIO_BUTTON, disabled=True)
            self.__update_element(Element.RESUME_AUDIO_BUTTON, disabled=False)

            self.__update_element(Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=False)
            self.__update_element(Element.SERIAL_LED_STRIP_CHECKBOX, disabled=False)
            self.__update_element(Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=False)

        def set_audio_playing_state():
            self.__update_element(Element.SETTINGS_BUTTON, disabled=True)
            self.__update_element(Element.PAUSE_AUDIO_BUTTON, disabled=False)
            self.__update_element(Element.RESUME_AUDIO_BUTTON, disabled=True)

            self.__update_element(Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=True)
            self.__update_element(Element.SERIAL_LED_STRIP_CHECKBOX, disabled=True)
            self.__update_element(Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=True)

        def get_group_index_to_led_range() -> List[Tuple[int, int]]:
            def shift_index_up_by_start_index(index: int) -> int:
                start_led = self.__setting_view.get_start_led_index()
                return index + start_led

            def get_number_of_leds() -> int:
                start_led = self.__setting_view.get_start_led_index()
                end_led = self.__setting_view.get_end_led_index()

                return end_led - start_led

            number_of_groups = self.__setting_view.get_number_of_groups()

            number_of_leds_per_group = max(1, get_number_of_leds() // number_of_groups)
            group_index_to_led_range = list()

            for group_index in range(number_of_groups):
                shifted_start_index = shift_index_up_by_start_index(group_index * number_of_leds_per_group)
                shifted_end_index = shifted_start_index + number_of_leds_per_group

                group_index_to_led_range.append((shifted_start_index, shifted_end_index))

            should_reverse_frequencies = self.__setting_view.should_reverse_indicies()

            if (should_reverse_frequencies):
                group_index_to_led_range.reverse()

            return group_index_to_led_range

        def get_led_strip():
            use_serial_led_strip = self.__get_element_value(Element.SERIAL_LED_STRIP_CHECKBOX)
            use_graphic_led_strip = self.__get_element_value(Element.GRAPHIC_LED_STRIP_CHECKBOX)

            start_led = self.__setting_view.get_start_led_index()
            end_led = self.__setting_view.get_end_led_index()

            led_range = (start_led, end_led)

            if (use_serial_led_strip):
                PORT = self.__setting_view.get_serial_port()
                BAUDRATE = self.__setting_view.get_serial_baudrate()
                PARITY = PARITY_NONE
                STOP_BITS = STOPBITS_ONE_POINT_FIVE
                BYTE_SIZE = EIGHTBITS
                READ_TIMEOUT = 1
                WRITE_TIMEOUT = 0

                serial = ProductionSerial(PORT, BAUDRATE, PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)
                brightness = self.__setting_view.get_brightness()

                serial_grouped_leds = SerialGroupedLeds(led_range, get_group_index_to_led_range(),
                                                        serial, brightness)

                return ProductionLedStrip(serial_grouped_leds)

            if (use_graphic_led_strip):
                WIDTH = 1350
                HEIGHT = 600

                gui = ProductionGui(WIDTH, HEIGHT)
                gui.update()

                graphic_grouped_leds = GraphicGroupedLeds(led_range,
                                                          get_group_index_to_led_range(),
                                                          gui)

                return ProductionLedStrip(graphic_grouped_leds)

        def init_spectrogram():
            self.__delete_spectrogram()

            visualizer_dropdown_value = self.__get_element_value(Element.SELECT_VISUALIZER_TYPE_DROPDOWN)

            if (visualizer_dropdown_value == VisualizerType.FREQUENCY):
                start_frequency = self.__setting_view.get_minimum_frequency()
                end_frequency = self.__setting_view.get_maximum_frequency()

                FREQUENCY_RANGE = (start_frequency, end_frequency)
                AMPLITUDE_TO_RGB = self.__setting_view.get_amplitude_to_rgb()
                self.__led_strip = get_led_strip()

                self.__spectrogram = Spectrogram(FREQUENCY_RANGE, AMPLITUDE_TO_RGB)

        def pause():
            if (self.__audio_player):
                self.__audio_player.stop_stream()

        def resume():
            if (self.__audio_player):
                self.__audio_player.start_stream()

        if (event == Event.PAUSE_AUDIO):
            pause()
            self.__delete_spectrogram()
            set_audio_paused_state()

        elif (event == Event.RESUME_AUDIO):
            input_source = self._audio_player_maker.get_default_input_device_info()["name"]
            current_input_source_message = f"Input Source : {input_source}"
            self.__update_element(Element.CURRENT_INPUT_SOURCE_MESSAGE, current_input_source_message)

            init_spectrogram()
            resume()
            set_audio_playing_state()

    def __handle_invalid_ui_event(self, event: str):
        if (event not in (Event.PAUSE_AUDIO, Event.RESUME_AUDIO)):
            error_message = f"Did not recognize the event {event}."

            LAYOUT = [[sg.Text(text=error_message)], [sg.Button(button_text="Ok")]]

            modal = sg.Window(title='Error', layout=LAYOUT, modal=True)

            while True:
                event = modal.read(timeout=0)[0]
                if (event == Event.WINDOW_CLOSED, Event.CONFIRMATION_MODAL_OK):
                    modal.close()
                    break

    def __delete_spectrogram(self):
        if (self.__spectrogram is not None):
            del self.__spectrogram
            self.__spectrogram = None
