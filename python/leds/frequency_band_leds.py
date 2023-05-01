import math
from abc import ABC, abstractmethod
from typing import Dict, Iterable, List, Set, Tuple

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


class FrequencyBandLeds(ABC):
    @property
    @abstractmethod
    def number_of_bands(self) -> int:
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
    def get_band_led_ranges(self, band: int) -> Tuple[int, int]:
        pass

    @abstractmethod
    def get_band_color(self, band: int) -> RGB:
        pass

    @abstractmethod
    def set_band_colors(self, band_colors: Iterable[Tuple[int, Iterable[int]]]):
        pass


class ProductionFrequencyBandLeds(FrequencyBandLeds):
    def __init__(self, led_range: Tuple[int, int] = (0, 0),
                 band_led_ranges: List[Iterable[Tuple[int, int]]] = []):
        start, end = led_range

        self.__led_strip_range = NonNegativeIntRange(start, end)
        self.__band_led_ranges: List[List[NonNegativeIntRange]] = []

        for band_number in range(len(band_led_ranges)):
            led_ranges: Set[Tuple(int, int)] = set()

            for start, end in band_led_ranges[band_number]:
                led_range = NonNegativeIntRange(start, end)

                if (led_range not in self.__led_strip_range):
                    raise ValueError(f'band_led_ranges[{band_number}] contains {(start, end)}, which '
                                     f'is not within the bounds of {self.__led_strip_range}.')

                led_ranges.add(led_range)

            self.__band_led_ranges.append(led_ranges)

        self.__band_colors = [RGB()] * len(band_led_ranges)

    @property
    def number_of_bands(self) -> int:
        return len(self.__band_led_ranges)

    @property
    def number_of_leds(self) -> int:
        return self.__led_strip_range.end - self.__led_strip_range.start

    @property
    def start_led(self) -> int:
        return self.__led_strip_range.start

    @property
    def end_led(self) -> int:
        return self.__led_strip_range.end

    def get_band_led_ranges(self, band: int) -> Set[Tuple[int, int]]:
        if (band < 0):
            raise ValueError(f'band must be >= 0, but was {band}.')

        led_ranges: Set[Tuple[int, int]] = set()

        for led_range in self.__band_led_ranges[band]:
            led_ranges.add((led_range.start, led_range.end))

        return led_ranges

    def get_band_color(self, band: int) -> RGB:
        if (band < 0):
            raise ValueError(f'band must be >= 0, but was {band}.')

        return self.__band_colors[band]

    def set_band_colors(self, band_colors: Iterable[Tuple[int, Iterable[int]]]):
        for band, rgb in band_colors:
            self._set_band_rgbs(band, RGB(*rgb))

    def _set_band_rgbs(self, band: int, rgb: RGB):
        if (band < 0):
            raise ValueError(f'band must be >= 0, but was {band}.')

        self.__band_colors[band] = rgb


class GraphicFrequencyBandLeds(ProductionFrequencyBandLeds):
    def __init__(self, led_range: Tuple[int, int], band_led_ranges: List[Iterable[Tuple[int, int]]],
                 gui: CanvasGui, led_diameter: int = 30):
        super().__init__(led_range, band_led_ranges)

        self.__gui = gui
        self.__gui.update()

        self.__led_diameter = led_diameter

        self.__led_element_ids: Dict[int, int] = dict()
        self.__draw_and_store_leds()

    @property
    def led_diameter(self) -> int:
        return self.__led_diameter

    def set_band_colors(self, band_colors: Iterable[Tuple[int, Iterable[int]]]):
        super().set_band_colors(band_colors)

        self.__gui.update()

    def _set_band_rgbs(self, band: int, rgb: RGB):
        self.__recolor_leds(band, rgb)

        super()._set_band_rgbs(band, rgb)

    def __recolor_leds(self, band: int, rgb: RGB):
        for start, end in self.get_band_led_ranges(band):
            for led in range(start, end):
                element_id = self.__led_element_ids[led]
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


BAND_SETUP_START_OF_MESSAGE_CODE = 0xFE
BAND_SETUP_END_OF_MESSAGE_CODE = 0xFF

BAND_COLOR_START_OF_MESSAGE_CODE = 0xFE
BAND_COLOR_END_OF_MESSAGE_CODE = 0xFF

BYTE_ORDER = 'little'


class SerialFrequencyBandLeds(ProductionFrequencyBandLeds):

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

    def __init__(self, led_range: Tuple[int, int], band_led_ranges: List[Iterable[Tuple[int, int]]],
                 serial: Serial, brightness: int):
        super().__init__(led_range, band_led_ranges)

        self.__brightness = brightness

        # Serial logic
        if (brightness < 0 or brightness > 255):
            raise ValueError(f'brightness must be >= 0 and <= 255, but was {brightness}.')

        if (self.number_of_leds > serial.number_of_leds):
            raise ValueError(f"The serial connection stated that there are {serial.number_of_leds} LEDs, but this LedArray object is set for {self.number_of_leds} LEDs.")

        if (self.end_led > serial.number_of_leds and self.number_of_leds > 0):
            raise ValueError(f"The serial connection stated that its led indicies range from 0 (inclusive) to {serial.number_of_leds} "
                             "(exclusive), but this LedArray ranges from {self.start_led} (inclusive) to {self.end_led} (exclusive).")

        DIVISOR = int.from_bytes(serial.read(1), byteorder="little")
        self.__serial_writer = self.SerialWriter(serial, DIVISOR)

        self.__configure_serial()

    def set_band_colors(self, band_colors: Iterable[Tuple[int, Iterable[int]]]):
        self.__send_bytes(BAND_COLOR_START_OF_MESSAGE_CODE.to_bytes(length=1, byteorder=BYTE_ORDER))
        self.__send_bytes(len(band_colors).to_bytes(1, BYTE_ORDER))

        super().set_band_colors(band_colors)

        self.__send_bytes(BAND_COLOR_END_OF_MESSAGE_CODE.to_bytes(1, BYTE_ORDER))

    def _set_band_rgbs(self, band: int, rgb: RGB):
        self.__send_packet(band, rgb)

        super()._set_band_rgbs(band, rgb)

    def __configure_serial(self):
        self.__send_bytes(self.__brightness.to_bytes(length=1, byteorder=BYTE_ORDER))
        self.__send_bytes(self.number_of_bands.to_bytes(length=1, byteorder=BYTE_ORDER))
        self.__send_bytes(BAND_SETUP_START_OF_MESSAGE_CODE.to_bytes(length=1, byteorder=BYTE_ORDER))

        for band_number in range(self.number_of_bands):
            led_ranges = self.get_band_led_ranges(band_number)
            led_ranges_length_bytes = len(led_ranges).to_bytes(length=1, byteorder=BYTE_ORDER)
            self.__send_bytes(led_ranges_length_bytes)

            for start, end in led_ranges:
                start_bytes = start.to_bytes(length=2, byteorder=BYTE_ORDER)
                end_bytes = end.to_bytes(length=2, byteorder=BYTE_ORDER)
                checksum = (sum(start_bytes) + sum(end_bytes) + sum(led_ranges_length_bytes)) % 256

                packet = start_bytes + end_bytes + checksum.to_bytes(length=1, byteorder=BYTE_ORDER)
                self.__send_bytes(packet)

        self.__send_bytes(BAND_SETUP_END_OF_MESSAGE_CODE.to_bytes(length=1, byteorder=BYTE_ORDER))

    def __send_packet(self, group_index: int, rgb: RGB):
        packet = group_index.to_bytes(length=1, byteorder=BYTE_ORDER)
        packet += rgb.red.to_bytes(1, BYTE_ORDER)
        packet += rgb.green.to_bytes(1, BYTE_ORDER)
        packet += rgb.blue.to_bytes(1, BYTE_ORDER)

        self.__send_bytes(packet)

        check_sum = (sum(packet) % 256).to_bytes(length=1, byteorder=BYTE_ORDER)

        self.__send_bytes(check_sum)

    def __send_bytes(self, bytes_: bytes):
        self.__serial_writer.write(bytes_)
