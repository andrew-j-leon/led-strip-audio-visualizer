import os
import unittest
from typing import List, Tuple

from leds.led_strip import FakeLedStrip
from spectrogram import ProductionSpectrogram


class TestSpectrogram(unittest.TestCase):
    NUMBER_OF_FRAMES = 2205
    SAMPLING_RATE = 44100

    NUMBER_OF_GROUPS = 60

    START_FREQUENCY = 0
    END_FREQUENCY = 2300

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

    def setUp(self):
        self.led_strip = FakeLedStrip(self.NUMBER_OF_GROUPS)
        self.spectrogram = ProductionSpectrogram(self.AMPLITUDE_RGBS, self.START_FREQUENCY, self.END_FREQUENCY)

    def test_setting_valid_amplitude_rgbs(self):
        VALID_AMPLITUDE_RGBS = [[],
                                [(10, 10, 10)],
                                [(10, 10, 10), (20, 20, 20), (30, 30, 30)]]

        for amplitude_rgbs in VALID_AMPLITUDE_RGBS:
            with self.subTest(amplitude_rgbs=amplitude_rgbs):
                self.spectrogram.set_amplitude_rgbs(amplitude_rgbs)

    def test_setting_invalid_amplitude_rgbs(self):
        INVALID_AMPLITUDE_RGBS = [[(-1, 0, 0)], [(0, -1, 0)], [(0, 0, -1)],
                                  [(-100, 0, 0)], [(0, -100, 0)], [(0, 0, -100)],

                                  [(256, 0, 0)], [(0, 256, 0)], [(0, 0, 256)],
                                  [(300, 0, 0)], [(0, 300, 0)], [(0, 0, 300)]]

        for amplitude_rgbs in INVALID_AMPLITUDE_RGBS:
            with self.subTest(amplitude_rgbs=amplitude_rgbs):
                with self.assertRaises(ValueError):
                    self.spectrogram.set_amplitude_rgbs(amplitude_rgbs)

    def test_setting_valid_frequency_ranges(self):
        FREQUENCY_RANGES = [(0, 0), (0, 1), (1, 10), (0, 2300)]

        for start_frequency, end_frequency in FREQUENCY_RANGES:
            with self.subTest(start_frequency=start_frequency, end_frequency=end_frequency):
                self.spectrogram.set_frequency_range(start_frequency, end_frequency)

    def test_setting_frequency_range_where_start_frequency_is_greater_than_end_frequency(self):
        FREQUENCY_RANGES = [(1, 0), (2, 1), (100, 50)]

        for start_frequency, end_frequency in FREQUENCY_RANGES:
            with self.subTest(start_frequency=start_frequency, end_frequency=end_frequency):
                with self.assertRaises(ValueError):
                    self.spectrogram.set_frequency_range(start_frequency, end_frequency)

    def test_setting_frequency_range_where_start_frequency_is_less_than_0(self):
        FREQUENCY_RANGES = [(-1, 10), (-100, 10)]

        for start_frequency, end_frequency in FREQUENCY_RANGES:
            with self.subTest(start_frequency=start_frequency, end_frequency=end_frequency):
                with self.assertRaises(ValueError):
                    self.spectrogram.set_frequency_range(start_frequency, end_frequency)

    def test_setting_frequency_range_where_end_frequency_is_less_than_0(self):
        FREQUENCY_RANGES = [(0, -1), (0, -10)]

        for start_frequency, end_frequency in FREQUENCY_RANGES:
            with self.subTest(start_frequency=start_frequency, end_frequency=end_frequency):
                with self.assertRaises(ValueError):
                    self.spectrogram.set_frequency_range(start_frequency, end_frequency)

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

        self.check_update_led_strips(EXPECTED_COLORS)

    def test_no_amplitude_rgbs(self):
        AMPLITUDE_RGBS = []
        self.spectrogram.set_amplitude_rgbs(AMPLITUDE_RGBS)

        EXPECTED_COLORS = [(0, 0, 0)] * self.led_strip.number_of_groups

        self.check_update_led_strips(EXPECTED_COLORS)

    def test_empty_audio_data(self):
        audio_data = b''

        with self.assertRaises(ValueError):
            self.spectrogram.update_led_strip(self.led_strip, audio_data, self.NUMBER_OF_FRAMES,
                                              self.SAMPLING_RATE)

    def test_audio_data_length(self):
        for valid_length in range(2, 100, 2):

            audio_data = b'0' * valid_length

            with self.subTest(f'len(audio_data) = {len(audio_data)}'):

                self.spectrogram.update_led_strip(self.led_strip, audio_data, self.NUMBER_OF_FRAMES,
                                                  self.SAMPLING_RATE)

        for invalid_length in range(1, 101, 2):

            audio_data = b'0' * invalid_length

            with self.subTest(f'len(audio_data) = {len(audio_data)}'):

                with self.assertRaises(ValueError):
                    self.spectrogram.update_led_strip(self.led_strip, audio_data, self.NUMBER_OF_FRAMES,
                                                      self.SAMPLING_RATE)

    def test_silent_audio_data(self):
        audio_data = b'\x00' * 141120

        self.spectrogram.update_led_strip(self.led_strip, audio_data, self.NUMBER_OF_FRAMES, self.SAMPLING_RATE)

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

        for group in range(self.led_strip.number_of_groups):
            with self.subTest(led_strip_group=group, actual_group_color=self.led_strip.group_colors[group]):

                self.assertTrue(self.led_strip.group_is_rgb(group, self.RGB_0))

    def check_update_led_strips(self, expected_rgbs: List[Tuple[int, int, int]]):
        ''' Check against the audio data contained in the file: `./audio` '''

        AUDIO_FILE_PATH = os.path.normpath(os.path.join(__file__, '../audio'))

        with open(AUDIO_FILE_PATH, 'rb') as audio_file:
            audio_data: bytes = audio_file.read()

            self.spectrogram.update_led_strip(self.led_strip, audio_data, self.NUMBER_OF_FRAMES, self.SAMPLING_RATE)

            self.assertEqual(self.led_strip.number_of_queued_colors, 0)
            self.assertEqual(self.led_strip.number_of_groups, len(expected_rgbs))

            for group in range(self.led_strip.number_of_groups):
                with self.subTest(led_strip_group=group, actual_group_color=self.led_strip.group_colors[group]):

                    self.assertTrue(self.led_strip.group_is_rgb(group, expected_rgbs[group]))
