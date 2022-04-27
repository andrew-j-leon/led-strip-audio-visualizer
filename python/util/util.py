from __future__ import annotations

import colorsys
import math
import os
import re
from functools import total_ordering
from typing import Any, Callable, Dict, Iterable, Iterator, List, Tuple, Type

import numpy


class NonNegativeIntegerRange:
    def __init__(self, start: NonNegativeInteger, end: NonNegativeInteger):
        """
            Args:
                `start (NonNegativeInteger)`: Inclusive.
                `end (NonNegativeInteger)`: Exclusive.

            Example 1 : NonNegativeIntegerRange(0, 5) includes integers 0, 1, 2, 3, 4.

            Example 2 : NonNegativeIntegerRange(0, 0) is an empty set.
        """
        start_non_negative_integer = NonNegativeInteger(start)
        end_non_negative_integer = NonNegativeInteger(end)

        if (start_non_negative_integer > end_non_negative_integer):
            raise ValueError(f'start ({start}) must be < end ({end}).')

        self.__start = start_non_negative_integer
        self.__end = end_non_negative_integer

    @property
    def start(self) -> int:
        return int(self.__start)

    @property
    def end(self) -> int:
        return int(self.__end)

    def __repr__(self) -> str:
        return f'NonNegativeIntegerRange({int(self.start)}, {int(self.end)})'

    def __contains__(self, value):
        if (self.start == self.end):
            return False

        if (isinstance(value, NonNegativeIntegerRange)):
            if (value.start == value.end):
                return True

            return (value.start in self) and (value.end - 1 in self)

        return (value >= self.start) and (value <= self.end - 1)

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.__start, self.__end))


@total_ordering
class NonNegativeInteger:
    def __init__(self, value):

        if (int(value) < 0):
            raise ValueError(f'int({value}) must be >= 0.')

        self.__value = int(value)

    def __repr__(self) -> str:
        return f'NonNegativeInteger({self.__value})'

    def __int__(self):
        return self.__value

    def __index__(self) -> int:
        return self.__value

    def __eq__(self, right_value):
        if (isinstance(right_value, NonNegativeInteger)):
            return self.__value == int(right_value)

        return self.__value == right_value

    def __lt__(self, right_value):
        if (isinstance(right_value, NonNegativeInteger)):
            return self.__value < int(right_value)

        return self.__value < right_value

    def __gt__(self, right_value):
        if (isinstance(right_value, NonNegativeInteger)):
            return self.__value > int(right_value)

        return self.__value > right_value

    def __add__(self, right_value):
        if (isinstance(right_value, NonNegativeInteger)):
            return NonNegativeInteger(self.__value + int(right_value))

        return self.__value + right_value

    def __radd__(self, left_value):
        return left_value + self.__value

    def __sub__(self, right_value):
        if (isinstance(right_value, NonNegativeInteger)):
            return self.__value - int(right_value)

        return self.__value - right_value

    def __rsub__(self, left_value):
        return left_value - self.__value

    def __mul__(self, right_value):
        if (isinstance(right_value, NonNegativeInteger)):
            return NonNegativeInteger(self.__value * int(right_value))

        return self.__value * right_value

    def __rmul__(self, left_value):
        return left_value * self.__value

    def __truediv__(self, right_value):
        if (isinstance(right_value, NonNegativeInteger)):
            return self.__value / int(right_value)

        return self.__value / right_value

    def __rtruediv__(self, left_value):
        return left_value / self.__value


def create_file(file_path: str):
    """
        Creates an empty file file_path if it does not already exist.
    """
    if (not os.path.isfile(file_path)):
        open(file_path, "x").close()


def string_is_int(string: str) -> bool:
    """
        Returns:
            `bool`: True if int(string) is valid; False if otherwise.
    """
    try:
        int(string)
        return True
    except ValueError:
        return False


def get_non_builtin_items(type: Type) -> Dict[str, Any]:
    """
        Args:
            `type (Type)`: The class whose __dict__.items() are searched through.
        Returns:
            `Dict[str,Any]`: The key:value pairs in type.__dict__ that do NOT
            match the regular expression "^__.*__$".
    """
    result = dict()
    for key, value in type.__dict__.items():
        if (not bool(re.match("^__.*__$", key) and not callable(value))):
            result.update({key: value})
    return result


def foreach(iterable: Iterable, func: Callable):
    for item in iterable:
        func(item)


def convert_milliseconds_to_hours_minutes_and_seconds(milliseconds: int) -> str:
    seconds = (milliseconds // 1000) % 60
    minutes = (milliseconds // (1000 * 60)) % 60
    hours = (milliseconds // (1000 * 60 * 60)) % 24

    return "{:02d} : {:02d} : {:02d}".format(hours, minutes, seconds)


def directory_contains_at_least_one_file_with_extension(directory_path: str, file_extensions: List[str]) -> bool:
    """
        Args:
            `file_extensions (List[str])`: The extensions to consider. Can include or exclude the period '.' prefix.
                Example: ['.wav'] and ['wav'] are equivalent arguments.
        Returns:
            `bool`: True if any file in directory_path end with an extension in file_extensions.
            False if otherwise.
    """
    try:
        for file_name in os.listdir(directory_path):
            if (filename_ends_with_extension(file_name, file_extensions)):
                return True
        return False
    except (FileNotFoundError, PermissionError):
        return False


def filename_ends_with_extension(file_name: str, file_extensions: List[str]) -> bool:
    """
        Args:
            `file_extensions (List[str])`: The extensions to consider. Can include or exclude the period '.' prefix.
                Example: ['.wav'] and ['wav'] are equivalent arguments.
        Returns:
            `bool`: True if file_name ends with an extension in file_extensions. False if otherwise.
    """
    extensions = list(map(lambda file_extension: __add_prefix_to_string_if_said_prefix_does_not_exist(file_extension, "."), file_extensions))

    for extension in extensions:
        if file_name.endswith(extension):
            return True
    return False


def __add_prefix_to_string_if_said_prefix_does_not_exist(string: str, prefix: str) -> str:
    return string if string.startswith(prefix) else prefix + string


def have_read_permission(file_or_directory_path: str) -> bool:
    return os.access(file_or_directory_path, os.R_OK)


def hsl_to_rgb(hue: int, saturation: int, lightness: int) -> Tuple[int, int, int]:
    """
        Args:
            `hue (int)`: A value between [0 degrees, 360 degrees].
            `saturation (int)`: A value between [0%, 100%].
            `lightness (int)`: A value between [0%, 100%].

        Returns:
            `Tuple[int,int,int]`: The RGB equivalent of the given HSL color.
    """
    # The colorsys library wants decimal values for hue, saturation, and lightness
    hue = hue / 360.0                # hue has 361 values [0 degrees, 360 degrees]
    saturation = saturation / 100.0  # saturation has 101 values [0%, 100%]
    lightness = lightness / 100.0    # lightness has 101 values [0%, 100%]

    # use colorsys.hsl_to_rgb to convert HSL to RGB, then use map(...) to convert RGB decimal values
    # to RGB integer values
    return tuple(map(lambda x: int(x * 255), colorsys.hls_to_rgb(hue, lightness, saturation)))


def rgb_to_hex(red: int, green: int, blue: int) -> str:
    """
        Args:
            `red (int)`: The red value within the range [0,255]
            `green (int)`: The green value within the range [0,255]
            `blue (int)`: The blue value within the range [0,255]

        Returns:
            `str`: A hexadecimal conversion of the given RGB color. For example,
                    an RGB of (3, 14, 210) returns "#0314D2"
    """
    return "#{:02x}{:02x}{:02x}".format(red, green, blue)


def hsl_to_hex(hue: int, saturation: int, lightness: int) -> str:
    """
        Args:
            `hue (int)`: A value between [0 degrees, 360 degrees].
            `saturation (int)`: A value between [0%, 100%].
            `lightness (int)`: A value between [0%, 100%].

        Returns:
            `str`: A hexadecimal conversion of the given HSL color. For example,
            an HSL of (138, 54, 43) returns "#32a856".
    """
    return rgb_to_hex(*hsl_to_rgb(hue, saturation, lightness))


def get_average_amplitude(audio_data: bytes) -> float:
    """
        Returns:
            `float`: The average amplitude of audio_data in decibels (dB)
    """
    audio_data_in_decimal: List[int] = numpy.frombuffer(audio_data, dtype=numpy.int16)  # convert bytes to List[int]

    # Convert wav_data_int to an average amplitude (in decibels)
    # *RMS = root mean square (a statistical term which means the average of a set of values)
    # See : https://stackoverflow.com/questions/51431859/how-do-i-get-the-frequency-and-amplitude-of-audio-thats-being-recorded-in-pytho
    linear_RMS = numpy.sqrt(numpy.mean(list(d**2 for d in audio_data_in_decimal)))
    if (linear_RMS == 0):
        return 0
    return 20 * math.log10(linear_RMS)


def is_empty(obj) -> bool:
    return len(obj) == 0


def get_nested_value(d: dict, path: str) -> Any:
    """
        Args:
            `path (str)`: A forward slash deliminated path to the value you want to retrieve from
            d.

                Example : If d = {"A":{"B": 10}}, to retrieve the value 10 you would set path = "A/B"
    """
    keys: List[str] = path.split("/")

    value = d[keys[0]]

    for i in range(1, len(keys)):
        value = value[keys[i]]

    return value


def join_paths(parent_path: str, relative_path: str) -> str:
    """
        Returns:
            `str`: The normalized path formed by parent_path + relative_path.

                Example : If parent_path = "A/B/C/D" and relative_path = "../../E",
                this function returns "A/B/E".
    """
    return os.path.normpath(os.path.join(parent_path, relative_path))
