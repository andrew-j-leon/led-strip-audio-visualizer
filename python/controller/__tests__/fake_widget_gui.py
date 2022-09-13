from typing import Dict, Hashable, List

from libraries.widget import Widget
from libraries.widget_gui import WidgetGui, WidgetGuiEvent


class FakeWidgetGui(WidgetGui):
    def __init__(self):
        self.__title = ''

        self.queued_widgets: Dict[Hashable, Widget] = dict()
        self.displayed_widgets: Dict[Hashable, Widget] = dict()

        self.queued_layout: List[List[Widget]] = []
        self.displayed_layout = []

        self.event = WidgetGuiEvent.TIMEOUT
        self.number_of_read_event_and_update_gui_calls = 0

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title

    def close(self):
        self.open = False

        self.queued_layout.clear()
        self.displayed_layout.clear()

        self.queued_widgets.clear()
        self.displayed_widgets.clear()

    def set_layout(self, layout: List[List[Widget]]):
        self.queued_layout = layout

        for row in layout:
            for widget in row:
                try:
                    self.queued_widgets[widget.key] = widget

                except AttributeError:
                    pass

    def append_layout(self, layout):
        self.set_layout(self.queued_layout + layout)

    def display_layout(self):
        self.displayed_layout = self.queued_layout

        for row in self.displayed_layout:
            for widget in row:
                try:
                    self.displayed_widgets[widget.key] = widget

                except AttributeError:
                    pass

        self.open = True

    def read_event_and_update_gui(self):
        self.number_of_read_event_and_update_gui_calls += 1
        for displayed_widget_key in self.displayed_widgets:
            try:
                self.displayed_widgets[displayed_widget_key] = self.queued_widgets[displayed_widget_key]

            except KeyError:
                continue

        return self.event

    def get_widget(self, widget_key):
        return self.displayed_widgets[widget_key]

    def update_widget(self, widget: Widget):
        WIDGET_KEY = widget.key

        if (WIDGET_KEY not in self.queued_widgets):
            raise KeyError(f'There is no Widget with the key {WIDGET_KEY}.')

        self.queued_widgets[WIDGET_KEY] = widget
        self.displayed_widgets = self.queued_widgets
