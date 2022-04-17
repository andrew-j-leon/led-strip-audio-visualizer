import gui.audio_visualizer.audio_model as audio_model
import pyaudio
import util


class NoDefaultInputDeviceDetectedError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class State(audio_model.State):
    pass


class AudioInModel(audio_model.AudioModel):
    def __init__(self):
        audio_model.AudioModel.__init__(self)
        self.__set_default_input_device()

    def __set_default_input_device(self):
        default_input_device_info: dict = self._audio_player_maker.get_default_input_device_info()

        if (util.is_empty(default_input_device_info)):
            raise NoDefaultInputDeviceDetectedError("There is no default input device set on this machine.")

        print(default_input_device_info)

        self._initialize_audio_player(format=pyaudio.paInt16, channels=default_input_device_info["maxInputChannels"],
                                      rate=int(default_input_device_info["defaultSampleRate"]), input=True)

        self._audio_player.stop_stream()

    def _read_milliseconds(self, milliseconds_of_audio_to_read: int) -> bytes:
        return self._audio_player.read(self.milliseconds_to_number_of_frames(milliseconds_of_audio_to_read))

    def get_current_input_device_name(self) -> str:
        return self._audio_player_maker.get_default_input_device_info()["name"]
