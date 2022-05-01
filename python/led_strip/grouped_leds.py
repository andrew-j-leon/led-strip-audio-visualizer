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
        '''
            Returns:
                `int`: Inclusive start led index.
        '''
        return self.__led_range.start

    @property
    def end_led(self) -> int:
        '''
            Returns:
                `int`: Exclusive end led index.
        '''
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
