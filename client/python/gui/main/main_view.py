import PySimpleGUI as sg

import python.gui.view as view
from python.gui.window import Window


class Element(view.Element):
    pass


class _Element(view._Element):
    AUDIO_OUT_BUTTON = "audio_out_button"
    AUDIO_IN_BUTTON = "audio_in_button"


class Event(view.Event):
    START_AUDIO_OUT_PLAYER = _Element.AUDIO_OUT_BUTTON
    START_AUDIO_IN_PLAYER = _Element.AUDIO_IN_BUTTON


class MainView(view.View):
    def __init__(self):
        view.View.__init__(self)

    def _create_main_window(self) -> Window:
        BUTTON_FONT = ("Courier New", 24)

        MAIN_WINDOW_LAYOUT = [[sg.Button(button_text="Audio Out", key=_Element.AUDIO_OUT_BUTTON, font=BUTTON_FONT, disabled=False),
                               sg.Button(button_text="Audio In", key=_Element.AUDIO_IN_BUTTON, font=BUTTON_FONT, disabled=False)]]

        return Window("Select Audio Player", layout=MAIN_WINDOW_LAYOUT, resizable=True, element_padding=(0, 0), margins=(0, 0),
                      titlebar_background_color="#000917", titlebar_text_color="#8a8a8a")

    def set_audio_is_stopped_state(self):
        self._update_element(_Element.AUDIO_IN_BUTTON, disabled=False)
        self._update_element(_Element.AUDIO_OUT_BUTTON, disabled=False)
        self._unhide()

    def set_audio_player_is_running_state(self):
        self._update_element(_Element.AUDIO_IN_BUTTON, disabled=True)
        self._update_element(_Element.AUDIO_OUT_BUTTON, disabled=True)
        self._hide()
