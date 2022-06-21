from abc import ABC, abstractmethod
from typing import Hashable, Union

from libraries.widget_gui import WidgetGuiEvent


class RunnableResource(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def close(self):
        pass


class Controller(RunnableResource):
    def run(self):
        self.display()
        settings_event = self.read_event_and_update_gui()

        while (settings_event != WidgetGuiEvent.CLOSE_WINDOW):
            self.handle_event(settings_event)
            settings_event = self.read_event_and_update_gui()

        self.handle_event(settings_event)

    @abstractmethod
    def display(self):
        pass

    @abstractmethod
    def read_event_and_update_gui(self) -> Union[WidgetGuiEvent, Hashable]:
        pass

    @abstractmethod
    def handle_event(self, event: Union[WidgetGuiEvent, Hashable]):
        pass
