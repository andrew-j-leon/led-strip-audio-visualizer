from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Dict, Hashable, Iterable, List

from libraries.widget import Button, Combo, Widget
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from selection.selection import Selection
from util import Font


class Element(Enum):
    SAVE_NAME_COMBO = auto()
    SAVE_BUTTON = auto()
    DELETE_BUTTON = auto()


class Event(Enum):
    SELECT_CURRENT_SAVE = auto()
    SELECT_NON_CURRENT_SAVE = auto()
    CLEAR_SAVE_NAME = auto()
    ENTER_NEW_SAVE_NAME = auto()
    NO_EVENT = auto()


class SelectionGui(ABC):
    def __init__(self, create_gui: Callable[[], WidgetGui]):
        self.__gui = create_gui()
        self.__gui.title = self._get_title()

    @abstractmethod
    def _get_title(self) -> str:
        pass

    @abstractmethod
    def _get_selection(self, selected_key: str, gui: WidgetGui) -> Selection:
        pass

    @abstractmethod
    def _create_layout(self, selection: Selection) -> List[List[Widget]]:
        pass

    @abstractmethod
    def _create_updatable_widgets(self, selection: Selection) -> Iterable[Widget]:
        pass

    def close(self):
        self.__gui.close()

    def get_current_save_name(self) -> str:
        try:
            COMBO = self.__gui.get_widget(Element.SAVE_NAME_COMBO)
            return COMBO.value

        except AttributeError:
            return ''

    def get_selection(self) -> Selection:
        CURRENT_SAVE_NAME = self.get_current_save_name()
        return self._get_selection(CURRENT_SAVE_NAME, self.__gui)

    def display(self, selection: Selection):
        WIDGETS = self.__create_updatable_widgets(selection)

        LAYOUT = [[WIDGETS[Element.SAVE_NAME_COMBO], WIDGETS[Element.SAVE_BUTTON],
                   WIDGETS[Element.DELETE_BUTTON]]]
        APPENDED_LAYOUT = self._create_layout(selection)

        self.__gui.set_layout(LAYOUT + APPENDED_LAYOUT)
        self.__gui.display_layout()

    def update_widgets(self, selection: Selection):
        for widget in self.__create_updatable_widgets(selection).values():
            self.__gui.update_widget(widget)

        for widget in self._create_updatable_widgets(selection):
            self.__gui.update_widget(widget)

    def read_event_and_update_gui(self, selection: Selection) -> Hashable:
        EVENT = self.__gui.read_event_and_update_gui()

        if (EVENT == WidgetGuiEvent.CLOSE_WINDOW):
            self.close()

        elif (EVENT == WidgetGuiEvent.TIMEOUT):
            SAVE_BUTTON: Button = self.__gui.get_widget(Element.SAVE_BUTTON)
            DELETE_BUTTON: Button = self.__gui.get_widget(Element.DELETE_BUTTON)

            if (self.__current_save_is_selected(selection)):
                SAVE_BUTTON.enabled = True
                DELETE_BUTTON.enabled = True

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

                return Event.SELECT_CURRENT_SAVE

            elif (self.__a_non_current_save_is_selected(selection)):
                SAVE_BUTTON.enabled = True
                DELETE_BUTTON.enabled = True

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

                return Event.SELECT_NON_CURRENT_SAVE

            elif (self.get_current_save_name() == ''):
                SAVE_BUTTON.enabled = False
                DELETE_BUTTON.enabled = False

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

                return Event.CLEAR_SAVE_NAME

            else:
                SAVE_BUTTON.enabled = True
                DELETE_BUTTON.enabled = False

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

                return Event.ENTER_NEW_SAVE_NAME

        return EVENT

    def __current_save_is_selected(self, selection: Selection) -> bool:
        try:
            return self.get_current_save_name() == selection.selected_key

        except AttributeError:
            return False

    def __a_non_current_save_is_selected(self, selection: Selection) -> bool:
        return (not self.__current_save_is_selected(selection)
                and self.get_current_save_name() in selection.keys())

    def __create_updatable_widgets(self, selection: Selection) -> Dict[Element, Widget]:
        def create_save_name_combo():
            SAVE_NAMES = list(selection.keys())
            COMBO_SIZE = (40, 7)

            combo = Combo(Element.SAVE_NAME_COMBO, SAVE_NAMES, size=COMBO_SIZE)

            try:
                combo.value = selection.selected_key
                return combo

            except AttributeError:
                return combo

        FONT = Font("Courier New", 14)

        WIDGETS: List[Widget] = [create_save_name_combo(),
                                 Button(Element.SAVE_BUTTON, "Save", FONT, True),
                                 Button(Element.DELETE_BUTTON, 'Delete', FONT, True)]

        return dict((widget.key, widget) for widget in WIDGETS)
