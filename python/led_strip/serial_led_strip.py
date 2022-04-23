from typing import List, Tuple

from led_strip.rgb import RGB
from libraries.serial import Serial
from util import NonNegativeInteger, NonNegativeIntegerRange

GROUPED_STRIP_TYPE = 1


class SerialLedStrip:
    def __init__(self, led_range: Tuple[int, int], group_led_ranges: List[Tuple[int, int]],
                 serial: Serial, brightness: int):
        if (brightness < 0 or brightness > 255):
            raise ValueError(f'brightness must be within the range [0,255], but was {brightness}.')

        start = NonNegativeInteger(led_range[0])
        end = NonNegativeInteger(led_range[1])

        self.__led_range = NonNegativeIntegerRange(start, end)

        self.__color_queue: List[Tuple(int, int, int)] = []

        self._group_led_ranges: List[NonNegativeIntegerRange] = []

        for i in range(len(group_led_ranges)):
            start, end = group_led_ranges[i]

            non_negative_integer_range = NonNegativeIntegerRange(start, end)

            if (non_negative_integer_range not in self.__led_range):
                raise ValueError(f'group_led_ranges[{i}]={(start, end)} is not within the bounds of led_range={led_range}.')

            self._group_led_ranges.append(non_negative_integer_range)

        self.__group_colors = [RGB(0, 0, 0)] * self.number_of_groups

        self.__serial = serial
        self.__brightness = brightness

        # Wait for arduino to state it's connected
        while (self.__serial.number_of_bytes_in_buffer == 0):
            pass

        self.__number_of_leds_from_serial = int.from_bytes(self.__serial.read(2), byteorder="big")

        if (self.number_of_leds > self.__number_of_leds_from_serial):
            raise ValueError(f"The serial connection stated that there are {self.__number_of_leds_from_serial} leds, but this LedStrip object is set for {self.number_of_leds} leds.")

        serial_end = self.__number_of_leds_from_serial
        if (self.__led_range.end > serial_end and self.number_of_leds > 0):
            raise ValueError(f"The serial connection stated that its led indicies range from 0 (inclusive) to {serial_end} (exclusive), but this LedStrip ranges from {self.__led_range.start} (inclusive) to {self.__led_range.end} (exclusive).")

        self.__configure_serial()

    def __del__(self):
        try:
            self.__serial.close()

        except AttributeError:
            pass

    @property
    def number_of_groups(self) -> int:
        return len(self._group_led_ranges)

    @property
    def number_of_leds(self) -> int:
        return self.__led_range.end - self.__led_range.start

    def enqueue_rgb(self, group: int, rgb: Tuple[int, int, int]):
        if (self.number_of_groups == 0):
            raise IndexError(f'Cannot enqueue RGB when GraphicLedStrip has 0 groups.')

        if (group < 0 or group >= self.number_of_groups):
            raise IndexError(f'Tried to enqueue an RGB color into group {group}, but group indices range from 0 (inclusive) to {self.number_of_groups - 1} (inclusive).')

        red, green, blue = rgb
        self.__color_queue.append((group, RGB(red, green, blue)))

    def group_is_color(self, group_index: int, rgb: Tuple[int, int, int]) -> bool:
        return self.__group_colors[group_index] == rgb

    def show_enqueued_colors(self):
        if (len(self.__color_queue) > 0):
            self.__send_bytes(len(self.__color_queue).to_bytes(length=1, byteorder="big"))  # Send expected number of packets

            for queued_color_change in self.__color_queue:
                group, rgb = queued_color_change

                self.__send_packet(group, rgb)
                self.__group_colors[group] = rgb

        self.__color_queue.clear()

    def __configure_serial(self):
        self.__send_bytes(self.__brightness.to_bytes(length=1, byteorder="big"))  # Send brightness

        self.__send_bytes(GROUPED_STRIP_TYPE.to_bytes(length=1, byteorder="big"))  # Send led strip type (Grouped or Array)
        self.__send_bytes(self.number_of_groups.to_bytes(length=1, byteorder="big"))  # Send number of groups

        # send group led ranges
        for group_index in range(len(self._group_led_ranges)):
            packet: bytes = self.__get_group_index_packet(group_index)
            self.__send_bytes(packet)

    def __send_packet(self, group_index: int, rgb: RGB):
        packet = group_index.to_bytes(length=1, byteorder="big")
        packet += rgb.red.to_bytes(1, "big")
        packet += rgb.green.to_bytes(1, "big")
        packet += rgb.blue.to_bytes(1, "big")

        self.__send_bytes(packet)

    def __get_group_index_packet(self, group_index: int) -> bytes:
        led_range = self._group_led_ranges[group_index]
        return (led_range.start.to_bytes(length=2, byteorder="big") + led_range.end.to_bytes(length=2, byteorder="big"))

    def __send_bytes(self, bytes_: bytes):
        """
            Sends the bytes_ over the serial one byte at a time. Continually resends
            the data if an acknowledgement is not received within serial's read timeout.
        """
        for byte_ in bytes_:
            self.__send_byte_lossless(byte_)

    def __send_byte_lossless(self, byte_: int):
        """
            Send a byte of data over serial. If an acknowledgement is
            not recieved within serial's read timeout, the byte is sent again. This continues
            indefinitely until an acknowledgement is received.
        """
        echo = bytes()
        while (echo == bytes()):
            self.__serial.write(byte_.to_bytes(length=1, byteorder="big"))
            echo = self.__serial.read(1)  # Make sure to set a read timeout on Serial's constructor. If timeout expired, assume the message wasn't received
