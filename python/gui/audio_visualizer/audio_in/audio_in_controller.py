from typing import List, Tuple

import gui.audio_visualizer.audio_in.audio_in_model as audio_in_model
import gui.audio_visualizer.audio_in.audio_in_view as audio_in_view
import numpy
from led_strip.grouped_leds import GraphicGroupedLeds, SerialGroupedLeds
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.gui import ProductionGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial
from visualizer.spectrogram import Spectrogram

_START_LED_INDEX = 0
_END_LED_INDEX = 1


class AudioInController:
    def __init__(self):
        self.view = audio_in_view.AudioInView()
        self.audio_player = audio_in_model.AudioInModel()
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

            if (event != audio_in_view.Event.TIMEOUT_EVENT):
                if (self.__ui_event_is_valid(event)):
                    self.__handle_valid_ui_event(event)
                else:
                    self.__handle_invalid_ui_event(event)

        self.view.run_concurrent(on_gui_event)

    def __ui_event_is_valid(self, event: str) -> bool:
        if (event == audio_in_view.Event.PAUSE_AUDIO):
            return self.audio_player.is_state(audio_in_model.State.PLAYING)

        elif (event == audio_in_view.Event.RESUME_AUDIO):
            return self.audio_player.is_state(audio_in_model.State.PAUSED)

        return event in (audio_in_view.Event.WINDOW_CLOSED, audio_in_view.Event.TIMEOUT_EVENT, audio_in_view.Event.OPEN_SETTINGS_MODAL)

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
            if (self.view.get_visualizer_type_dropdown_value() == audio_in_view.VisualizerType.FREQUENCY):
                FREQUENCY_RANGE = self.view.get_frequency_range()
                AMPLITUDE_TO_RGB = self.view.get_amplitude_to_rgb()
                self.led_strip = get_led_strip()

                self.spectrogram = Spectrogram(FREQUENCY_RANGE, AMPLITUDE_TO_RGB)

        if (event == audio_in_view.Event.PAUSE_AUDIO):
            self.audio_player.pause()
            self.__delete_spectrogram()
            self.view.set_audio_paused_state()

        elif (event == audio_in_view.Event.RESUME_AUDIO):
            current_input_source_message = f"Input Source : {self.audio_player.get_current_input_device_name()}"
            self.view.set_current_input_source_message(current_input_source_message)

            init_spectrogram()
            self.audio_player.resume()
            self.view.set_audio_playing_state()

    def __handle_invalid_ui_event(self, event: str):
        if (event not in (audio_in_view.Event.PAUSE_AUDIO, audio_in_view.Event.RESUME_AUDIO)):
            self.view.display_confirmation_modal("Error", "Did not recognize the event {}.".format(event))

    def __delete_spectrogram(self):
        if (self.spectrogram is not None):
            del self.spectrogram
            self.spectrogram = None
