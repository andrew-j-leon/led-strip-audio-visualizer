import time
from abc import ABC, abstractmethod
from typing import Any, Union

import serial

PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)


class SerialException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Serial(ABC):
    @property
    @abstractmethod
    def number_of_leds(self) -> int:
        pass

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @abstractmethod
    def read(self, number_of_bytes: int) -> bytes:
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


INIT_SERIAL_MESSAGE = b'\0'
SERIAL_INIT_DELAY = 1
SERIAL_ERROR_MESSAGE = "Did you remember to call open(...)? Did you call open(...), and then call close(...), but never called open(...) again?"


class ProductionSerial(Serial):
    def open(self, port: str, baud_rate: int, parity: str, stop_bits: Union[int, float], byte_size: int,
             read_timeout: int, write_timeout: int):
        self.close()

        try:
            self.__serial = serial.Serial(port, baud_rate, byte_size, parity, stop_bits,
                                          read_timeout, write_timeout=write_timeout)

            time.sleep(SERIAL_INIT_DELAY)
            self.write(INIT_SERIAL_MESSAGE)

            NUMBER_OF_BYTES = 2
            self.__number_of_leds = int.from_bytes(self.read(NUMBER_OF_BYTES), byteorder="little")

        except serial.SerialException as err:
            raise SerialException(str(err))

    @property
    def number_of_leds(self) -> int:
        try:
            return self.__number_of_leds

        except AttributeError:
            raise SerialException(f"Did not receive the number of LEDs from the serial connection. {SERIAL_ERROR_MESSAGE}")

    def is_open(self):
        try:
            return self.__serial.is_open
        except AttributeError:
            return False

    def read(self, number_of_bytes):
        try:
            data = self.__serial.read(number_of_bytes)

            if (len(data) < number_of_bytes):
                raise SerialException(f"Expected {number_of_bytes} bytes from serial connection, but received {len(data)} bytes.")

            return data

        except (AttributeError, serial.SerialException):
            raise SerialException(f"Did not receive the number of LEDs from the serial connection. {SERIAL_ERROR_MESSAGE}")

    def write(self, data: bytes):
        try:
            return self.__serial.write(data)

        except (AttributeError, serial.SerialException):
            raise SerialException("No serial connection is currently established.")

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

    def is_open(self):
        return self.opened

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
