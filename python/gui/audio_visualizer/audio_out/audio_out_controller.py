import os

import gui.audio_visualizer.audio_out.audio_out_model as audio_out_model
import gui.audio_visualizer.audio_out.audio_out_view as audio_out_view
import gui.audio_visualizer.audio_view as audio_view
import util.util as util
from visualizer.spectrogram import Spectrogram
from typing import List, Tuple

import gui.audio_visualizer.audio_model as audio_model
import gui.audio_visualizer.audio_view as audio_view
import numpy
from led_strip.grouped_leds import GraphicGroupedLeds, SerialGroupedLeds
from led_strip.led_strip import ProductionLedStrip
from libraries.gui import ProductionGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial
from visualizer.spectrogram import Spectrogram

_START_LED_INDEX = 0
_END_LED_INDEX = 1


class AudioOutController:
    def __init__(self):
        self.view = audio_out_view.AudioOutView()
        self._audio_player = audio_out_model.AudioOutModel()
        self.__visualizer: Spectrogram = None

    def __get_led_strip(self):
        if (self.view.get_serial_led_strip_checkbox_value()):

            PORT = self.view.get_serial_port()
            BAUDRATE = self.view.get_serial_baudrate()
            PARITY = PARITY_NONE
            STOP_BITS = STOPBITS_ONE_POINT_FIVE
            BYTE_SIZE = EIGHTBITS
            READ_TIMEOUT = 1
            WRITE_TIMEOUT = 0

            serial = ProductionSerial(PORT, BAUDRATE, PARITY, STOP_BITS, BYTE_SIZE, READ_TIMEOUT, WRITE_TIMEOUT)

            serial_grouped_leds = SerialGroupedLeds(self.view.get_led_index_range(), self.__get_group_index_to_led_range(),
                                                    serial, self.view.get_brightness())

            return ProductionLedStrip(serial_grouped_leds)

        if (self.view.get_graphic_led_strip_checkbox_value()):
            WIDTH = 1350
            HEIGHT = 600

            gui = ProductionGui(WIDTH, HEIGHT)
            gui.update()

            graphic_grouped_leds = GraphicGroupedLeds(self.view.get_led_index_range(),
                                                      self.__get_group_index_to_led_range(),
                                                      gui)

            return ProductionLedStrip(graphic_grouped_leds)

    def __get_group_index_to_led_range(self) -> List[Tuple[int, int]]:
        number_of_leds_per_group = max(1, self.__get_number_of_leds() // self.view.get_number_of_groups())
        group_index_to_led_range = list()

        for group_index in range(self.view.get_number_of_groups()):
            shifted_start_index = self.__shift_index_up_by_start_index(group_index * number_of_leds_per_group)
            shifted_end_index = shifted_start_index + number_of_leds_per_group

            group_index_to_led_range.append((shifted_start_index, shifted_end_index))

        if (self.view.should_reverse_indicies()):
            group_index_to_led_range.reverse()

        return group_index_to_led_range

    def __shift_index_up_by_start_index(self, index: int) -> int:
        return index + self.__get_start_led_index()

    def __get_number_of_leds(self) -> int:
        return self.__get_end_led_index() - self.__get_start_led_index()

    def __get_start_led_index(self) -> int:
        return self.view.get_led_index_range()[_START_LED_INDEX]

    def __get_end_led_index(self) -> int:
        return self.view.get_led_index_range()[_END_LED_INDEX]

    def _delete_visualizer(self):
        if (self.__visualizer):
            del self.__visualizer
            self.__visualizer = None

    def _delete_led_strip(self):
        if (self.led_strip):
            BLACK_RGB = (0, 0, 0)

            self.led_strip.clear_queued_colors()

            for group in range(self.led_strip.number_of_groups):
                self.led_strip.enqueue_rgb(group, BLACK_RGB)

            self.led_strip.show_queued_colors()

            del self.led_strip
            self.led_strip = None

    def _on_audio_player_update(self, audio_chunk: bytes):
        self._update_visualizer(audio_chunk)

    def _update_visualizer(self, audio_chunk: bytes):
        if (self.__visualizer):
            if (isinstance(self.__visualizer, Spectrogram)):

                number_of_frames = self._audio_player.milliseconds_to_number_of_frames(self.view.get_milliseconds_per_audio_chunk())
                self.__visualizer.update_led_strips(self.led_strip, audio_chunk, number_of_frames, self._audio_player.get_framerate(),
                                                    numpy.int16)

    # Helper methods the child class can use

    def _pause_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_model.State.PLAYING)

    def _resume_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_model.State.PAUSED)

    def _initialize_visualizer(self):
        self._delete_visualizer()
        if (self.view.get_visualizer_type_dropdown_value() == audio_view.VisualizerType.FREQUENCY):
            FREQUENCY_RANGE = self.view.get_frequency_range()
            AMPLITUDE_TO_RGB = self.view.get_amplitude_to_rgb()
            self.led_strip = self.__get_led_strip()

            self.__visualizer = Spectrogram(FREQUENCY_RANGE, AMPLITUDE_TO_RGB)

    def __del__(self):
        self._delete_visualizer()
        self._delete_led_strip()
        del self.view
        del self._audio_player

    def start(self):
        self.view.run_concurrent(self.__on_gui_event)

    def __on_gui_event(self, event: str):
        self._audio_player.update(self.view.get_milliseconds_per_audio_chunk(), self._on_audio_player_update)

        if (event != audio_view.Event.TIMEOUT_EVENT):
            if (self._ui_event_is_valid(event)):
                self._handle_valid_ui_event(event)
            else:
                self._handle_invalid_ui_event(event)

    def _on_audio_player_update(self, audio_chunk: bytes):
        self._update_visualizer(audio_chunk)
        self.view.set_runtime_message(self.__get_runtime_message())

        if (util.is_empty(audio_chunk)):
            self.view.set_audio_playing_state()
            self.view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

    def _ui_event_is_valid(self, event: str) -> bool:
        if (event == audio_out_view.Event.SHUFFLE_PLAY):
            return self.__shuffle_play_event_is_valid(self.view.get_audio_directory())

        elif (event == audio_out_view.Event.PREVIOUS_AUDIO):
            return self.__previous_audio_event_is_valid()

        elif (event == audio_out_view.Event.PAUSE_AUDIO):
            return self.__pause_audio_event_is_valid()

        elif (event == audio_out_view.Event.RESUME_AUDIO):
            return self.__resume_audio_event_is_valid()

        elif (event == audio_out_view.Event.STOP_AUDIO):
            return self.__stop_audio_event_is_valid()

        elif (event == audio_out_view.Event.NEXT_AUDIO):
            return self.__next_audio_event_is_valid()

        return event in (audio_out_view.Event.WINDOW_CLOSED, audio_out_view.Event.TIMEOUT_EVENT, audio_out_view.Event.OPEN_SETTINGS_MODAL)

    def _handle_valid_ui_event(self, event: str):
        try:
            if (event == audio_out_view.Event.SHUFFLE_PLAY):
                self._audio_player.insert_playlist(self.view.get_audio_directory())
                self._audio_player.shuffle_play()
                self._initialize_visualizer()
                self.view.set_audio_playing_state()
                self.view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

            elif (event == audio_out_view.Event.PREVIOUS_AUDIO):
                self._audio_player.previous()
                self.view.set_audio_playing_state()
                self.view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

            elif (event == audio_out_view.Event.PAUSE_AUDIO):
                self._audio_player.pause()
                self.view.set_audio_paused_state()

            elif (event == audio_out_view.Event.RESUME_AUDIO):
                self._audio_player.resume()
                self.view.set_audio_playing_state()

            elif (event == audio_out_view.Event.STOP_AUDIO):
                self._audio_player.stop()
                self._delete_visualizer()
                self.view.set_audio_stopped_state()
                self.view.set_runtime_message("")
                self.view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

            elif (event == audio_out_view.Event.NEXT_AUDIO):
                self._audio_player.next()
                self.view.set_audio_playing_state()
                self.view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

        except audio_out_model.NoValidAudioFilesFoundException:
            self.view.display_confirmation_modal("Error", "No valid audio files were found in the directory.")

    def _handle_invalid_ui_event(self, event: str):
        if (event == audio_out_view.Event.SHUFFLE_PLAY):
            self.__handle_invalid_shuffle_event(self.view.get_audio_directory())

        elif (event not in (audio_out_view.Event.STOP_AUDIO, audio_out_view.Event.NEXT_AUDIO, audio_out_view.Event.PAUSE_AUDIO, audio_out_view.Event.RESUME_AUDIO)):
            self.view.display_confirmation_modal("Error", "Did not recognize the event : {}.".format(event))

    def __get_runtime_message(self):
        return (util.convert_milliseconds_to_hours_minutes_and_seconds(self._audio_player.get_milliseconds_since_start())
                + " / " + util.convert_milliseconds_to_hours_minutes_and_seconds(self._audio_player.get_total_audio_length()))

    def __get_current_audio_playing_message(self) -> str:
        current_audio_filename = self._audio_player.get_current_audio_name()
        if (current_audio_filename == None):
            return "No audio playing."
        return ("Playing : {}").format(os.path.basename(current_audio_filename))

    def __shuffle_play_event_is_valid(self, audio_directory: str):
        return audio_out_model.is_valid_audio_directory(audio_directory)

    def __previous_audio_event_is_valid(self):
        return (self._audio_player.is_state(audio_out_model.State.PLAYING) or self._audio_player.is_state(audio_out_model.State.PAUSED))

    def __pause_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_out_model.State.PLAYING)

    def __resume_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_out_model.State.PAUSED)

    def __stop_audio_event_is_valid(self):
        return (self._audio_player.is_state(audio_out_model.State.PLAYING) or self._audio_player.is_state(audio_out_model.State.PAUSED))

    def __next_audio_event_is_valid(self):
        return (self._audio_player.is_state(audio_out_model.State.PLAYING) or self._audio_player.is_state(audio_out_model.State.PAUSED))

    def __handle_invalid_shuffle_event(self, audio_directory: str):
        if (not os.path.isdir(audio_directory)):
            self.view.display_confirmation_modal("Error", "The directory \"{}\" either does not exist or is not a directory.".format(audio_directory))

        elif (not util.have_read_permission(audio_directory)):
            self.view.display_confirmation_modal("Error", "You do not have read permission for the directory \"{}\".".format(audio_directory))

        elif (not audio_out_model.is_valid_audio_directory(audio_directory)):
            self.view.display_confirmation_modal("Error", "The directory \"{}\" has no files with supported audio files.".format(audio_directory))

        else:
            self.view.display_confirmation_modal("Error", "An unknown error occurred when processing the {} event.".format(audio_out_view.Event.SHUFFLE_PLAY))
