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
    def get_group_led_range(self, group: int) -> Tuple[int, int]:
        pass

    @abstractmethod
    def get_group_rgb(self, group: int) -> RGB:
        pass

    @abstractmethod
    def set_group_rgbs(self, group_rgbs: Iterable[Tuple[int, Iterable[int]]]):
        pass


class ProductionGroupedLeds(GroupedLeds):
    def __init__(self, led_range: Tuple[int, int] = (0, 0),
                 group_led_ranges: List[Tuple[int, int]] = []):
        start, end = led_range

        self.__led_range = NonNegativeIntRange(start, end)

        self.__group_led_ranges: List[NonNegativeIntRange] = []

        for i in range(len(group_led_ranges)):
            start, end = group_led_ranges[i]

            non_negative_integer_range = NonNegativeIntRange(start, end)

            if (non_negative_integer_range not in self.__led_range):
                raise ValueError(f'group_led_ranges[{i}]={(start, end)} is not within the bounds of led_range={led_range}.')

            self.__group_led_ranges.append(non_negative_integer_range)

        self.__group_colors = [RGB()] * len(group_led_ranges)

    @property
    def number_of_groups(self) -> int:
        return len(self.__group_led_ranges)

    @property
    def number_of_leds(self) -> int:
        return self.__led_range.end - self.__led_range.start

    @property
    def start_led(self) -> int:
        return self.__led_range.start

    @property
    def end_led(self) -> int:
        return self.__led_range.end

    def get_group_led_range(self, group: int) -> Tuple[int, int]:
        if (group < 0):
            raise ValueError(f'group must be >= 0, but was {group}.')

        non_negative_int_range = self.__group_led_ranges[group]

        return (non_negative_int_range.start, non_negative_int_range.end)

    def get_group_rgb(self, group: int) -> RGB:
        if (group < 0):
            raise ValueError(f'group must be >= 0, but was {group}.')

        return self.__group_colors[group]

    def set_group_rgbs(self, group_rgbs: Iterable[Tuple[int, Iterable[int]]]):
        for group, rgb in group_rgbs:
            self._set_group_rgbs(group, RGB(*rgb))

    def _set_group_rgbs(self, group: int, rgb: RGB):
        if (group < 0):
            raise ValueError(f'group must be >= 0, but was {group}.')

        self.__group_colors[group] = rgb


class GraphicGroupedLeds(ProductionGroupedLeds):
    def __init__(self, led_range: Tuple[int, int], group_led_ranges: List[Tuple[int, int]],
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

    def set_group_rgbs(self, group_rgbs: Iterable[Tuple[int, Iterable[int]]]):
        super().set_group_rgbs(group_rgbs)

        self.__gui.update()

    def _set_group_rgbs(self, group: int, rgb: RGB):
        self.__recolor_leds(group, rgb)

        super()._set_group_rgbs(group, rgb)

    def __recolor_leds(self, group: int, rgb: RGB):
        start, end = self.get_group_led_range(group)

        for i in range(start, end):
            element_id = self.__led_element_ids[i]

            self.__gui.set_element_fill_color(element_id, rgb_to_hex(rgb.red, rgb.green, rgb.blue))

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


class SerialGroupedLeds(ProductionGroupedLeds):
    def __init__(self, led_range: Tuple[int, int], group_led_ranges: List[Tuple[int, int]],
                 serial: Serial, brightness: int):
        super().__init__(led_range, group_led_ranges)

        # Serial logic
        if (brightness < 0 or brightness > 255):
            raise ValueError(f'brightness must be >= 0 and <= 255, but was {brightness}.')

        self.__serial = serial
        self.__brightness = brightness

        if (self.number_of_leds > serial.number_of_leds):
            raise ValueError(f"The serial connection stated that there are {serial.number_of_leds} leds, but this LedStrip object is set for {self.number_of_leds} leds.")

        if (self.end_led > serial.number_of_leds and self.number_of_leds > 0):
            raise ValueError(f"The serial connection stated that its led indicies range from 0 (inclusive) to {serial.number_of_leds} (exclusive), but this LedStrip ranges from {self.start_led} (inclusive) to {self.end_led} (exclusive).")

        self.__configure_serial()

    def set_group_rgbs(self, group_rgbs: Iterable[Tuple[int, Iterable[int]]]):
        self.__send_bytes(len(group_rgbs).to_bytes(length=1, byteorder="big"))

        super().set_group_rgbs(group_rgbs)

    def _set_group_rgbs(self, group: int, rgb: RGB):
        self.__send_packet(group, rgb)

        super()._set_group_rgbs(group, rgb)

    def __configure_serial(self):
        GROUPED_STRIP_TYPE = 1

        self.__send_bytes(self.__brightness.to_bytes(length=1, byteorder="big"))

        self.__send_bytes(GROUPED_STRIP_TYPE.to_bytes(length=1, byteorder="big"))
        self.__send_bytes(self.number_of_groups.to_bytes(length=1, byteorder="big"))

        # send group led ranges
        for group in range(self.number_of_groups):
            start, end = self.get_group_led_range(group)

            packet = (start.to_bytes(length=2, byteorder="big")
                      + end.to_bytes(length=2, byteorder="big"))

            self.__send_bytes(packet)

    def __send_packet(self, group_index: int, rgb: RGB):
        packet = group_index.to_bytes(length=1, byteorder="big")
        packet += rgb.red.to_bytes(1, "big")
        packet += rgb.green.to_bytes(1, "big")
        packet += rgb.blue.to_bytes(1, "big")

        self.__send_bytes(packet)

    def __send_bytes(self, bytes_: bytes):
        '''
            Sends the bytes_ over the serial one byte at a time. Continually resends
            the data if an acknowledgement is not received within serial's read timeout.
        '''
        for byte_ in bytes_:
            self.__send_byte_lossless(byte_)

    def __send_byte_lossless(self, byte_: int):
        '''
            Send a byte of data over serial. If an acknowledgement is
            not recieved within serial's read timeout, the byte is sent again. This continues
            indefinitely until an acknowledgement is received.
        '''
        echo = bytes()
        while (echo == bytes()):
            self.__serial.write(byte_.to_bytes(length=1, byteorder="big"))
            echo = self.__serial.read(1)
