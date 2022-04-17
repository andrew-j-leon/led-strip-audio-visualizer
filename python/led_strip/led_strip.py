from typing import Callable, Tuple
import abc


_START_INDEX = 0
_END_INDEX = 1


class LedStrip:
    def __init__(self, led_index_range: Tuple[int, int]):  # start_index inclusive ; end_index exclusive
        """
            Args:
                `led_index_range (Tuple[int,int])`: Specifies the range of led indicies this LedStrip represents. Index 0
                is the start_index (inclusive) and index 1 is the stop_index (exclusive).

                    Example : (10, 20) creates an LedStrip whose first led is at index 10 and whose last led is
                    at index 19.
            Raises:
                `ValueError`: If led_index_range[0] >= led_index_range[1]
                `ValueError`: If led_index_range[0] < 0
        """
        if (led_index_range[0] >= led_index_range[1]):
            raise ValueError("led_index_range[0] must be < led_index_range[1].")

        if (led_index_range[0] < 0):
            raise ValueError("led_index_range[0] must be >= 0.")

        self.__led_index_range: Tuple[int, int] = led_index_range

        self.__queued_color_changes: list = []

    def get_number_of_leds(self) -> int:
        return self._get_end_index() - self._get_start_index() + 1

    def show(self):
        self._show()
        self._clear_queue()

    def _show(self):
        pass

    def _get_start_index(self) -> int:
        return self.__led_index_range[_START_INDEX]

    def _get_end_index(self) -> int:
        return self.__led_index_range[_END_INDEX] - 1

    def _shift_led_index_up_by_start_index(self, index: int) -> int:
        return index + self._get_start_index()

    def _clear_queue(self):
        self.__queued_color_changes.clear()

    def _enqueue_color_change_by_range_of_indices(self, start_index: int, end_index: int, *args):
        """
            Raises:
                `ValueError`: If start_index >= end_index.
        """
        if (start_index >= end_index):
            raise ValueError("start_index must be < end_index")

        self.__queued_color_changes.append((start_index, end_index, *args))

    def _enqueue_color_change_by_index(self, index: int, *args):
        self.__queued_color_changes.append((index, *args))

    def _get_number_of_queued_color_changes(self) -> int:
        return len(self.__queued_color_changes)

    def _for_each_queued_color_change(self, callable: Callable):
        for queued_color_change in self.__queued_color_changes:
            callable(*queued_color_change)
