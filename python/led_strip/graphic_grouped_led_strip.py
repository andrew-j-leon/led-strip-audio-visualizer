from typing import Dict, List, Tuple

import math

import PySimpleGUI as sg

from gui.window import Window

from util import NonNegativeInteger, NonNegativeIntegerRange, rgb_to_hex

# LedStrip
_START_INDEX = 0
_END_INDEX = 1


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

    def get_tuple(self) -> Tuple[int, int]:
        return (self.__x, self.__y)


class GraphicGroupedLedStrip:
    def __init__(self, led_index_range: Tuple[int, int], group_index_to_led_range: List[Tuple[int, int]]):
        # end_led_index = exclusive ; start_led_index = inclusive

        start = NonNegativeInteger(led_index_range[0])
        end = NonNegativeInteger(led_index_range[1])
        self.__led_index_range = NonNegativeIntegerRange(start, end)

        self.__queued_color_changes: list = []

        canvas_ = sg.Canvas(size=(1350, 600), background_color='#4a4a4a', key="canvas")
        layout: List[List[sg.Element]] = [[canvas_]]
        self.__window: Window = Window('LED Strip Visualizer', layout=layout, resizable=True, element_padding=(0, 0),
                                       margins=(0, 0), titlebar_background_color="#000917", titlebar_text_color="#8a8a8a", disable_close=True,
                                       disable_minimize=False)

        self.__window.read(timeout=0)
        self.__led_index_to_tkinter_id: Dict[int, int] = dict()
        self.__draw_and_store_leds()

        self._group_index_to_led_range: List[NonNegativeIntegerRange] = []

        for led_range in group_index_to_led_range:
            start = NonNegativeInteger(led_range[0])
            end = NonNegativeInteger(led_range[1])
            self._group_index_to_led_range.append(NonNegativeIntegerRange(start, end))

        self.__group_index_to_its_rgb: List[Tuple[int, int, int]] = [(0, 0, 0) for i in range(self.get_number_of_groups())]

    def __del__(self):
        # Graphic
        try:
            self.__window.close()

        except AttributeError:
            pass

    def _recolor_leds(self, group_index: int, rgb: Tuple[int, int, int]):

        range_ = self._group_index_to_led_range[group_index]

        start_index = range_.start
        end_index = range_.end

        for led_index in range(start_index, end_index):
            tkinter_id = self.__led_index_to_tkinter_id[led_index]

            self.__window["canvas"].TKCanvas.itemconfig(tkinter_id, fill=rgb_to_hex(*rgb))

    # Graphic

    def __draw_and_store_leds(self):
        led_diameter = 30
        MAX_X_COORDINATE = self.__window["canvas"].get_size()[0]
        LEDS_PER_ROW = math.floor(MAX_X_COORDINATE / led_diameter)
        LED_RADIUS = led_diameter / 2

        BLACK_HEX = "#000000"
        WHITE_HEX = "#ffffff"

        # Draw the LEDs on the TKinter Canvas
        for i in range(self._get_start_index(), self._get_end_index() + 1):
            # center coordinates of the LED
            led_center_point = Point(x_value=LED_RADIUS + led_diameter * (i % LEDS_PER_ROW), y_value=LED_RADIUS + led_diameter * (i // LEDS_PER_ROW),)

            top_left_point = Point(led_center_point.x_value - LED_RADIUS, led_center_point.y_value - LED_RADIUS)
            bottom_right_point = Point(led_center_point.x_value + LED_RADIUS, led_center_point.y_value + LED_RADIUS)

            self.__led_index_to_tkinter_id[i] = self.__window["canvas"].TKCanvas.create_oval(top_left_point.get_tuple(),
                                                                                             bottom_right_point.get_tuple(), fill=BLACK_HEX)

            # This font size ensures that the longest index values are as large as possible while still fitting inside
            # their LEDs
            font_size_pixels = (led_diameter + 5) / len(str(self.get_number_of_leds()))
            font = ('Arial', int(-1 * font_size_pixels), 'bold')

            # Draw the index numbers in each led
            self.__window["canvas"].TKCanvas.create_text(led_center_point.x_value, led_center_point.y_value,
                                                         text=str(i), fill=WHITE_HEX, font=font)

        self.__window.read(timeout=0)

    # Grouped
    def get_number_of_groups(self) -> int:
        return len(self._group_index_to_led_range)

    def set_group_color(self, group_index: int, rgb: Tuple[int, int, int]):
        self._enqueue_color_change_by_index(group_index, rgb)

    def group_is_color(self, group_index: int, rgb: Tuple[int, int, int]) -> bool:
        return self.__group_index_to_its_rgb[group_index] == rgb

    # LedStrip
    def get_number_of_leds(self) -> int:
        return self._get_end_index() - self._get_start_index() + 1

    def show(self):
        self._show()
        self.__queued_color_changes.clear()

    def _show(self):
        # graphic
        for queued_color_change in self.__queued_color_changes:
            self._recolor_leds(*queued_color_change)

        self.__window.read(timeout=0)

        # grouped
        for queued_color_change in self.__queued_color_changes:
            group_index, rgb = queued_color_change

            self.__group_index_to_its_rgb[group_index] = rgb

    def _get_start_index(self) -> NonNegativeInteger:
        return self.__led_index_range.start

    def _get_end_index(self) -> NonNegativeInteger:
        return self.__led_index_range.end - 1

    def _enqueue_color_change_by_index(self, index: int, *args):
        self.__queued_color_changes.append((index, *args))
