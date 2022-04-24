import abc
import unittest
from typing import Dict

from led_strip.graphic_led_strip import GraphicLedStrip, Point
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


class TestConstructor(unittest.TestCase):
    def test_number_of_leds(self):
        VALID_NUMBER_OF_LEDS = [0, 1, 100,
                                1.5, 100.5]

        for number_of_leds in VALID_NUMBER_OF_LEDS:
            led_range = (0, number_of_leds)

            with self.subTest(led_range=led_range):
                group_led_ranges = []

                GraphicLedStrip(led_range, group_led_ranges, FakeGui())

        INVALID_NUMBER_OF_LEDS = [-1, -100]

        for number_of_leds in INVALID_NUMBER_OF_LEDS:
            led_range = (0, number_of_leds)

            with self.subTest(led_range=led_range):

                with self.assertRaises(ValueError):
                    group_led_ranges = []

                    GraphicLedStrip(led_range, group_led_ranges, FakeGui())

    def test_led_ranges(self):
        VALID_LED_RANGES = [(0, 0), (0, 1), (0, 150), (1, 1), (1, 150)]

        for valid_led_range in VALID_LED_RANGES:
            with self.subTest(led_range=valid_led_range):
                group_led_ranges = []

                GraphicLedStrip(valid_led_range, group_led_ranges, FakeGui())

        INVALID_LED_RANGES = [(-1, 0), (0, -1), (-1, -1),
                              (-10, 0), (0, -10),
                              (1, 0), (10, 0),
                              (10, 9), (10, 5)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(ValueError):
                    group_led_ranges = []

                    GraphicLedStrip(invalid_led_range, group_led_ranges, FakeGui())

    def test_group_led_ranges_with_led_range_starting_at_0(self):
        LED_RANGE_STARTING_AT_0 = (0, 150)

        VALID_GROUP_LED_RANGES = [[(0, 0)], [(0, 1)], [(0, 150)], [(1, 1)], [(1, 150)],
                                  [(150, 150), (151, 151), (300, 300)]]

        INVALID_GROUP_LED_RANGES = [[(-1, 0)], [(0, -1)], [(-1, -1)],
                                    [(-10, 0)], [(0, -10)],
                                    [(1, 0)], [(10, 0)],
                                    [(10, 9)], [(10, 5)]]

        self.check_valid_group_led_ranges(LED_RANGE_STARTING_AT_0, VALID_GROUP_LED_RANGES)
        self.check_invalid_group_led_ranges(LED_RANGE_STARTING_AT_0, INVALID_GROUP_LED_RANGES)

    def test_group_led_ranges_with_led_range_starting_at_10(self):

        LED_RANGE_STARTING_AT_10 = (10, 150)

        VALID_GROUP_LED_RANGES = [
            [(10, 10)], [(10, 11)], [(10, 150)],
            [(149, 150)], [(150, 150)],
            [(10, 90), (90, 150)]
        ]

        INVALID_GROUP_LED_RANGES = [
            [(0, 1)], [(0, 10)], [(0, 150)], [(0, 151)], [(0, 300)],
            [(9, 10)], [(9, 11)], [(9, 150)], [(9, 300)],
            [(10, 151)], [(10, 300)],
            [(50, 151)], [(50, 300)],
            [(150, 151)], [(150, 300)],
            [(151, 152)], [(152, 300)]
        ]

        self.check_valid_group_led_ranges(LED_RANGE_STARTING_AT_10, VALID_GROUP_LED_RANGES)
        self.check_invalid_group_led_ranges(LED_RANGE_STARTING_AT_10, INVALID_GROUP_LED_RANGES)

    def check_valid_group_led_ranges(self, led_range, valid_group_led_ranges):
        for group_led_ranges in valid_group_led_ranges:
            with self.subTest(led_range=led_range, group_led_ranges=group_led_ranges):

                GraphicLedStrip(led_range, group_led_ranges, FakeGui())

    def check_invalid_group_led_ranges(self, led_range, invalid_group_led_ranges):
        for group_led_ranges in invalid_group_led_ranges:
            with self.subTest(led_range=led_range, group_led_ranges=group_led_ranges):

                with self.assertRaises(ValueError):
                    GraphicLedStrip(led_range, group_led_ranges, FakeGui())


class TestNumberOfGroups(unittest.TestCase):

    def test_number_of_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = [[],
                            [(0, 10)],
                            [(0, 10), (10, 20)],

                            [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
                             (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]]

        for group_led_ranges in GROUP_LED_RANGES:

            with self.subTest(f'number_of_groups={len(group_led_ranges)}'):

                led_strip = GraphicLedStrip(LED_RANGE, group_led_ranges, FakeGui())

                self.assertEqual(led_strip.number_of_groups, len(group_led_ranges))


class TestNumberOfLeds(unittest.TestCase):
    def test_number_of_leds(self):
        NUMBER_OF_LEDS = [0, 1, 15, 300]

        for number_of_leds in NUMBER_OF_LEDS:
            with self.subTest(f'number_of_leds={number_of_leds}'):

                led_range = (0, number_of_leds)

                led_strip = GraphicLedStrip(led_range, [], FakeGui())

                self.assertEqual(number_of_leds, led_strip.number_of_leds)


class TestEnqueueColor(unittest.TestCase):

    def setUp(self) -> None:
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = [(0, 10), (10, 20)]

        self.led_strip = GraphicLedStrip(LED_RANGE, GROUP_LED_RANGES, FakeGui())

        self.group_0 = 0
        self.group_1 = 1

    def test_enqueue_one_group_color(self):
        RGB = (10, 20, 30)

        self.led_strip.enqueue_rgb(self.group_0, RGB)

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

        self.assertFalse(self.led_strip.group_is_color(self.group_0, RGB))
        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB))

        self.led_strip.show_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

        self.assertTrue(self.led_strip.group_is_color(self.group_0, RGB))
        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB))

    def test_enqueue_two_group_colors(self):
        RGB_0 = (10, 20, 30)
        RGB_1 = (100, 150, 200)

        self.led_strip.enqueue_rgb(self.group_0, RGB_0)
        self.led_strip.enqueue_rgb(self.group_1, RGB_1)

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertFalse(self.led_strip.group_is_color(self.group_0, RGB_0))
        self.assertFalse(self.led_strip.group_is_color(self.group_0, RGB_1))

        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB_0))
        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB_1))

        self.led_strip.show_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertTrue(self.led_strip.group_is_color(self.group_0, RGB_0))
        self.assertFalse(self.led_strip.group_is_color(self.group_0, RGB_1))

        self.assertFalse(self.led_strip.group_is_color(self.group_1, RGB_0))
        self.assertTrue(self.led_strip.group_is_color(self.group_1, RGB_1))

    def test_overwrite_group_color(self):
        RGB_0 = (10, 20, 30)
        RGB_1 = (40, 50, 60)

        GROUP = self.group_0

        self.led_strip.enqueue_rgb(GROUP, RGB_0)
        self.led_strip.enqueue_rgb(GROUP, RGB_1)

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertFalse(self.led_strip.group_is_color(GROUP, RGB_0))
        self.assertFalse(self.led_strip.group_is_color(GROUP, RGB_1))

        self.led_strip.show_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 2)

        self.assertFalse(self.led_strip.group_is_color(GROUP, RGB_0))
        self.assertTrue(self.led_strip.group_is_color(GROUP, RGB_1))

    def test_no_groups(self):
        GROUPS = [0, 1, 100]

        for group in GROUPS:
            with self.subTest(f'group={group}'):

                LED_RANGE = (0, 100)
                GROUP_LED_RANGES = []
                led_strip = GraphicLedStrip(LED_RANGE, GROUP_LED_RANGES, FakeGui())

                with self.assertRaises(IndexError) as error:
                    rbg = (1, 2, 3)

                    led_strip.enqueue_rgb(group, rbg)

                actual_error_message = str(error.exception)
                expected_error_message = f'Cannot enqueue RGB when GraphicLedStrip has 0 groups.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_group_does_not_exist(self):
        INVALID_GROUPS = [-6, -1, 1, 10]

        for invalid_group in INVALID_GROUPS:
            with self.subTest(f'group={invalid_group}'):

                LED_RANGE = (0, 100)
                GROUP_LED_RANGES = [(0, 50)]

                led_strip = GraphicLedStrip(LED_RANGE, GROUP_LED_RANGES, FakeGui())

                with self.assertRaises(IndexError) as error:
                    rgb = (1, 2, 3)

                    led_strip.enqueue_rgb(invalid_group, rgb)

                actual_error_message = str(error.exception)
                expected_error_message = f'Tried to enqueue an RGB color into group {invalid_group}, but group indices range from 0 (inclusive) to {len(GROUP_LED_RANGES) - 1} (inclusive).'

                self.assertEqual(actual_error_message, expected_error_message)


class TestClearQueuedColors(unittest.TestCase):
    def setUp(self) -> None:
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = [(0, 10), (10, 20)]

        self.led_strip = GraphicLedStrip(LED_RANGE, GROUP_LED_RANGES, FakeGui())

        self.group_0 = 0
        self.group_1 = 1

    def test_clear_empty_queue(self):
        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

        self.led_strip.clear_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

    def test_clear_one_element_queue(self):
        self.led_strip.enqueue_rgb(0, (1, 1, 1))

        self.assertEqual(self.led_strip.number_of_queued_colors, 1)

        self.led_strip.clear_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)

    def test_clear_multi_element_queue(self):
        self.led_strip.enqueue_rgb(0, (1, 1, 1))
        self.led_strip.enqueue_rgb(1, (1, 1, 1))
        self.led_strip.enqueue_rgb(0, (1, 1, 1))

        self.assertEqual(self.led_strip.number_of_queued_colors, 3)

        self.led_strip.clear_queued_colors()

        self.assertEqual(self.led_strip.number_of_queued_colors, 0)
