from __future__ import annotations

from typing import Any, Iterable, List, Tuple

from util import Jsonable


class ColorPalette(Jsonable):
    def __init__(self, amplitude_rgbs: List[Iterable[int]] = []):
        self.amplitude_rgbs = amplitude_rgbs

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, ColorPalette)):
            return self.amplitude_rgbs == other.amplitude_rgbs

        return False

    def to_json(self):
        return {'amplitude_rgbs': self.amplitude_rgbs}

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
