import abc
import unittest
from typing import Dict

from led_strip.graphic_led_strip import GraphicLedStrip, Point
from led_strip.led_strip import GroupedLeds
from libraries.gui import Font, Gui, Rectangle


class FakeGui(Gui):
    def __init__(self):
        self.closed = False
        self.number_of_updates = 0

        self.elements: Dict[int, Element] = dict()

    @property
    def dimensions(self) -> Rectangle:
        WIDTH = 1920
        HEIGHT = 1080
        return Rectangle(WIDTH, HEIGHT)

    def close(self):
        self.closed = True

    def create_oval(self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int, fill_color: str) -> int:
        element = Oval(top_left_x, top_left_y, bottom_right_x, bottom_right_y, fill_color)
        element_id = id(element)

        self.elements[element_id] = element

        return element_id

    def create_text(self, center_x: int, center_y: int, text: str, font: Font) -> int:
        element = Text(center_x, center_y, text, font)
        element_id = id(element)

        self.elements[element_id] = element

        return element_id

    def update(self):
        self.number_of_updates += 1

    def set_element_fill_color(self, element_id: int, color: str):
        self.elements[element_id].set_fill_color(color)


class Element(abc.ABC):
    @property
    @abc.abstractmethod
    def fill_color(self) -> str:
        pass

    @abc.abstractmethod
    def set_fill_color(self, color: str):
        pass


class Oval(Element):
    def __init__(self, left_most_x: int, top_most_y: int, right_most_x: int, bottom_most_y: int, fill_color: str):
        self.left_most_x = left_most_x
        self.top_most_y = top_most_y

        self.right_most_x = right_most_x
        self.bottom_most_y = bottom_most_y

        self.__fill_color = fill_color

    @property
    def fill_color(self) -> str:
        return self.__fill_color

    def set_fill_color(self, color: str):
        self.__fill_color = color


class Text(Element):
    def __init__(self, center_x: int, center_y: int, text: str, font: Font):
        self.center_x = center_x
        self.center_y = center_y

        self.text = text
        self.font = font

    @property
    def fill_color(self) -> str:
        return self.font.color

    def set_fill_color(self, color: str):
        self.font.color = color


class TestPoint(unittest.TestCase):
    def test_constructor(self):
        X = 0
        Y = 5
        point = Point(X, Y)

        self.assertEqual(point.x, X)
        self.assertEqual(point.y, Y)

    def test_repr(self):
        X = 0
        Y = 5
        point = Point(X, Y)

        self.assertEqual(repr(point), f'Point({X}, {Y})')


class TestNumberOfGroups(unittest.TestCase):
    def test_number_of_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = [[],
                            [(0, 10)],
                            [(0, 10), (10, 20)],

                            [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
                             (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]]

        for group_led_ranges in GROUP_LED_RANGES:
            with self.subTest(number_of_groups=len(group_led_ranges)):

                leds = GroupedLeds(LED_RANGE, group_led_ranges)

                led_strip = GraphicLedStrip(leds, FakeGui())

                self.assertEqual(led_strip.number_of_groups, len(group_led_ranges))


class TestEnqueueColor(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 10), (10, 20)]

    GROUP_0 = 0
    GROUP_1 = 1
    GROUP_2 = 2

    def setUp(self):
        leds = GroupedLeds(self.LED_RANGE, self.GROUP_LED_RANGES)

        self.led_strip = GraphicLedStrip(leds, FakeGui())

    def test_enqueue_one_group_color(self):
        RGB = (10, 20, 30)

        self.led_strip.enqueue_rgb(self.GROUP_0, RGB)

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, RGB))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB))

        self.led_strip.show_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, RGB))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB))

    def test_enqueue_multiple_group_colors(self):
        RGB_0 = (10, 20, 30)
        RGB_1 = (100, 150, 200)

        self.led_strip.enqueue_rgb(self.GROUP_0, RGB_0)
        self.led_strip.enqueue_rgb(self.GROUP_1, RGB_1)

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, RGB_0))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, RGB_1))

        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB_0))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB_1))

        self.led_strip.show_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, RGB_0))
        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, RGB_1))

        self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, RGB_0))
        self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_1, RGB_1))

    def test_overwrite_group_color(self):
        RGB_0 = (10, 20, 30)
        RGB_1 = (40, 50, 60)

        GROUP = self.GROUP_0

        self.led_strip.enqueue_rgb(GROUP, RGB_0)
        self.led_strip.enqueue_rgb(GROUP, RGB_1)

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertFalse(self.led_strip.group_is_rgb(GROUP, RGB_0))
        self.assertFalse(self.led_strip.group_is_rgb(GROUP, RGB_1))

        self.led_strip.show_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertFalse(self.led_strip.group_is_rgb(GROUP, RGB_0))
        self.assertTrue(self.led_strip.group_is_rgb(GROUP, RGB_1))

    def test_no_groups(self):
        GROUPS = [0, 1, 100]

        for group in GROUPS:
            with self.subTest(group=group):
                led_range = (0, 100)
                group_led_ranges = []

                leds = GroupedLeds(led_range, group_led_ranges)

                led_strip = GraphicLedStrip(leds, FakeGui())

                with self.assertRaises(IndexError) as error:
                    rbg = (1, 2, 3)

                    led_strip.enqueue_rgb(group, rbg)

                actual_error_message = str(error.exception)
                expected_error_message = f'Cannot enqueue RGB when GraphicLedStrip has 0 groups.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_group_does_not_exist(self):
        INVALID_GROUPS = [-6, -1, 1, 10]

        for invalid_group in INVALID_GROUPS:
            with self.subTest(group=invalid_group):

                led_range = (0, 100)
                group_led_ranges = [(0, 50)]

                leds = GroupedLeds(led_range, group_led_ranges)

                led_strip = GraphicLedStrip(leds, FakeGui())

                with self.assertRaises(IndexError) as error:
                    rgb = (1, 2, 3)

                    led_strip.enqueue_rgb(invalid_group, rgb)

                actual_error_message = str(error.exception)
                expected_error_message = f'Tried to enqueue an RGB color into group {invalid_group}, but group indices range from 0 (inclusive) to {len(group_led_ranges) - 1} (inclusive).'

                self.assertEqual(actual_error_message, expected_error_message)


class TestClearQueuedColors(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 10), (10, 20)]

    GROUP_0 = 0
    GROUP_1 = 1
    GROUP_2 = 2

    def setUp(self):
        leds = GroupedLeds(self.LED_RANGE, self.GROUP_LED_RANGES)

        self.led_strip = GraphicLedStrip(leds, FakeGui())

    def test_clear_empty_queue(self):
        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

        self.led_strip.clear_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

    def test_clear_one_element_queue(self):
        self.led_strip.enqueue_rgb(self.GROUP_0, (1, 1, 1))

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

        self.led_strip.clear_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

    def test_clear_multi_element_queue(self):
        self.led_strip.enqueue_rgb(self.GROUP_0, (1, 1, 1))
        self.led_strip.enqueue_rgb(self.GROUP_1, (1, 1, 1))
        self.led_strip.enqueue_rgb(self.GROUP_0, (1, 1, 1))

        self.assertEqual(self.led_strip.number_of_queued_colors, 3)

        self.led_strip.clear_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)
