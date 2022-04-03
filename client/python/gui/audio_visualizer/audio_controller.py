from typing import Any, Dict, List, Tuple
from python.led_strip.grouped.grouped_led_strip import GroupedLedStrip
from python.led_strip.array.array_led_strip import ArrayLedStrip


import python.gui.controller as controller
import python.gui.audio_visualizer.audio_view as audio_view
import python.gui.audio_visualizer.audio_model as audio_model
from python.led_strip.graphic.array.graphic_array_led_strip import GraphicArrayLedStrip
from python.led_strip.graphic.grouped.graphic_grouped_led_strip import GraphicGroupedLedStrip
from python.led_strip.serial.array.serial_array_led_strip import SerialArrayLedStrip
from python.led_strip.serial.grouped.serial_grouped_led_strip import SerialGroupedLedStrip
from python.visualizer.visualizer import Visualizer
from python.visualizer.frequency.frequency_visualizer import FrequencyVisualizer

from serial import Serial
import serial.serialutil as serialutil



_START_LED_INDEX = 0
_END_LED_INDEX = 1


class AudioController(controller.Controller):
    def __init__(self, audio_view:audio_view.AudioView, audio_player:audio_model.AudioModel):
        controller.Controller.__init__(self, audio_view)
        self._audio_player:audio_model.AudioModel = audio_player
        self.__visualizer:Visualizer = None

    def __get_serial_parameters(self)->Dict[str,Any]:
        return dict(port=self._view.get_serial_port(), baudrate=self._view.get_serial_baudrate(), timeout=1, write_timeout=None,
                    parity=serialutil.PARITY_NONE, stopbits=serialutil.STOPBITS_ONE_POINT_FIVE, bytesize=serialutil.EIGHTBITS)

    def __get_frequency_visualizer_parameters(self):
        return dict(frequency_range=self._view.get_frequency_range(), amplitude_to_rgb=self._view.get_amplitude_to_rgb(),
                    grouped_led_strips=self.__get_grouped_led_strips())

    def __get_grouped_led_strips(self)->List[GroupedLedStrip]:
        led_strips = []
        if (self._view.get_serial_led_strip_checkbox_value()):
            led_strips.append(SerialGroupedLedStrip(led_index_range=self._view.get_led_index_range(),
                                                    serial_connection=Serial(**self.__get_serial_parameters()),
                                                    brightness=self._view.get_brightness(),
                                                    group_index_to_led_range=self.__get_group_index_to_led_range()))

        if (self._view.get_graphic_led_strip_checkbox_value()):
            led_strips.append(GraphicGroupedLedStrip(led_index_range=self._view.get_led_index_range(),
                                                     group_index_to_led_range=self.__get_group_index_to_led_range()))

        return led_strips

    def __get_group_index_to_led_range(self)->List[Tuple[int,int]]:
        number_of_leds_per_group = max(1, self.__get_number_of_leds()//self._view.get_number_of_groups())
        group_index_to_led_range = list()

        for group_index in range(self._view.get_number_of_groups()):
            shifted_start_index = self.__shift_index_up_by_start_index(group_index*number_of_leds_per_group)
            shifted_end_index = shifted_start_index + number_of_leds_per_group

            group_index_to_led_range.append((shifted_start_index, shifted_end_index))

        if (self._view.should_reverse_indicies()):
            group_index_to_led_range.reverse()

        return group_index_to_led_range

    def __shift_index_up_by_start_index(self, index:int)->int:
        return index + self.__get_start_led_index()

    def __get_number_of_leds(self)->int:
        return self.__get_end_led_index() - self.__get_start_led_index()

    def __get_start_led_index(self)->int:
        return self._view.get_led_index_range()[_START_LED_INDEX]

    def __get_end_led_index(self)->int:
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

    def __on_gui_event(self, event:str):
        self._audio_player.update(self._view.get_milliseconds_per_audio_chunk(), self._on_audio_player_update)

        if (event != audio_view.Event.TIMEOUT_EVENT):
            if (self._ui_event_is_valid(event)):
                self._handle_valid_ui_event(event)
            else:
                self._handle_invalid_ui_event(event)

    def _on_audio_player_update(self, audio_chunk:bytes):
        self._update_visualizer(audio_chunk)

    def _update_visualizer(self, audio_chunk:bytes):
        if (self.__visualizer):
            if (isinstance(self.__visualizer, FrequencyVisualizer)):
                self.__visualizer.update_led_strips(audio_chunk, self._audio_player.get_framerate(),
                                                    self._audio_player.milliseconds_to_number_of_frames(self._view.get_milliseconds_per_audio_chunk()))


    # Methods that the child class can/should override
    def _ui_event_is_valid(self, event:str)->bool:
        pass

    def _handle_valid_ui_event(self, event:str):
        pass

    def _handle_invalid_ui_event(self, event:str):
        pass


    # Helper methods the child class can use
    def _pause_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_model.State.PLAYING)

    def _resume_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_model.State.PAUSED)

    def _initialize_visualizer(self):
        self._delete_visualizer()
        if (self._view.get_visualizer_type_dropdown_value() == audio_view.VisualizerType.FREQUENCY):
            self.__visualizer = FrequencyVisualizer(**self.__get_frequency_visualizer_parameters())