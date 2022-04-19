from typing import List

import gui.audio_visualizer.audio_view as audio_view
import gui.styling as styling
import PySimpleGUI as sg


class Element(audio_view.Element):
    pass


class _Element(audio_view._Element):
    PAUSE_AUDIO_BUTTON = "pause_audio_button"
    RESUME_AUDIO_BUTTON = "resume_audio_button"

    CURRENT_INPUT_SOURCE_MESSAGE = "current_input_source_message"
    SELECT_INPUT_SOURCE_DROPDOWN = "select_input_source_dropdown"
    SELECT_INPUT_SOURCE_LABEL = "select_input_source_label"


class Event(audio_view.Event):
    PAUSE_AUDIO = _Element.PAUSE_AUDIO_BUTTON
    RESUME_AUDIO = _Element.RESUME_AUDIO_BUTTON


class AudioInView(audio_view.AudioView):
    def __init__(self):
        audio_view.AudioView.__init__(self)

    def _get_rows_above_default_visualizer_and_led_selection(self) -> List[List[sg.Element]]:
        CURRENT_INPUT_SOURCE_FONT = ("Courier New", 20)

        return self._create_gui_rows([sg.Text(text="No audio currently playing.", key=_Element.CURRENT_INPUT_SOURCE_MESSAGE, font=CURRENT_INPUT_SOURCE_FONT)],
                                     [sg.Button(button_text="Pause (||)", disabled=True, key=_Element.PAUSE_AUDIO_BUTTON, font=styling.BUTTON_FONT),
                                      sg.Button(button_text="Resume (>)", disabled=False, key=_Element.RESUME_AUDIO_BUTTON, font=styling.BUTTON_FONT)])

    def set_current_input_source_message(self, message: str):
        self._update_element(_Element.CURRENT_INPUT_SOURCE_MESSAGE, message)

    def set_audio_paused_state(self):
        self._update_element(_Element.SETTINGS_BUTTON, disabled=False)
        self._update_element(_Element.PAUSE_AUDIO_BUTTON, disabled=True)
        self._update_element(_Element.RESUME_AUDIO_BUTTON, disabled=False)

        self._update_element(_Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=False)
        self._update_element(_Element.SERIAL_LED_STRIP_CHECKBOX, disabled=False)
        self._update_element(_Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=False)

    def set_audio_playing_state(self):
        self._update_element(_Element.SETTINGS_BUTTON, disabled=True)
        self._update_element(_Element.PAUSE_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.RESUME_AUDIO_BUTTON, disabled=True)

        self._update_element(_Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=True)
        self._update_element(_Element.SERIAL_LED_STRIP_CHECKBOX, disabled=True)
        self._update_element(_Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=True)
