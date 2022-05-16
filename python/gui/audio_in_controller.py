from typing import List, Tuple

import pyaudio
import PySimpleGUI as sg
import util.util as util
from gui.setting.setting_controller import SettingController
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
    OPEN_SETTINGS_MODAL = Element.SETTINGS_BUTTON
    PAUSE_AUDIO = Element.PAUSE_AUDIO_BUTTON
    RESUME_AUDIO = Element.RESUME_AUDIO_BUTTON


class VisualizerType:
    NONE = "None"
    FREQUENCY = "Frequency"


class State:
    PLAYING = "playing"
    PAUSED = "paused"


class AudioInController:
    def __init__(self):
        self.__setting_controller = SettingController()
        self.__main_window: sg.Window = None

        self._audio_player_maker = pyaudio.PyAudio()
        self.__audio_player: pyaudio.Stream = None
        self.__audio_chunk: bytes = b''
        self.__init_audio_player()

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
        self.__main_window = self.__create_main_window()
        self.__main_window.read(timeout=0)

        while (self.__main_window is not None):
            event: str = self.__main_window.read(timeout=0)[0]

            if (event == Event.OPEN_SETTINGS_MODAL):
                self.__setting_controller.run_concurrent()

            if (self.__is_state(State.PLAYING)):
                MILLISECONDS_PER_SECOND = 1000
                frames_per_millisecond = self.__audio_player._rate / MILLISECONDS_PER_SECOND  # sample rate (frames / second) / 1000 ms/second = frames / millisecond

                milleseconds_per_audio_chunk = self.__setting_controller.get_milliseconds_per_audio_chunk()  # ms
                number_of_frames = int(frames_per_millisecond * milleseconds_per_audio_chunk)  # frames / ms * ms = frames

                self.__audio_chunk = self.__audio_player.read(number_of_frames)

                self.__spectrogram.update_led_strips(self.__led_strip, self.__audio_chunk, number_of_frames,
                                                     self.__audio_player._rate)

            if (event != Event.TIMEOUT_EVENT):
                self.__handle_ui_event(event)

            if (event == Event.WINDOW_CLOSED):
                self.__close_main_window()

    def __is_state(self, state: str) -> bool:
        if (state == State.PLAYING):
            return (isinstance(self.__audio_player, pyaudio.Stream) and self.__audio_player.is_active())

        elif (state == State.PAUSED):
            return (isinstance(self.__audio_player, pyaudio.Stream) and self.__audio_player.is_stopped())

        return False

    def __init_audio_player(self):
        default_input_device_info: dict = self._audio_player_maker.get_default_input_device_info()

        if (util.is_empty(default_input_device_info)):
            raise ValueError("There is no default input device set on this machine.")

        self.__close_audio_player()

        # format (aka audio bit depth) = bits per sample (more bits = more discreet values for loudness levels
        # [according to this website https://www.provideocoalition.com/understanding-24-bit-vs-16-bit-audio-production-distribution/
        #  16 bits gets you 65,536 values for a dynamic range of 96 dB whereas 24 bit gets you 16,777,216 for a dynamic range of
        # 144 dB])
        self.__audio_player = self._audio_player_maker.open(format=pyaudio.paInt16, channels=default_input_device_info["maxInputChannels"],
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

    def __create_main_window(self) -> sg.Window:
        VISUALIZER_DROPDOWN_VALUES: List[str] = [VisualizerType.NONE, VisualizerType.FREQUENCY]

        CURRENT_INPUT_SOURCE_FONT = ("Courier New", 20)

        layout = [[sg.Button(button_text="Settings", key=Element.SETTINGS_BUTTON)],

                  [sg.Text(text="No audio currently playing.", key=Element.CURRENT_INPUT_SOURCE_MESSAGE, font=CURRENT_INPUT_SOURCE_FONT)],

                  [sg.Button(button_text="Pause (||)", disabled=True, key=Element.PAUSE_AUDIO_BUTTON, font=BUTTON_FONT),
                   sg.Button(button_text="Resume (>)", disabled=False, key=Element.RESUME_AUDIO_BUTTON, font=BUTTON_FONT)],

                  [sg.Text(text="Visualizer : ", key=Element.SELECT_VISUALIZER_TYPE_LABEL, font=INPUT_LABEL_FONT),
                   sg.Combo(values=VISUALIZER_DROPDOWN_VALUES,
                            default_value=VisualizerType.FREQUENCY, key=Element.SELECT_VISUALIZER_TYPE_DROPDOWN, font=DROPDOWN_INPUT_FONT),
                   sg.Checkbox(text="Serial Led Strip", key=Element.SERIAL_LED_STRIP_CHECKBOX, font=CHECKBOX_INPUT_FONT),
                   sg.Checkbox(text="Graphic Led Strip", key=Element.GRAPHIC_LED_STRIP_CHECKBOX, font=CHECKBOX_INPUT_FONT)]]

        return sg.Window('Led Strip Music Visualizer', layout=layout, resizable=True, element_padding=(0, 0),
                         margins=(0, 0), titlebar_background_color="#000917", titlebar_text_color="#8a8a8a")

    def __handle_ui_event(self, event: str):
        def update_element(element: str, **update_kwargs):
            self.__main_window[element].update(**update_kwargs)

        def set_audio_paused_state():
            update_element(Element.SETTINGS_BUTTON, disabled=False)
            update_element(Element.PAUSE_AUDIO_BUTTON, disabled=True)
            update_element(Element.RESUME_AUDIO_BUTTON, disabled=False)

            update_element(Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=False)
            update_element(Element.SERIAL_LED_STRIP_CHECKBOX, disabled=False)
            update_element(Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=False)

        def set_audio_playing_state():
            update_element(Element.SETTINGS_BUTTON, disabled=True)
            update_element(Element.PAUSE_AUDIO_BUTTON, disabled=False)
            update_element(Element.RESUME_AUDIO_BUTTON, disabled=True)

            update_element(Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=True)
            update_element(Element.SERIAL_LED_STRIP_CHECKBOX, disabled=True)
            update_element(Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=True)

        def get_group_index_to_led_range() -> List[Tuple[int, int]]:
            def get_number_of_leds() -> int:
                start_led = self.__setting_controller.get_start_led_index()
                end_led = self.__setting_controller.get_end_led_index()

                return end_led - start_led

            number_of_groups = self.__setting_controller.get_number_of_groups()

            number_of_leds_per_group = max(1, get_number_of_leds() // number_of_groups)
            group_index_to_led_range = list()

            for group_index in range(number_of_groups):
                start_led = self.__setting_controller.get_start_led_index()
                shifted_start_index = group_index * number_of_leds_per_group + start_led

                shifted_end_index = shifted_start_index + number_of_leds_per_group

                group_index_to_led_range.append((shifted_start_index, shifted_end_index))

            if (self.__setting_controller.should_reverse_indicies()):
                group_index_to_led_range.reverse()

            return group_index_to_led_range

        def get_led_strip():
            use_serial_led_strip = self.__main_window[Element.SERIAL_LED_STRIP_CHECKBOX].get()
            use_graphic_led_strip = self.__main_window[Element.GRAPHIC_LED_STRIP_CHECKBOX].get()

            start_led = self.__setting_controller.get_start_led_index()
            end_led = self.__setting_controller.get_end_led_index()

            led_range = (start_led, end_led)

            if (use_serial_led_strip):
                PORT = self.__setting_controller.get_serial_port()
                BAUDRATE = self.__setting_controller.get_serial_baudrate()
                PARITY = PARITY_NONE
                STOP_BITS = STOPBITS_ONE_POINT_FIVE
                BYTE_SIZE = EIGHTBITS
                READ_TIMEOUT = 1
                WRITE_TIMEOUT = 0

                serial = ProductionSerial(PORT, BAUDRATE, PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)
                brightness = self.__setting_controller.get_brightness()

                serial_grouped_leds = SerialGroupedLeds(led_range, get_group_index_to_led_range(),
                                                        serial, brightness)

                return ProductionLedStrip(serial_grouped_leds)

            if (use_graphic_led_strip):
                WIDTH = 1350
                HEIGHT = 600

                gui = ProductionGui(WIDTH, HEIGHT)
                gui.update()

                graphic_grouped_leds = GraphicGroupedLeds(led_range, get_group_index_to_led_range(), gui)

                return ProductionLedStrip(graphic_grouped_leds)

        def init_spectrogram():
            self.__delete_spectrogram()
            visualizer_dropdown_value = self.__main_window[Element.SELECT_VISUALIZER_TYPE_DROPDOWN].get()

            if (visualizer_dropdown_value == VisualizerType.FREQUENCY):
                start_frequency = self.__setting_controller.get_minimum_frequency()
                end_frequency = self.__setting_controller.get_maximum_frequency()

                FREQUENCY_RANGE = (start_frequency, end_frequency)
                AMPLITUDE_TO_RGB = self.__setting_controller.get_amplitude_to_rgb()
                self.__led_strip = get_led_strip()

                self.__spectrogram = Spectrogram(FREQUENCY_RANGE, AMPLITUDE_TO_RGB)

        if (event == Event.PAUSE_AUDIO):
            self.__audio_player.stop_stream()
            self.__delete_spectrogram()
            set_audio_paused_state()

        elif (event == Event.RESUME_AUDIO):
            input_source = self._audio_player_maker.get_default_input_device_info()["name"]
            current_input_source_message = f"Input Source : {input_source}"
            update_element(Element.CURRENT_INPUT_SOURCE_MESSAGE, value=current_input_source_message)

            init_spectrogram()
            self.__audio_player.start_stream()
            set_audio_playing_state()

    def __delete_spectrogram(self):
        if (self.__spectrogram is not None):
            del self.__spectrogram
            self.__spectrogram = None
