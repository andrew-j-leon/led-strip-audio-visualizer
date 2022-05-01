import abc
import math
from typing import Dict, Iterable, List, Tuple

from led_strip.grouped_leds import GroupedLeds
from libraries.gui import Font, Gui
from libraries.serial import Serial
from util.rgb import RGB
from util.util import rgb_to_hex


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


class LedStrip(abc.ABC):
    @property
    @abc.abstractmethod
    def number_of_groups(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def number_of_queued_colors(self) -> int:
        pass

    @abc.abstractmethod
    def enqueue_rgb(self, group: int, rgb: Iterable[int]):
        pass

    @abc.abstractmethod
    def group_is_rgb(self, group: int, rgb: Iterable[int]) -> bool:
        pass

    @abc.abstractmethod
    def show_queued_colors(self):
        pass

    @abc.abstractmethod
    def clear_queued_colors(self):
        pass


class GraphicLedStrip(LedStrip):
    def __init__(self, grouped_leds: GroupedLeds, gui: Gui):
        self.__grouped_leds = grouped_leds

        self.__color_queue: List[Tuple[int, RGB]] = []

        self.__gui = gui

        self.__led_element_ids: Dict[int, int] = dict()
        self.__draw_and_store_leds()

    def __del__(self):
        try:
            self.__gui.close()

        except AttributeError:
            pass

    @property
    def number_of_groups(self) -> int:
        return self.__grouped_leds.number_of_groups

    @property
    def number_of_queued_colors(self) -> int:
        return len(self.__color_queue)

    def enqueue_rgb(self, group: int, rgb: Iterable[int]):
        if (self.number_of_groups == 0):
            raise IndexError(f'Cannot enqueue RGB when GraphicLedStrip has 0 groups.')

        if (group < 0 or group >= self.number_of_groups):
            raise IndexError(f'Tried to enqueue an RGB color into group {group}, but group indices range from 0 (inclusive) to {self.number_of_groups - 1} (inclusive).')

        self.__color_queue.append((group, RGB(*rgb)))

    def group_is_rgb(self, group: int, rgb: Iterable[int]) -> bool:
        return self.__grouped_leds.get_group_rgb(group) == rgb

    def show_queued_colors(self):
        for queued_color_change in self.__color_queue:
            group, rgb = queued_color_change

            self.__recolor_leds(group, rgb)
            self.__grouped_leds.set_group_rgb(group, rgb)

        self.__gui.update()

    def clear_queued_colors(self):
        self.__color_queue.clear()

    def __recolor_leds(self, group: int, rgb: RGB):
        int_range = self.__grouped_leds.get_group_led_range(group)

        for i in int_range:
            element_id = self.__led_element_ids[i]

            self.__gui.set_element_fill_color(element_id, rgb_to_hex(rgb.red, rgb.green, rgb.blue))

    def __draw_and_store_leds(self):
        led_diameter = 30
        MAX_X_COORDINATE = self.__gui.dimensions.width
        LEDS_PER_ROW = math.floor(MAX_X_COORDINATE / led_diameter)
        LED_RADIUS = led_diameter / 2

        BLACK_HEX = "#000000"
        WHITE_HEX = "#ffffff"

        # Draw the LEDs on the TKinter Canvas
        for i in range(self.__grouped_leds.start_led, self.__grouped_leds.end_led):
            # center coordinates of the LED
            led_center_point = Point(x=LED_RADIUS + led_diameter * (i % LEDS_PER_ROW), y=LED_RADIUS + led_diameter * (i // LEDS_PER_ROW),)

            top_left_point = Point(led_center_point.x - LED_RADIUS, led_center_point.y - LED_RADIUS)
            bottom_right_point = Point(led_center_point.x + LED_RADIUS, led_center_point.y + LED_RADIUS)

            self.__led_element_ids[i] = self.__gui.create_oval(top_left_point.x, top_left_point.y,
                                                               bottom_right_point.x, bottom_right_point.y,
                                                               fill_color=BLACK_HEX)

            # This font size ensures that the longest index values are as large as possible while still fitting inside
            # their LEDs
            font_size_pixels = (led_diameter + 5) / len(str(self.__grouped_leds.number_of_leds))

            # Draw the index numbers in each led
            font_size_pixels = (led_diameter + 5) / len(str(self.__grouped_leds.number_of_leds))
            font = Font(size=int(-1 * font_size_pixels), style='bold', color=WHITE_HEX)
            self.__gui.create_text(led_center_point.x, led_center_point.y, text=str(i), font=font)

        self.__gui.update()


class SerialLedStrip(LedStrip):
    def __init__(self, grouped_leds: GroupedLeds, serial: Serial, brightness: int):
        self.__grouped_leds = grouped_leds

        self.__color_queue: List[Tuple[int, RGB]] = []

        # Serial logic
        if (brightness < 0 or brightness > 255):
            raise ValueError(f'brightness must be within the range [0,255], but was {brightness}.')

        self.__serial = serial
        self.__brightness = brightness

        # Wait for arduino to state it's connected
        while (self.__serial.number_of_bytes_in_buffer == 0):
            pass

        number_of_leds_from_serial = int.from_bytes(self.__serial.read(2), byteorder="big")

        if (self.__grouped_leds.number_of_leds > number_of_leds_from_serial):
            raise ValueError(f"The serial connection stated that there are {number_of_leds_from_serial} leds, but this LedStrip object is set for {self.__grouped_leds.number_of_leds} leds.")

        serial_end = number_of_leds_from_serial

        if (self.__grouped_leds.end_led > serial_end and self.__grouped_leds.number_of_leds > 0):
            raise ValueError(f"The serial connection stated that its led indicies range from 0 (inclusive) to {serial_end} (exclusive), but this LedStrip ranges from {self.__grouped_leds.start_led} (inclusive) to {self.__grouped_leds.end_led} (exclusive).")

        self.__configure_serial()

    def __del__(self):
        try:
            self.__serial.close()

        except AttributeError:
            pass

    @property
    def number_of_groups(self) -> int:
        return self.__grouped_leds.number_of_groups

    @property
    def number_of_queued_colors(self) -> int:
        return len(self.__color_queue)

    def enqueue_rgb(self, group: int, rgb: Iterable[int]):
        if (self.number_of_groups == 0):
            raise IndexError(f'Cannot enqueue RGB when GraphicLedStrip has 0 groups.')

        if (group < 0 or group >= self.number_of_groups):
            raise IndexError(f'Tried to enqueue an RGB color into group {group}, but group indices range from 0 (inclusive) to {self.number_of_groups - 1} (inclusive).')

        red, green, blue = rgb
        self.__color_queue.append((group, RGB(red, green, blue)))

    def group_is_rgb(self, group: int, rgb: Iterable[int]) -> bool:
        return self.__grouped_leds.get_group_rgb(group) == rgb

    def show_queued_colors(self):
        if (len(self.__color_queue) > 0):
            self.__send_bytes(len(self.__color_queue).to_bytes(length=1, byteorder="big"))  # Send expected number of packets

            for queued_color_change in self.__color_queue:
                group, rgb = queued_color_change

                self.__send_packet(group, rgb)
                self.__grouped_leds.set_group_rgb(group, rgb)

    def clear_queued_colors(self):
        self.__color_queue.clear()

    def __configure_serial(self):
        GROUPED_STRIP_TYPE = 1

        self.__send_bytes(self.__brightness.to_bytes(length=1, byteorder="big"))  # Send brightness

        self.__send_bytes(GROUPED_STRIP_TYPE.to_bytes(length=1, byteorder="big"))  # Send led strip type (Grouped or Array)
        self.__send_bytes(self.number_of_groups.to_bytes(length=1, byteorder="big"))  # Send number of groups

        # send group led ranges
        for group in range(self.__grouped_leds.number_of_groups):
            led_range = self.__grouped_leds.get_group_led_range(group)

            packet = (led_range.start.to_bytes(length=2, byteorder="big")
                      + led_range.end.to_bytes(length=2, byteorder="big"))

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
            echo = self.__serial.read(1)  # Make sure to set a read timeout on Serial's constructor. If timeout expired, assume the message wasn't received
