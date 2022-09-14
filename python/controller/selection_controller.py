from typing import Callable

from controller.controller import Controller
from libraries.widget_gui import WidgetGuiEvent
from selection.selection import Selection
from selection.selection_gui import Element, Event, SelectionGui


class SelectionController(Controller):
    def __init__(self, selection_gui: SelectionGui,
                 save_selection: Callable[[Selection], None],
                 selection: Selection):
        self.__selection_gui = selection_gui
        self.__save_selection = save_selection
        self.__selection = selection

    def close(self):
        self.__selection_gui.close()

    def display(self):
        self.__selection_gui.display(self.__selection)

    def read_event_and_update_gui(self):
        return self.__selection_gui.read_event_and_update_gui(self.__selection)

    def handle_event(self, event):
        if (event == Element.SAVE_BUTTON):
            SELECTION = self.__selection_gui.get_selection()

            if (len(SELECTION) > 0):
                self.__selection[SELECTION.selected_key] = SELECTION.selected_value
                self.__selection.selected_key = SELECTION.selected_key

                self.__selection_gui.update_widgets(self.__selection)
                self.__save_selection(self.__selection)

        elif (event == Element.DELETE_BUTTON):
            CURRENT_SAVE_NAME = self.__selection_gui.get_current_save_name()

            try:
                del self.__selection[CURRENT_SAVE_NAME]

                self.__selection_gui.update_widgets(self.__selection)
                self.__save_selection(self.__selection)

            except KeyError:
                raise ValueError(f'No item in the Selection {self.__selection} has the key "{CURRENT_SAVE_NAME}".')

        elif (event == Event.SELECT_NON_CURRENT_SAVE):
            try:
                CURRENT_SAVE_NAME = self.__selection_gui.get_current_save_name()
                self.__selection.selected_key = CURRENT_SAVE_NAME
                self.__selection_gui.update_widgets(self.__selection)

            except ValueError:
                raise ValueError(f"The selected Settings name {CURRENT_SAVE_NAME} is not in "
                                 "this SettingsController's Settings Selection.")

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.close()
