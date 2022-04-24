import abc
from typing import Tuple


class LedStrip(abc.ABC):
    @property
    @abc.abstractmethod
    def number_of_groups(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def number_of_leds(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def number_of_queued_colors(self) -> int:
        pass

    @abc.abstractmethod
    def enqueue_rgb(self, group: int, rgb: Tuple[int, int, int]):
        pass

    @abc.abstractmethod
    def group_is_color(self, group_index: int, rgb: Tuple[int, int, int]) -> bool:
        pass

    @abc.abstractmethod
    def show_queued_colors(self):
        pass

    @abc.abstractmethod
    def clear_queued_colors(self):
        pass
