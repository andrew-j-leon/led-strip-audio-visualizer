from typing import Any, Dict, List, Tuple

import gui.audio_visualizer.audio_model as audio_model
import gui.audio_visualizer.audio_view as audio_view
import gui.controller as controller
import numpy
from led_strip.graphic_led_strip import GraphicLedStrip
from led_strip.led_strip import GroupedLeds
from led_strip.serial_led_strip import SerialLedStrip
from libraries.gui import ProductionGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial
from visualizer.spectrogram import Spectrogram

_START_LED_INDEX = 0
_END_LED_INDEX = 1


class AudioController(controller.Controller):
    def __init__(self, audio_view: audio_view.AudioView, audio_player: audio_model.AudioModel):
        controller.Controller.__init__(self, audio_view)
        self._audio_player: audio_model.AudioModel = audio_player
        self.__visualizer: Visualizer = None

    def __get_grouped_led_strips(self):
        led_strips = []
        if (self._view.get_serial_led_strip_checkbox_value()):

            PORT = self._view.get_serial_port()
            BAUDRATE = self._view.get_serial_baudrate()
            PARITY = PARITY_NONE
            STOP_BITS = STOPBITS_ONE_POINT_FIVE
            BYTE_SIZE = EIGHTBITS
            READ_TIMEOUT = 1
            WRITE_TIMEOUT = 0

            grouped_leds = GroupedLeds(self._view.get_led_index_range(), self.__get_group_index_to_led_range())
            serial = ProductionSerial(PORT, BAUDRATE, PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)

            led_strips.append(SerialLedStrip(grouped_leds, serial,
                                             self._view.get_brightness()))

        if (self._view.get_graphic_led_strip_checkbox_value()):
            WIDTH = 1350
            HEIGHT = 600

            grouped_leds = GroupedLeds(self._view.get_led_index_range(), self.__get_group_index_to_led_range())

            gui = ProductionGui(WIDTH, HEIGHT)
            gui.update()

            led_strips.append(GraphicLedStrip(grouped_leds, gui))

        return led_strips

    def __get_group_index_to_led_range(self) -> List[Tuple[int, int]]:
        number_of_leds_per_group = max(1, self.__get_number_of_leds() // self._view.get_number_of_groups())
        group_index_to_led_range = list()

        for group_index in range(self._view.get_number_of_groups()):
            shifted_start_index = self.__shift_index_up_by_start_index(group_index * number_of_leds_per_group)
            shifted_end_index = shifted_start_index + number_of_leds_per_group

            group_index_to_led_range.append((shifted_start_index, shifted_end_index))

        if (self._view.should_reverse_indicies()):
            group_index_to_led_range.reverse()

        return group_index_to_led_range

    def __shift_index_up_by_start_index(self, index: int) -> int:
        return index + self.__get_start_led_index()

    def __get_number_of_leds(self) -> int:
        return self.__get_end_led_index() - self.__get_start_led_index()

    def __get_start_led_index(self) -> int:
        return self._view.get_led_index_range()[_START_LED_INDEX]

    def __get_end_led_index(self) -> int:
        return self._view.get_led_index_range()[_END_LED_INDEX]

    def __del__(self):
        self._delete_visualizer()
        del self._view
        del self._audio_player

    def _delete_visualizer(self):
        if (self.__visualizer):
            del self.__visualizer
            self.__visualizer = None

    def start(self):
        self._view.run_concurrent(self.__on_gui_event)

    def __on_gui_event(self, event: str):
        self._audio_player.update(self._view.get_milliseconds_per_audio_chunk(), self._on_audio_player_update)

        if (event != audio_view.Event.TIMEOUT_EVENT):
            if (self._ui_event_is_valid(event)):
                self._handle_valid_ui_event(event)
            else:
                self._handle_invalid_ui_event(event)

    def _on_audio_player_update(self, audio_chunk: bytes):
        self._update_visualizer(audio_chunk)

    def _update_visualizer(self, audio_chunk: bytes):
        if (self.__visualizer):
            if (isinstance(self.__visualizer, Spectrogram)):

                number_of_frames = self._audio_player.milliseconds_to_number_of_frames(self._view.get_milliseconds_per_audio_chunk())
                self.__visualizer.update_led_strips(audio_chunk, number_of_frames, self._audio_player.get_framerate(),
                                                    numpy.int16)  # TODO : This should equal the format in audio_in_model

    # Methods that the child class can/should override
    def _ui_event_is_valid(self, event: str) -> bool:
        pass

    def _handle_valid_ui_event(self, event: str):
        pass

    def _handle_invalid_ui_event(self, event: str):
        pass

    # Helper methods the child class can use

    def _pause_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_model.State.PLAYING)

    def _resume_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_model.State.PAUSED)

    def _initialize_visualizer(self):
        self._delete_visualizer()
        if (self._view.get_visualizer_type_dropdown_value() == audio_view.VisualizerType.FREQUENCY):
            FREQUENCY_RANGE = self._view.get_frequency_range()
            AMPLITUDE_TO_RGB = self._view.get_amplitude_to_rgb()
            GROUPED_LED_STRIPS = self.__get_grouped_led_strips()

            self.__visualizer = Spectrogram(FREQUENCY_RANGE, AMPLITUDE_TO_RGB, GROUPED_LED_STRIPS)
