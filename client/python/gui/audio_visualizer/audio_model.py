from typing import Callable
import pyaudio


class State:
    PLAYING = "playing"
    PAUSED = "paused"

class AudioModel:
    def __init__(self):
        self._audio_player_maker:pyaudio.PyAudio = pyaudio.PyAudio()
        self._audio_player:pyaudio.Stream = None
        self._audio_chunk:bytes = b''

    def __del__(self):
        self._close_audio_player()
        self._terminate_audio_player_maker()
        self._do_stuff_on_delete()

    def _close_audio_player(self):
        if (self._audio_player):
            self._audio_player.close()
            self._audio_player = None

    def _terminate_audio_player_maker(self):
        if (self._audio_player_maker):
            self._audio_player_maker.terminate()

    def update(self, milliseconds_of_audio_to_read:int, on_audio_read:Callable):
        if (self.is_state(State.PLAYING)):
            self._audio_chunk:bytes = self._read_milliseconds(milliseconds_of_audio_to_read)
            self._do_stuff_before_client_on_read()
            on_audio_read(self._audio_chunk)
            self._do_stuff_after_client_on_read()

    def is_state(self, state:str)->bool:
        if (state == State.PLAYING):
            return (isinstance(self._audio_player, pyaudio.Stream) and self._audio_player.is_active())

        elif (state == State.PAUSED):
            return (isinstance(self._audio_player, pyaudio.Stream) and self._audio_player.is_stopped())

        return self._is_state(state)

    def pause(self):
        if (self._audio_player):
            self._audio_player.stop_stream()

    def resume(self):
        if (self._audio_player):
            self._audio_player.start_stream()

    def milliseconds_to_number_of_frames(self, milliseconds:int)->int:
        return int(self.__get_number_of_frames_per_millisecond() * milliseconds)

    def number_of_frames_to_milliseconds(self, number_of_frames:int)->int:
        return int((1/self.__get_number_of_frames_per_millisecond()) * number_of_frames)

    def get_framerate(self)->int:
        return self._audio_player._rate

    def __get_number_of_frames_per_millisecond(self)->int:
        number_of_milliseconds_per_second = 1000
        return self.get_framerate() / number_of_milliseconds_per_second


    # Methods the child class can/should override
    def _do_stuff_on_delete(self):
        pass

    def _read_milliseconds(self, milliseconds_of_audio_to_read:int)->bytes:
        pass

    def _do_stuff_before_client_on_read(self):
        pass

    def _do_stuff_after_client_on_read(self):
        pass

    def _is_state(self, state:str)->bool:
        return False


    # Helper methods the child class can use
    def _initialize_audio_player(self, *stream_args, **stream_kwargs):
        self._close_audio_player()
        self._audio_player = self._audio_player_maker.open(*stream_args, **stream_kwargs)