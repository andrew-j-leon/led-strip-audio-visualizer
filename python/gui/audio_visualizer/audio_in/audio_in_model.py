from typing import Callable

import pyaudio
import util.util as util


class State:
    PLAYING = "playing"
    PAUSED = "paused"


class NoDefaultInputDeviceDetectedError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class AudioInModel:
    def __init__(self):
        self._audio_player_maker = pyaudio.PyAudio()
        self._audio_player: pyaudio.Stream = None
        self._audio_chunk: bytes = b''

        self.__set_default_input_device()

    def __del__(self):
        self.__close_audio_player()

        if (self._audio_player_maker is not None):
            self._audio_player_maker.terminate()

    def update(self, milliseconds_of_audio_to_read: int, on_audio_read: Callable):
        if (self.is_state(State.PLAYING)):
            number_of_frames = self.milliseconds_to_number_of_frames(milliseconds_of_audio_to_read)

            self._audio_chunk: bytes = self._audio_player.read(number_of_frames)
            on_audio_read(self._audio_chunk)

    def is_state(self, state: str) -> bool:
        if (state == State.PLAYING):
            return (isinstance(self._audio_player, pyaudio.Stream) and self._audio_player.is_active())

        elif (state == State.PAUSED):
            return (isinstance(self._audio_player, pyaudio.Stream) and self._audio_player.is_stopped())

        return False

    def milliseconds_to_number_of_frames(self, milliseconds: int) -> int:
        return int(self.__get_number_of_frames_per_millisecond() * milliseconds)

    def pause(self):
        if (self._audio_player):
            self._audio_player.stop_stream()

    def resume(self):
        if (self._audio_player):
            self._audio_player.start_stream()

    def number_of_frames_to_milliseconds(self, number_of_frames: int) -> int:
        return int((1 / self.__get_number_of_frames_per_millisecond()) * number_of_frames)

    def get_framerate(self) -> int:
        return self._audio_player._rate

    def get_current_input_device_name(self) -> str:
        return self._audio_player_maker.get_default_input_device_info()["name"]

    def __get_number_of_frames_per_millisecond(self) -> int:
        number_of_milliseconds_per_second = 1000
        return self.get_framerate() / number_of_milliseconds_per_second

    def __set_default_input_device(self):
        def init_audio_player(*stream_args, **stream_kwargs):
            self.__close_audio_player()
            self._audio_player = self._audio_player_maker.open(*stream_args, **stream_kwargs)

        default_input_device_info: dict = self._audio_player_maker.get_default_input_device_info()

        if (util.is_empty(default_input_device_info)):
            raise NoDefaultInputDeviceDetectedError("There is no default input device set on this machine.")

        init_audio_player(format=pyaudio.paInt16, channels=default_input_device_info["maxInputChannels"],
                          rate=int(default_input_device_info["defaultSampleRate"]), input=True)

        self._audio_player.stop_stream()

    def __close_audio_player(self):
        if (self._audio_player):
            self._audio_player.close()
            self._audio_player = None
