import unittest
from typing import Iterable, List, Tuple

import util
from led_strip.led_strip import LedStrip
from spectrogram import Spectrogram


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

        Spectrogram(frequency_range, amplitude_rgbs)

    def test_amplitude_rgbs(self):
        VALID_AMPLITUDE_RGBS = [[],
                                [(10, 10, 10)],
                                [(10, 10, 10), (20, 20, 20), (30, 30, 30)]]

        for amplitude_rgbs in VALID_AMPLITUDE_RGBS:
            with self.subTest(amplitude_rgbs=amplitude_rgbs):
                frequency_range = (0, 2300)

                Spectrogram(frequency_range, amplitude_rgbs)

        INVALID_AMPLITUDE_RGBS = [[(-1, 0, 0)], [(0, -1, 0)], [(0, 0, -1)],
                                  [(-100, 0, 0)], [(0, -100, 0)], [(0, 0, -100)],

                                  [(256, 0, 0)], [(0, 256, 0)], [(0, 0, 256)],
                                  [(300, 0, 0)], [(0, 300, 0)], [(0, 0, 300)]]

        for amplitude_rgbs in INVALID_AMPLITUDE_RGBS:
            with self.subTest(amplitude_rgbs=amplitude_rgbs):
                frequency_range = (0, 2300)

                with self.assertRaises(ValueError):
                    Spectrogram(frequency_range, amplitude_rgbs)

    def test_valid_frequency_range(self):
        FREQUENCY_RANGES = [(0, 0), (0, 1), (1, 10), (0, 2300)]

        for frequency_range in FREQUENCY_RANGES:
            with self.subTest(frequency_range=frequency_range):
                amplitude_rgbs = []

                Spectrogram(frequency_range, amplitude_rgbs)

    def test_start_frequency_greater_than_end_frequency(self):
        FREQUENCY_RANGES = [(1, 0), (2, 1), (100, 50)]

        for frequency_range in FREQUENCY_RANGES:
            with self.subTest(frequency_range=frequency_range):
                amplitude_rgbs = []

                with self.assertRaises(ValueError):
                    Spectrogram(frequency_range, amplitude_rgbs)

    def test_start_frequency_less_than_0(self):
        FREQUENCY_RANGES = [(-1, 10), (-100, 10)]

        for frequency_range in FREQUENCY_RANGES:
            with self.subTest(start_frequency=frequency_range[0]):
                amplitude_rgbs = []

                with self.assertRaises(ValueError):
                    Spectrogram(frequency_range, amplitude_rgbs)

    def test_end_frequency_less_than_0(self):
        FREQUENCY_RANGES = [(0, -1), (0, -10)]

        for frequency_range in FREQUENCY_RANGES:
            with self.subTest(end_frequency=frequency_range[1]):
                amplitude_rgbs = []

                with self.assertRaises(ValueError):
                    Spectrogram(frequency_range, amplitude_rgbs)


class TestUpdateLedStrips(unittest.TestCase):
    NUMBER_OF_FRAMES = 2205
    SAMPLING_RATE = 44100

    FREQUENCY_RANGE = (0, 2300)

    RGB_0 = (13, 13, 165)
    RGB_1 = (13, 165, 165)
    RGB_2 = (13, 165, 13)
    RGB_3 = (165, 165, 13)
    RGB_4 = (165, 13, 13)

    AMPLITUDE_RGBS = ([RGB_0] * 42
                      + [RGB_1] * 5
                      + [RGB_2] * 6
                      + [RGB_3] * 5
                      + [RGB_4] * 143)

    NUMBER_OF_GROUPS = 60

    def setUp(self):
        self.led_strip = FakeLedStrip(self.NUMBER_OF_GROUPS)
        self.spectrogram = Spectrogram(self.FREQUENCY_RANGE, self.AMPLITUDE_RGBS)

    def test_complex_audio_data(self):
        EXPECTED_COLORS = [(165, 165, 13), (165, 165, 13), (165, 165, 13), (165, 13, 13), (165, 13, 13), (165, 165, 13),
                           (13, 165, 13), (13, 165, 13), (13, 165, 165), (13, 165, 165), (13, 13, 165), (13, 165, 165),
                           (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                           (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                           (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                           (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                           (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                           (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                           (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165),
                           (13, 13, 165), (13, 13, 165), (13, 13, 165), (13, 13, 165)]

        self.check_update_led_strips(self.led_strip, self.spectrogram, EXPECTED_COLORS)

    def test_no_amplitude_rgbs(self):
        AMPLITUDE_RGBS = []
        spectrogram = Spectrogram(self.FREQUENCY_RANGE, AMPLITUDE_RGBS)

        EXPECTED_COLORS = [(0, 0, 0)] * self.NUMBER_OF_GROUPS

        self.check_update_led_strips(self.led_strip, spectrogram, EXPECTED_COLORS)

    def test_empty_audio_data(self):
        audio_data = b''

        with self.assertRaises(ValueError):
            self.spectrogram.update_led_strips(self.led_strip, audio_data, self.NUMBER_OF_FRAMES,
                                               self.SAMPLING_RATE)

    def test_audio_data_length(self):
        for valid_length in range(2, 100, 2):

            audio_data = b'0' * valid_length

            with self.subTest(f'len(audio_data) = {len(audio_data)}'):

                self.spectrogram.update_led_strips(self.led_strip, audio_data, self.NUMBER_OF_FRAMES, self.SAMPLING_RATE)

        for invalid_length in range(1, 101, 2):

            audio_data = b'0' * invalid_length

            with self.subTest(f'len(audio_data) = {len(audio_data)}'):

                with self.assertRaises(ValueError):
                    self.spectrogram.update_led_strips(self.led_strip, audio_data, self.NUMBER_OF_FRAMES,
                                                       self.SAMPLING_RATE)

    def test_silent_audio_data(self):
        audio_data = b'\x00' * 141120

        self.spectrogram.update_led_strips(self.led_strip, audio_data, self.NUMBER_OF_FRAMES, self.SAMPLING_RATE)

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

        for group in range(self.led_strip.number_of_groups):
            with self.subTest(led_strip_group=group, actual_group_color=self.led_strip.group_colors[group]):

                self.assertTrue(self.led_strip.group_is_rgb(group, self.RGB_0))

    def check_update_led_strips(self, led_strip: FakeLedStrip, spectrogram: Spectrogram, expected_rgbs: List[Tuple[int, int, int]]):
        ''' Check against the audio data contained in the file: `./audio` '''

        AUDIO_FILE_PATH = util.join_paths(__file__, '../audio')

        with open(AUDIO_FILE_PATH, 'rb') as audio_file:
            audio_data: bytes = audio_file.read()

            spectrogram.update_led_strips(led_strip, audio_data, self.NUMBER_OF_FRAMES, self.SAMPLING_RATE)

            self.assertEqual(led_strip.number_of_queued_colors, 0)
            self.assertEqual(led_strip.number_of_groups, len(expected_rgbs))

            for group in range(led_strip.number_of_groups):
                with self.subTest(led_strip_group=group, actual_group_color=led_strip.group_colors[group]):

                    self.assertTrue(led_strip.group_is_rgb(group, expected_rgbs[group]))
