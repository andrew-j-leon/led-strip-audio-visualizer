import abc
from typing import List, Tuple

from util.rgb import RGB
from util.util import NonNegativeInteger, NonNegativeIntegerRange


class GroupedLeds:
    def __init__(self, led_range: Tuple[int, int], group_led_ranges: List[Tuple[int, int]]):
        start = NonNegativeInteger(led_range[0])
        end = NonNegativeInteger(led_range[1])

        self.__led_range = NonNegativeIntegerRange(start, end)

        self.__group_led_ranges: List[NonNegativeIntegerRange] = []

        for i in range(len(group_led_ranges)):
            start, end = group_led_ranges[i]

            non_negative_integer_range = NonNegativeIntegerRange(start, end)

            if (non_negative_integer_range not in self.__led_range):
                raise ValueError(f'group_led_ranges[{i}]={(start, end)} is not within the bounds of led_range={led_range}.')

            self.__group_led_ranges.append(non_negative_integer_range)

        self.__group_colors = [RGB(0, 0, 0)] * len(group_led_ranges)

    @property
    def number_of_groups(self) -> int:
        return len(self.__group_led_ranges)

    @property
    def number_of_leds(self) -> int:
        return self.__led_range.end - self.__led_range.start

    @property
    def start_led(self) -> int:
        """
            Returns:
                `int`: Inclusive start led index.
        """
        return self.__led_range.start

    @property
    def end_led(self) -> int:
        """
            Returns:
                `int`: Exclusive end led index.
        """
        return self.__led_range.end

    def get_group_rgb(self, group: int) -> RGB:
        if (group < 0):
            raise ValueError(f'group must be >= 0, but was {group}.')

        return self.__group_colors[group]

    def set_group_rgb(self, group: int, rgb: RGB):
        if (group < 0):
            raise ValueError(f'group must be >= 0, but was {group}.')

        self.__group_colors[group] = rgb

    def get_group_led_range(self, group: int) -> NonNegativeIntegerRange:
        if (group < 0):
            raise ValueError(f'group must be >= 0, but was {group}.')

        return self.__group_led_ranges[group]


class LedStrip(abc.ABC):
    @property
    @abc.abstractmethod
    def number_of_groups(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def number_of_queued_colors(self) -> int:
        pass

    @abc.abstractmethod
    def enqueue_rgb(self, group: int, rgb: Tuple[int, int, int]):
        pass

    @abc.abstractmethod
    def group_is_rgb(self, group_index: int, rgb: Tuple[int, int, int]) -> bool:
        pass

    @abc.abstractmethod
    def show_queued_colors(self):
        pass

    @abc.abstractmethod
    def clear_queued_colors(self):
        pass


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

    def enqueue_rgb(self, group: int, rgb: Tuple[int, int, int]):
        self.__color_queue.append((group, rgb))

    def group_is_rgb(self, group_index: int, rgb: Tuple[int, int, int]) -> bool:
        return self.group_colors[group_index] == rgb

    def show_queued_colors(self):
        for queued_color in self.__color_queue:
            group, rgb = queued_color

            self.group_colors[group] = rgb

    def clear_queued_colors(self):
        self.__color_queue.clear()
