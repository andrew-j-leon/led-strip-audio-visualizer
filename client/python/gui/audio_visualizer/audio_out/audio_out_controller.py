import os
import python.util.util as util

import python.gui.audio_visualizer.audio_controller as audio_controller

import python.gui.audio_visualizer.audio_out.audio_out_view as audio_out_view
import python.gui.audio_visualizer.audio_out.audio_out_model as audio_out_model


class AudioOutController(audio_controller.AudioController):
    def __init__(self):
        audio_controller.AudioController.__init__(self, audio_view=audio_out_view.AudioOutView(), audio_player=audio_out_model.AudioOutModel())

    def _on_audio_player_update(self, audio_chunk: bytes):
        self._update_visualizer(audio_chunk)
        self._view.set_runtime_message(self.__get_runtime_message())

        if (util.is_empty(audio_chunk)):
            self._view.set_audio_playing_state()
            self._view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

    def _ui_event_is_valid(self, event: str) -> bool:
        if (event == audio_out_view.Event.SHUFFLE_PLAY):
            return self.__shuffle_play_event_is_valid(self._view.get_audio_directory())

        elif (event == audio_out_view.Event.PREVIOUS_AUDIO):
            return self.__previous_audio_event_is_valid()

        elif (event == audio_out_view.Event.PAUSE_AUDIO):
            return self.__pause_audio_event_is_valid()

        elif (event == audio_out_view.Event.RESUME_AUDIO):
            return self.__resume_audio_event_is_valid()

        elif (event == audio_out_view.Event.STOP_AUDIO):
            return self.__stop_audio_event_is_valid()

        elif (event == audio_out_view.Event.NEXT_AUDIO):
            return self.__next_audio_event_is_valid()

        return event in (audio_out_view.Event.WINDOW_CLOSED, audio_out_view.Event.TIMEOUT_EVENT, audio_out_view.Event.OPEN_SETTINGS_MODAL)

    def _handle_valid_ui_event(self, event: str):
        try:
            if (event == audio_out_view.Event.SHUFFLE_PLAY):
                self._audio_player.insert_playlist(self._view.get_audio_directory())
                self._audio_player.shuffle_play()
                self._initialize_visualizer()
                self._view.set_audio_playing_state()
                self._view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

            elif (event == audio_out_view.Event.PREVIOUS_AUDIO):
                self._audio_player.previous()
                self._view.set_audio_playing_state()
                self._view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

            elif (event == audio_out_view.Event.PAUSE_AUDIO):
                self._audio_player.pause()
                self._view.set_audio_paused_state()

            elif (event == audio_out_view.Event.RESUME_AUDIO):
                self._audio_player.resume()
                self._view.set_audio_playing_state()

            elif (event == audio_out_view.Event.STOP_AUDIO):
                self._audio_player.stop()
                self._delete_visualizer()
                self._view.set_audio_stopped_state()
                self._view.set_runtime_message("")
                self._view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

            elif (event == audio_out_view.Event.NEXT_AUDIO):
                self._audio_player.next()
                self._view.set_audio_playing_state()
                self._view.set_current_audio_playing_message(self.__get_current_audio_playing_message())

        except audio_out_model.NoValidAudioFilesFoundException:
            self._view.display_confirmation_modal("Error", "No valid audio files were found in the directory.")

    def _handle_invalid_ui_event(self, event: str):
        if (event == audio_out_view.Event.SHUFFLE_PLAY):
            self.__handle_invalid_shuffle_event(self._view.get_audio_directory())

        elif (event not in (audio_out_view.Event.STOP_AUDIO, audio_out_view.Event.NEXT_AUDIO, audio_out_view.Event.PAUSE_AUDIO, audio_out_view.Event.RESUME_AUDIO)):
            self._view.display_confirmation_modal("Error", "Did not recognize the event : {}.".format(event))

    def __get_runtime_message(self):
        return (util.convert_milliseconds_to_hours_minutes_and_seconds(self._audio_player.get_milliseconds_since_start())
                + " / " + util.convert_milliseconds_to_hours_minutes_and_seconds(self._audio_player.get_total_audio_length()))

    def __get_current_audio_playing_message(self) -> str:
        current_audio_filename = self._audio_player.get_current_audio_name()
        if (current_audio_filename == None):
            return "No audio playing."
        return ("Playing : {}").format(os.path.basename(current_audio_filename))

    def __shuffle_play_event_is_valid(self, audio_directory: str):
        return audio_out_model.is_valid_audio_directory(audio_directory)

    def __previous_audio_event_is_valid(self):
        return (self._audio_player.is_state(audio_out_model.State.PLAYING) or self._audio_player.is_state(audio_out_model.State.PAUSED))

    def __pause_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_out_model.State.PLAYING)

    def __resume_audio_event_is_valid(self):
        return self._audio_player.is_state(audio_out_model.State.PAUSED)

    def __stop_audio_event_is_valid(self):
        return (self._audio_player.is_state(audio_out_model.State.PLAYING) or self._audio_player.is_state(audio_out_model.State.PAUSED))

    def __next_audio_event_is_valid(self):
        return (self._audio_player.is_state(audio_out_model.State.PLAYING) or self._audio_player.is_state(audio_out_model.State.PAUSED))

    def __handle_invalid_shuffle_event(self, audio_directory: str):
        if (not os.path.isdir(audio_directory)):
            self._view.display_confirmation_modal("Error", "The directory \"{}\" either does not exist or is not a directory.".format(audio_directory))

        elif (not util.have_read_permission(audio_directory)):
            self._view.display_confirmation_modal("Error", "You do not have read permission for the directory \"{}\".".format(audio_directory))

        elif (not audio_out_model.is_valid_audio_directory(audio_directory)):
            self._view.display_confirmation_modal("Error", "The directory \"{}\" has no files with supported audio files.".format(audio_directory))

        else:
            self._view.display_confirmation_modal("Error", "An unknown error occurred when processing the {} event.".format(audio_out_view.Event.SHUFFLE_PLAY))
