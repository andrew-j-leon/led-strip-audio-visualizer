import abc
import unittest
from typing import Dict

from led_strip.graphic_led_strip import GraphicLedStrip
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

    def create_oval(self, left_most_x: int, top_most_y: int, right_most_x: int, bottom_most_y: int, fill_color: str):
        element = Oval(left_most_x, top_most_y, right_most_x, bottom_most_y, fill_color)
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


class TestConstructor(unittest.TestCase):

    def test_led_ranges(self):
        VALID_LED_RANGES = [(0, 0), (3, 3), (0, 150), (1, 150)]
        GROUP_INDEX_TO_LED_RANGE = []
        GUI = FakeGui()

        for VALID_LED_RANGE in VALID_LED_RANGES:
            with self.subTest(f'led_range={VALID_LED_RANGE}'):

                GraphicLedStrip(VALID_LED_RANGE, GROUP_INDEX_TO_LED_RANGE, GUI)

        INVALID_LED_RANGES = [(-1, 0), (-2, -1), (-10, -1), (-1, -1),
                              (1, 0), (2, 0), (10, 0)]

        for INVALID_LED_RANGE in INVALID_LED_RANGES:

            with self.subTest(f'led_range={INVALID_LED_RANGE}'):

                with self.assertRaises(ValueError):
                    GraphicLedStrip(INVALID_LED_RANGE, GROUP_INDEX_TO_LED_RANGE, GUI)

    def test_group_index_to_led_range(self):
        LED_RANGE = (10, 150)

        VALID_GROUP_LED_RANGES = [
            [(0, 0)], [(200, 200)],
            [(9, 9)],
            [(10, 10)],
            [(150, 150)],
            [(151, 151)],
            [(10, 11)],
            [(10, 20), (20, 30)],
            [(10, 20), (10, 30)],
            [(10, 50), (50, 100), (100, 150)],
            [(149, 150)], [(10, 11)]
        ]

        GUI = FakeGui()

        for GROUP_LED_RANGE in VALID_GROUP_LED_RANGES:

            with self.subTest(f'group_led_ranges={GROUP_LED_RANGE}'):

                GraphicLedStrip(LED_RANGE, GROUP_LED_RANGE, GUI)

        INVALID_GROUP_LED_RANGES = [
            [(9, 10)], [(0, 10)],
            [(150, 151)], [(149, 151)], [(150, 151)],
            [(10, 151)],
            [(-1, 0)], [(-2, -1)]
        ]

        for GROUP_LED_RANGE in INVALID_GROUP_LED_RANGES:

            with self.subTest(f'group_led_ranges={GROUP_LED_RANGE}'):

                with self.assertRaises(ValueError):
                    GraphicLedStrip(LED_RANGE, GROUP_LED_RANGE, GUI)


class TestNumberOfGroups(unittest.TestCase):

    def test_0_groups(self):
        LED_RANGE = (0, 100)
        GROUP_INDEX_TO_LED_RAGE = []
        GUI = FakeGui()

        led_strip = GraphicLedStrip(LED_RANGE, GROUP_INDEX_TO_LED_RAGE, GUI)

        actual = led_strip.number_of_groups
        expected = 0

        self.assertEqual(actual, expected)

    def test_1_group(self):
        LED_RANGE = (0, 100)
        GROUP_INDEX_TO_LED_RAGE = [(10, 20)]
        GUI = FakeGui()

        led_strip = GraphicLedStrip(LED_RANGE, GROUP_INDEX_TO_LED_RAGE, GUI)

        actual = led_strip.number_of_groups
        expected = 1

        self.assertEqual(actual, expected)

    def test_many_groups(self):
        LED_RANGE = (0, 100)
        GROUP_INDEX_TO_LED_RAGE = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
                                   (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
        GUI = FakeGui()

        led_strip = GraphicLedStrip(LED_RANGE, GROUP_INDEX_TO_LED_RAGE, GUI)

        actual = led_strip.number_of_groups
        expected = len(GROUP_INDEX_TO_LED_RAGE)

        self.assertEqual(actual, expected)


class TestNumberOfLeds(unittest.TestCase):
    def test_0_leds(self):
        LED_RANGE = (0, 0)
        GROUP_INDEX_TO_LED_RAGE = []
        GUI = FakeGui()

        led_strip = GraphicLedStrip(LED_RANGE, GROUP_INDEX_TO_LED_RAGE, GUI)

        actual = led_strip.number_of_leds
        expected = 0

        self.assertEqual(actual, expected)

    def test_1_led(self):
        LED_RANGE = (0, 1)
        GROUP_INDEX_TO_LED_RAGE = []
        GUI = FakeGui()

        led_strip = GraphicLedStrip(LED_RANGE, GROUP_INDEX_TO_LED_RAGE, GUI)

        actual = led_strip.number_of_leds
        expected = 1

        self.assertEqual(actual, expected)

    def test_many_leds(self):
        LED_RANGE = (0, 150)
        GROUP_INDEX_TO_LED_RAGE = []
        GUI = FakeGui()

        led_strip = GraphicLedStrip(LED_RANGE, GROUP_INDEX_TO_LED_RAGE, GUI)

        actual = led_strip.number_of_leds
        expected = 150

        self.assertEqual(actual, expected)


class TestSetGroupColor(unittest.TestCase):

    def test_set_valid_color(self):
        LED_RANGE = (0, 100)
        GROUP_INDEX_TO_LED_RAGE = [(10, 20), (20, 30)]
        GUI = FakeGui()

        led_strip = GraphicLedStrip(LED_RANGE, GROUP_INDEX_TO_LED_RAGE, GUI)

        GROUP = 0
        RGB = (10, 20, 30)

        led_strip.enqueue_group_color(GROUP, RGB)

        self.assertFalse(led_strip.group_is_color(GROUP, RGB))

        led_strip.show_colors()

        self.assertTrue(led_strip.group_is_color(GROUP, RGB))
