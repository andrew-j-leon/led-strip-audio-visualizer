from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Hashable, List, Tuple, Union

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
    def __init__(self, key: Hashable = None, disabled: bool = False):
        self.__key = key
        self.disabled = disabled

    @property
    def key(self) -> Hashable:
        if (self.__key is None):
            raise AttributeError('This Widget does not have a key attribute.')

        return self.__key

    @property
    @abstractmethod
    def value(self) -> Any:
        pass

    @value.setter
    @abstractmethod
    def value(self, value: Any):
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Widget)):
            SELF_HAS_KEY = hasattr(self, 'key')
            OTHER_HAS_KEY = hasattr(other, 'key')

            NEITHER_HAVE_KEY = not SELF_HAS_KEY and not OTHER_HAS_KEY
            BOTH_HAVE_KEY = SELF_HAS_KEY and OTHER_HAS_KEY

            return (self.disabled == other.disabled
                    and (NEITHER_HAVE_KEY or (BOTH_HAVE_KEY and self.key == other.key)))

        return False


class Button(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font(), disabled: bool = False):
        super().__init__(key, disabled)
        self.__text = text
        self.__font = font

    @property
    def font(self) -> Font:
        return self.__font

    @property
    def value(self) -> Any:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = value

    def __repr__(self):
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Button({KEY_ARGUMENT}text={self.value}, font={self.font}, disabled={self.disabled})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Button)):
            return (super().__eq__(other)
                    and self.value == other.value
                    and self.font == other.font
                    and self.disabled == other.disabled)

        return False


class Text(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font()):
        super().__init__(key)
        self.__text = text
        self.__font = font

    @property
    def font(self) -> Font:
        return self.__font

    @property
    def value(self) -> Any:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = value

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Text({KEY_ARGUMENT}text={self.value}, font={self.font})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Text)):
            return (super().__eq__(other)
                    and self.value == other.value
                    and self.font == other.font)

        return False


class Combo(Widget):

    def __init__(self, key: Hashable = None, values: List[str] = [], value: int = None,
                 font: Font = Font(), size: Tuple[int, int] = (20, 1)):
        super().__init__(key)

        self.__values = values
        self.value = value
        self.__font = font
        self.__size = size

    @property
    def values(self) -> List[str]:
        return self.__values.copy()

    @property
    def font(self) -> Font:
        return self.__font

    @property
    def size(self) -> Tuple[int, int]:
        return self.__size

    @property
    def value(self) -> Any:
        try:
            return self.values[self.__value]

        except TypeError:
            raise AttributeError('This Combo does not have a set value.')

    @value.setter
    def value(self, value):
        try:
            self.__values[value]
            self.__value = value

        except TypeError:
            if (value is None):
                self.__value = value

            else:
                raise TypeError('value must be an int or NoneType. However, the '
                                f'given value {value} was of type {type(value)}.')

        except IndexError:
            raise IndexError(f'This Combo does not have a value at index {value}. '
                             f'Its values include: {self.__values}')

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Combo({KEY_ARGUMENT}values={self.values}, value={self.__value}, font={self.font}, size={self.size})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Combo)):
            SELF_HAS_VALUE = hasattr(self, 'value')
            OTHER_HAS_VALUE = hasattr(other, 'value')

            NEITHER_HAVE_VALUE = not SELF_HAS_VALUE and not OTHER_HAS_VALUE
            BOTH_HAVE_VALUE = SELF_HAS_VALUE and OTHER_HAS_VALUE

            VALUES_ARE_EQUAL = (NEITHER_HAVE_VALUE
                                or (BOTH_HAVE_VALUE and self.value == other.value))

            return (super().__eq__(other)
                    and self.values == other.values
                    and VALUES_ARE_EQUAL
                    and self.font == other.font
                    and self.size == other.size)

        return False


class CheckBox(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font(), value: bool = False):
        super().__init__(key)

        self.__text = text
        self.__font = font
        self.__value = value

    @property
    def text(self) -> str:
        return self.__text

    @property
    def font(self) -> Font:
        return self.__font

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'CheckBox({KEY_ARGUMENT}text={self.text}, font={self.font}, value={self.value})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, CheckBox)):
            return (super().__eq__(other)
                    and self.text == other.text
                    and self.font == other.font
                    and self.value == other.value)

        return False


class Multiline(Widget):
    def __init__(self, key: Hashable = None, text: str = '', size: Tuple[int, int] = (50, 7), auto_scroll: bool = True):
        super().__init__(key)

        self.__text = text
        self.__size = size
        self.__auto_scroll = auto_scroll

    @property
    def size(self) -> Tuple[int, int]:
        return self.__size

    @property
    def auto_scroll(self) -> bool:
        return self.__auto_scroll

    @property
    def value(self) -> str:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = value

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Multiline({KEY_ARGUMENT}text={self.value}, size={self.size}, auto_scroll={self.auto_scroll})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Multiline)):
            are_equal = (self.value == other.value
                         and self.size == other.size
                         and self.auto_scroll == other.auto_scroll)

            try:
                return are_equal and (self.key == other.key)

            except AttributeError:
                if (not hasattr(self, 'key') and not hasattr(other, 'key')):
                    return are_equal

        return False


class Input(Widget):
    def __init__(self, key: Hashable = None, text: str = ''):
        super().__init__(key)

        self.__text = text

    @property
    def value(self):
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = value

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Input({KEY_ARGUMENT}text={self.value})'

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Input)):
            are_equal = self.value == other.value

            try:
                return are_equal and (self.key == other.key)

            except AttributeError:
                if (not hasattr(self, 'key') and not hasattr(other, 'key')):
                    return are_equal

        return False


class WidgetGuiEvent(Enum):
    TIMEOUT = auto()
    CLOSE_WINDOW = auto()


class WidgetGui(ABC):
    @abstractmethod
    def set_layout(self, layout: List[List[Widget]]):
        pass

    @abstractmethod
    def redraw_gui(self):
        pass

    @abstractmethod
    def read_event_and_update_gui(self) -> Union[Hashable, WidgetGuiEvent]:
        pass

    @abstractmethod
    def disable_widget(self, widget_key: Hashable):
        pass

    @abstractmethod
    def enable_widget(self, widget_key: Hashable):
        pass

    @abstractmethod
    def set_widget_value(self, widget_key: Hashable, value: Any):
        pass

    @abstractmethod
    def get_widget_value(self, widget_key: Hashable) -> Any:
        pass

    @abstractmethod
    def close(self):
        pass


class ProductionWidgetGui(WidgetGui):
    @classmethod
    def _create_element(cls, widget: Widget) -> sg.Element:

        KEY = None if (not hasattr(widget, 'key')) else widget.key

        if (isinstance(widget, Button)):
            WIDGET_FONT = widget.font
            FONT = (WIDGET_FONT.name, WIDGET_FONT.size, WIDGET_FONT.style)

            return sg.Button(key=KEY,
                             button_text=widget.value,
                             font=FONT,
                             disabled=widget.disabled)

        elif (isinstance(widget, Text)):
            WIDGET_FONT = widget.font
            FONT = (WIDGET_FONT.name, WIDGET_FONT.size, WIDGET_FONT.style)

            return sg.Text(key=KEY,
                           text=widget.value,
                           font=FONT)

        elif (isinstance(widget, Combo)):
            def get_default_value():
                try:
                    return widget.value

                except AttributeError:
                    return None

            WIDGET_FONT = widget.font
            FONT = (WIDGET_FONT.name, WIDGET_FONT.size, WIDGET_FONT.style)

            return sg.Combo(key=KEY,
                            values=widget.values,
                            default_value=get_default_value(),
                            font=FONT,
                            size=widget.size)

        elif (isinstance(widget, CheckBox)):
            WIDGET_FONT = widget.font
            FONT = (WIDGET_FONT.name, WIDGET_FONT.size, WIDGET_FONT.style)

            return sg.Checkbox(key=KEY,
                               text=widget.text,
                               font=FONT,
                               default=widget.value)

        elif (isinstance(widget, Multiline)):
            return sg.Multiline(key=KEY,
                                default_text=widget.value,
                                size=widget.size,
                                autoscroll=widget.auto_scroll)

        elif (isinstance(widget, Input)):
            return sg.Input(key=KEY,
                            default_text=widget.value)

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

    def close(self):
        self.__window.close()

    def set_layout(self, layout):
        widgets = dict()

        for row in layout:
            for widget in row:
                try:
                    if (widget.key in widgets):
                        raise ValueError(f'Each widget in layout should have a unique key, but there were '
                                         + f'multiple widgets with the key {widget.key} in the layout {layout}.')

                    widgets[widget.key] = widget

                except AttributeError:
                    pass

        self.__layout = layout
        self.__widgets = widgets
        self.__is_new_layout = True

    def redraw_gui(self):
        layout: List[List[sg.Element]] = []

        for row in self.__layout:

            new_row: List[sg.Element] = []

            for widget in row:
                if (not self.__is_new_layout):
                    try:
                        element = self.__window.find_element(widget.key)
                        widget = self.__widgets[widget.key]

                        widget.value = element.get()

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

    def read_event_and_update_gui(self) -> Union[Hashable, WidgetGuiEvent]:
        EVENT = 0
        event = self.__window.read(timeout=0)[EVENT]

        if (event == TIMEOUT_EVENT):
            return WidgetGuiEvent.TIMEOUT

        if (event == WINDOW_CLOSED):
            return WidgetGuiEvent.CLOSE_WINDOW

        return event

    def disable_widget(self, widget_key):
        try:
            element: sg.Element = self.__window.find_element(widget_key)
            element.update(disabled=True)

            self.__widgets[widget_key].disabled = True

        except KeyError as error:
            if (widget_key not in self.__widgets):
                raise KeyError(f'There is no widget with the key {widget_key}. Widget keys include: {tuple(self.__widgets.keys())}')

            raise error

    def enable_widget(self, widget_key):
        try:
            element: sg.Element = self.__window.find_element(widget_key)
            element.update(disabled=False)

            self.__widgets[widget_key].disabled = False

        except KeyError as error:
            if (widget_key not in self.__widgets):
                raise KeyError(f'There is no widget with the key {widget_key}. Widget keys include: {tuple(self.__widgets.keys())}')

            raise error

    def set_widget_value(self, widget_key, value):
        try:
            element: sg.Element = self.__window.find_element(widget_key)
            element.update(value=value)

            self.__widgets[widget_key].value = value

        except KeyError as error:
            if (widget_key not in self.__widgets):
                raise KeyError(f'There is no widget with the key {widget_key}. Widget keys include: {tuple(self.__widgets.keys())}')

            raise error

    def get_widget_value(self, widget_key) -> Any:
        return self.__window.find_element(widget_key).get()

    def __enter__(self) -> ProductionWidgetGui:
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.__window.close()
