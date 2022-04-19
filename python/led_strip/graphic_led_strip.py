import math
from typing import Dict, List, Tuple

from libraries.gui import Font, Gui
from util import NonNegativeInteger, NonNegativeIntegerRange, rgb_to_hex


# Graphic
class Point:
    def __init__(self, x_value: int, y_value: int):
        self.__x = x_value
        self.__y = y_value

    @property
    def x_value(self) -> int:
        return self.__x

    @property
    def y_value(self) -> int:
        return self.__y


class GraphicLedStrip:
    def __init__(self, led_range: Tuple[int, int], group_led_ranges: List[Tuple[int, int]], gui: Gui):
        start = NonNegativeInteger(led_range[0])
        end = NonNegativeInteger(led_range[1])

        self.__led_range = NonNegativeIntegerRange(start, end)

        self.__color_queue: List[Tuple(int, int, int)] = []

        self.__gui = gui

        self.__led_element_ids: Dict[int, int] = dict()
        self.__draw_and_store_leds()

        self._group_led_ranges: List[NonNegativeIntegerRange] = []

        for i in range(len(group_led_ranges)):
            start, end = group_led_ranges[i]

            non_negative_integer_range = NonNegativeIntegerRange(start, end)

            if (non_negative_integer_range not in self.__led_range):
                raise ValueError(f'group_led_ranges[{i}]={(start, end)} is not within the bounds of led_range={led_range}.')

            self._group_led_ranges.append(non_negative_integer_range)

        self.__group_colors: List[Tuple[int, int, int]] = [(0, 0, 0)] * self.number_of_groups

    def __del__(self):
        try:
            self.__gui.close()

        except AttributeError:
            pass

    @property
    def number_of_groups(self) -> int:
        return len(self._group_led_ranges)

    @property
    def number_of_leds(self) -> int:
        return self.__led_range.end - self.__led_range.start

    def enqueue_group_color(self, group_index: int, rgb: Tuple[int, int, int]):
        self.__color_queue.append((group_index, rgb))

    def group_is_color(self, group_index: int, rgb: Tuple[int, int, int]) -> bool:
        return self.__group_colors[group_index] == rgb

    def show_colors(self):
        for queued_color_change in self.__color_queue:
            self._recolor_leds(*queued_color_change)

        self.__gui.update()

        for queued_color_change in self.__color_queue:
            group_index, rgb = queued_color_change

            self.__group_colors[group_index] = rgb

        self.__color_queue.clear()

    def _recolor_leds(self, group_index: int, rgb: Tuple[int, int, int]):
        range_ = self._group_led_ranges[group_index]

        start_index = range_.start
        end_index = range_.end

        for led_index in range(start_index, end_index):
            element_id = self.__led_element_ids[led_index]
            self.__gui.set_element_fill_color(element_id, rgb_to_hex(*rgb))

    def __draw_and_store_leds(self):
        led_diameter = 30
        MAX_X_COORDINATE = self.__gui.dimensions.width
        LEDS_PER_ROW = math.floor(MAX_X_COORDINATE / led_diameter)
        LED_RADIUS = led_diameter / 2

        BLACK_HEX = "#000000"
        WHITE_HEX = "#ffffff"

        # Draw the LEDs on the TKinter Canvas
        for i in range(self.__led_range.start, self.__led_range.end):
            # center coordinates of the LED
            led_center_point = Point(x_value=LED_RADIUS + led_diameter * (i % LEDS_PER_ROW), y_value=LED_RADIUS + led_diameter * (i // LEDS_PER_ROW),)

            top_left_point = Point(led_center_point.x_value - LED_RADIUS, led_center_point.y_value - LED_RADIUS)
            bottom_right_point = Point(led_center_point.x_value + LED_RADIUS, led_center_point.y_value + LED_RADIUS)

            self.__led_element_ids[i] = self.__gui.create_oval(top_left_point.x_value, top_left_point.y_value,
                                                               bottom_right_point.x_value, bottom_right_point.y_value,
                                                               fill_color=BLACK_HEX)

            # This font size ensures that the longest index values are as large as possible while still fitting inside
            # their LEDs
            font_size_pixels = (led_diameter + 5) / len(str(self.number_of_leds))

            # Draw the index numbers in each led
            font_size_pixels = (led_diameter + 5) / len(str(self.number_of_leds))
            font = Font(size=int(-1 * font_size_pixels), style='bold', color=WHITE_HEX)
            self.__gui.create_text(led_center_point.x_value, led_center_point.y_value, text=str(i), font=font)

        self.__gui.update()
