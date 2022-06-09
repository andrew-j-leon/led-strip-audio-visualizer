from abc import ABC, abstractmethod
from pyaudio import PyAudio, paInt16


class AudioInStream(ABC):
    @property
    @abstractmethod
    def input_source(self) -> str:
        pass

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        '''
            Returns:
                `int`: The audio sampling rate in frames per second.
        '''

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def read(self, number_of_frames: int) -> bytes:
        pass


class ProductionAudioInStream(AudioInStream):
    def open(self):
        try:
            self.__pyaudio = PyAudio()

            DEFAULT_INPUT_DEVICE_INFO = self.__pyaudio.get_default_input_device_info()

            self.__sample_rate = int(DEFAULT_INPUT_DEVICE_INFO["defaultSampleRate"])
            NUMBER_OF_CHANNELS = DEFAULT_INPUT_DEVICE_INFO["maxInputChannels"]
            FORMAT = paInt16
            INPUT = True

            self.__audio_stream = self.__pyaudio.open(self.__sample_rate, NUMBER_OF_CHANNELS, FORMAT, INPUT)

        except OSError:
            raise OSError("No default input device was found. Make sure your Operating System has a default input device set.")

    @property
    def input_source(self):
        try:
            DEFAULT_INPUT_DEVICE_INFO = self.__pyaudio.get_default_input_device_info()

            return DEFAULT_INPUT_DEVICE_INFO['name']

        except AttributeError:
            raise ValueError('No Audio In Stream was established. Did you remember to call open?')

        except OSError:
            raise OSError("No default input device was found. Make sure your Operating System has a default input device set.")

    def is_open(self):
        try:
            return self.__audio_stream.is_active()

        except (AttributeError, OSError):
            return False

    @property
    def sample_rate(self):
        try:
            return self.__sample_rate

        except AttributeError:
            raise ValueError('No Audio In Stream was established. Did you remember to call open?')

    def close(self):
        try:
            self.__pyaudio.terminate()

        except AttributeError:
            pass

        try:
            self.__audio_stream.close()

        except AttributeError:
            pass

    def read(self, number_of_frames):
        try:
            return self.__audio_stream.read(number_of_frames)

        except AttributeError:
            raise ValueError('No Audio In Stream was established. Did you remember to call open?')

        except OSError:
            raise OSError(f'Could not read from default input source.')
