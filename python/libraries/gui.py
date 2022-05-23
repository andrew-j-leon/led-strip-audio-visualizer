from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Hashable, List, Tuple

import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED


class Font:
    def __init__(self, name: str = 'Arial', size: int = 12, style: str = 'normal'):
        self.__name = name
        self.__size = size
        self.__style = style

    @property
    def name(self) -> str:
        return self.__name

    @property
    def size(self) -> int:
        return self.__size

    @property
    def style(self) -> str:
        return self.__style

    def __repr__(self) -> str:
        return f'Font(name={self.name}, size={self.size}, style={self.style})'

    def __eq__(self, right_value: Any) -> bool:
        if (isinstance(right_value, Font)):
            return (self.name == right_value.name
                    and self.size == right_value.size
                    and self.style == right_value.style)

        return False

    def __hash__(self) -> int:
        return hash((self.name, self.size, self.style))


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


class Widget(ABC):
    def __init__(self, key: Hashable):
        self.__key = key

    @property
    def key(self) -> Hashable:
        return self.__key

    @abstractmethod
    def set_value(self, value: Any):
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass


class Button(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font(), disabled: bool = False):
        super().__init__(key)
        self.text = text
        self.font = font
        self.disabled = disabled

    def set_value(self, value: Any):
        self.text = value

    def __repr__(self) -> str:
        return f'Button(key={self.key}, text={self.text}, font={self.font}, disabled={self.disabled})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Button)):
            return (self.key == other.key
                    and self.text == other.text
                    and self.font == other.font
                    and self.disabled == other.disabled)

        return False


class Text(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font()):
        super().__init__(key)
        self.text = text
        self.font = font

    def set_value(self, value: Any):
        self.text = value

    def __repr__(self) -> str:
        return f'Text(key={self.key}, text={self.text}, font={self.font})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Text)):
            return (self.key == other.key
                    and self.text == other.text
                    and self.font == other.font)

        return False


class Combo(Widget):
    def __init__(self, key: Hashable = None, values: List[str] = [],
                 default_value: str = None, font: Font = Font(), size=(20, 1)):
        super().__init__(key)

        self.values = values
        self.font = font
        self.default_value = default_value
        self.size = size

    def set_value(self, value: Any):
        self.default_value = value

    def __repr__(self) -> str:
        return f'Combo(key={self.key}, values={self.values}, default_value={self.default_value}, font={self.font}, size={self.size})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Combo)):
            return (self.key == other.key
                    and self.values == other.values
                    and self.font == other.font
                    and self.default_value == other.default_value)

        return False


class CheckBox(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font(), default: bool = False):
        super().__init__(key)

        self.text = text
        self.font = font
        self.default = default

    def set_value(self, value: Any):
        self.default = value

    def __repr__(self) -> str:
        return f'CheckBox(key={self.key}, text={self.text}, font={self.font}, default={self.default})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, CheckBox)):
            return (self.key == other.key
                    and self.text == other.text
                    and self.font == other.font)

        return False


class Multiline(Widget):
    def __init__(self, key: Hashable = None, text: str = '', size: Tuple[int, int] = (50, 7), auto_scroll: bool = True):
        super().__init__(key)

        self.text = text
        self.size = size
        self.auto_scroll = auto_scroll

    def set_value(self, value: Any):
        self.text = value

    def __repr__(self) -> str:
        return f'Multiline(key={self.key}, text={self.text}, size={self.size}, auto_scroll={self.auto_scroll})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Multiline)):
            return (self.key == other.key
                    and self.text == other.text
                    and self.size == other.size
                    and self.auto_scroll == other.auto_scroll)

        return False


class Input(Widget):
    def __init__(self, key: Hashable = None, text: str = ''):
        super().__init__(key)

        self.text = text

    def set_value(self, value: Any):
        self.text = value

    def __repr__(self) -> str:
        return f'Input(key={self.key}, text={self.text})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Input)):
            return (self.key == other.key
                    and self.text == other.text)

        return False


class WidgetGuiEvent(Enum):
    TIMEOUT = auto()
    CLOSE_WINDOW = auto()


class WidgetGui:
    @classmethod
    def _create_element(cls, widget: Widget) -> sg.Element:
        if (isinstance(widget, Button)):
            WIDGET_FONT = widget.font
            FONT = (WIDGET_FONT.name, WIDGET_FONT.size, WIDGET_FONT.style)

            return sg.Button(key=widget.key,
                             button_text=widget.text,
                             font=FONT,
                             disabled=widget.disabled)

        elif (isinstance(widget, Text)):
            WIDGET_FONT = widget.font
            FONT = (WIDGET_FONT.name, WIDGET_FONT.size, WIDGET_FONT.style)

            return sg.Text(key=widget.key,
                           text=widget.text,
                           font=FONT)

        elif (isinstance(widget, Combo)):
            WIDGET_FONT = widget.font
            FONT = (WIDGET_FONT.name, WIDGET_FONT.size, WIDGET_FONT.style)

            return sg.Combo(key=widget.key,
                            values=widget.values,
                            default_value=widget.default_value,
                            font=FONT,
                            size=widget.size)

        elif (isinstance(widget, CheckBox)):
            WIDGET_FONT = widget.font
            FONT = (WIDGET_FONT.name, WIDGET_FONT.size, WIDGET_FONT.style)

            return sg.Checkbox(key=widget.key,
                               text=widget.text,
                               font=FONT,
                               default=widget.default)

        elif (isinstance(widget, Multiline)):
            return sg.Multiline(key=widget.key,
                                default_text=widget.text,
                                size=widget.size,
                                autoscroll=widget.auto_scroll)

        elif (isinstance(widget, Input)):
            return sg.Input(key=widget.key,
                            default_text=widget.text)

        raise TypeError(f'widget ({widget}) of type {type(widget)} is not a recognized Widget type.')

    def __init__(self, title: str = '', is_modal: bool = False, resizable: bool = True,
                 element_padding: Tuple[int, int] = (0, 0), margins: Tuple[int, int] = (0, 0),
                 titlebar_background_color: str = "#000917", titlebar_text_color: str = "#8a8a8a"):

        self.__layout: List[List[Widget]] = [[]]
        self.__widgets: Dict[Hashable, Widget] = dict()

        self.__is_new_layout = True

        self.title = title
        self.is_modal = is_modal
        self.resizable = resizable
        self.element_padding = element_padding
        self.margins = margins
        self.titlebar_background_color = titlebar_background_color
        self.titlebar_text_color = titlebar_text_color

        self.__window = sg.Window(self.title, layout=self.__layout, modal=self.is_modal,
                                  resizable=self.resizable, element_padding=self.element_padding, margins=self.margins,
                                  titlebar_background_color=self.titlebar_background_color, titlebar_text_color=self.titlebar_text_color)

    def set_layout(self, layout: List[List[Widget]]):
        widgets = dict()

        for row in layout:
            for widget in row:
                if (widget.key in widgets and widget.key is not None):
                    raise ValueError(f'Each widget in layout should have a unique key. There were multiple widgets with the key {widget.key} in the layout {layout}.')

                widgets[widget.key] = widget

        self.__layout = layout
        self.__widgets = widgets
        self.__is_new_layout = True

    def update_display(self):
        layout: List[List[sg.Element]] = []

        for row in self.__layout:

            new_row: List[sg.Element] = []

            for widget in row:
                if (not self.__is_new_layout):
                    try:
                        element = self.__window.find_element(widget.key)
                        widget = self.__widgets[widget.key]

                        widget.set_value(element.get())

                    except KeyError:
                        pass

                element = self._create_element(widget)
                new_row.append(element)

            layout.append(new_row)

        self.__window.close()

        self.__window = sg.Window(self.title, layout=layout, modal=self.is_modal,
                                  resizable=self.resizable, element_padding=self.element_padding, margins=self.margins,
                                  titlebar_background_color=self.titlebar_background_color, titlebar_text_color=self.titlebar_text_color)

        self.__window.read(timeout=0)

        self.__is_new_layout = False

    def read_event(self) -> Hashable:
        EVENT = 0
        event = self.__window.read(timeout=0)[EVENT]

        if (event == TIMEOUT_EVENT):
            return WidgetGuiEvent.TIMEOUT

        if (event == WINDOW_CLOSED):
            return WidgetGuiEvent.CLOSE_WINDOW

        return event

    def disable_widget(self, widget_key: Hashable):
        try:
            self.__window.find_element(widget_key).update(disabled=True)
            self.__widgets[widget_key].disabled = True

        except KeyError as error:
            if (widget_key not in self.__widgets):
                raise KeyError(f'There is no widget with the key {widget_key}. Widget keys include: {tuple(self.__widgets.keys())}')

            raise error

    def enable_widget(self, widget_key: Hashable):
        try:
            self.__window.find_element(widget_key).update(disabled=False)
            self.__widgets[widget_key].disabled = False

        except KeyError as error:
            if (widget_key not in self.__widgets):
                raise KeyError(f'There is no widget with the key {widget_key}. Widget keys include: {tuple(self.__widgets.keys())}')

            raise error

    def set_widget_value(self, widget_key: Hashable, value: Any):
        try:
            self.__window.find_element(widget_key).update(value=value)
            self.__widgets[widget_key].set_value(value)

        except KeyError as error:
            if (widget_key not in self.__widgets):
                raise KeyError(f'There is no widget with the key {widget_key}. Widget keys include: {tuple(self.__widgets.keys())}')

            raise error

    def get_widget_value(self, widget_key: Hashable) -> Any:
        return self.__window.find_element(widget_key).get()

    def __enter__(self) -> WidgetGui:
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        try:
            self.__window.close()

        except AttributeError:
            pass
