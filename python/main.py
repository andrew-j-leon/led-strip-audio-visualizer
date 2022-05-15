from typing import Callable

import gui.audio_visualizer.audio_in.audio_in_controller as audio_in_controller
import gui.audio_visualizer.audio_out.audio_out_controller as audio_out_controller
import PySimpleGUI as sg
from gui.window import Window
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED


class Element:
    CONFIRMATION_MODAL_OK_BUTTON = "error_modal_ok_button"
    AUDIO_OUT_BUTTON = "audio_out_button"
    AUDIO_IN_BUTTON = "audio_in_button"


class Event:
    WINDOW_CLOSED = WINDOW_CLOSED
    TIMEOUT_EVENT = TIMEOUT_EVENT
    CONFIRMATION_MODAL_OK = Element.CONFIRMATION_MODAL_OK_BUTTON
    START_AUDIO_OUT_PLAYER = Element.AUDIO_OUT_BUTTON
    START_AUDIO_IN_PLAYER = Element.AUDIO_IN_BUTTON


class MainController:
    def __init__(self):
        self.view = MainView()
        self.__audio_controller = None

    def start(self):
        self.view.run_concurrent(self.__on_gui_event)

    def __on_gui_event(self, event: str):
        if (event == Event.START_AUDIO_IN_PLAYER):
            self.view.set_audio_player_is_running_state()
            self.__audio_controller = audio_in_controller.AudioInController()
            self.__audio_controller.start()
            self.__delete_audio_controller()
            self.view.set_audio_is_stopped_state()

        elif (event == Event.START_AUDIO_OUT_PLAYER):
            self.view.set_audio_player_is_running_state()
            self.__audio_controller = audio_out_controller.AudioOutController()
            self.__audio_controller.start()
            self.__delete_audio_controller()
            self.view.set_audio_is_stopped_state()

    def __delete_audio_controller(self):
        if (self.__audio_controller):
            del self.__audio_controller
            self.__audio_controller = None


class MainView:
    def __init__(self):
        self.__main_window: Window = None

    def __del__(self):
        self.__close_main_window()

    def run_concurrent(self, on_event: Callable[[str], None] = lambda event: None):
        '''
            Args:
                `on_event (Callable[[str], None], optional)`: Called with the name of the event whenever an event occurs.
        '''
        self.__main_window: Window = self.__create_main_window()
        self.__main_window.read(timeout=0)

        while (self.__main_window):
            event: str = self.__main_window.read(timeout=0)

            on_event(event)

            if (event == Event.WINDOW_CLOSED):
                self.__close_main_window()

    def set_audio_is_stopped_state(self):
        self.__update_element(Element.AUDIO_IN_BUTTON, disabled=False)
        self.__update_element(Element.AUDIO_OUT_BUTTON, disabled=False)
        self.__main_window.un_hide()

    def set_audio_player_is_running_state(self):
        self.__update_element(Element.AUDIO_IN_BUTTON, disabled=True)
        self.__update_element(Element.AUDIO_OUT_BUTTON, disabled=True)
        self.__main_window.hide()

    def __close_main_window(self):
        if (self.__main_window):
            self.__main_window.close()
            self.__main_window = None

    def __update_element(self, element: str, *update_args, **update_kwargs):
        self.__main_window[element].update(*update_args, **update_kwargs)

    def __create_main_window(self) -> Window:
        BUTTON_FONT = ("Courier New", 24)

        MAIN_WINDOW_LAYOUT = [[sg.Button(button_text="Audio Out", key=Element.AUDIO_OUT_BUTTON, font=BUTTON_FONT, disabled=False),
                               sg.Button(button_text="Audio In", key=Element.AUDIO_IN_BUTTON, font=BUTTON_FONT, disabled=False)]]

        return Window("Select Audio Player", layout=MAIN_WINDOW_LAYOUT, resizable=True, element_padding=(0, 0), margins=(0, 0),
                      titlebar_background_color="#000917", titlebar_text_color="#8a8a8a")


main_controller = MainController()
main_controller.start()
