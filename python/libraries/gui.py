import abc
from typing import List

from PySimpleGUI import Canvas, Element, Window


class Font:
    def __init__(self, name: str = 'Arial', size: int = 12, style: str = 'normal', color: str = '#000000'):
        self.__name = name
        self.__size = size
        self.__style = style
        self.__color = color

    @property
    def name(self) -> str:
        return self.__name

    @property
    def size(self) -> int:
        return self.__size

    @property
    def style(self) -> str:
        return self.__style

    @property
    def color(self) -> str:
        return self.__color

    def __repr__(self) -> str:
        return f'Font(name={self.name}, size={self.size}, style={self.style}, color={self.color})'


class Rectangle:
    def __init__(self, width: int, height: int):
        if (width < 0):
            raise ValueError(f'width must be >= 0, but was {width}.')

        if (height < 0):
            raise ValueError(f'height must be >= 0, but was {height}.')

        self.__width = width
        self.__height = height

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    def __repr__(self) -> str:
        return f'Rectangle({self.width}, {self.height})'


class Gui(abc.ABC):
    @property
    @abc.abstractmethod
    def dimensions(self) -> Rectangle:
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def create_oval(self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int, fill_color: str) -> int:
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


class ProductionGui(Gui):
    CANVAS_KEY = 'canvas'

    def __init__(self, width: int, height: int):
        self.__dimensions = Rectangle(width, height)

        canvas = Canvas(size=(width, height), background_color='#4a4a4a', key=ProductionGui.CANVAS_KEY)

        layout: List[List[Element]] = [[canvas]]

        self.__window = Window(title='LED Strip Visualizer', layout=layout, resizable=True, element_padding=(0, 0),
                               margins=(0, 0), titlebar_background_color="#000917", titlebar_text_color="#8a8a8a",
                               disable_close=True, disable_minimize=False)

    @property
    def dimensions(self) -> Rectangle:
        return self.__dimensions

    def update(self):
        self.__window.read(timeout=0)

    def close(self):
        self.__window.close()

    def create_text(self, center_x: int, center_y: int, text: str, font: Font) -> int:
        try:
            FONT = (font.name, font.size, font.style)
            canvas_element: Element = self.__window.find_element(ProductionGui.CANVAS_KEY)

            return canvas_element.TKCanvas.create_text(center_x, center_y,
                                                       text=text, fill=font.color, font=FONT)

        except AttributeError:
            raise ValueError('You must call self.update() before creating elements on a ProductionGui.')

    def create_oval(self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int, fill_color: str) -> int:
        try:
            canvas_element: Element = self.__window.find_element(ProductionGui.CANVAS_KEY)

            return canvas_element.TKCanvas.create_oval((top_left_x, top_left_y),
                                                       (bottom_right_x, bottom_right_y),
                                                       fill=fill_color)

        except AttributeError:
            raise ValueError('You must call self.update() before creating elements on a ProductionGui.')

    def set_element_fill_color(self, element_id: int, color: str):
        try:
            canvas_element: Element = self.__window.find_element(ProductionGui.CANVAS_KEY)

            canvas_element.TKCanvas.itemconfig(element_id, fill=color)

        except AttributeError:
            raise ValueError('You must call self.update() before editting elements.')
