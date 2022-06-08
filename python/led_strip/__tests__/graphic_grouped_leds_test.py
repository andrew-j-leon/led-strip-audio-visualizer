import math
import unittest
from abc import ABC, abstractmethod
from collections import Counter
from typing import Any, Dict, Iterable, List, Tuple

from led_strip.grouped_leds import GraphicGroupedLeds, Point
from libraries.canvas_gui import CanvasGui
from util import Font, convert_to_hex


class FakeCanvasGui(CanvasGui):
    def __init__(self):
        self.closed = False
        self.number_of_updates = 0

        self.__queued_elements: Dict[int, Element] = dict()

        self.elements: Dict[int, Element] = dict()

    @property
    def width(self) -> int:
        return 1920

    def close(self):
        self.closed = True

    def create_oval(self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int, fill_color: str = '#000000') -> int:
        element = Oval(top_left_x, top_left_y, bottom_right_x, bottom_right_y)
        element.set_fill_color(fill_color)

        element_hash = hash(element)

        self.__queued_elements[element_hash] = element

        return element_hash

    def create_text(self, center_x: int, center_y: int, text: str, font: Font = Font(), fill_color: str = '#000000') -> int:
        element = Text(center_x, center_y, text, font, fill_color)
        element_hash = hash(element)

        self.__queued_elements[element_hash] = element

        return element_hash

    def update(self):
        self.elements.update(self.__queued_elements)
        self.__queued_elements.clear()

    def set_element_fill_color(self, element_id: int, color: str):
        self.elements[element_id].set_fill_color(color)

    def set_group_rgbs(self, leds: GraphicGroupedLeds, group_rgbs: Iterable[Tuple[int, Iterable[int]]]):
        for group, rgb in group_rgbs:
            led_start, led_end = leds.get_group_led_range(group)

            for i in range(led_start, led_end):
                self.__set_led_fill_color(leds.led_diameter, i, rgb)

    def __set_led_fill_color(self, led_diameter: int, led_index: int, rgb: Tuple[int, int, int]):
        LEDS_PER_ROW = math.floor(self.width / led_diameter)
        LED_RADIUS = led_diameter / 2

        led_center_point = Point(LED_RADIUS + led_diameter * (led_index % LEDS_PER_ROW),
                                 LED_RADIUS + led_diameter * (led_index // LEDS_PER_ROW))

        top_left_point = Point(led_center_point.x - LED_RADIUS,
                               led_center_point.y - LED_RADIUS)
        bottom_right_point = Point(led_center_point.x + LED_RADIUS,
                                   led_center_point.y + LED_RADIUS)

        oval_hash = hash(Oval(top_left_point.x, top_left_point.y,
                              bottom_right_point.x, bottom_right_point.y))

        self.elements[oval_hash].set_fill_color(convert_to_hex(*rgb))

    def __eq__(self, right_value: Any) -> bool:
        if (isinstance(right_value, FakeCanvasGui)):
            self_gui_elements = Counter(self.elements.values())
            right_value_gui_elements = Counter(right_value.elements.values())

            return self_gui_elements == right_value_gui_elements

        return False


class Element(ABC):
    @property
    @abstractmethod
    def fill_color(self) -> str:
        pass

    @abstractmethod
    def set_fill_color(self, color: str):
        pass

    @abstractmethod
    def __eq__(self, right_value: Any) -> bool:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass


class Oval(Element):
    def __init__(self, left_most_x: int, top_most_y: int, right_most_x: int, bottom_most_y: int):
        self.left_most_x = left_most_x
        self.top_most_y = top_most_y

        self.right_most_x = right_most_x
        self.bottom_most_y = bottom_most_y

        self.__fill_color = '#000000'

    @property
    def fill_color(self) -> str:
        return self.__fill_color

    def set_fill_color(self, color: str):
        self.__fill_color = color

    def __eq__(self, right_value: Any) -> bool:
        if (isinstance(right_value, Oval)):
            return (self.left_most_x == right_value.left_most_x
                    and self.top_most_y == right_value.top_most_y
                    and self.right_most_x == right_value.right_most_x
                    and self.bottom_most_y == right_value.bottom_most_y
                    and self.fill_color == right_value.fill_color)

        return False

    def __repr__(self) -> str:
        return f'Oval(left_most_x={self.left_most_x}, top_most_y={self.top_most_y}, right_most_x={self.right_most_x}, bottom_most_y={self.bottom_most_y}, fill_color={self.fill_color})'

    def __hash__(self) -> int:
        return hash((self.left_most_x, self.top_most_y,
                     self.right_most_x, self.bottom_most_y))


class Text(Element):
    def __init__(self, center_x: int, center_y: int, text: str, font: Font, fill_color: str):
        self.center_x = center_x
        self.center_y = center_y

        self.text = text
        self.font = font
        self.__fill_color = fill_color

    @property
    def fill_color(self) -> str:
        return self.__fill_color

    def set_fill_color(self, color: str):
        self.__fill_color = color

    def __eq__(self, right_value: Any) -> bool:
        if (isinstance(right_value, Text)):
            return (self.center_x == right_value.center_x
                    and self.center_y == right_value.center_y
                    and self.text == right_value.text
                    and self.font == right_value.font
                    and self.fill_color == right_value.fill_color)

        return False

    def __repr__(self) -> str:
        return f'Text(center_x={self.center_x}, center_y={self.center_y}, text={self.text}, font={self.font}, fill_color={self.fill_color})'

    def __hash__(self) -> int:
        return hash((self.center_x, self.center_y, self.text))


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


def create_gui_after_init(gui_width: int, leds: GraphicGroupedLeds) -> FakeCanvasGui:
    FONT_NAME = 'Arial'
    FONT_SIZE = int((leds.led_diameter + 5) / len(str(leds.number_of_leds)))
    FONT_STYLE = 'bold'
    FILL_COLOR = "#ffffff"

    LEDS_PER_ROW = math.floor(gui_width / leds.led_diameter)
    LED_RADIUS = leds.led_diameter / 2

    gui = FakeCanvasGui()

    for i in range(leds.start_led, leds.end_led):
        led_center_point = Point(LED_RADIUS + leds.led_diameter * (i % LEDS_PER_ROW),
                                 LED_RADIUS + leds.led_diameter * (i // LEDS_PER_ROW))

        top_left_point = Point(led_center_point.x - LED_RADIUS,
                               led_center_point.y - LED_RADIUS)
        bottom_right_point = Point(led_center_point.x + LED_RADIUS,
                                   led_center_point.y + LED_RADIUS)

        gui.create_oval(top_left_point.x, top_left_point.y,
                        bottom_right_point.x, bottom_right_point.y)

        font = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)
        text = str(i)
        gui.create_text(led_center_point.x, led_center_point.y, text, font, FILL_COLOR)

    gui.update()

    return gui


class TestConstructor(unittest.TestCase):
    def test_valid_led_ranges(self):
        VALID_LED_RANGES = [(0, 0), (0, 1), (0, 150), (1, 1), (1, 150)]

        for valid_led_range in VALID_LED_RANGES:
            with self.subTest(led_range=valid_led_range):

                group_led_ranges = []
                gui = FakeCanvasGui()

                leds = GraphicGroupedLeds(valid_led_range, group_led_ranges, gui)

                expected_gui = create_gui_after_init(gui.width, leds)
                self.assertEqual(gui, expected_gui)

    def test_led_ranges_where_start_is_greater_than_end(self):
        INVALID_LED_RANGES = [(-1, 0), (0, -1), (-1, -1),
                              (-10, 0), (0, -10),
                              (1, 0), (10, 0),
                              (10, 9), (10, 5)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(ValueError):
                    group_led_ranges = []
                    gui = FakeCanvasGui()

                    GraphicGroupedLeds(invalid_led_range, group_led_ranges, gui)

    def test_led_ranges_where_start_is_not_int(self):
        INVALID_LED_RANGES = [(0.0, 1), (1.0, 10), (100.0, 200)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(TypeError):
                    group_led_ranges = []
                    gui = FakeCanvasGui()

                    GraphicGroupedLeds(invalid_led_range, group_led_ranges, gui)

    def test_led_ranges_where_end_is_float(self):
        INVALID_LED_RANGES = [(0, 0.0), (0, 1.0), (0, 100.0)]

        for invalid_led_range in INVALID_LED_RANGES:
            with self.subTest(led_range=invalid_led_range):

                with self.assertRaises(TypeError):
                    group_led_ranges = []
                    gui = FakeCanvasGui()

                    GraphicGroupedLeds(invalid_led_range, group_led_ranges, gui)

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

    def check_valid_group_led_ranges(self, led_range: Tuple[int, int], valid_group_led_ranges: List[Tuple[int, int]]):
        for group_led_ranges in valid_group_led_ranges:
            with self.subTest(led_range=led_range, group_led_ranges=group_led_ranges):

                gui = FakeCanvasGui()

                leds = GraphicGroupedLeds(led_range, group_led_ranges, gui)

                expected_gui = create_gui_after_init(gui.width, leds)
                self.assertEqual(gui, expected_gui)

    def check_invalid_group_led_ranges(self, led_range: Tuple[int, int], invalid_group_led_ranges: List[Tuple[int, int]]):
        for group_led_ranges in invalid_group_led_ranges:
            with self.subTest(led_range=led_range, group_led_ranges=group_led_ranges):

                with self.assertRaises(ValueError):
                    gui = FakeCanvasGui()

                    GraphicGroupedLeds(led_range, group_led_ranges, gui)


class TestSetGroupRGB(unittest.TestCase):
    LED_RANGE = (0, 100)
    GROUP_LED_RANGES = [(0, 10), (10, 20), (20, 30)]

    NUMBER_OF_GROUPS = len(GROUP_LED_RANGES)

    BLACK_RGB = (0, 0, 0)

    GROUP_0 = 0
    GROUP_1 = 1
    GROUP_2 = 2

    def setUp(self):
        self.gui = FakeCanvasGui()
        self.leds = GraphicGroupedLeds(self.LED_RANGE, self.GROUP_LED_RANGES, self.gui)

        self.gui_after_init = create_gui_after_init(self.gui.width, self.leds)

        assert self.gui == self.gui_after_init

    def test_set_one_group(self):
        RGB = (10, 11, 12)

        GROUP_RGBS = [(self.GROUP_0, RGB)]

        self.leds.set_group_rgbs(GROUP_RGBS)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_1), self.BLACK_RGB)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_2), self.BLACK_RGB)

        self.gui_after_init.set_group_rgbs(self.leds, GROUP_RGBS)
        self.assertEqual(self.gui, self.gui_after_init)

    def test_set_no_group(self):
        GROUP_RGBS = []

        self.leds.set_group_rgbs(GROUP_RGBS)

        for group in range(self.NUMBER_OF_GROUPS):
            with self.subTest(group=group):
                self.assertEqual(self.leds.get_group_rgb(group), self.BLACK_RGB)

        self.gui_after_init.set_group_rgbs(self.leds, GROUP_RGBS)
        self.assertEqual(self.gui, self.gui_after_init)

    def test_set_multiple_groups(self):
        RGB_0 = (1, 2, 3)
        RGB_1 = (4, 5, 6)
        RGB_2 = (7, 8, 9)

        GROUP_RGBS_0 = [(self.GROUP_0, RGB_0)]
        GROUP_RGBS_1 = [(self.GROUP_1, RGB_1)]
        GROUP_RGBS_2 = [(self.GROUP_2, RGB_2)]

        self.leds.set_group_rgbs(GROUP_RGBS_0)
        self.leds.set_group_rgbs(GROUP_RGBS_1)
        self.leds.set_group_rgbs(GROUP_RGBS_2)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB_0)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_1), RGB_1)
        self.assertEqual(self.leds.get_group_rgb(self.GROUP_2), RGB_2)

        self.gui_after_init.set_group_rgbs(self.leds, GROUP_RGBS_0)
        self.gui_after_init.set_group_rgbs(self.leds, GROUP_RGBS_1)
        self.gui_after_init.set_group_rgbs(self.leds, GROUP_RGBS_2)
        self.assertEqual(self.gui, self.gui_after_init)

    def test_set_same_group_multiple_times_separate_calls(self):
        RGB_OLD = (10, 11, 12)
        RGB_NEW = (100, 110, 120)

        GROUP_RGBS_OLD = [(self.GROUP_0, RGB_OLD)]
        GROUP_RGBS_NEW = [(self.GROUP_0, RGB_NEW)]

        self.leds.set_group_rgbs(GROUP_RGBS_OLD)
        self.leds.set_group_rgbs(GROUP_RGBS_NEW)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB_NEW)

        self.gui_after_init.set_group_rgbs(self.leds, GROUP_RGBS_OLD)
        self.gui_after_init.set_group_rgbs(self.leds, GROUP_RGBS_NEW)
        self.assertEqual(self.gui, self.gui_after_init)

    def test_set_same_group_multiple_times_same_call(self):
        RGB_OLD = (10, 11, 12)
        RGB_NEW = (100, 110, 120)

        GROUP_RGBS = [(self.GROUP_0, RGB_OLD), (self.GROUP_0, RGB_NEW)]

        self.leds.set_group_rgbs(GROUP_RGBS)

        self.assertEqual(self.leds.get_group_rgb(self.GROUP_0), RGB_NEW)

        self.gui_after_init.set_group_rgbs(self.leds, GROUP_RGBS)
        self.assertEqual(self.gui, self.gui_after_init)

    def test_no_groups(self):
        LED_RANGE = (0, 100)
        GROUP_LED_RANGES = []
        gui = FakeCanvasGui()

        leds = GraphicGroupedLeds(LED_RANGE, GROUP_LED_RANGES, gui)

        GROUPS = [0, 1, 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):
                    rgb = (10, 20, 30)
                    group_rgbs = [(group, rgb)]

                    leds.set_group_rgbs(group_rgbs)

                self.assertEqual(self.gui, self.gui_after_init)

    def test_group_less_than_0(self):
        GROUPS = [-1, -2, -100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(ValueError):
                    rgb = (10, 20, 30)

                    group_rgbs = [(group, rgb)]

                    self.leds.set_group_rgbs(group_rgbs)

                self.assertEqual(self.gui, self.gui_after_init)

    def test_group_exceeds_max_group(self):
        GROUPS = [self.NUMBER_OF_GROUPS, self.NUMBER_OF_GROUPS + 1, self.NUMBER_OF_GROUPS + 100]

        for group in GROUPS:
            with self.subTest(group=group):

                with self.assertRaises(IndexError):
                    rgb = (10, 20, 30)

                    group_rgbs = [(group, rgb)]

                    self.leds.set_group_rgbs(group_rgbs)

                self.assertEqual(self.gui, self.gui_after_init)
