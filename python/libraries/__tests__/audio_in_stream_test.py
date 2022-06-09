import unittest
from unittest.mock import MagicMock, patch

from libraries.audio_in_stream import ProductionAudioInStream


class AudioInStreamTestCase(unittest.TestCase):
    FRAME_RATE = 44100
    NUMBER_OF_CHANNELS = 2
    INPUT_SOURCE = 'Microphone'

    DEFAULT_INPUT_DEVICE_INFO = {'defaultSampleRate': FRAME_RATE, 'maxInputChannels': NUMBER_OF_CHANNELS, 'name': INPUT_SOURCE}

    def setUp(self):
        self.__pyaudio_patch = patch('libraries.audio_in_stream.PyAudio')

        self.addCleanup(self.__pyaudio_patch.stop)

        self.pyaudio_mock = self.__pyaudio_patch.start()

        self.pyaudio_instance_mock = self.pyaudio_mock()

        self.pyaudio_instance_mock.get_default_input_device_info.return_value = self.DEFAULT_INPUT_DEVICE_INFO

        self.audio_stream_instance_mock = self.pyaudio_instance_mock.open.return_value = MagicMock()

        self.pyaudio_mock.reset_mock()

        self.production_audio_in_stream = ProductionAudioInStream()


class TestOpen(AudioInStreamTestCase):
    def test_open(self):
        self.production_audio_in_stream.open()

        self.pyaudio_instance_mock.open.assert_called_once()

    def test_open_when_no_default_input_device_is_detected(self):
        self.pyaudio_instance_mock.get_default_input_device_info.side_effect = OSError()

        with self.assertRaises(OSError):
            self.production_audio_in_stream.open()


class TestAudioInStreamWhenOpenWasNotCalled(AudioInStreamTestCase):
    def test_input_source(self):
        with self.assertRaises(ValueError):
            self.production_audio_in_stream.input_source

    def test_is_open_true(self):
        self.assertFalse(self.production_audio_in_stream.is_open())

    def test_sample_rate(self):
        with self.assertRaises(ValueError):
            self.production_audio_in_stream.sample_rate

    def test_close(self):
        self.production_audio_in_stream.close()

    def test_read(self):
        with self.assertRaises(ValueError):
            NUMBER_OF_FRAMES = 10
            self.production_audio_in_stream.read(NUMBER_OF_FRAMES)


class TestAudioInStreamAfterCallingOpen(AudioInStreamTestCase):
    def setUp(self):
        super().setUp()

        self.production_audio_in_stream.open()

    def test_input_source(self):
        INPUT_SOURCE = self.production_audio_in_stream.input_source

        self.assertEqual(INPUT_SOURCE, self.INPUT_SOURCE)

    def test_input_source_when_input_device_not_found(self):
        self.pyaudio_instance_mock.get_default_input_device_info.side_effect = OSError()

        with self.assertRaises(OSError):
            self.production_audio_in_stream.input_source

    def test_is_open_true(self):
        self.audio_stream_instance_mock.is_active.return_value = True

        self.assertTrue(self.production_audio_in_stream.is_open())

    def test_is_open_false(self):
        self.audio_stream_instance_mock.is_active.return_value = False

        self.assertFalse(self.production_audio_in_stream.is_open())

    def test_is_open_when_input_device_not_found(self):
        self.audio_stream_instance_mock.is_active.side_effect = OSError()

        self.assertFalse(self.production_audio_in_stream.is_open())

    def test_sample_rate(self):
        FRAMES_PER_SECOND = self.production_audio_in_stream.sample_rate

        self.assertEqual(FRAMES_PER_SECOND, self.FRAME_RATE)

    def test_close(self):
        self.production_audio_in_stream.close()

        self.pyaudio_instance_mock.terminate.assert_called_once()
        self.audio_stream_instance_mock.close.assert_called_once()

    def test_read(self):
        NUMBER_OF_FRAMES = 10

        EXPECTED_RETURN_VALUE = b'hello'

        self.audio_stream_instance_mock.read.return_value = EXPECTED_RETURN_VALUE

        RETURN_VALUE = self.production_audio_in_stream.read(NUMBER_OF_FRAMES)

        self.audio_stream_instance_mock.read.assert_called_once_with(NUMBER_OF_FRAMES)

        self.assertEqual(RETURN_VALUE, EXPECTED_RETURN_VALUE)

    def test_read_when_input_device_not_found(self):
        self.audio_stream_instance_mock.read.side_effect = OSError()

        with self.assertRaises(OSError):
            NUMBER_OF_FRAMES = 10
            self.production_audio_in_stream.read(NUMBER_OF_FRAMES)
