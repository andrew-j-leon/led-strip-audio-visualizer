from typing import Any, Callable, Dict, List, Tuple

import PySimpleGUI as sg
import util
from gui.window import Window
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED


class Element:
    pass


class _Element(Element):
    CONFIRMATION_MODAL_OK_BUTTON = "error_modal_ok_button"


class Event:
    WINDOW_CLOSED = WINDOW_CLOSED
    TIMEOUT_EVENT = TIMEOUT_EVENT
    CONFIRMATION_MODAL_OK = _Element.CONFIRMATION_MODAL_OK_BUTTON


class View:
    def __init__(self):
        self.__main_window: Window = None

    def __del__(self):
        self._do_stuff_on_delete()
        self.__close_main_window()

    def display_confirmation_modal(self, title: str, error_message: str):
        """
            Display a modal that blocks input from all other windows until said modal's
            "Ok" button or upper-right "X" button is clicked.

            Args:
                `title (str)`: The title of the modal.
                `error_message (str)`: The modal's message to the user.
        """
        LAYOUT = [[sg.Text(text=error_message)], [sg.Button(button_text="Ok")]]

        modal: Window = Window(title=title, layout=LAYOUT, modal=True)

        while True:
            event = modal.read(timeout=0)
            if (event == Event.WINDOW_CLOSED, Event.CONFIRMATION_MODAL_OK):
                modal.close()
                break

    def run_concurrent(self, on_event: Callable[[str], None] = lambda event: None):
        """
            Args:
                `on_event (Callable[[str], None], optional)`: Called with the name of the event whenever an event occurs.
        """
        self.__main_window: Window = self._create_main_window()
        self.__main_window.read(timeout=0)

        self._do_things_before_event_loop_starts()

        while (self.__main_window):
            event: str = self.__main_window.read(timeout=0)
            event: str = self._handle_event_before_client_on_event(event)

            on_event(event)

            if (event == Event.WINDOW_CLOSED):
                self.__close_main_window()

        self._do_things_after_event_loop_ends()

    def __close_main_window(self):
        if (self.__main_window):
            self.__main_window.close()
            self.__main_window = None

    # Helper methods for child classes
    def _hide(self):
        self.__main_window.hide()

    def _unhide(self):
        self.__main_window.un_hide()

    def _update_element(self, element: str, *update_args, **update_kwargs):
        self.__main_window[element].update(*update_args, **update_kwargs)

    def _create_gui_rows(self, *rows: Tuple[List[sg.Element]]) -> List[List[sg.Element]]:
        gui_rows: List[List[sg.Element]] = []
        util.foreach(rows, lambda row: gui_rows.append(row))
        return gui_rows

    def _element_is_enabled(self, element: str) -> bool:
        return not self.__main_window[element].Disabled

    def _get_element_value(self, element: str) -> Any:
        return self.__main_window[element].get()

    def _fill_input_fields(self, values: Dict[str, Any]):
        self.__main_window.fill(values)

    # Methods the child class can/shold override

    def _do_stuff_on_delete(self):
        pass

    def _do_things_before_event_loop_starts(self):
        pass

    def _handle_event_before_client_on_event(self, event: str) -> str:
        return event

    def _do_things_after_event_loop_ends(self):
        pass

    def _create_main_window(self) -> Window:
        pass
