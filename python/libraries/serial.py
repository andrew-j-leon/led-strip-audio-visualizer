from abc import ABC, abstractmethod
from typing import Any, Union

import serial
from serial.serialutil import SerialException

PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)
INIT_SERIAL_MESSAGE = b'\0'


class Serial(ABC):
    @property
    @abstractmethod
    def number_of_leds(self) -> int:
        pass

    @abstractmethod
    def read(self, number_of_bytes: int) -> Any:
        pass

    @abstractmethod
    def write(self, data: bytes):
        pass

    @abstractmethod
    def open(self, port: str, baud_rate: int, parity: str, stop_bits: Union[int, float], byte_size: int,
             read_timeout: int, write_timeout: int):
        pass

    @abstractmethod
    def close(self):
        pass


class ProductionSerial(Serial):
    def open(self, port: str, baud_rate: int, parity: str, stop_bits: Union[int, float], byte_size: int,
             read_timeout: int, write_timeout: int):
        self.close()

        self.__serial = serial.Serial(port, baud_rate, byte_size, parity, stop_bits,
                                      read_timeout, write_timeout=write_timeout)

        self.write(INIT_SERIAL_MESSAGE)

        NUMBER_OF_BYTES = 2
        number_of_leds: bytes = self.read(NUMBER_OF_BYTES)

        if (len(number_of_leds) != NUMBER_OF_BYTES):
            raise ValueError(f'ProductionSerial expected {NUMBER_OF_BYTES} bytes from the serial connection (representing the number of leds in the led strip), but instead received {len(number_of_leds)} bytes.')

        self.__number_of_leds = int.from_bytes(number_of_leds, byteorder="little")

    @property
    def number_of_leds(self) -> int:
        try:
            return self.__number_of_leds

        except (AttributeError, SerialException):
            raise ValueError('No Serial connection is established. Did you remember to call '
                             'open? Did you call close, but never called open after?')

    def read(self, number_of_bytes: int) -> Any:
        try:
            return self.__serial.read(number_of_bytes)

        except (AttributeError, SerialException):
            raise ValueError('No Serial connection is established. Did you remember to call '
                             'open? Did you call close, but never called open after?')

    def write(self, data: bytes):
        try:
            return self.__serial.write(data)

        except (AttributeError, SerialException):
            raise ValueError('No Serial connection is established. Did you remember to call '
                             'open? Did you call close, but never called open after?')

    def close(self):
        try:
            self.__serial.close()

        except AttributeError:
            pass


class FakeSerial(Serial):
    def __init__(self, number_of_leds: int = 300):
        self.__number_of_leds = number_of_leds
        self.opened = False

    @property
    def number_of_leds(self) -> int:
        return self.__number_of_leds

    def read(self, number_of_bytes: int) -> Any:
        LENGTH = 2
        BYTE_ORDER = 'big'

        return self.__number_of_leds.to_bytes(LENGTH, BYTE_ORDER)

    def write(self, data):
        pass

    def close(self):
        self.opened = False

    def open(self, port, baud_rate, parity, stop_bits, byte_size, read_timeout, write_timeout):
        self.closed = True
        self.port = port
        self.baud_rate = baud_rate
        self.parity = parity
        self.stop_bits = stop_bits
        self.byte_size = byte_size
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
