from typing import Any, List
import PySimpleGUI as sg
from pynput import keyboard

import python.gui.audio_visualizer.audio_view as audio_view
import python.gui.styling as styling

class Element(audio_view.Element):
    pass

class _Element(audio_view._Element):
    CURRENT_AUDIO_PLAYING_MESSAGE = "current_audio_playing_message"
    SHUFFLE_PLAY_AUDIO_BUTTON = "shuffle_play_audio_button"
    PREVIOUS_AUDIO_BUTTON = "previous_audio_button"
    PAUSE_AUDIO_BUTTON = "pause_audio_button"
    RESUME_AUDIO_BUTTON = "resume_audio_button"
    STOP_AUDIO_BUTTON = "stop_audio_button"
    NEXT_AUDIO_BUTTON = "next_audio_button"
    RUNTIME_TEXT = "runtime_text"
    SELECT_AUDIO_DIRECTORY_BUTTON = "select_audio_directory_button"
    SELECTED_AUDIO_DIRECTORY_TEXT = "the_directory_path_selected_with_the_{}".format(SELECT_AUDIO_DIRECTORY_BUTTON)

class Event(audio_view.Event):
    SHUFFLE_PLAY = _Element.SHUFFLE_PLAY_AUDIO_BUTTON
    PREVIOUS_AUDIO = _Element.PREVIOUS_AUDIO_BUTTON
    PAUSE_AUDIO = _Element.PAUSE_AUDIO_BUTTON
    RESUME_AUDIO = _Element.RESUME_AUDIO_BUTTON
    STOP_AUDIO = _Element.STOP_AUDIO_BUTTON
    NEXT_AUDIO = _Element.NEXT_AUDIO_BUTTON


class AudioOutView(audio_view.AudioView):
    def __init__(self):
        audio_view.AudioView.__init__(self)
        self.__keyboard_listener_thread = None
        self.__keyboard_induced_ui_event:str = None

    def _do_stuff_on_delete(self):
        self.__stop_keyboard_listener_thread()

    def __stop_keyboard_listener_thread(self):
        if (self.__keyboard_listener_thread):
            self.__keyboard_listener_thread.stop()
            self.__keyboard_listener_thread = None

    def _get_rows_above_default_visualizer_and_led_selection(self)->List[List[sg.Element]]:
        CURRENT_AUDIO_FONT = ("Courier New", 20)

        return self._create_gui_rows([sg.Text(text="No audio currently playing.", key=_Element.CURRENT_AUDIO_PLAYING_MESSAGE, font=CURRENT_AUDIO_FONT)],
                                     [sg.Button(button_text="Shuffle Play", disabled=False, key=_Element.SHUFFLE_PLAY_AUDIO_BUTTON, font=styling.BUTTON_FONT),
                                      sg.Button(button_text="Previous (<<)", disabled=True, key=_Element.PREVIOUS_AUDIO_BUTTON, font=styling.BUTTON_FONT),
                                      sg.Button(button_text="Pause (||)", disabled=True, key=_Element.PAUSE_AUDIO_BUTTON, font=styling.BUTTON_FONT),
                                      sg.Button(button_text="Resume (>)", disabled=True, key=_Element.RESUME_AUDIO_BUTTON, font=styling.BUTTON_FONT),
                                      sg.Button(button_text="Stop ([])", disabled=True, key=_Element.STOP_AUDIO_BUTTON, font=styling.BUTTON_FONT),
                                      sg.Button(button_text="Next (>>)", disabled=True, key=_Element.NEXT_AUDIO_BUTTON, font=styling.BUTTON_FONT),
                                      sg.Text(text="", key=_Element.RUNTIME_TEXT, font=styling.INPUT_LABEL_FONT)])

    def _get_elements_to_the_right_of_default_visualizer_and_led_selection(self)->List[sg.Element]:
        return [sg.In(disabled=True, key=_Element.SELECTED_AUDIO_DIRECTORY_TEXT, font=styling.INPUT_LABEL_FONT),
                sg.FolderBrowse(button_text="Select Audio Folder", key=_Element.SELECT_AUDIO_DIRECTORY_BUTTON,
                                target=_Element.SELECTED_AUDIO_DIRECTORY_TEXT, font=styling.BUTTON_FONT)]

    def _do_things_before_event_loop_starts(self):
        self.__start_keyboard_listener_thread()

    def __start_keyboard_listener_thread(self):
        self.__stop_keyboard_listener_thread()
        self.__keyboard_listener_thread = keyboard.Listener(on_press=self.__on_keyboard_press, on_release=None)
        self.__keyboard_listener_thread.start()

    def __on_keyboard_press(self, keyboard_event:keyboard.Key):
        try:
            if (keyboard_event == keyboard.Key.media_play_pause):
                if (self._element_is_enabled(_Element.RESUME_AUDIO_BUTTON)):
                    self.__keyboard_induced_ui_event = Event.RESUME_AUDIO

                elif (self._element_is_enabled((_Element.PAUSE_AUDIO_BUTTON))):
                    self.__keyboard_induced_ui_event = Event.PAUSE_AUDIO

                elif (self._element_is_enabled(_Element.SHUFFLE_PLAY_AUDIO_BUTTON)):
                    self.__keyboard_induced_ui_event = Event.SHUFFLE_PLAY

            elif (keyboard_event == keyboard.Key.media_next):
                if (self._element_is_enabled(_Element.NEXT_AUDIO_BUTTON)):
                    self.__keyboard_induced_ui_event = Event.NEXT_AUDIO

            elif (keyboard_event == keyboard.Key.media_previous):
                if (self._element_is_enabled(_Element.PREVIOUS_AUDIO_BUTTON)):
                    self.__keyboard_induced_ui_event = Event.PREVIOUS_AUDIO

        except AttributeError:
            pass # Some keys don't have a .value attribute

    def _handle_event_before_client_on_event(self, event:str)->str:
        if (self.__keyboard_induced_ui_event and event == Event.TIMEOUT_EVENT):
            event = self.__keyboard_induced_ui_event
            self.__keyboard_induced_ui_event = None
        return event

    def get_audio_directory(self):
        return self._get_element_value(_Element.SELECTED_AUDIO_DIRECTORY_TEXT)

    def set_current_audio_playing_message(self, current_audio_playing_message:str):
        self._update_element(_Element.CURRENT_AUDIO_PLAYING_MESSAGE, current_audio_playing_message)

    def set_runtime_message(self, runtime_message:str):
        self._update_element(_Element.RUNTIME_TEXT, runtime_message)

    def set_audio_paused_state(self):
        self._update_element(_Element.SETTINGS_BUTTON, disabled=True)
        self._update_element(_Element.SHUFFLE_PLAY_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.NEXT_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.PREVIOUS_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.STOP_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.PAUSE_AUDIO_BUTTON, disabled=True)
        self._update_element(_Element.RESUME_AUDIO_BUTTON, disabled=False)

        self._update_element(_Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=True)
        self._update_element(_Element.SERIAL_LED_STRIP_CHECKBOX, disabled=True)
        self._update_element(_Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=True)
        self._update_element(_Element.SELECT_AUDIO_DIRECTORY_BUTTON, disabled=True)

    def set_audio_playing_state(self):
        self._update_element(_Element.SETTINGS_BUTTON, disabled=True)
        self._update_element(_Element.SHUFFLE_PLAY_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.NEXT_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.PREVIOUS_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.STOP_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.PAUSE_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.RESUME_AUDIO_BUTTON, disabled=True)

        self._update_element(_Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=True)
        self._update_element(_Element.SERIAL_LED_STRIP_CHECKBOX, disabled=True)
        self._update_element(_Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=True)
        self._update_element(_Element.SELECT_AUDIO_DIRECTORY_BUTTON, disabled=True)

    def set_audio_stopped_state(self):
        self._update_element(_Element.SETTINGS_BUTTON, disabled=False)
        self._update_element(_Element.SHUFFLE_PLAY_AUDIO_BUTTON, disabled=False)
        self._update_element(_Element.NEXT_AUDIO_BUTTON, disabled=True)
        self._update_element(_Element.PREVIOUS_AUDIO_BUTTON, disabled=True)
        self._update_element(_Element.STOP_AUDIO_BUTTON, disabled=True)
        self._update_element(_Element.PAUSE_AUDIO_BUTTON, disabled=True)
        self._update_element(_Element.RESUME_AUDIO_BUTTON, disabled=True)

        self._update_element(_Element.SELECT_VISUALIZER_TYPE_DROPDOWN, disabled=False)
        self._update_element(_Element.SERIAL_LED_STRIP_CHECKBOX, disabled=False)
        self._update_element(_Element.GRAPHIC_LED_STRIP_CHECKBOX, disabled=False)
        self._update_element(_Element.SELECT_AUDIO_DIRECTORY_BUTTON, disabled=False)