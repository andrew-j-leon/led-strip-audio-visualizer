import math
import statistics
from typing import List, Union

import numpy
from color_palette import ColorPalette
from grouped_leds import GroupedLedsQueue

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


def update(grouped_leds: GroupedLedsQueue, audio_data: bytes, number_of_frames: int, sampling_rate: int,
           bands: List[List[int]], color_palette_groups: List[ColorPalette]):

    audio_data_decimal: bytes = numpy.frombuffer(audio_data, dtype=numpy.int16)
    fft: numpy.ndarray = numpy.fft.fft(audio_data_decimal)

    fft_length = math.ceil(len(fft) / 2)  # the first half of the fft is a mirror copy of the 2nd half; we can ignore the 2nd half

    for band in bands:
        frequency_start_index = _get_fft_index(band[0], sampling_rate, number_of_frames)
        frequency_end_index = _get_fft_index(band[1], sampling_rate, number_of_frames)

        average_amplitude = statistics.mean(_get_fft_amplitude(fft[i], fft_length)
                                            for i in range(frequency_start_index, frequency_end_index))

        colors = color_palette_groups[band[2]].get_colors(average_amplitude)

        for i in range(3, len(band)):
            if (not grouped_leds.group_is_color(band[i], colors[i - 3])):
                grouped_leds.enqueue_color(band[i], colors[i - 3])

    grouped_leds.show_queued_colors()
    grouped_leds.clear_queued_colors()
