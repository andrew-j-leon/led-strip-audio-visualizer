from typing import List, Tuple

from serial import Serial
from util import NonNegativeInteger, NonNegativeIntegerRange

GROUPED_STRIP_TYPE = 1


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


class SerialLedStrip:
    def __init__(self, led_range: Tuple[int, int], serial_connection: Serial, brightness: int,
                 group_led_ranges: List[Tuple[int, int]]):

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

        self.__group_colors: List[Tuple[int, int, int]] = [(0, 0, 0)] * self.number_of_groups

        # SerialLedStrip
        if (brightness < 0 or brightness > 255):
            raise ValueError("brightness must be within the range [0,255].")

        self.__serial_connection = serial_connection
        self.__brightness: int = brightness

        # Wait for arduino to state it's connected
        while (not self.__serial_connection.in_waiting):
            pass

        self.__number_of_leds_from_serial = int.from_bytes(self.__serial_connection.read(size=2), byteorder="big")

        if (self.number_of_leds > self.__number_of_leds_from_serial):
            raise ValueError("The serial connection stated that there are {} leds, but this LedStrip object is set for {} leds.".format(self.__number_of_leds_from_serial, self.number_of_leds))

        if (self._get_end_index() >= self.__number_of_leds_from_serial):
            raise ValueError("The serial connection states that its led strip indicies range from 0 (inclusive) to {} (inclusive), but this LedStrip object has an end_index of {}.".format(self.__number_of_leds_from_serial - 1, self._get_end_index()))

        self._send_config_data_to_arduino()

    def __del__(self):
        try:
            self.__serial_connection.close()

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
        # Serial
        if (len(self.__color_queue) >= 1):
            self._send_bytes(len(self.__color_queue).to_bytes(length=1, byteorder="big"))  # Send expected number of packets

            for queued_color_change in self.__color_queue:
                group_index, rgb = queued_color_change
                self._send_packet(group_index, rgb)

        # Grouped
        for queued_color_change in self.__color_queue:
            group_index, rgb = queued_color_change
            self.__group_colors[group_index] = rgb

        self.__color_queue.clear()

    def __send_group_indices_to_led_ranges(self):
        for group_index in range(len(self._group_led_ranges)):
            packet: bytes = self.__get_group_index_packet(group_index)
            self._send_bytes(packet)

    def __get_group_index_packet(self, group_index: int) -> bytes:
        led_range = self._group_led_ranges[group_index]
        return (led_range.start.to_bytes(length=2, byteorder="big") + led_range.end.to_bytes(length=2, byteorder="big"))

    def _send_packet(self, group_index: int, rgb: Tuple[int, int, int]):
        packet = group_index.to_bytes(length=1, byteorder="big")

        for color in rgb:
            packet += color.to_bytes(1, "big")

        self._send_bytes(packet)

    def _get_start_index(self) -> int:
        return self.__led_range.start

    def _get_end_index(self) -> int:
        return self.__led_range.end - 1

    def _shift_led_index_up_by_start_index(self, index: int) -> int:
        return index + self._get_start_index()

    def _enqueue_color_change_by_range_of_indices(self, start_index: int, end_index: int, *args):
        """
            Raises:
                `ValueError`: If start_index >= end_index.
        """
        if (start_index >= end_index):
            raise ValueError("start_index must be < end_index")

        self.__color_queue.append((start_index, end_index, *args))

    # SerialLedStrip
    def _send_bytes(self, bytes_: bytes):
        """
            Sends the bytes_ over the serial_connection one byte at a time. Continually resends
            the data if an acknowledgement is not received within serial_connection's read timeout.
        """
        for byte_ in bytes_:
            self.__send_byte_lossless(byte_)

    def __send_byte_lossless(self, byte_: int):
        """
            Send a byte of data over serial_connection. If an acknowledgement is
            not recieved within serial_connection's read timeout, the byte is sent again. This continues
            indefinitely until an acknowledgement is received.
        """
        echo = bytes()
        while (echo == bytes()):
            self.__serial_connection.write(byte_.to_bytes(length=1, byteorder="big"))
            echo = self.__serial_connection.read(size=1)  # Make sure to set a read timeout on Serial's constructor. If timeout expired, assume the message wasn't received

            if (echo == bytes()):
                print('echo')

    def _send_config_data_to_arduino(self):
        self._send_bytes(self.__brightness.to_bytes(length=1, byteorder="big"))  # Send brightness

        self._send_bytes(GROUPED_STRIP_TYPE.to_bytes(length=1, byteorder="big"))  # Send led strip type (Grouped or Array)
        self._send_bytes(self.number_of_groups.to_bytes(length=1, byteorder="big"))  # Send number of groups
        self.__send_group_indices_to_led_ranges()
