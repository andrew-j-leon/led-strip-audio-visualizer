from typing import Tuple

from serial import Serial

from python.led_strip.serial.serial_led_strip import SerialLedStrip
from python.led_strip.array.array_led_strip import ArrayLedStrip

ARRAY_STRIP_TYPE = 0


class SerialArrayLedStrip(ArrayLedStrip, SerialLedStrip):
    def __init__(self, led_index_range: Tuple[int, int], serial_connection: Serial, brightness: int):
        ArrayLedStrip.__init__(self, led_index_range)
        SerialLedStrip.__init__(self, led_index_range, serial_connection, brightness)

    def _send_led_strip_type(self):
        self._send_bytes(ARRAY_STRIP_TYPE.to_bytes(length=1, byteorder="big"))

    def _send_packet(self, start_index: int, end_index: int, rgb: Tuple[int, int, int]):
        packet = start_index.to_bytes(length=2, byteorder="big") + end_index.to_bytes(2, "big")

        for color in rgb:
            packet += color.to_bytes(1, "big")

        self._send_bytes(packet)

    def _show(self):
        SerialLedStrip._show(self)
        ArrayLedStrip._show(self)
