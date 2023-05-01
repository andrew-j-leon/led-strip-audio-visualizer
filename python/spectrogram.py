import math
from abc import ABC, abstractmethod
from statistics import mean
from typing import Iterable, List, Union

import numpy
from leds.led_strip import LedStrip
from non_negative_int_range import NonNegativeIntRange
from util import RGB

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


class Spectrogram(ABC):
    @abstractmethod
    def set_amplitude_rgbs(self, amplitude_rgbs: List[Iterable[int]]):
        pass

    @abstractmethod
    def set_frequency_range(self, start_frequency: int, end_frequency: int):
        pass

    @abstractmethod
    def update_led_strip(self, led_strip: LedStrip, audio_data: bytes, number_of_frames: int, sampling_rate: int):
        '''
            Args:
                `audio_data (bytes)`: WAV audio data.
                `number_of_frames (int)`: The number of frames `audio_data` represents.
                `sampling_rate (int)`: The number of samples per second.
                `format (numpy.signedinteger)`: The format of the audio (i.e. 16 bit, 32 bit, etc.).
        '''


class ProductionSpectrogram(Spectrogram):
    def __init__(self, amplitude_rgbs: List[Iterable[int]] = [],
                 start_frequency: int = 0, end_frequency: int = 0):
        self.__amplitude_rgbs: List[RGB] = []
        self.__frequency_range: NonNegativeIntRange = NonNegativeIntRange()

        self.set_amplitude_rgbs(amplitude_rgbs)
        self.set_frequency_range(start_frequency, end_frequency)

    def set_amplitude_rgbs(self, amplitude_rgbs):
        self.__amplitude_rgbs = [RGB(red, green, blue) for red, green, blue in amplitude_rgbs]

    def set_frequency_range(self, start_frequency, end_frequency):
        self.__frequency_range = NonNegativeIntRange(start_frequency, end_frequency)

    def update_led_strip(self, led_strip, audio_data, number_of_frames, sampling_rate):
        '''
            Args:
                `audio_data (bytes)`: WAV audio data.
                `number_of_frames (int)`: The number of frames `audio_data` represents.
                `sampling_rate (int)`: The number of samples per second.
                `format (numpy.signedinteger)`: The format of the audio (i.e. 16 bit, 32 bit, etc.).
        '''
        audio_data_decimal: bytes = numpy.frombuffer(audio_data, dtype=numpy.int16)
        fft: numpy.ndarray = numpy.fft.fft(audio_data_decimal)

        fft_length = math.ceil(len(fft) / 2)  # the first half of the fft is a mirror copy of the 2nd half; we can ignore the 2nd half

        fft_start_at_min_freq: int = min(fft_length - 1,
                                         _get_fft_index(self.__frequency_range.start, sampling_rate, number_of_frames))

        fft_end_at_max_freq: int = min(fft_length - 1,
                                       _get_fft_index(self.__frequency_range.end, sampling_rate, number_of_frames)) + 1

        fft_sublist_length: int = max(1, (fft_end_at_max_freq - fft_start_at_min_freq) // led_strip.number_of_groups)

        for fft_sublist_start, led_strip_group in zip(range(fft_start_at_min_freq, fft_end_at_max_freq, fft_sublist_length),
                                                      range(led_strip.number_of_groups)):

            fft_sublist_end: int = min(fft_sublist_start + fft_sublist_length, fft_end_at_max_freq)

            fft_sublist_average_amplitude = mean(_get_fft_amplitude(fft[i], fft_length)
                                                 for i in range(fft_sublist_start, fft_sublist_end))

            rgb = self.__get_rgb(fft_sublist_average_amplitude)

            if (not led_strip.group_is_rgb(led_strip_group, rgb)):
                led_strip.enqueue_rgb(led_strip_group, rgb)

        led_strip.show_queued_colors()
        led_strip.clear_queued_colors()

    def __get_rgb(self, amplitude: Union[int, float]) -> RGB:
        try:
            amplitude = max(0, amplitude)
            amplitude = min(amplitude, len(self.__amplitude_rgbs) - 1)
            return self.__amplitude_rgbs[round(amplitude)]

        except IndexError:
            return RGB()
