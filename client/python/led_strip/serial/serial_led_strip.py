from typing import Tuple
from serial import Serial

import python.led_strip.led_strip as led_strip


class SerialLedStrip(led_strip.LedStrip):
    def __init__(self, led_index_range: Tuple[int, int], serial_connection: Serial, brightness: int):
        """
            Args:
                `brightness (int)`: A value within the range [0,255]. 0 is the dimmest; 255 is the brightest.
            Raises:
                `ValueError`: If brightness is outside its range.
                `ValueError`: If led_index_range specifies more leds than the serial connections states there are.

                    Example : If an arduino reports that there are 300 leds connected, but led_index_range is (0,400),
                    then there would be too many leds in this LedStrip compared to the 300 reported by the arduino.

                `ValueError`: If the led_index_range represents indicies outside the range of the led index range given by
                the serial connection

                    Example : If an arduino reports that there are 300 leds connected, then indicies range from 0 to 299. If
                    led_index_range is (10, 310), this exception will be thrown because indicies [300,309] are outside the range
                    of the led strip reported by the arduino.
        """
        if (brightness < 0 or brightness > 255):
            raise ValueError("brightness must be within the range [0,255].")

        led_strip.LedStrip.__init__(self, led_index_range)

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

    def _send_config_data_to_arduino(self):
        self.__send_brightness()

        self._send_led_strip_type()
        self._send_any_additional_config_data()

    def _send_led_strip_type(self):
        pass

    def __send_brightness(self):
        self._send_bytes(self.__brightness.to_bytes(length=1, byteorder="big"))

    def _send_any_additional_config_data(self):
        pass

    def _show(self):
        if (self._get_number_of_queued_color_changes() >= 1):
            self.__send_expected_number_of_packets()

            self._for_each_queued_color_change(self._send_packet)

    def __send_expected_number_of_packets(self):
        self._send_bytes(self._get_number_of_queued_color_changes().to_bytes(length=1, byteorder="big"))

    def _send_packet(self, *args):
        pass
