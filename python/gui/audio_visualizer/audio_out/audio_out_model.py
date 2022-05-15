import os
import random
import shutil
from pathlib import Path
from typing import Callable, List, Union
from wave import Wave_read

import pyaudio
import util.util as util
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError, CouldntEncodeError


class NoValidAudioFilesFoundException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class State:
    PLAYING = "playing"
    PAUSED = "paused"
    SHUFFLE_PLAYING = "shuffle_playing"
    STOPPED = "stopped"


_VALID_AUDIO_FILE_EXTENSIONS = [".wav", ".mp3", ".m4a", ".pcm", ".aiff", ".acc", ".ogg", ".wma", ".flac", ".alac", ".wma"]
_AUDIO_FILE_DIRECTORY = '.audio_file'
_MAX_TIME_THAT_PREVIOUS_BUTTON_WILL_GO_TO_PREVIOUS_OTHERWISE_IT_WILL_RESTART_CURRENT_AUDIO = 7000  # milliseconds


def get_valid_extensions() -> List[str]:
    return _VALID_AUDIO_FILE_EXTENSIONS


def is_valid_audio_directory(audio_directory: str) -> bool:
    return util.directory_contains_at_least_one_file_with_extension(audio_directory, get_valid_extensions())


class AudioOutModel:
    def __init__(self):
        self._audio_player_maker: pyaudio.PyAudio = pyaudio.PyAudio()
        self._audio_player: pyaudio.Stream = None
        self._audio_chunk: bytes = b''

        self.__audio_stream: Wave_read = None
        self.__playlist: List[str] = []

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

    def update(self, milliseconds_of_audio_to_read: int, on_audio_read: Callable):
        if (self.is_state(State.PLAYING)):
            self._audio_chunk: bytes = self._read_milliseconds(milliseconds_of_audio_to_read)
            self._do_stuff_before_client_on_read()
            on_audio_read(self._audio_chunk)
            self._do_stuff_after_client_on_read()

    def is_state(self, state: str) -> bool:
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

    def milliseconds_to_number_of_frames(self, milliseconds: int) -> int:
        return int(self.__get_number_of_frames_per_millisecond() * milliseconds)

    def number_of_frames_to_milliseconds(self, number_of_frames: int) -> int:
        return int((1 / self.__get_number_of_frames_per_millisecond()) * number_of_frames)

    def get_framerate(self) -> int:
        return self._audio_player._rate

    def __get_number_of_frames_per_millisecond(self) -> int:
        number_of_milliseconds_per_second = 1000
        return self.get_framerate() / number_of_milliseconds_per_second

    # Methods the child class can/should override

    def _do_stuff_on_delete(self):
        pass

    def _read_milliseconds(self, milliseconds_of_audio_to_read: int) -> bytes:
        pass

    def _do_stuff_before_client_on_read(self):
        pass

    def _do_stuff_after_client_on_read(self):
        pass

    def _is_state(self, state: str) -> bool:
        return False

    # Helper methods the child class can use

    def _initialize_audio_player(self, *stream_args, **stream_kwargs):
        self._close_audio_player()
        self._audio_player = self._audio_player_maker.open(*stream_args, **stream_kwargs)

    def _do_stuff_on_delete(self):
        self.__close_audio_stream()
        self.__delete_wav_file_directory()

    def __close_audio_stream(self):
        if (self.__audio_stream):
            self.__audio_stream.close()
            self.__audio_stream = None

    def __delete_wav_file_directory(self):
        if (os.path.isdir(_AUDIO_FILE_DIRECTORY)):
            shutil.rmtree(_AUDIO_FILE_DIRECTORY)

    def _is_state(self, state: str) -> bool:
        if (state == State.SHUFFLE_PLAYING):
            return (isinstance(self._audio_player, pyaudio.Stream) and self._audio_player.is_active())
        elif (state == State.STOPPED):
            return not self.__audio_stream

    def insert_playlist(self, audio_directory: str):
        if (is_valid_audio_directory(audio_directory)):
            self.__close_audio_stream()
            self._close_audio_player()
            self.__set_playlist(audio_directory)
            self.__playlist_index: int = 0

    def __set_playlist(self, audio_directory: str):
        self.__playlist.clear()
        for file_name in os.listdir(audio_directory):
            if (util.filename_ends_with_extension(file_name, _VALID_AUDIO_FILE_EXTENSIONS)):
                self.__playlist.append(os.path.join(audio_directory, file_name))

    def _read_milliseconds(self, milliseconds_of_audio_to_read: int) -> bytes:
        return self.__audio_stream.readframes(self.milliseconds_to_number_of_frames(milliseconds_of_audio_to_read))

    def _do_stuff_before_client_on_read(self):
        if (util.is_empty(self._audio_chunk)):
            self.__setup_next_song()

    def _do_stuff_after_client_on_read(self):
        self._audio_player.write(self._audio_chunk)

    def __setup_next_song(self):
        self.__move_playlist_index_to_next_audio()
        self.__insert_audio_stream_into_audio_player()

    def __move_playlist_index_to_next_audio(self):
        if (self.__playlist_index + 1 < len(self.__playlist)):
            self.__playlist_index += 1
        else:
            self.__playlist_index = 0

    def __move_playlist_index_to_previous_audio(self):
        if (self.__playlist_index - 1 >= 0):
            self.__playlist_index -= 1
        else:
            self.__playlist_index = len(self.__playlist) - 1

    def __insert_audio_stream_into_audio_player(self):
        self.__close_audio_stream()

        file_path = self.__get_next_valid_audio_file_path_and_remove_invalid_audio_file_paths()
        if (not file_path):
            self.stop()
            raise NoValidAudioFilesFoundException("No files in the given directory are valid audio files.")

        self.__audio_stream: Wave_read = Wave_read(file_path)
        self._initialize_audio_player(format=self._audio_player_maker.get_format_from_width(self.__audio_stream.getsampwidth()),
                                      channels=self.__audio_stream.getnchannels(),
                                      rate=self.__audio_stream.getframerate(),
                                      output=True)

    def __get_next_valid_audio_file_path_and_remove_invalid_audio_file_paths(self) -> Union[str, None]:
        file_path = None
        while (not file_path and not util.is_empty(self.__playlist)):
            file_path = self.__convert_and_store_as_wav(self.__playlist[self.__playlist_index])
            if (not file_path):
                self.__remove_current_audio_from_playlist()
        return file_path

    def __convert_and_store_as_wav(self, file_path: str) -> Union[str, None]:
        try:
            self.__create_an_empty_wav_file_directory()

            file_name = os.path.basename(file_path)

            new_file_name = Path(file_name).with_suffix(".wav")
            new_file_path = os.path.join(_AUDIO_FILE_DIRECTORY, new_file_name)

            AudioSegment.from_file(file_path).export(new_file_path, format="wav")
            return new_file_path

        except (CouldntDecodeError, CouldntEncodeError):
            return None

    def __remove_current_audio_from_playlist(self):
        self.__playlist.pop(self.__playlist_index)
        if (self.__playlist_index >= len(self.__playlist)):
            self.__playlist_index = 0

    def __create_an_empty_wav_file_directory(self):
        self.__delete_wav_file_directory()
        os.mkdir(_AUDIO_FILE_DIRECTORY)

    def shuffle_play(self):
        if (not util.is_empty(self.__playlist)):
            self.__shuffle_playlist()
            self.__playlist_index = 0
            self.__insert_audio_stream_into_audio_player()

    def __shuffle_playlist(self):
        random.shuffle(self.__playlist)

    def previous(self):
        if (self.__playlist_index == 0 or self.get_milliseconds_since_start() > _MAX_TIME_THAT_PREVIOUS_BUTTON_WILL_GO_TO_PREVIOUS_OTHERWISE_IT_WILL_RESTART_CURRENT_AUDIO):
            self.__insert_audio_stream_into_audio_player()
        else:
            self.__move_playlist_index_to_previous_audio()
            self.__insert_audio_stream_into_audio_player()

    def get_milliseconds_since_start(self) -> int:
        return int(self.number_of_frames_to_milliseconds(self.__audio_stream.tell()))

    def stop(self):
        self.__close_audio_stream()
        self._close_audio_player()
        self.__delete_wav_file_directory()

    def next(self):
        self.__move_playlist_index_to_next_audio()
        self.__insert_audio_stream_into_audio_player()

    def seek(self, milliseconds_since_start: int):
        milliseconds_since_start = min(self.get_total_audio_length(), max(0, milliseconds_since_start))
        self.__audio_stream.setpos(self.milliseconds_to_number_of_frames(milliseconds_since_start))

    def get_total_audio_length(self) -> int:
        return int(self.number_of_frames_to_milliseconds(self.__audio_stream.getnframes()))

    def get_current_audio_name(self) -> str:
        if (self.is_state(State.PLAYING) or self.is_state(State.PAUSED)):
            return Path(self.__playlist[self.__playlist_index]).stem
        return None
