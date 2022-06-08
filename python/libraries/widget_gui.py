from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Hashable, List, Tuple, Union

import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED

from libraries.widget import Widget, Button, CheckBox, Combo, Input, Multiline, Text
from util import Font


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
