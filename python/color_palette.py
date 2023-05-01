from __future__ import annotations

from typing import Any, Iterable, Iterator, List, Tuple


def load_color_palettes(lines: Iterable[str]) -> List[ColorPalette]:
    color_palettes = []
    amplitude_rgbs = []

    for line in lines:
        stripped_line = line.strip()

        if (stripped_line == '' and len(amplitude_rgbs) > 0):
            color_palettes.append(ColorPalette(amplitude_rgbs))
            amplitude_rgbs = []

        elif(not stripped_line.startswith('#')):
            count, red, green, blue = stripped_line.split()
            amplitude_rgbs.extend((int(red), int(green), int(blue)) for i in range(int(count)))

    if (len(amplitude_rgbs) > 0):
        color_palettes.append(ColorPalette(amplitude_rgbs))

    return color_palettes


class ColorPalette:
    def __init__(self, amplitude_rgbs: List[Iterable[int]] = []):
        self.amplitude_rgbs = amplitude_rgbs

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, ColorPalette)):
            return self.amplitude_rgbs == other.amplitude_rgbs

        return False

    def __iter__(self) -> Iterator[Iterable[int]]:
        return iter(self.amplitude_rgbs)

    @property
    def amplitude_rgbs(self) -> List[Tuple[int, int, int]]:
        return self.__amplitude_rgbs

    @amplitude_rgbs.setter
    def amplitude_rgbs(self, amplitude_rgbs: List[Iterable[int]]):

        new_amplitude_rgbs: List[Tuple[int, int, int]] = []

        for i in range(len(amplitude_rgbs)):
            try:
                red, green, blue = amplitude_rgbs[i]

                if (red < 0 or red > 255):
                    raise ValueError(f'The red value for the rgb at index {i}, {amplitude_rgbs[i]}, was not >= 0 and <= 255.')

                if (green < 0 or green > 255):
                    raise ValueError(f'The green value for the rgb at index {i}, {amplitude_rgbs[i]}, was not >= 0 and <= 255.')

                if (blue < 0 or blue > 255):
                    raise ValueError(f'The blue value for the rgb at index {i}, {amplitude_rgbs[i]}, was not >= 0 and <= 255.')

                new_amplitude_rgbs.append((red, green, blue))

            except ValueError as error:
                raise ValueError(f'The rgb at index {i}, {amplitude_rgbs[i]}, was not an Iterable with three values.')

        self.__amplitude_rgbs = new_amplitude_rgbs
