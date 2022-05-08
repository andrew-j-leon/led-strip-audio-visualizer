import unittest
from typing import Iterable, List, Tuple

from led_strip.grouped_leds import GroupedLeds
from led_strip.led_strip import ProductionLedStrip
from util.rgb import RGB


class FakeGroupedLeds(GroupedLeds):
    def __init__(self, number_of_groups: int = 0):
        self.__group_colors: List[RGB] = [RGB() for i in range(number_of_groups)]

    @property
    def number_of_groups(self) -> int:
        return len(self.__group_colors)

    @property
    def number_of_leds(self) -> int:
        return 1

    @property
    def start_led(self) -> int:
        return 0

    @property
    def end_led(self) -> int:
        return 1

    def get_group_led_range(self, group: int) -> Tuple[int, int]:
        return (0, 1)

    def get_group_rgb(self, group: int) -> RGB:
        return self.__group_colors[group]

    def set_group_rgbs(self, group_rgbs: Iterable[Tuple[int, Iterable[int]]]):
        for group, rgb in group_rgbs:
            self.__group_colors[group] = RGB(*rgb)


class TestConstructor(unittest.TestCase):
    def test_constructor(self):
        ProductionLedStrip(FakeGroupedLeds())


class TestNumberOfGroupes(unittest.TestCase):
    def test_number_of_groups(self):
        leds = FakeGroupedLeds()

        led_strip = ProductionLedStrip(leds)

        self.assertEqual(leds.number_of_groups, led_strip.number_of_groups)


class TestNumberOfQueuedColors(unittest.TestCase):
    NUMBER_OF_GROUPS = 1

    def setUp(self) -> None:
        self.leds = FakeGroupedLeds(self.NUMBER_OF_GROUPS)
        self.led_strip = ProductionLedStrip(self.leds)

    def test_number_of_queued_colors(self):
        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

    def test_one_queued_color(self):
        GROUP = 0
        RGB = (10, 20, 30)

        self.led_strip.enqueue_rgb(GROUP, RGB)

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

    def test_many_queued_colors(self):
        GROUP = 0
        RGB = (10, 20, 30)

        EXPECTED_NUMBER_OF_QUEUED_COLORS = 100

        for i in range(EXPECTED_NUMBER_OF_QUEUED_COLORS):
            self.led_strip.enqueue_rgb(GROUP, RGB)

        self.assertEqual(self.led_strip.number_of_queued_colors, EXPECTED_NUMBER_OF_QUEUED_COLORS)


class EnqueueRGBTestCase(unittest.TestCase):
    BLACK_RGB = (0, 0, 0)
    NUMBER_OF_GROUPS = 3

    GROUP_0 = 0
    GROUP_1 = 1
    GROUP_2 = 2

    def setUp(self):
        self.leds = FakeGroupedLeds(self.NUMBER_OF_GROUPS)
        self.led_strip = ProductionLedStrip(self.leds)

    def check_all_groups_are_rgb(self, rgb: Iterable[int]):
        for group in range(self.NUMBER_OF_GROUPS):
            self.assertTrue(self.led_strip.group_is_rgb(group, rgb))


class TestEnqueueRGB(EnqueueRGBTestCase):
    def test_enqueue_one_group_one_time(self):
        RGB = (10, 20, 30)

        self.led_strip.enqueue_rgb(self.GROUP_0, RGB)

        self.check_all_groups_are_rgb(self.BLACK_RGB)

        self.led_strip.show_queued_colors()

        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, RGB))
        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_1, self.BLACK_RGB))
        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_2, self.BLACK_RGB))

    def test_enqueue_one_group_many_times(self):
        RGB_1 = (1, 2, 3)
        RGB_2 = (4, 5, 6)
        RGB_3 = (7, 8, 9)

        self.led_strip.enqueue_rgb(self.GROUP_0, RGB_1)
        self.led_strip.enqueue_rgb(self.GROUP_0, RGB_2)
        self.led_strip.enqueue_rgb(self.GROUP_0, RGB_3)

        self.check_all_groups_are_rgb(self.BLACK_RGB)

        self.led_strip.show_queued_colors()

        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, RGB_3))
        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_1, self.BLACK_RGB))
        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_2, self.BLACK_RGB))

    def test_enqueue_multiple_groups(self):
        RGB_0 = (1, 2, 3)
        RGB_1 = (4, 5, 6)
        RGB_2 = (7, 8, 9)

        self.led_strip.enqueue_rgb(self.GROUP_0, RGB_0)
        self.led_strip.enqueue_rgb(self.GROUP_1, RGB_1)
        self.led_strip.enqueue_rgb(self.GROUP_2, RGB_2)

        self.check_all_groups_are_rgb(self.BLACK_RGB)

        self.led_strip.show_queued_colors()

        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, RGB_0))
        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_1, RGB_1))
        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_2, RGB_2))

    def test_zero_groups(self):
        NUMBER_OF_GROUPS = 0

        leds = FakeGroupedLeds(NUMBER_OF_GROUPS)
        led_strip = ProductionLedStrip(leds)

        INVALID_GROUPS = [0, 1, 100]
        for invalid_group in INVALID_GROUPS:
            with self.subTest(group=invalid_group):

                with self.assertRaises(IndexError) as error:
                    rgb = (10, 20, 30)

                    led_strip.enqueue_rgb(invalid_group, rgb)

                error_message = str(error.exception)
                expected_error_message = f'Tried to enqueue RGB {repr(rgb)} into group {invalid_group}, but valid group indices range from 0 (inclusive) to {NUMBER_OF_GROUPS} (exclusive).'

                self.assertEqual(error_message, expected_error_message)

                self.check_all_groups_are_rgb(self.BLACK_RGB)

    def test_group_out_of_bounds(self):
        INVALID_GROUPS = [-100, -1, self.NUMBER_OF_GROUPS, self.NUMBER_OF_GROUPS + 100]

        for invalid_group in INVALID_GROUPS:
            with self.subTest(group=invalid_group):

                with self.assertRaises(IndexError) as error:
                    rgb = (10, 20, 30)

                    self.led_strip.enqueue_rgb(invalid_group, rgb)

                error_message = str(error.exception)
                expected_error_message = f'Tried to enqueue RGB {repr(rgb)} into group {invalid_group}, but valid group indices range from 0 (inclusive) to {self.NUMBER_OF_GROUPS} (exclusive).'

                self.assertEqual(error_message, expected_error_message)

                self.check_all_groups_are_rgb(self.BLACK_RGB)


class TestClearQueuedColors(EnqueueRGBTestCase):
    def test_no_rgbs_were_queued(self):
        self.led_strip.clear_queued_colors()

        self.led_strip.show_queued_colors()

        self.check_all_groups_are_rgb(self.BLACK_RGB)

    def test_some_rgbs_were_queued(self):
        RGB_0 = (1, 2, 3)
        RGB_1 = (4, 5, 6)
        RGB_2 = (7, 8, 9)

        self.led_strip.enqueue_rgb(self.GROUP_0, RGB_0)
        self.led_strip.enqueue_rgb(self.GROUP_1, RGB_1)
        self.led_strip.enqueue_rgb(self.GROUP_2, RGB_2)

        self.led_strip.clear_queued_colors()

        self.led_strip.show_queued_colors()

        self.check_all_groups_are_rgb(self.BLACK_RGB)
