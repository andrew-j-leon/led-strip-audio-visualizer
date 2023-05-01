from __future__ import annotations

from typing import Any, Iterable, Iterator, List, Tuple


def load_color_palettes(lines: Iterable[str]) -> List[ColorPalette]:
    color_palettes = []
    amplitude_colors = []

    for line in lines:
        stripped_line = line.strip()

        if (stripped_line == '' and len(amplitude_colors) > 0):
            color_palettes.append(ColorPalette(amplitude_colors))
            amplitude_colors = []

        elif(not stripped_line.startswith('#')):
            count, red, green, blue = stripped_line.split()
            amplitude_colors.extend((int(red), int(green), int(blue)) for i in range(int(count)))

    if (len(amplitude_colors) > 0):
        color_palettes.append(ColorPalette(amplitude_colors))

    return color_palettes


class ColorPalette:
    def __init__(self, amplitude_colors: List[Iterable[int]] = []):
        self.amplitude_colors = amplitude_colors

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, ColorPalette)):
            return self.amplitude_colors == other.amplitude_colors

        return False

    def __iter__(self) -> Iterator[Iterable[int]]:
        return iter(self.amplitude_colors)

    @property
    def amplitude_colors(self) -> List[Tuple[int, int, int]]:
        return self.__amplitude_colors

    @amplitude_colors.setter
    def amplitude_colors(self, amplitude_colors: List[Iterable[int]]):

        new_amplitude_colors: List[Tuple[int, int, int]] = []

        for i in range(len(amplitude_colors)):
            try:
                red, green, blue = amplitude_colors[i]

                if (red < 0 or red > 255):
                    raise ValueError(f'The red value for the rgb at index {i}, {amplitude_colors[i]}, was not >= 0 and <= 255.')

                if (green < 0 or green > 255):
                    raise ValueError(f'The green value for the rgb at index {i}, {amplitude_colors[i]}, was not >= 0 and <= 255.')

                if (blue < 0 or blue > 255):
                    raise ValueError(f'The blue value for the rgb at index {i}, {amplitude_colors[i]}, was not >= 0 and <= 255.')

                new_amplitude_colors.append((red, green, blue))

            except ValueError as error:
                raise ValueError(f'The rgb at index {i}, {amplitude_colors[i]}, was not an Iterable with three values.')

        self.__amplitude_colors = new_amplitude_colors
