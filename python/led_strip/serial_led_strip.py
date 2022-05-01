from typing import Iterable, List, Tuple

from led_strip.led_strip import GroupedLeds, LedStrip
from libraries.serial import Serial
from util.rgb import RGB

GROUPED_STRIP_TYPE = 1


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
