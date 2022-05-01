import unittest
from typing import Iterable, List, Tuple

import numpy
import util.util as util
from led_strip.led_strip import LedStrip
from visualizer.spectrogram import Spectrogram


class FakeLedStrip(LedStrip):
    def __init__(self, number_of_groups: int = 1):
        self.__number_of_groups = number_of_groups

        self.__color_queue: List[Tuple[int, Tuple[int, int, int]]] = []
        self.group_colors: List[Tuple[int, int, int]] = [(0, 0, 0)] * number_of_groups

    @property
    def number_of_groups(self) -> int:
        return self.__number_of_groups

    @property
    def number_of_queued_colors(self) -> int:
        return len(self.__color_queue)

    def enqueue_rgb(self, group: int, rgb: Iterable[int]):
        self.__color_queue.append((group, rgb))

    def group_is_rgb(self, group: int, rgb: Iterable[int]) -> bool:
        return self.group_colors[group] == rgb

    def show_queued_colors(self):
        for queued_color in self.__color_queue:
            group, rgb = queued_color

            self.group_colors[group] = rgb

    def clear_queued_colors(self):
        self.__color_queue.clear()


class TestConstructor(unittest.TestCase):

    def test_constructor(self):
        frequency_range = (0, 2300)

        amplitude_rgbs = ([(13, 13, 165)] * 42
                          + [(13, 165, 165)] * 5
                          + [(13, 165, 13)] * 6
                          + [(165, 165, 13)] * 5
                          + [(165, 13, 13)] * 143)

        led_strips = [FakeLedStrip()]

        Spectrogram(frequency_range, amplitude_rgbs, led_strips)

    def test_led_strips(self):
        frequency_range = (0, 2300)

        amplitude_rgbs = ([(13, 13, 165)] * 42
                          + [(13, 165, 165)] * 5
                          + [(13, 165, 13)] * 6
                          + [(165, 165, 13)] * 5
                          + [(165, 13, 13)] * 143)

        LED_STRIPS = [[], [FakeLedStrip()], [FakeLedStrip()] * 100]

        for led_strips in LED_STRIPS:
            with self.subTest(number_of_leds_strips=len(led_strips)):

                Spectrogram(frequency_range, amplitude_rgbs, led_strips)

    def test_amplitude_rgbs(self):
        frequency_range = (0, 2300)

        VALID_AMPLITUDE_RGBS = [[],
                                [(10, 10, 10)],
                                [(10, 10, 10), (20, 20, 20), (30, 30, 30)]]

        led_strips = [FakeLedStrip()]

        for amplitude_rgbs in VALID_AMPLITUDE_RGBS:
            with self.subTest(amplitude_rgbs=amplitude_rgbs):

                Spectrogram(frequency_range, amplitude_rgbs, led_strips)

        INVALID_AMPLITUDE_RGBS = [[(-1, 0, 0)], [(0, -1, 0)], [(0, 0, -1)],
                                  [(-100, 0, 0)], [(0, -100, 0)], [(0, 0, -100)],

                                  [(256, 0, 0)], [(0, 256, 0)], [(0, 0, 256)],
                                  [(300, 0, 0)], [(0, 300, 0)], [(0, 0, 300)]]

        for amplitude_rgbs in INVALID_AMPLITUDE_RGBS:
            with self.subTest(amplitude_rgbs=amplitude_rgbs):

                with self.assertRaises(ValueError):
                    Spectrogram(frequency_range, amplitude_rgbs, led_strips)

    def test_valid_frequency_range(self):
        FREQUENCY_RANGES = [(0, 0), (0, 1), (1, 10), (0, 2300)]

        for frequency_range in FREQUENCY_RANGES:
            with self.subTest(frequency_range=frequency_range):
                amplitude_rgbs = []
                led_strips = [FakeLedStrip()]

                Spectrogram(frequency_range, amplitude_rgbs, led_strips)

    def test_start_frequency_greater_than_end_frequency(self):
        FREQUENCY_RANGES = [(1, 0), (2, 1), (100, 50)]

        for frequency_range in FREQUENCY_RANGES:
            with self.subTest(frequency_range=frequency_range):
                amplitude_rgbs = []
                led_strips = [FakeLedStrip()]

                with self.assertRaises(ValueError):
                    Spectrogram(frequency_range, amplitude_rgbs, led_strips)

    def test_start_frequency_less_than_0(self):
        FREQUENCY_RANGES = [(-1, 10), (-100, 10)]

        for frequency_range in FREQUENCY_RANGES:
            with self.subTest(start_frequency=frequency_range[0]):
                amplitude_rgbs = []
                led_strips = [FakeLedStrip()]

                with self.assertRaises(ValueError):
                    Spectrogram(frequency_range, amplitude_rgbs, led_strips)

    def test_end_frequency_less_than_0(self):
        FREQUENCY_RANGES = [(0, -1), (0, -10)]

        for frequency_range in FREQUENCY_RANGES:
            with self.subTest(end_frequency=frequency_range[1]):
                amplitude_rgbs = []
                led_strips = [FakeLedStrip()]

                with self.assertRaises(ValueError):
                    Spectrogram(frequency_range, amplitude_rgbs, led_strips)


class TestUpdateLedStrips(unittest.TestCase):
    def setUp(self):
        FREQUENCY_RANGE = (0, 2300)

        AMPLITUDE_RGBS = ([(13, 13, 165)] * 42
                          + [(13, 165, 165)] * 5
                          + [(13, 165, 13)] * 6
                          + [(165, 165, 13)] * 5
                          + [(165, 13, 13)] * 143)

        NUMBER_OF_GROUPS = 60
        self.led_strip = FakeLedStrip(NUMBER_OF_GROUPS)

        led_strips = [self.led_strip]

        self.spectrogram = Spectrogram(FREQUENCY_RANGE, AMPLITUDE_RGBS, led_strips)

    def test_empty_audio_data(self):
        audio_data = b''
        number_of_frames = 2205
        sampling_rate = 44100
        format = numpy.int16

        with self.assertRaises(ValueError) as error:

            self.spectrogram.update_led_strips(audio_data, number_of_frames, sampling_rate, format)

        actual_error_message = str(error.exception)
        expected_error_message = 'Invalid number of FFT data points (0) specified.'

        self.assertEqual(actual_error_message, expected_error_message)

    def test_audio_data_length(self):
        number_of_frames = 2205
        sampling_rate = 44100
        format = numpy.int16

        for valid_length in range(2, 1000, 2):

            audio_data = b'0' * valid_length

            with self.subTest(f'len(audio_data) = {len(audio_data)}'):
                self.spectrogram.update_led_strips(audio_data, number_of_frames, sampling_rate, format)

        for invalid_length in range(1, 1001, 2):

            audio_data = b'0' * invalid_length

            with self.subTest(f'len(audio_data) = {len(audio_data)}'):

                with self.assertRaises(ValueError) as error:
                    self.spectrogram.update_led_strips(audio_data, number_of_frames, sampling_rate, format)

                actual_error_message = str(error.exception)
                expected_error_message = 'buffer size must be a multiple of element size'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_silent_audio_data(self):
        audio_data = b'\x00' * 141120
        number_of_frames = 2205
        sampling_rate = 44100
        format = numpy.int16

        self.spectrogram.update_led_strips(audio_data, number_of_frames, sampling_rate, format)

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

        for group in range(self.led_strip.number_of_groups):
            with self.subTest(led_strip_group=group, actual_group_color=self.led_strip.group_colors[group]):

                self.assertTrue(self.led_strip.group_is_rgb(group, (13, 13, 165)))

    def test_audio_data(self):
        audio_file_path = util.join_paths(__file__, '../audio')

        with open(audio_file_path, 'rb') as audio_file:
            audio_data: bytes = audio_file.read()

            number_of_frames = 2205
            sampling_rate = 44100
            format = numpy.int16

            self.spectrogram.update_led_strips(audio_data, number_of_frames, sampling_rate, format)

            self.assertEqual(self.led_strip.number_of_queued_colors, 0)

            expected_colors = [(165, 165, 13), (165, 165, 13), (165, 165, 13), (165, 13, 13), (165, 13, 13), (165, 165, 13),
                               (13, 165, 13), (13, 165, 13), (13, 165, 165), (13, 165, 165), (13, 13, 165), (13, 165, 165),
                               (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                               (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                               (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                               (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                               (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                               (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                               (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                               (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165)]

            self.assertEqual(self.led_strip.number_of_groups, len(expected_colors))

            for group in range(self.led_strip.number_of_groups):
                with self.subTest(led_strip_group=group, actual_group_color=self.led_strip.group_colors[group]):

                    self.assertTrue(self.led_strip.group_is_rgb(group, expected_colors[group]))
