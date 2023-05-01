from __future__ import annotations

from typing import Any, Tuple


class Font:
    def __init__(self, name: str = 'Arial', size: int = 12, style: str = 'normal'):
        self.__name = name
        self.__size = size
        self.__style = style

    @property
    def name(self) -> str:
        return self.__name

    @property
    def size(self) -> int:
        return self.__size

    @property
    def style(self) -> str:
        return self.__style

    def __repr__(self) -> str:
        return f'Font(name={self.name}, size={self.size}, style={self.style})'

    def __eq__(self, right_value: Any) -> bool:
        if (isinstance(right_value, Font)):
            return (self.name == right_value.name
                    and self.size == right_value.size
                    and self.style == right_value.style)

        return False

    def __hash__(self) -> int:
        return hash((self.name, self.size, self.style))


class RGB:
    def __init__(self, red: int = 0, green: int = 0, blue: int = 0):
        rgb = (red, green, blue)

        for channel in rgb:
            if (channel < 0 or channel > 255):
                raise ValueError(f'rgb values must be between 0 (inclusive) & 255 (inclusive), (red, green, blue) was {rgb}.')

        self.__red = red
        self.__green = green
        self.__blue = blue

    @property
    def red(self) -> int:
        return self.__red

    @property
    def green(self) -> int:
        return self.__green

    @property
    def blue(self) -> int:
        return self.__blue

    def __iter__(self):
        yield self.red
        yield self.green
        yield self.blue

    def __repr__(self) -> str:
        return f'RGB({self.red}, {self.green}, {self.blue})'

    def __eq__(self, right_value) -> bool:
        return tuple(self) == tuple(right_value)


def rgb_to_hex(red: int, green: int, blue: int) -> str:
    '''
        Args:
            `red (int)`: The red value within the range [0,255]
            `green (int)`: The green value within the range [0,255]
            `blue (int)`: The blue value within the range [0,255]

        Returns:
            `str`: A hexadecimal conversion of the given RGB color. For example,
                    an RGB of (3, 14, 210) returns "#0314D2"
    '''
    return "#{:02x}{:02x}{:02x}".format(red, green, blue)


def hex_to_rgb(hex: str) -> Tuple[int, int, int]:
    BASE_16 = 16

    RED_HEXADECIMAL = int(hex[1:3], BASE_16)
    GREEN_HEXADECIMAL = int(hex[3:5], BASE_16)
    BLUE_HEXADECIMAL = int(hex[5:7], BASE_16)

    return (RED_HEXADECIMAL, GREEN_HEXADECIMAL, BLUE_HEXADECIMAL)
