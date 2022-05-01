import math
from statistics import mean
from typing import Dict, List, Tuple, Union

import numpy
from led_strip.led_strip import LedStrip
from util.rgb import RGB
from util.util import NonNegativeRange

# ================================================================== Some useful formulas ==================================================================
#
# The smaller (sampling_rate / number_of_frames) is, the more frequencies within the given frequency_range will be calculated.
# Conversely, the larger this ratio, the fewer frequencies will be calculated.
#       This means that more frequency precision can be attained with a smaller sampling_rate and/or a larger number_of_frames.
#
# To find how many frequencies within a given frequency_range=(minimum_frequency, maximum_frequency) will be calculated, use this formula:
#
#       (Equation 1): 1 + floor(maximum_frequency / (sampling_rate / number_of_frames)) - ceil(minimum_frequency / (sampling_rate / number_of_frames))
#
# To find the minimum frequency calculated, use this formula:
#       (Equation 2): ceil(minimum_frequency / (sampling_rate / number_of_frames)) * (sampling_rate / number_of_frames)
#
# To find the maximum frequency calculated, use this formula:
#       (Equation 3): floor(maximum_frequency / (sampling_rate / number_of_frames)) * (sampling_rate / number_of_frames)
#
# Let a_0 ("a subscript 0") = minimum_frequency_calculated. You can use this arithmetic sequence to find the i-th frequency calculated:
#       (Equation 4): a_i = a_0 + i*(sampling_rate / number_of_frames)
#
#       For example : If a_0 = 20 Hz, then a_1 (the smallest frequency calculated that is
#       larger than a_0) is:
#           a_1 = 20 + 1*(sampling_rate / number_of_frames)
#
# The possible frequencies that can be calculated is given by the following arithmetic sequence where freq_0 = 0 Hz & freq_i is the i-th frequency calculated:
#       freq_i = freq_0 + i*(sampling_rate/number_of_frames)
#
# ============================================================================================================================================================


def _get_fft_amplitude(fft_value: complex, number_of_fft_values: int) -> float:
    hypotenuse = math.sqrt(fft_value.real**2 + fft_value.imag**2).real

    try:
        return 20 * math.log10(hypotenuse / number_of_fft_values)

    except ValueError:
        return 0


def _get_fft_index(frequency: Union[int, float], sampling_rate: int, number_of_frames: int) -> int:
    return round(frequency / (sampling_rate / number_of_frames))


def _get_number_of_groups_to_led_strips(led_strips: List[LedStrip]) -> Dict[int, List[LedStrip]]:
    number_of_groups_to_led_strips = dict()
    for led_strip in led_strips:
        try:
            number_of_groups_to_led_strips[led_strip.number_of_groups].append(led_strip)

        except KeyError:
            number_of_groups_to_led_strips[led_strip.number_of_groups] = [led_strip]

    return number_of_groups_to_led_strips


class Spectrogram:
    def __init__(self, frequency_range: Tuple[Union[int, float], Union[int, float]],
                 amplitude_rgbs: List[Tuple[int, int, int]], led_strips: List[LedStrip]):
        '''
            Args:
                `frequency_range (Tuple[Union[int, float], Union[int, float]])`: Range of frequencies to represent. The start frequency
                is index 0 (inclusive) and end frequency is index 1 (exclusive).
                `amplitude_rgbs (List[Tuple[int, int, int]])`: The index is the amplitude (in decibels) and the value at said index is
                the rgb color.
                `led_strips (List[LedStrip])`: The strips to display the spectrogram on.
        '''
        self.__number_of_groups_to_led_strips = _get_number_of_groups_to_led_strips(led_strips)

        self.__amplitude_rgbs = [RGB(red, green, blue) for red, green, blue in amplitude_rgbs]
        '''
            Indices represent amplitudes (in decibels). The value at an index is the RGB color for that amplitude.
                Example : If __amplitude_rgbs[10] == (200, 0, 0), then an amplitude of 10dB will be represented by the RGB color (200, 0, 0).
        '''

        start_frequency, end_frequency = frequency_range
        self.__frequency_range = NonNegativeRange(start_frequency, end_frequency)

    def update_led_strips(self, audio_data: bytes, number_of_frames: int, sampling_rate: int, format: numpy.signedinteger):
        '''
            Args:
                `audio_data (bytes)`: WAV audio data.
                `number_of_frames (int)`: The number of frames `audio_data` represents.
                `sampling_rate (int)`: The number of samples per second.
                `format (numpy.signedinteger)`: The format of the audio (i.e. 16 bit, 32 bit, etc.).
        '''
        for number_of_groups in self.__number_of_groups_to_led_strips:
            self.__set_led_strip_color(number_of_groups, audio_data, sampling_rate, number_of_frames, format)
            self.__show_led_strips(number_of_groups)

    def __set_led_strip_color(self, number_of_groups: int, audio_data: bytes, sampling_rate: int, number_of_frames: int, format: numpy.signedinteger):
        audio_data_decimal: bytes = numpy.frombuffer(audio_data, dtype=format)
        fft: numpy.ndarray = numpy.fft.fft(audio_data_decimal)

        fft_length = math.ceil(len(fft) / 2)  # the first half of the fft is a mirror copy of the 2nd half; we can ignore the 2nd half

        fft_start_at_min_freq: int = min(fft_length - 1,
                                         _get_fft_index(self.__frequency_range.start, sampling_rate, number_of_frames))

        fft_end_at_max_freq: int = min(fft_length - 1,
                                       _get_fft_index(self.__frequency_range.end, sampling_rate, number_of_frames)) + 1

        fft_sublist_length: int = max(1, (fft_end_at_max_freq - fft_start_at_min_freq) // number_of_groups)

        led_strip: LedStrip = self.__number_of_groups_to_led_strips[number_of_groups][0]

        for fft_sublist_start, led_strip_group in zip(range(fft_start_at_min_freq, fft_end_at_max_freq, fft_sublist_length),
                                                      range(number_of_groups)):

            fft_sublist_end: int = min(fft_sublist_start + fft_sublist_length, fft_end_at_max_freq)

            fft_sublist_average_amplitude = mean(_get_fft_amplitude(fft[i], fft_length)
                                                 for i in range(fft_sublist_start, fft_sublist_end))

            rgb = self.__get_rgb(fft_sublist_average_amplitude)

            if (not led_strip.group_is_rgb(led_strip_group, rgb)):
                for led_strip in self.__number_of_groups_to_led_strips[number_of_groups]:
                    led_strip.enqueue_rgb(led_strip_group, rgb)

    def __show_led_strips(self, number_of_groups: int):
        for led_strip in self.__number_of_groups_to_led_strips[number_of_groups]:
            led_strip.show_queued_colors()
            led_strip.clear_queued_colors()

    def __get_rgb(self, amplitude: Union[int, float]) -> RGB:
        amplitude = max(0, amplitude)
        amplitude = min(amplitude, len(self.__amplitude_rgbs) - 1)
        return self.__amplitude_rgbs[round(amplitude)]

    def __del__(self):
        self.__turn_off_leds()

        for led_strips in self.__number_of_groups_to_led_strips.values():
            for led_strip in led_strips:
                del led_strip

    def __turn_off_leds(self):
        BLACK_RGB = (0, 0, 0)
        for number_of_groups in self.__number_of_groups_to_led_strips:
            self.__set_group_range_color(number_of_groups, 0, number_of_groups, BLACK_RGB)
            self.__show_led_strips(number_of_groups)

    def __set_group_range_color(self, number_of_groups: int, start_group_index: int, end_group_index: int, rgb: Tuple[int, int, int]):
        for led_strip in self.__number_of_groups_to_led_strips[number_of_groups]:
            for group_index in range(start_group_index, end_group_index):
                led_strip.enqueue_rgb(group_index, rgb)
