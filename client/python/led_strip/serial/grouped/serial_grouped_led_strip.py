from typing import List, Tuple

from serial import Serial


from python.led_strip.serial.serial_led_strip import SerialLedStrip
from python.led_strip.grouped.grouped_led_strip import GroupedLedStrip

GROUPED_STRIP_TYPE = 1


class SerialGroupedLedStrip(SerialLedStrip, GroupedLedStrip):
    def __init__(self, led_index_range: Tuple[int, int], serial_connection: Serial, brightness: int, group_index_to_led_range: List[Tuple[int, int]]):

        GroupedLedStrip.__init__(self, led_index_range, group_index_to_led_range)
        SerialLedStrip.__init__(self, led_index_range, serial_connection, brightness)

    def _send_led_strip_type(self):
        self._send_bytes(GROUPED_STRIP_TYPE.to_bytes(length=1, byteorder="big"))

    def _send_any_additional_config_data(self):
        self.__send_number_of_groups()
        self.__send_group_indices_to_led_ranges()

    def __send_number_of_groups(self):
        self._send_bytes(self.get_number_of_groups().to_bytes(length=1, byteorder="big"))

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

    def _show(self):
        SerialLedStrip._show(self)
        GroupedLedStrip._show(self)
