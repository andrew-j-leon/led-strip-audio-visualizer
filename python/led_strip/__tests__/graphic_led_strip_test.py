import abc
import unittest
from typing import Dict

from led_strip.graphic_led_strip import GraphicLedStrip, Point
from led_strip.led_strip import GroupedLeds
from libraries.gui import Font, Gui, Rectangle
from util.rgb import RGB


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


class TestGroupIsRGB(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 10), (10, 20)]

    GROUP_0 = 0
    GROUP_1 = 1

    def setUp(self):
        leds = GroupedLeds(self.LED_RANGE, self.GROUP_LED_RANGES)

        self.led_strip = GraphicLedStrip(leds, FakeGui())

    def test_group_is_rgb(self):
        RED_ENQUEUED = 10
        GREEN_ENQUEUED = 20
        BLUE_ENQUEUED = 30

        RED_NOT_ENQUEUED = 100
        GREEN_NOT_ENQUEUED = 150
        BLUE_NOT_ENQUEUED = 200

        self.led_strip.enqueue_rgb(self.GROUP_0, (RED_ENQUEUED, GREEN_ENQUEUED, BLUE_ENQUEUED))
        self.led_strip.show_queued_colors()

        RGBS = [((RED_ENQUEUED, GREEN_ENQUEUED, BLUE_ENQUEUED), (RED_NOT_ENQUEUED, GREEN_NOT_ENQUEUED, BLUE_NOT_ENQUEUED)),
                (RGB(RED_ENQUEUED, GREEN_ENQUEUED, BLUE_ENQUEUED), RGB(RED_NOT_ENQUEUED, GREEN_NOT_ENQUEUED, BLUE_NOT_ENQUEUED)),
                [(RED_ENQUEUED, GREEN_ENQUEUED, BLUE_ENQUEUED), (RED_NOT_ENQUEUED, GREEN_NOT_ENQUEUED, BLUE_NOT_ENQUEUED)]]

        for rgb_enqueued, rgb_not_enqueued in RGBS:
            with self.subTest(rgb_enqueued=rgb_enqueued, rgb_not_enqueued=rgb_not_enqueued):

                self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, rgb_enqueued))

                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, rgb_not_enqueued))
                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, rgb_enqueued))
                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, rgb_not_enqueued))


class TestEnqueueColor(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 10), (10, 20)]

    GROUP_0 = 0
    GROUP_1 = 1

    def setUp(self):
        leds = GroupedLeds(self.LED_RANGE, self.GROUP_LED_RANGES)

        self.led_strip = GraphicLedStrip(leds, FakeGui())

    def test_enqueue_one_group_color(self):
        RED = 10
        GREEN = 20
        BLUE = 30

        RGBS = [(RED, GREEN, BLUE), RGB(RED, GREEN, BLUE), [RED, GREEN, BLUE]]

        for rgb in RGBS:
            with self.subTest(f'rgb = {repr(rgb)}'):
                self.setUp()

                self.led_strip.enqueue_rgb(self.GROUP_0, rgb)

                self.assertEqual(self.led_strip.number_of_queued_colors, 1)

                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, rgb))
                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, rgb))

                self.led_strip.show_queued_colors()

                self.assertEqual(self.led_strip.number_of_queued_colors, 1)

                self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, rgb))
                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, rgb))

                self.tearDown()

    def test_enqueue_multiple_group_colors(self):
        RGB_0 = 10
        GREEN_0 = 20
        BLUE_0 = 30

        RED_1 = 100
        GREEN_1 = 150
        BLUE_1 = 200

        RGBS = [((RGB_0, GREEN_0, BLUE_0), (RED_1, GREEN_1, BLUE_1)),
                (RGB(RGB_0, GREEN_0, BLUE_0), RGB(RED_1, GREEN_1, BLUE_1)),
                [(RGB_0, GREEN_0, BLUE_0), (RED_1, GREEN_1, BLUE_1)]]

        for rgb_0, rgb_1 in RGBS:
            with self.subTest(f'rgb_0 = {repr(rgb_0)}, rgb_1 = {rgb_1}'):
                self.setUp()

                self.led_strip.enqueue_rgb(self.GROUP_0, rgb_0)
                self.led_strip.enqueue_rgb(self.GROUP_1, rgb_1)

                self.assertEqual(self.led_strip.number_of_queued_colors, 2)

                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, rgb_0))
                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, rgb_1))

                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, rgb_0))
                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, rgb_1))

                self.led_strip.show_queued_colors()

                self.assertEqual(self.led_strip.number_of_queued_colors, 2)

                self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_0, rgb_0))
                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_0, rgb_1))

                self.assertFalse(self.led_strip.group_is_rgb(self.GROUP_1, rgb_0))
                self.assertTrue(self.led_strip.group_is_rgb(self.GROUP_1, rgb_1))

                self.tearDown()

    def test_overwrite_group_color(self):
        RED_OLD = 10
        GREEN_OLD = 20
        BLUE_OLD = 30

        RED_NEW = 100
        GREEN_NEW = 150
        BLUE_NEW = 200

        RGBS = [((RED_OLD, GREEN_OLD, BLUE_OLD), (RED_NEW, GREEN_NEW, BLUE_NEW)),
                (RGB(RED_OLD, GREEN_OLD, BLUE_OLD), RGB(RED_NEW, GREEN_NEW, BLUE_NEW)),
                [(RED_OLD, GREEN_OLD, BLUE_OLD), (RED_NEW, GREEN_NEW, BLUE_NEW)]]

        GROUP = self.GROUP_0

        for rgb_old, rgb_new in RGBS:
            with self.subTest(f'rgb_old = {repr(rgb_old)}, rgb_new = {rgb_new}'):
                self.setUp()

                self.led_strip.enqueue_rgb(GROUP, rgb_old)
                self.led_strip.enqueue_rgb(GROUP, rgb_new)

                self.assertEqual(self.led_strip.number_of_queued_colors, 2)

                self.assertFalse(self.led_strip.group_is_rgb(GROUP, rgb_old))
                self.assertFalse(self.led_strip.group_is_rgb(GROUP, rgb_new))

                self.led_strip.show_queued_colors()

                self.assertEqual(self.led_strip.number_of_queued_colors, 2)

                self.assertFalse(self.led_strip.group_is_rgb(GROUP, rgb_old))
                self.assertTrue(self.led_strip.group_is_rgb(GROUP, rgb_new))

                self.tearDown()

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
