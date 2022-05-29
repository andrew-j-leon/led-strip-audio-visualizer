from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import PySimpleGUI as sg
from util import Font


class CanvasGui(ABC):
    @property
    @abstractmethod
    def width(self) -> int:
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def create_oval(self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int, fill_color: str = '#000000') -> int:
        pass

    @abstractmethod
    def create_text(self, center_x: int, center_y: int, text: str, font: Font = Font(), fill_color: str = '#000000') -> int:
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def set_element_fill_color(self, element_id: int, color: str):
        pass


class ProductionCanvasGui(CanvasGui):
    CANVAS_KEY = 'canvas'

    def __init__(self, width: int, height: int):
        if (width < 0):
            raise ValueError(f'width must be >= 0, but was {width}.')

        if (height < 0):
            raise ValueError(f'height must be >= 0, but was {height}.')

        self.__width = width

        canvas = sg.Canvas(size=(width, height), background_color='#4a4a4a', key=self.CANVAS_KEY)

        layout: List[List[sg.Element]] = [[canvas]]

        self.__window = sg.Window(title='LED Strip Visualizer', layout=layout, resizable=True, element_padding=(0, 0),
                                  margins=(0, 0), titlebar_background_color="#000917", titlebar_text_color="#8a8a8a",
                                  disable_close=True, disable_minimize=False)

    @property
    def width(self):
        return self.__width

    def update(self):
        self.__window.read(timeout=0)

    def close(self):
        self.__window.close()

    def create_text(self, center_x: int, center_y: int, text: str, font: Font = Font(), fill_color: str = '#000000') -> int:
        try:
            FONT = (font.name, font.size, font.style)
            canvas_element: sg.Element = self.__window.find_element(self.CANVAS_KEY)

            return canvas_element.TKCanvas.create_text(center_x, center_y,
                                                       text=text, fill=fill_color, font=FONT)

        except AttributeError:
            raise ValueError('You must call self.update() before creating elements on a ProductionCanvasGui.')

    def create_oval(self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int, fill_color: str = '#000000') -> int:
        try:
            canvas_element: sg.Element = self.__window.find_element(self.CANVAS_KEY)

            return canvas_element.TKCanvas.create_oval((top_left_x, top_left_y),
                                                       (bottom_right_x, bottom_right_y),
                                                       fill=fill_color)

        except AttributeError:
            raise ValueError('You must call self.update() before creating elements on a ProductionCanvasGui.')

    def set_element_fill_color(self, element_id: int, color: str):
        try:
            canvas_element: sg.Element = self.__window.find_element(self.CANVAS_KEY)

            canvas_element.TKCanvas.itemconfig(element_id, fill=color)

        except AttributeError:
            raise ValueError('You must call self.update() before editting elements.')
