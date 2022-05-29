from __future__ import annotations

from abc import ABC, abstractmethod
from copy import copy
from enum import Enum, auto
from typing import Any, Dict, Hashable, List, Tuple, Union

import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED
from util import Font


class Widget(ABC):
    def __init__(self, key: Hashable = None):
        self.__key = key

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

            return (NEITHER_HAVE_KEY or (BOTH_HAVE_KEY and self.key == other.key))

        return False


class Button(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font(), enabled: bool = True):
        super().__init__(key)
        self.__text = text
        self.__font = font
        self.enabled = enabled

    @property
    def value(self) -> str:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = value

    @property
    def font(self) -> Font:
        return copy(self.__font)

    def __repr__(self):
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Button({KEY_ARGUMENT}text={self.value}, font={self.font}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        return (super().__eq__(other)
                and type(other) is Button
                and self.value == other.value
                and self.font == other.font
                and self.enabled == other.enabled)


class CheckBox(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font(), value: bool = False,
                 enabled: bool = True):
        super().__init__(key)

        self.__value = value
        self.text = text
        self.__font = font
        self.enabled = enabled

    @property
    def value(self) -> bool:
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def font(self) -> Font:
        return self.__font

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'CheckBox({KEY_ARGUMENT}text={self.text}, font={self.font}, value={self.value}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        return (super().__eq__(other)
                and type(other) is CheckBox
                and self.text == other.text
                and self.font == other.font
                and self.value == other.value
                and self.enabled == other.enabled)


class Combo(Widget):
    def __init__(self, key: Hashable = None, values: List[str] = [],
                 font: Font = Font(), size: Tuple[int, int] = (20, 7), enabled: bool = True):
        super().__init__(key)

        self.__values = list(dict.fromkeys(values))
        self.__value = 0
        self.font = font
        self.size = size
        self.enabled = enabled

    @property
    def values(self) -> List[str]:
        return self.__values.copy()

    @property
    def value(self) -> str:
        try:
            return self.__values[self.__value]

        except IndexError:
            raise AttributeError('This Combo does not have any values.')

    @value.setter
    def value(self, value):
        try:
            self.__value = self.__values.index(value)

        except ValueError:
            raise ValueError(f"{value} is not in this Combo's list of values.")

    def add_value(self, value: str):
        if (value not in self.__values):
            self.__values.append(value)

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '
        VALUE = 'value=None, ' if (not hasattr(self, 'value')) else f'value={self.value}, '

        return f'Combo({KEY_ARGUMENT}values={self.__values}, {VALUE}font={self.font}, size={self.size}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        SELF_HAS_VALUE = hasattr(self, 'value')
        OTHER_HAS_VALUE = hasattr(other, 'value')

        NEITHER_HAVE_VALUE = not SELF_HAS_VALUE and not OTHER_HAS_VALUE
        BOTH_HAVE_VALUE = SELF_HAS_VALUE and OTHER_HAS_VALUE

        VALUES_ARE_EQUAL = (NEITHER_HAVE_VALUE
                            or (BOTH_HAVE_VALUE and self.value == other.value))

        return (super().__eq__(other)
                and type(other) is Combo
                and self.values == other.values
                and VALUES_ARE_EQUAL
                and self.font == other.font
                and self.size == other.size
                and self.enabled == other.enabled)


class Input(Widget):
    def __init__(self, key: Hashable = None, text: str = '', enabled: bool = True):
        super().__init__(key)

        self.__text = text
        self.enabled = enabled

    @property
    def value(self) -> str:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = value

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Input({KEY_ARGUMENT}text={self.value}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        return(super().__eq__(other)
               and type(other) is Input
               and self.value == other.value
               and self.enabled == other.enabled)


class Multiline(Widget):
    def __init__(self, key: Hashable = None, text: str = '', size: Tuple[int, int] = (50, 7),
                 auto_scroll: bool = True, enabled: bool = True):
        super().__init__(key)

        self.__text = text
        self.size = size
        self.auto_scroll = auto_scroll
        self.enabled = enabled

    @property
    def value(self) -> str:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = value

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Multiline({KEY_ARGUMENT}text={self.value}, size={self.size}, auto_scroll={self.auto_scroll}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        return (super().__eq__(other)
                and type(other) is Multiline
                and self.value == other.value
                and self.size == other.size
                and self.auto_scroll == other.auto_scroll
                and self.enabled == other.enabled)


class Text(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font()):
        super().__init__(key)
        self.__text = text
        self.font = font

    @property
    def value(self) -> str:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = value

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Text({KEY_ARGUMENT}text={self.value}, font={self.font})'

    def __eq__(self, other: Any) -> bool:
        return (super().__eq__(other)
                and type(other) is Text
                and self.value == other.value
                and self.font == other.font)


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
    def get_widget(self, widget_key: Hashable) -> Widget:
        pass

    @abstractmethod
    def update_widget(self, widget: Widget):
        pass


class ProductionWidgetGui(WidgetGui):
    @classmethod
    def _create_font(cls, font: Font) -> Tuple[str, int, str]:
        return (font.name, font.size, font.style)

    @classmethod
    def _create_element(cls, widget: Widget) -> sg.Element:

        KEY = None if (not hasattr(widget, 'key')) else widget.key

        if (type(widget) is Button):
            FONT = cls._create_font(widget.font)

            return sg.Button(key=KEY,
                             button_text=widget.value,
                             font=FONT,
                             disabled=not widget.enabled)

        elif (type(widget) is CheckBox):
            FONT = cls._create_font(widget.font)

            return sg.Checkbox(key=KEY,
                               text=widget.text,
                               font=FONT,
                               default=widget.value,
                               disabled=not widget.enabled)

        elif (type(widget) is Combo):
            def create_default_value():
                try:
                    return widget.value

                except AttributeError:
                    return None

            DEFAULT_VALUE = create_default_value()
            FONT = cls._create_font(widget.font)

            return sg.Combo(key=KEY,
                            values=widget.values,
                            default_value=DEFAULT_VALUE,
                            font=FONT,
                            size=widget.size,
                            disabled=not widget.enabled)

        elif (type(widget) is Input):
            return sg.Input(key=KEY,
                            default_text=widget.value,
                            disabled=not widget.enabled)

        elif (type(widget) is Multiline):
            return sg.Multiline(key=KEY,
                                default_text=widget.value,
                                size=widget.size,
                                autoscroll=widget.auto_scroll,
                                disabled=not widget.enabled)

        elif (type(widget) is Text):
            FONT = cls._create_font(widget.font)

            return sg.Text(key=KEY,
                           text=widget.value,
                           font=FONT)

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
        event, values = self.__window.read(timeout=0)
        self.__synchronize_widgets_with_elements(values)

        if (event == TIMEOUT_EVENT):
            return WidgetGuiEvent.TIMEOUT

        if (event == WINDOW_CLOSED):
            return WidgetGuiEvent.CLOSE_WINDOW

        return event

    def __synchronize_widgets_with_elements(self, element_values: Dict[Hashable, Any]):
        try:
            for widget_key, value in element_values.items():
                widget = self.__widgets[widget_key]

                if (isinstance(widget, Combo)):
                    widget.add_value(value)

                widget.value = value

        except AttributeError as error:
            if (element_values is not None):
                raise error

    def get_widget(self, widget_key) -> Widget:
        try:
            return self.__widgets[widget_key]

        except KeyError:
            raise KeyError(f'There is no Widget with the key {widget_key}.')

    def update_widget(self, widget: Widget):
        WIDGET_KEY = widget.key

        if (WIDGET_KEY not in self.__widgets):
            raise KeyError(f'There is no Widget with the key {WIDGET_KEY}.')

        self.__widgets[WIDGET_KEY] = widget

        element: sg.Element = self.__window.find_element(WIDGET_KEY)

        if (type(widget) is Button):
            element: sg.Button
            element.update(text=widget.value,
                           disabled=not widget.enabled)

        elif (type(widget) is CheckBox):
            element: sg.Checkbox
            element.update(value=widget.value,
                           text=widget.text,
                           disabled=not widget.enabled)

        elif (type(widget) is Combo):
            element: sg.Combo

            def create_default_value():
                try:
                    return widget.value

                except AttributeError:
                    return None

            VALUE = create_default_value()
            FONT = self._create_font(widget.font)

            element.update(values=widget.values,
                           value=VALUE,
                           font=FONT,
                           size=widget.size,
                           disabled=not widget.enabled)

        elif (type(widget) is Input):
            element: sg.Input
            element.update(value=widget.value,
                           disabled=not widget.enabled)

        elif (type(widget) is Multiline):
            element: sg.Multiline
            element.update(value=widget.value,
                           autoscroll=widget.auto_scroll,
                           disabled=not widget.enabled)

        elif (type(widget) is Text):
            element: sg.Text
            FONT = self._create_font(widget.font)

            element.update(value=widget.value,
                           font=FONT)

        else:
            raise TypeError(f'widget ({widget}) of type {type(widget)} was not a recognized Widget type.')
