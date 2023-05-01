from abc import ABC, abstractmethod
from typing import Iterable, List, Tuple

from leds.grouped_leds import GroupedLeds, ProductionGroupedLeds
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

    @abstractmethod
    def turn_off(self):
        pass


class ProductionLedStrip(LedStrip):
    def __init__(self, grouped_leds: GroupedLeds = ProductionGroupedLeds()):
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

    def turn_off(self):
        self.clear_queued_colors()

        BLACK = (0, 0, 0)

        for group in range(self.number_of_groups):
            self.enqueue_rgb(group, BLACK)

        self.show_queued_colors()
        self.clear_queued_colors()


class FakeLedStrip(LedStrip):
    def __init__(self, number_of_groups: int = 1):
        self.__number_of_groups = number_of_groups

        self.__color_queue: List[Tuple[int, Tuple[int, int, int]]] = []
        self.group_colors: List[Tuple[int, int, int]] = [(0, 0, 0)] * number_of_groups

    @property
    def number_of_groups(self) -> int:
        return self.__number_of_groups

    @property
    def number_of_queued_colors(self) -> int:
        return len(self.__color_queue)

    def enqueue_rgb(self, group: int, rgb: Iterable[int]):
        self.__color_queue.append((group, rgb))

    def group_is_rgb(self, group: int, rgb: Iterable[int]) -> bool:
        return self.group_colors[group] == rgb

    def show_queued_colors(self):
        for queued_color in self.__color_queue:
            group, rgb = queued_color

            self.group_colors[group] = rgb

    def clear_queued_colors(self):
        self.__color_queue.clear()

    def turn_off(self):
        self.clear_queued_colors()

        BLACK = (0, 0, 0)

        for group in range(self.number_of_groups):
            self.enqueue_rgb(group, BLACK)

        self.show_queued_colors()

        self.clear_queued_colors()
