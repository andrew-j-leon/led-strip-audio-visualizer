import gui.audio_visualizer.audio_controller as audio_controller

import gui.audio_visualizer.audio_in.audio_in_model as audio_in_model
import gui.audio_visualizer.audio_in.audio_in_view as audio_in_view


class AudioInController(audio_controller.AudioController):
    def __init__(self):
        audio_controller.AudioController.__init__(self, audio_view=audio_in_view.AudioInView(), audio_player=audio_in_model.AudioInModel())

    def _ui_event_is_valid(self, event: str) -> bool:
        if (event == audio_in_view.Event.PAUSE_AUDIO):
            return self.__pause_audio_event_is_valid()

        elif (event == audio_in_view.Event.RESUME_AUDIO):
            return self.__resume_audio_event_is_valid()

        return event in (audio_in_view.Event.WINDOW_CLOSED, audio_in_view.Event.TIMEOUT_EVENT, audio_in_view.Event.OPEN_SETTINGS_MODAL)

    def _handle_valid_ui_event(self, event: str):
        if (event == audio_in_view.Event.PAUSE_AUDIO):
            self._audio_player.pause()
            self._delete_visualizer()
            self._view.set_audio_paused_state()

        elif (event == audio_in_view.Event.RESUME_AUDIO):
            self._view.set_current_input_source_message(self.__get_current_input_source_message())
            self._initialize_visualizer()
            self._audio_player.resume()
            self._view.set_audio_playing_state()

    def _handle_invalid_ui_event(self, event: str):
        if (event not in (audio_in_view.Event.PAUSE_AUDIO, audio_in_view.Event.RESUME_AUDIO)):
            self._view.display_confirmation_modal("Error", "Did not recognize the event {}.".format(event))

    def __pause_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_in_model.State.PLAYING)

    def __resume_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_in_model.State.PAUSED)

    def __get_current_input_source_message(self) -> str:
        return "Input Source : {}".format(self._audio_player.get_current_input_device_name())
