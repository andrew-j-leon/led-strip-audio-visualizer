from typing import List, Tuple

import python.led_strip.led_strip as led_strip


class GroupedLedStrip(led_strip.LedStrip):
    def __init__(self, led_index_range: Tuple[int, int], group_index_to_led_range: List[Tuple[int, int]] = []):
        """
            Args:
                `group_index_to_led_range (List[Tuple[int,int]], optional)`: Indices are the group index and values are tuple denoting the
                range of leds said group index represents.

                    Example : Think of the led strip as an array of leds (starting at index 0). If group_index_to_led_range[2] = (15, 20),
                    then group 2 maps to the leds from index 15 (inclusive) to index 20 (exclusive). So, if group 2 is set to a red color
                    (such as the rgb color (100, 0, 0)), then leds 15 through 19 will be set to a red color.
            Raises:
                `ValueError`: If a start_index (index 0 of a tuple) in group_index_to_led_range is >= end_index (index 1).
                `IndexError`: If end_index in group_index_to_led_range is >= led_index_range[1] (the end_index of the LedStrip).
        """
        led_strip.LedStrip.__init__(self, led_index_range)

        for i in range(len(group_index_to_led_range)):
            start_index, end_index = group_index_to_led_range[i]
            if (start_index >= end_index):
                raise ValueError("group_index_to_led_range[{}] : start_index ({}) must be < end_index ({}).".format(i, start_index, end_index))
            if (end_index > self._get_end_index() + 1):
                raise IndexError("group_index[{}] : indicies range from {} to {}, but the (exclusive) end_index was {}.".format(i, self._get_start_index(), self._get_end_index(), end_index))

        self._group_index_to_led_range: List[Tuple[int, int]] = group_index_to_led_range

        self.__group_index_to_its_rgb: List[Tuple[int, int, int]] = [(0, 0, 0) for i in range(self.get_number_of_groups())]

    def get_number_of_groups(self) -> int:
        return len(self._group_index_to_led_range)

    def set_group_color(self, group_index: int, rgb: Tuple[int, int, int]):
        self._enqueue_color_change_by_index(group_index, rgb)

    def group_is_color(self, group_index: int, rgb: Tuple[int, int, int]) -> bool:
        return self.__group_index_to_its_rgb[group_index] == rgb

    def _show(self):
        self._for_each_queued_color_change(self.__set_group_color)

    def __set_group_color(self, group_index: int, rgb: Tuple[int, int, int]):
        self.__group_index_to_its_rgb[group_index] = rgb
