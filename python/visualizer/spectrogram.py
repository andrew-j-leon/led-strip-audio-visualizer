import math
from typing import Dict, List, Tuple, Union

import numpy

from led_strip.led_strip import LedStrip
from util.rgb import RGB

# ================================================================== Some useful formulas ==================================================================
#
# The smaller (sampling_rate / chunk_size) is, the more frequencies within the given frequency_range will be calculated.
# Conversely, the larger this ratio, the fewer frequencies will be calculated.
#       This means that more frequency precision can be attained with a smaller sampling_rate and/or a larger chunk_size.
#
# To find how many frequencies within a given frequency_range=(minimum_frequency, maximum_frequency) will be calculated, use this formula:
#
#       (Equation 1): 1 + floor(maximum_frequency / (sampling_rate / chunk_size)) - ceil(minimum_frequency / (sampling_rate / chunk_size))
#
# To find the minimum frequency calculated, use this formula:
#       (Equation 2): ceil(minimum_frequency / (sampling_rate / chunk_size)) * (sampling_rate / chunk_size)
#
# To find the maximum frequency calculated, use this formula:
#       (Equation 3): floor(maximum_frequency / (sampling_rate / chunk_size)) * (sampling_rate / chunk_size)
#
# Let a_0 ("a subscript 0") = minimum_frequency_calculated. You can use this arithmetic sequence to find the i-th frequency calculated:
#       (Equation 4): a_i = a_0 + i*(sampling_rate / chunk_size)
#
#       For example : If a_0 = 20 Hz, then a_1 (the smallest frequency calculated that is
#       larger than a_0) is:
#           a_1 = 20 + 1*(sampling_rate / chunk_size)
#
# The possible frequencies that can be calculated is given by the following arithmetic sequence where freq_0 = 0 Hz & freq_i is the i-th frequency calculated:
#       freq_i = freq_0 + i*(sampling_rate/chunk_size)
#
# ============================================================================================================================================================


MIN_FREQUENCY_INDEX = 0
MAX_FREQUENCY_INDEX = 1


def _get_fft(audio_data: bytes) -> numpy.ndarray:
    """
        Returns:
            `numpy.ndarray`: The fast fourier transformation of the given audio_data. The i-th element contains
            the fft for the frequency equal to i*(sampling_rate / chunk_size) Hz.
    """
    audio_data_decimal = numpy.frombuffer(audio_data, dtype=numpy.int16)  # convert byte array to an array of ints
    fft: numpy.ndarray = numpy.fft.fft(audio_data_decimal)
    return fft[0:int(len(fft) / 2)]  # We only need the 1st half of the FFT data; the 2nd half is a mirror of the 1st half
    # Interesting fact : this [0:int(len(fft)/2)] has the same number of elements as the chunk_size (but only when the audio is in stereo?
    # When in mono, it's chunk_size/2? <- unsure...)


def _get_fft_sublist_average_amplitude(fft_sublist: List[complex], number_of_fft_values: int) -> float:
    """
        Args:
            fft_sublist (List[complex]): A sub-list of fft values.
            number_of_fft_values (int): The number of fft values in the list from which fft_sublist came from.

                Example: If the original fft list has 100 values and fft_sublist represents 10 values from the
                original, then number_of_fft_values = 100.
        Returns:
            float: The average amplitude of the frequencies described by fft_sublist.
    """
    return sum(_get_fft_amplitude(complex_number, number_of_fft_values) for complex_number in fft_sublist) / len(fft_sublist)


def _get_fft_amplitude(fft_value: complex, number_of_fft_values: int) -> float:
    """
    Args:
        fft_value (complex): An fft value.
        number_of_fft_values (int): The number of fft values in the list from which fft_sublist came from.

            Example: If the original fft list has 100 values and fft_sublist represents 10 values from the
            original, then number_of_fft_values = 100.
    Returns:
        float: The amplitude of the frequency described by fft_value.
    """
    hypotenuse = math.sqrt(fft_value.real**2 + fft_value.imag**2).real

    if (hypotenuse == 0):
        return 0
    return 20 * math.log10(hypotenuse / number_of_fft_values)


def _fft_index_to_frequency(fft_index: int, sampling_rate: int, chunk_size: int) -> float:
    """
        Args:
            `fft_index (int)`: An FFT index.
            `sampling_rate (int)`: The number of samples / second (samples = number_of_bytes?...it might depend, but in my experiments 1 sample = 1 byte).
            `chunk_size (int)`: The number of samples per chunk of audio (again, I believe 1 sample = 1 byte)
        Returns:
            `int`: The frequency at the given FFT fft_index.
    """
    return fft_index * (sampling_rate / chunk_size)


def _get_frequency_to_fft_index(frequency: Union[int, float], sampling_rate: int, chunk_size: int) -> int:
    """
        Args:
            `frequency (Union[int,float])`: A frequency >= 0 in Hz.
            `sampling_rate (int)`: The number of samples / second (samples = number_of_bytes?...it might depend, but in my experiments 1 sample = 1 byte).
            `chunk_size (int)`: The number of samples per chunk of audio (again, I believe 1 sample = 1 byte)
        Returns:
            `int`: The nearest FFT index of the given frequency.
    """
    return round(frequency / (sampling_rate / chunk_size))

# TODO : Get rid of the ability to have multipel led_strips (for now at least...should simplify the design so we can make it better)
# & so it's easier to test.


class Spectrogram:
    """
        Uses an LED_Strip as an audio spectrum analyzer. An audio spectrum analyzer
        divides an audio sample into frequency groups & associates each frequency group
        with said group's average amplitude.
    """

    def __init__(self, frequency_range: Tuple[Union[int, float], Union[int, float]], amplitude_rgbs: List[Tuple[int, int, int]],
                 led_strips: List[LedStrip]):
        """
            Args:
                `frequency_range (Tuple[Union[int,float], Union[int,float]])`: The range of frequencies this visualizer will attempt to
                display. Index 0 contains the minimum_frequency and index 1 the maximum_frequency. It is unlikely
                this visualizer will exactly match the minimum and maximum frequencies (unless you can somehow run this program in an analog fashion on
                an analog computer), but it will try to display as close to these values as possible.

                `amplitude_rgbs (List[Tuple[int,int,int]])`: Indices represent amplitude values (in decibels [dB]) and
                an index's associated value is the RGB color. When a frequency's rounded amplitude equals an index in this list, said frequency will be
                represented on the led strip by said index's RGB value.

                An empty value leads to a deafault amplitude_rgbs list being used.

                    Example : If amplitude_rgbs[50] == (200, 0, 0) (which is a very red color), then any frequency whose rounded amplitude value is 50Hz
                    will be represented on the led strip by the RGB color (200, 0, 0).

                All negative amplitudes are set to 0dB.

                    Example : If the frequency 50Hz has an amplitude of -10dB, said frequency will get the RGB color amplitude_rgbs[0]

                All amplitudes >= len(amplitude_rgbs) will get the RGB color at amplitude_rgbs[len(amplitude_rgbs) - 1].

                    Example : If len(amplitude_rgbs) == 10 and the frequency 50Hz has an amplitude of 12dB, said frequency will get the RGB
                    color at amplitude_rgbs[9].

                `led_strips (List[LedStrip], optional)`: The led strips this visualizer will control.

            Raises:
                `ValueError`: If frequency_range[0] >= frequency_range[1].
        """
        if (frequency_range[0] < 0):
            raise ValueError(f'frequency_range[0] ({frequency_range[0]}) must be >= 0.')

        if (frequency_range[1] < 0):
            raise ValueError(f'frequency_range[1] ({frequency_range[1]}) must be >= 0.')

        if (frequency_range[0] > frequency_range[1]):
            raise ValueError(f"frequency_range[0] ({frequency_range[0]}) must be <= frequency_range[1] ({frequency_range[1]}).")

        self.__number_of_groups_to_led_strips = self.__get_number_of_groups_to_led_strips(led_strips)

        self.__amplitude_rgbs = [RGB(*rgb) for rgb in amplitude_rgbs]
        """
            Indices represent amplitude values and their associated values is the RGB color used to represent said amplitude.
                Example : If __amplitude_rgbs[10] == (200, 0, 0), then an amplitude of 10dB should be represented by the RGB color (200, 0, 0)
        """
        self.__frequency_range = frequency_range

    def update_led_strips(self, audio_data: bytes, chunk_size: int, sampling_rate: int):
        """
            Args:
                `sampling_rate (int)`: The number of samples per second. Typically, 1 sample = 1 byte, so this
                can also be considered the number of bytes (of audio data) per second.
                `chunk_size (int)`: The number of bytes per audio_data.
        """
        if (len(audio_data) == 0):
            self.__turn_off_leds()
        else:
            for number_of_groups in self.__number_of_groups_to_led_strips:
                self.__set_led_strip_color(number_of_groups, audio_data, sampling_rate, chunk_size)
                self.__show_led_strips(number_of_groups)

    def __get_number_of_groups_to_led_strips(self, led_strips: List[LedStrip]) -> Dict[int, List[LedStrip]]:
        """
            Returns:
                `Dict[int, List[LedStrip]]`: Goes through led_strips and maps the number of groups (LedStrip.get_number_of_groups)
                to the GroupedLedStrips that have that many groups.
        """
        number_of_groups_to_led_strips = dict()
        for led_strip in led_strips:
            if (led_strip.number_of_groups in number_of_groups_to_led_strips):
                number_of_groups_to_led_strips[led_strip.number_of_groups].append(led_strip)
            else:
                number_of_groups_to_led_strips[led_strip.number_of_groups] = [led_strip]
        return number_of_groups_to_led_strips

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

    def __set_led_strip_color(self, number_of_groups: int, audio_data: bytes, sampling_rate: int, chunk_size: int):
        fft: numpy.ndarray = _get_fft(audio_data)

        fft_start_index_based_on_the_minimum_frequency: int = min(len(fft) - 1, _get_frequency_to_fft_index(self.__get_minimum_frequency(), sampling_rate, chunk_size))  # inclusive
        fft_end_index_based_on_the_maximum_frequency: int = min(len(fft) - 1, _get_frequency_to_fft_index(self.__get_maximum_frequency(), sampling_rate, chunk_size)) + 1  # exclusive

        number_of_fft_values_per_led_strip_group: int = max(1, (fft_end_index_based_on_the_maximum_frequency - fft_start_index_based_on_the_minimum_frequency) // number_of_groups)

        reference_led_strip: LedStrip = self.__number_of_groups_to_led_strips[number_of_groups][0]

        # Calculate the average amplitude for each frequency group, then convert this average amplitude to
        # an RGB color. Each frequency group maps to a led_strip_group_index. If the led strip group
        # at said led_strip_group_index already has the calculated RGB color, then we will NOT set the group color
        # (as doing so would cause unecessary processing when we call LedStrip.show()). We do this until either
        # we reach the end of the frequency groups OR the end of the led_strip_group_index.
        for fft_sublist_start_index, led_strip_group_index in zip(range(fft_start_index_based_on_the_minimum_frequency, fft_end_index_based_on_the_maximum_frequency, number_of_fft_values_per_led_strip_group),
                                                                  range(number_of_groups)):
            fft_sublist_end_index: int = min(fft_sublist_start_index + number_of_fft_values_per_led_strip_group, fft_end_index_based_on_the_maximum_frequency)
            fft_sublist_average_amplitude: float = _get_fft_sublist_average_amplitude(fft[fft_sublist_start_index:fft_sublist_end_index], len(fft))
            led_strip_group_color = tuple(self.__get_rgb(fft_sublist_average_amplitude))

            if (not reference_led_strip.group_is_rgb(led_strip_group_index, led_strip_group_color)):
                self.__set_group_color(number_of_groups, led_strip_group_index, led_strip_group_color)

    def __get_minimum_frequency(self) -> int:
        return self.__frequency_range[MIN_FREQUENCY_INDEX]

    def __get_maximum_frequency(self) -> int:
        return self.__frequency_range[MAX_FREQUENCY_INDEX]

    def __set_group_color(self, number_of_groups: int, group_index: int, rgb: Tuple[int, int, int]):
        for led_strip in self.__number_of_groups_to_led_strips[number_of_groups]:
            led_strip.enqueue_rgb(group_index, rgb)

    def __set_group_range_color(self, number_of_groups: int, start_group_index: int, end_group_index: int, rgb: Tuple[int, int, int]):
        for led_strip in self.__number_of_groups_to_led_strips[number_of_groups]:
            for group_index in range(start_group_index, end_group_index):
                led_strip.enqueue_rgb(group_index, rgb)

    def __show_led_strips(self, number_of_groups: int):
        for led_strip in self.__number_of_groups_to_led_strips[number_of_groups]:
            led_strip.show_queued_colors()
            led_strip.clear_queued_colors()

    def __get_rgb(self, amplitude: Union[int, float]) -> RGB:
        amplitude = max(0, amplitude)
        amplitude = min(amplitude, len(self.__amplitude_rgbs) - 1)
        return self.__amplitude_rgbs[round(amplitude)]
