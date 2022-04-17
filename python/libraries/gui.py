import abc
from typing import Tuple


class Font:
    def __init__(self, name: str = 'Arial', size: int = 12, style: str = 'normal', color: str = '#000000'):
        self.name = name
        self.size = size
        self.style = style
        self.color = color


class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class Gui(abc.ABC):
    def __init__(self, dimensions: Tuple[int, int]):
        self.__dimensions = dimensions

    @property
    def dimensions(self) -> Rectangle:
        return Rectangle(self.__dimensions[0], self.__dimensions[1])

    @abc.abstractmethod
    def set_background_color(self, color: str):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def create_oval(self, left_most_x: int, top_most_y: int, right_most_x: int, bottom_most_y: int, fill_color: str):
        pass

    @abc.abstractmethod
    def create_text(self, center_x: int, center_y: int, text: str, font: Font):
        pass

    @abc.abstractmethod
    def update(self):
        pass


class PySimpleGui(Gui):
    pass


class FakeGui(Gui):
    pass
