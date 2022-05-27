from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from tkinter import TclError
from typing import Any, Dict, Hashable, List, Tuple, Union

import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED
from util import Font


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

    def __init__(self, key: Hashable = None, values: List[str] = [],
                 font: Font = Font(), size: Tuple[int, int] = (20, 1)):
        super().__init__(key)

        self.__values = list(dict.fromkeys(values))
        self.__value = 0
        self.__font = font
        self.__size = size

    @property
    def values(self) -> List[str]:
        return self.__values

    @property
    def value(self) -> Any:
        try:
            return self.values[self.__value]

        except IndexError:
            raise AttributeError('This Combo does not have any values.')

    @value.setter
    def value(self, value):
        try:
            self.__value = self.__values.index(value)

        except ValueError:
            raise ValueError(f"{value} is not in this Combo's list of values.")

    @property
    def font(self) -> Font:
        return self.__font

    @property
    def size(self) -> Tuple[int, int]:
        return self.__size

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Combo({KEY_ARGUMENT}values={self.values}, font={self.font}, size={self.size})'

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
    def close(self):
        pass

    @abstractmethod
    def set_layout(self, layout: List[List[Widget]]):
        pass

    @abstractmethod
    def display_layout(self):
        pass

    @abstractmethod
    def read_event_and_update_gui(self) -> Union[Hashable, WidgetGuiEvent]:
        pass

    @abstractmethod
    def get_widget_value(self, widget_key: Hashable) -> Any:
        pass

    @abstractmethod
    def set_widget_value(self, widget_key: Hashable, value: Any):
        pass

    @abstractmethod
    def disable_widget(self, widget_key: Hashable):
        pass

    @abstractmethod
    def enable_widget(self, widget_key: Hashable):
        pass


class ProductionWidgetGui(WidgetGui):
    @classmethod
    def _create_element(cls, widget: Widget) -> sg.Element:

        def create_font(font: Font) -> Tuple[str, int, str]:
            return (font.name, font.size, font.style)

        KEY = None if (not hasattr(widget, 'key')) else widget.key

        if (isinstance(widget, Button)):
            FONT = create_font(widget.font)

            return sg.Button(key=KEY,
                             button_text=widget.value,
                             font=FONT,
                             disabled=widget.disabled)

        elif (isinstance(widget, Text)):
            FONT = create_font(widget.font)

            return sg.Text(key=KEY,
                           text=widget.value,
                           font=FONT)

        elif (isinstance(widget, Combo)):
            def create_default_value():
                try:
                    return widget.value

                except AttributeError:
                    return None

            DEFAULT_VALUE = create_default_value()
            FONT = create_font(widget.font)

            return sg.Combo(key=KEY,
                            values=widget.values,
                            default_value=DEFAULT_VALUE,
                            font=FONT,
                            size=widget.size)

        elif (isinstance(widget, CheckBox)):
            FONT = create_font(widget.font)

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

    def __enter__(self) -> ProductionWidgetGui:
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.__window.close()

    def close(self):
        self.__window.close()

    def set_layout(self, layout):
        widgets = dict()

        for row in layout:
            for widget in row:
                try:
                    if (widget.key in widgets):
                        raise ValueError(f'Each widget in layout should have a unique key, but there were '
                                         + f'multiple widgets with the key {widget.key}.')

                    widgets[widget.key] = widget

                except AttributeError:
                    pass

        self.__layout = layout
        self.__widgets = widgets

    def display_layout(self):
        layout: List[List[sg.Element]] = []

        for row in self.__layout:

            new_row: List[sg.Element] = []

            for widget in row:
                element = self._create_element(widget)
                new_row.append(element)

            layout.append(new_row)

        self.__window.close()

        self.__window = sg.Window(self.title, layout=layout, modal=self.is_modal,
                                  resizable=self.resizable, element_padding=self.element_padding, margins=self.margins,
                                  titlebar_background_color=self.titlebar_background_color, titlebar_text_color=self.titlebar_text_color)

        self.__window.read(timeout=0)

    def read_event_and_update_gui(self) -> Union[Hashable, WidgetGuiEvent]:
        EVENT = 0
        event = self.__window.read(timeout=0)[EVENT]
        self.__synchronize_widgets_with_elements()

        if (event == TIMEOUT_EVENT):
            return WidgetGuiEvent.TIMEOUT

        if (event == WINDOW_CLOSED):
            return WidgetGuiEvent.CLOSE_WINDOW

        return event

    def __synchronize_widgets_with_elements(self):
        for widget in self.__widgets.values():
            element = self.__window.find_element(widget.key)

            try:
                widget.value = element.get()

            except ValueError:
                if (isinstance(widget, Combo)):
                    widget.values.append(element.get())
                    widget.value = element.get()

            except (KeyError, AttributeError, TclError):
                pass

    def get_widget_value(self, widget_key) -> Any:
        return self.__widgets[widget_key].value

    def set_widget_value(self, widget_key, value):
        try:
            widget = self.__widgets[widget_key]
            widget.value = value

            element: sg.Element = self.__window.find_element(widget_key)
            element.update(value=value)

        except KeyError:
            raise KeyError(f'There is no widget with the key {widget_key}.')

    def disable_widget(self, widget_key):
        try:
            self.__widgets[widget_key].disabled = True

            element: sg.Element = self.__window.find_element(widget_key)
            element.update(disabled=True)

        except KeyError:
            raise KeyError(f'There is no widget with the key {widget_key}.')

    def enable_widget(self, widget_key):
        try:
            self.__widgets[widget_key].disabled = False

            element: sg.Element = self.__window.find_element(widget_key)
            element.update(disabled=False)

        except KeyError:
            raise KeyError(f'There is no widget with the key {widget_key}.')
