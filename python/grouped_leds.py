import math
from abc import ABC, abstractmethod
from typing import Dict, Iterable, List, Tuple

from libraries.canvas_gui import CanvasGui
from libraries.serial import Serial
from non_negative_int_range import NonNegativeIntRange
from util import RGB, Font, rgb_to_hex


class Point:
    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    def __repr__(self) -> str:
        return f'Point({self.x}, {self.y})'


class GroupedLeds(ABC):
    @property
    @abstractmethod
    def number_of_groups(self) -> int:
        pass

    @property
    @abstractmethod
    def number_of_leds(self) -> int:
        pass

    @property
    @abstractmethod
    def start_led(self) -> int:
        '''
            Returns:
                `int`: Inclusive start led index.
        '''

    @property
    @abstractmethod
    def end_led(self) -> int:
        '''
            Returns:
                `int`: Exclusive end led index.
        '''

    @abstractmethod
    def get_group_led_ranges(self, group: int) -> List[Tuple[int, int]]:
        pass

    @abstractmethod
    def get_group_color(self, group: int) -> RGB:
        pass

    @abstractmethod
    def set_colors(self, group_colors: Iterable[Tuple[int, Tuple[int, int, int]]]):
        pass


class ProductionGroupedLeds(GroupedLeds):
    def __init__(self, led_range: Tuple[int, int] = (0, 0),
                 group_led_ranges: List[Iterable[Tuple[int, int]]] = []):
        start, end = led_range

        self.__led_strip_range = NonNegativeIntRange(start, end)
        self.__group_led_ranges: List[List[NonNegativeIntRange]] = []

        for group in range(len(group_led_ranges)):
            led_ranges: List[NonNegativeIntRange] = []

            for start, end in group_led_ranges[group]:
                led_range = NonNegativeIntRange(start, end)

                if (led_range not in self.__led_strip_range):
                    raise ValueError(f'group_led_ranges[{group}] contains {(start, end)}, which '
                                     f'is not within the bounds of {self.__led_strip_range}.')

                led_ranges.append(led_range)

            self.__group_led_ranges.append(led_ranges)

        self.__group_colors = [RGB()] * len(group_led_ranges)

    @property
    def number_of_groups(self) -> int:
        return len(self.__group_led_ranges)

    @property
    def number_of_leds(self) -> int:
        return self.__led_strip_range.end - self.__led_strip_range.start

    @property
    def start_led(self) -> int:
        return self.__led_strip_range.start

    @property
    def end_led(self) -> int:
        return self.__led_strip_range.end

    def get_group_led_ranges(self, group):
        if (group < 0):
            raise ValueError(f'group must be >= 0, but was {group}.')

        led_ranges: List[Tuple[int, int]] = []

        for led_range in self.__group_led_ranges[group]:
            led_ranges.append((led_range.start, led_range.end))

        return led_ranges

    def get_group_color(self, group):
        if (group < 0):
            raise ValueError(f'group must be >= 0, but was {group}.')

        return self.__group_colors[group]

    def set_colors(self, group_colors):
        for group, color in group_colors:
            self._set_color(group, RGB(*color))

    def _set_color(self, group: int, color: RGB):
        if (group < 0):
            raise ValueError(f'group must be >= 0, but was {group}.')

        self.__group_colors[group] = color


class GraphicGroupedLeds(ProductionGroupedLeds):
    def __init__(self, led_range: Tuple[int, int], group_led_ranges: List[Iterable[Tuple[int, int]]],
                 gui: CanvasGui, led_diameter: int = 30):
        super().__init__(led_range, group_led_ranges)

        self.__gui = gui
        self.__gui.update()

        self.__led_diameter = led_diameter

        self.__led_element_ids: Dict[int, int] = dict()
        self.__draw_and_store_leds()

    @property
    def led_diameter(self) -> int:
        return self.__led_diameter

    def set_colors(self, group_colors):
        super().set_colors(group_colors)

        self.__gui.update()

    def _set_color(self, group: int, color: RGB):
        self.__recolor_leds(group, color)

        super()._set_color(group, color)

    def __recolor_leds(self, group: int, color: RGB):
        for start, end in self.get_group_led_ranges(group):
            for led in range(start, end):
                element_id = self.__led_element_ids[led]
                self.__gui.set_element_fill_color(element_id, rgb_to_hex(color.red, color.green, color.blue))

    def __draw_and_store_leds(self):
        FONT_NAME = 'Arial'
        FONT_SIZE = int((self.led_diameter + 5) / len(str(self.number_of_leds)))
        FONT_STYLE = 'bold'
        TEXT_COLOR = "#ffffff"

        LEDS_PER_ROW = math.floor(self.__gui.width / self.led_diameter)
        LED_RADIUS = self.led_diameter / 2

        for i in range(self.start_led, self.end_led):
            led_center_point = Point(LED_RADIUS + self.led_diameter * (i % LEDS_PER_ROW),
                                     LED_RADIUS + self.led_diameter * (i // LEDS_PER_ROW))

            top_left_point = Point(led_center_point.x - LED_RADIUS,
                                   led_center_point.y - LED_RADIUS)
            bottom_right_point = Point(led_center_point.x + LED_RADIUS,
                                       led_center_point.y + LED_RADIUS)

            self.__led_element_ids[i] = self.__gui.create_oval(top_left_point.x, top_left_point.y,
                                                               bottom_right_point.x, bottom_right_point.y)

            font = Font(FONT_NAME, FONT_SIZE, FONT_STYLE)
            text = str(i)
            self.__gui.create_text(led_center_point.x, led_center_point.y, text, font, TEXT_COLOR)

        self.__gui.update()


GROUP_SETUP_START_OF_MESSAGE_CODE = 0xFE
GROUP_SETUP_END_OF_MESSAGE_CODE = 0xFF

GROUP_COLOR_START_OF_MESSAGE_CODE = 0xFE
GROUP_COLOR_END_OF_MESSAGE_CODE = 0xFF

BYTE_ORDER = 'little'


class SerialGroupedLeds(ProductionGroupedLeds):

    class SerialWriter:
        def __init__(self, serial: Serial, divisor: int):
            self.__dividend = 0
            self.__divisor = divisor

            if (divisor == 0):
                raise ValueError("Received a modulus divisor of 0.")

            self.__serial = serial

        def write(self, data: bytes):
            for byte_ in data:
                byte_ = byte_.to_bytes(length=1, byteorder=BYTE_ORDER)

                if (self.__dividend == 0):
                    echo = bytes()
                    while (echo == bytes()):
                        self.__serial.write(byte_)
                        echo = self.__serial.read(1)

                else:
                    self.__serial.write(byte_)

                self.__dividend = (self.__dividend + 1) % self.__divisor

    def __init__(self, led_range: Tuple[int, int], group_led_ranges: List[Iterable[Tuple[int, int]]],
                 serial: Serial, brightness: int):
        super().__init__(led_range, group_led_ranges)

        self.__brightness = brightness

        # Serial logic
        if (brightness < 0 or brightness > 255):
            raise ValueError(f'brightness must be >= 0 and <= 255, but was {brightness}.')

        if (self.number_of_leds > serial.number_of_leds):
            raise ValueError(f"The serial connection stated that there are {serial.number_of_leds} LEDs, but this GroupedLedsQueue object is set for {self.number_of_leds} LEDs.")

        if (self.end_led > serial.number_of_leds and self.number_of_leds > 0):
            raise ValueError(f"The serial connection stated that its led indicies range from 0 (inclusive) to {serial.number_of_leds} "
                             "(exclusive), but this GroupedLedsQueue ranges from {self.start_led} (inclusive) to {self.end_led} (exclusive).")

        DIVISOR = int.from_bytes(serial.read(1), byteorder="little")
        self.__serial_writer = self.SerialWriter(serial, DIVISOR)

        self.__configure_serial()

    def set_colors(self, group_colors):
        self.__send_bytes(GROUP_COLOR_START_OF_MESSAGE_CODE.to_bytes(length=1, byteorder=BYTE_ORDER))
        self.__send_bytes(len(group_colors).to_bytes(1, BYTE_ORDER))

        super().set_colors(group_colors)

        self.__send_bytes(GROUP_COLOR_END_OF_MESSAGE_CODE.to_bytes(1, BYTE_ORDER))

    def _set_color(self, group: int, color: RGB):
        self.__send_packet(group, color)

        super()._set_color(group, color)

    def __configure_serial(self):
        self.__send_bytes(self.__brightness.to_bytes(length=1, byteorder=BYTE_ORDER))
        self.__send_bytes(self.number_of_groups.to_bytes(length=1, byteorder=BYTE_ORDER))
        self.__send_bytes(GROUP_SETUP_START_OF_MESSAGE_CODE.to_bytes(length=1, byteorder=BYTE_ORDER))

        for group in range(self.number_of_groups):
            led_ranges = self.get_group_led_ranges(group)
            led_ranges_length_bytes = len(led_ranges).to_bytes(length=1, byteorder=BYTE_ORDER)
            self.__send_bytes(led_ranges_length_bytes)

            for start, end in led_ranges:
                start_bytes = start.to_bytes(length=2, byteorder=BYTE_ORDER)
                end_bytes = end.to_bytes(length=2, byteorder=BYTE_ORDER)
                checksum = (sum(start_bytes) + sum(end_bytes) + sum(led_ranges_length_bytes)) % 256

                packet = start_bytes + end_bytes + checksum.to_bytes(length=1, byteorder=BYTE_ORDER)
                self.__send_bytes(packet)

        self.__send_bytes(GROUP_SETUP_END_OF_MESSAGE_CODE.to_bytes(length=1, byteorder=BYTE_ORDER))

    def __send_packet(self, group: int, color: RGB):
        packet = group.to_bytes(length=1, byteorder=BYTE_ORDER)
        packet += color.red.to_bytes(1, BYTE_ORDER)
        packet += color.green.to_bytes(1, BYTE_ORDER)
        packet += color.blue.to_bytes(1, BYTE_ORDER)

        self.__send_bytes(packet)

        check_sum = (sum(packet) % 256).to_bytes(length=1, byteorder=BYTE_ORDER)

        self.__send_bytes(check_sum)

    def __send_bytes(self, bytes_: bytes):
        self.__serial_writer.write(bytes_)


class GroupedLedsQueue:
    def __init__(self, grouped_leds: GroupedLeds = ProductionGroupedLeds()):
        self.__grouped_leds = grouped_leds
        self.__color_queue: List[Tuple[int, RGB]] = []

    @property
    def number_of_groups(self) -> int:
        return self.__grouped_leds.number_of_groups

    @property
    def number_of_queued_colors(self) -> int:
        return len(self.__color_queue)

    def enqueue_color(self, group: int, rgb: Iterable[int]):
        if (group < 0 or group >= self.number_of_groups):
            raise IndexError(f'Tried to enqueue RGB {repr(rgb)} into group {group}, but valid group '
                             f'indices range from 0 (inclusive) to {self.number_of_groups} (exclusive).')

        self.__color_queue.append((group, RGB(*rgb)))

    def group_is_color(self, group: int, rgb: Iterable[int]) -> bool:
        return self.__grouped_leds.get_group_color(group) == rgb

    def show_queued_colors(self):
        self.__grouped_leds.set_colors(self.__color_queue)

    def clear_queued_colors(self):
        self.__color_queue.clear()

    def turn_off(self):
        self.clear_queued_colors()

        BLACK = (0, 0, 0)

        for group in range(self.number_of_groups):
            self.enqueue_color(group, BLACK)

        self.show_queued_colors()
        self.clear_queued_colors()
