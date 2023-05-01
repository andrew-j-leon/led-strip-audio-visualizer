from abc import ABC, abstractmethod
from typing import Iterable, List, Tuple

from leds.frequency_band_leds import FrequencyBandLeds, ProductionFrequencyBandLeds
from util import RGB


class LedArray(ABC):
    @property
    @abstractmethod
    def number_of_bands(self) -> int:
        pass

    @property
    @abstractmethod
    def number_of_queued_colors(self) -> int:
        pass

    @abstractmethod
    def enqueue_rgb(self, band: int, rgb: Iterable[int]):
        pass

    @abstractmethod
    def band_is_rgb(self, band: int, rgb: Iterable[int]) -> bool:
        pass

    @abstractmethod
    def show_queued_colors(self):
        pass

    @abstractmethod
    def clear_queued_colors(self):
        pass

    @abstractmethod
    def turn_off(self):
        pass


class ProductionLedArray(LedArray):
    def __init__(self, frequency_band_leds: FrequencyBandLeds = ProductionFrequencyBandLeds()):
        self.__frequency_band_leds = frequency_band_leds
        self.__color_queue: List[Tuple[int, RGB]] = []

    @property
    def number_of_bands(self) -> int:
        return self.__frequency_band_leds.number_of_bands

    @property
    def number_of_queued_colors(self) -> int:
        return len(self.__color_queue)

    def enqueue_rgb(self, band: int, rgb: Iterable[int]):
        if (band < 0 or band >= self.number_of_bands):
            raise IndexError(f'Tried to enqueue RGB {repr(rgb)} into band {band}, but valid band '
                             f'indices range from 0 (inclusive) to {self.number_of_bands} (exclusive).')

        self.__color_queue.append((band, RGB(*rgb)))

    def band_is_rgb(self, band: int, rgb: Iterable[int]) -> bool:
        return self.__frequency_band_leds.get_band_color(band) == rgb

    def show_queued_colors(self):
        self.__frequency_band_leds.set_band_colors(self.__color_queue)

    def clear_queued_colors(self):
        self.__color_queue.clear()

    def turn_off(self):
        self.clear_queued_colors()

        BLACK = (0, 0, 0)

        for band in range(self.number_of_bands):
            self.enqueue_rgb(band, BLACK)

        self.show_queued_colors()
        self.clear_queued_colors()


class FakeLedArray(LedArray):
    def __init__(self, number_of_bands: int = 1):
        self.__number_of_bands = number_of_bands

        self.__color_queue: List[Tuple[int, Tuple[int, int, int]]] = []
        self.band_colors: List[Tuple[int, int, int]] = [(0, 0, 0)] * number_of_bands

    @property
    def number_of_bands(self) -> int:
        return self.__number_of_bands

    @property
    def number_of_queued_colors(self) -> int:
        return len(self.__color_queue)

    def enqueue_rgb(self, band: int, rgb: Iterable[int]):
        self.__color_queue.append((band, rgb))

    def band_is_rgb(self, band: int, rgb: Iterable[int]) -> bool:
        return self.band_colors[band] == rgb

    def show_queued_colors(self):
        for queued_color in self.__color_queue:
            band, rgb = queued_color

            self.band_colors[band] = rgb

    def clear_queued_colors(self):
        self.__color_queue.clear()

    def turn_off(self):
        self.clear_queued_colors()

        BLACK = (0, 0, 0)

        for band in range(self.number_of_bands):
            self.enqueue_rgb(band, BLACK)

        self.show_queued_colors()

        self.clear_queued_colors()
