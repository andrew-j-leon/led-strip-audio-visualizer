import abc
from typing import List

import PySimpleGUI
from gui.window import Window


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
    @property
    @abc.abstractmethod
    def dimensions(self) -> Rectangle:
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def create_oval(self, left_most_x: int, top_most_y: int, right_most_x: int, bottom_most_y: int, fill_color: str) -> int:
        pass

    @abc.abstractmethod
    def create_text(self, center_x: int, center_y: int, text: str, font: Font) -> int:
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def set_element_fill_color(self, element_id: int, color: str):
        pass


class PySimpleGui(Gui):
    def __init__(self):
        SIZE = (1350, 600)
        BACKGROUND_COLOR = '#4a4a4a'
        KEY = 'canvas'

        canvas = PySimpleGUI.Canvas(size=SIZE, background_color=BACKGROUND_COLOR, key=KEY)

        layout: List[List[PySimpleGUI.Element]] = [[canvas]]

        self.__window: Window = Window('LED Strip Visualizer', layout=layout, resizable=True, element_padding=(0, 0),
                                       margins=(0, 0), titlebar_background_color="#000917", titlebar_text_color="#8a8a8a",
                                       disable_close=True, disable_minimize=False)

        self.__window.read(timeout=0)

    @property
    def dimensions(self) -> Rectangle:
        width, height = self.__window["canvas"].get_size()

        return Rectangle(width, height)

    def close(self):
        self.__window.close()

    def create_oval(self, left_most_x: int, top_most_y: int, right_most_x: int, bottom_most_y: int, fill_color: str) -> int:
        return self.__window['canvas'].TKCanvas.create_oval((left_most_x, top_most_y),
                                                            (right_most_x, bottom_most_y),
                                                            fill=fill_color)

    def create_text(self, center_x: int, center_y: int, text: str, font: Font) -> int:
        FONT = (font.name, font.size, font.style)

        self.__window["canvas"].TKCanvas.create_text(center_x, center_y,
                                                     text=text, fill=font.color, font=FONT)

    def update(self):
        self.__window.read(timeout=0)

    def set_element_fill_color(self, element_id: int, color: str):
        self.__window["canvas"].TKCanvas.itemconfig(element_id, fill=color)
