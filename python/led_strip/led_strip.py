from abc import ABC, abstractmethod
from typing import Iterable, List, Tuple

from led_strip.grouped_leds import GroupedLeds
from util import RGB


class LedStrip(ABC):
    @property
    @abstractmethod
    def number_of_groups(self) -> int:
        pass

    @property
    @abstractmethod
    def number_of_queued_colors(self) -> int:
        pass

    @abstractmethod
    def enqueue_rgb(self, group: int, rgb: Iterable[int]):
        pass

    @abstractmethod
    def group_is_rgb(self, group: int, rgb: Iterable[int]) -> bool:
        pass

    @abstractmethod
    def show_queued_colors(self):
        pass

    @abstractmethod
    def clear_queued_colors(self):
        pass


class ProductionLedStrip(LedStrip):
    def __init__(self, grouped_leds: GroupedLeds):
        self.__grouped_leds = grouped_leds
        self.__color_queue: List[Tuple[int, RGB]] = []

    @property
    def number_of_groups(self) -> int:
        return self.__grouped_leds.number_of_groups

    @property
    def number_of_queued_colors(self) -> int:
        return len(self.__color_queue)

    def enqueue_rgb(self, group: int, rgb: Iterable[int]):
        if (group < 0 or group >= self.number_of_groups):
            raise IndexError(f'Tried to enqueue RGB {repr(rgb)} into group {group}, but valid group indices range from 0 (inclusive) to {self.number_of_groups} (exclusive).')

        self.__color_queue.append((group, RGB(*rgb)))

    def group_is_rgb(self, group: int, rgb: Iterable[int]) -> bool:
        return self.__grouped_leds.get_group_rgb(group) == rgb

    def show_queued_colors(self):
        self.__grouped_leds.set_group_rgbs(self.__color_queue)

    def clear_queued_colors(self):
        self.__color_queue.clear()
