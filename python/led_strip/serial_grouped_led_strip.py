from typing import List, Tuple

from serial import Serial

GROUPED_STRIP_TYPE = 1

_START_INDEX = 0
_END_INDEX = 1


class SerialGroupedLedStrip:
    def __init__(self, led_index_range: Tuple[int, int], serial_connection: Serial, brightness: int, group_index_to_led_range: List[Tuple[int, int]]):

        # LedStrip
        if (led_index_range[0] >= led_index_range[1]):
            raise ValueError("led_index_range[0] must be < led_index_range[1].")

        if (led_index_range[0] < 0):
            raise ValueError("led_index_range[0] must be >= 0.")

        self.__led_index_range: Tuple[int, int] = led_index_range

        self.__queued_color_changes: list = []

        # GroupedLedStrip
        for i in range(len(group_index_to_led_range)):
            start_index, end_index = group_index_to_led_range[i]
            if (start_index >= end_index):
                raise ValueError("group_index_to_led_range[{}] : start_index ({}) must be < end_index ({}).".format(i, start_index, end_index))
            if (end_index > self._get_end_index() + 1):
                raise IndexError("group_index[{}] : indicies range from {} to {}, but the (exclusive) end_index was {}.".format(i, self._get_start_index(), self._get_end_index(), end_index))

        self._group_index_to_led_range: List[Tuple[int, int]] = group_index_to_led_range

        self.__group_index_to_its_rgb: List[Tuple[int, int, int]] = [(0, 0, 0) for i in range(self.get_number_of_groups())]

        # SerialLedStrip
        if (brightness < 0 or brightness > 255):
            raise ValueError("brightness must be within the range [0,255].")

        self.__serial_connection: Serial = serial_connection
        self.__brightness: int = brightness

        # Wait for arduino to state it's connected
        while (not self.__serial_connection.in_waiting):
            pass

        self.__number_of_leds_from_serial = int.from_bytes(self.__serial_connection.read(size=2), byteorder="big")

        if (self.get_number_of_leds() > self.__number_of_leds_from_serial):
            self.__close_serial_connection()
            raise ValueError("The serial connection stated that there are {} leds, but this LedStrip object is set for {} leds.".format(self.__number_of_leds_from_serial, self.get_number_of_leds()))

        if (self._get_end_index() >= self.__number_of_leds_from_serial):
            self.__close_serial_connection()
            raise ValueError("The serial connection states that its led strip indicies range from 0 (inclusive) to {} (inclusive), but this LedStrip object has an end_index of {}.".format(self.__number_of_leds_from_serial - 1, self._get_end_index()))

        self._send_config_data_to_arduino()

    def __send_group_indices_to_led_ranges(self):
        for group_index in range(len(self._group_index_to_led_range)):
            packet: bytes = self.__get_group_index_packet(group_index)
            self._send_bytes(packet)

    def __get_group_index_packet(self, group_index: int) -> bytes:
        start_index, end_index = self._group_index_to_led_range[group_index]
        return (start_index.to_bytes(length=2, byteorder="big") + end_index.to_bytes(length=2, byteorder="big"))

    def _send_packet(self, group_index: int, rgb: Tuple[int, int, int]):
        packet = group_index.to_bytes(length=1, byteorder="big")

        for color in rgb:
            packet += color.to_bytes(1, "big")

        self._send_bytes(packet)

    # LedStrip
    def get_number_of_leds(self) -> int:
        return self._get_end_index() - self._get_start_index() + 1

    def show(self):
        # Serial
        if (self._get_number_of_queued_color_changes() >= 1):
            self._send_bytes(self._get_number_of_queued_color_changes().to_bytes(length=1, byteorder="big"))  # Send expected number of packets

            for queued_color_change in self.__queued_color_changes:
                group_index, rgb = queued_color_change
                self._send_packet(group_index, rgb)

        # Grouped
        for queued_color_change in self.__queued_color_changes:
            group_index, rgb = queued_color_change
            self.__group_index_to_its_rgb[group_index] = rgb

        self.__queued_color_changes.clear()

    def _get_start_index(self) -> int:
        return self.__led_index_range[_START_INDEX]

    def _get_end_index(self) -> int:
        return self.__led_index_range[_END_INDEX] - 1

    def _shift_led_index_up_by_start_index(self, index: int) -> int:
        return index + self._get_start_index()

    def _enqueue_color_change_by_range_of_indices(self, start_index: int, end_index: int, *args):
        """
            Raises:
                `ValueError`: If start_index >= end_index.
        """
        if (start_index >= end_index):
            raise ValueError("start_index must be < end_index")

        self.__queued_color_changes.append((start_index, end_index, *args))

    def _enqueue_color_change_by_index(self, index: int, *args):
        self.__queued_color_changes.append((index, *args))

    def _get_number_of_queued_color_changes(self) -> int:
        return len(self.__queued_color_changes)

    # GroupedLedStrip

    def get_number_of_groups(self) -> int:
        return len(self._group_index_to_led_range)

    def set_group_color(self, group_index: int, rgb: Tuple[int, int, int]):
        self._enqueue_color_change_by_index(group_index, rgb)

    def group_is_color(self, group_index: int, rgb: Tuple[int, int, int]) -> bool:
        return self.__group_index_to_its_rgb[group_index] == rgb

    # SerialLedStrip

    def __del__(self):
        self.__close_serial_connection()

    def __close_serial_connection(self):
        if (self.__serial_connection):
            self.__serial_connection.close()

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
        self._send_bytes(self.get_number_of_groups().to_bytes(length=1, byteorder="big"))  # Send number of groups
        self.__send_group_indices_to_led_ranges()
