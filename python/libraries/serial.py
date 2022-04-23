import abc
from typing import Any, Union

import serial

PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)


class Serial(abc.ABC):
    @property
    @abc.abstractmethod
    def number_of_bytes_in_buffer(self) -> int:
        pass

    @abc.abstractmethod
    def read(self, number_of_bytes: int) -> Any:
        pass

    @abc.abstractmethod
    def write(self, data: bytes):
        pass

    @abc.abstractmethod
    def close(self):
        pass


class ProductionSerial(Serial):
    def __init__(self, port: str, baudrate: int, parity: str, stop_bits: Union[int, float], byte_size: int,
                 read_timeout: int, write_timeout: int):
        self.__serial = serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stop_bits,
                                      bytesize=byte_size, timeout=read_timeout, write_timeout=write_timeout)

    @property
    def number_of_bytes_in_buffer(self) -> int:
        return self.__serial.in_waiting

    def read(self, number_of_bytes: int) -> Any:
        return self.__serial.read(number_of_bytes)

    def write(self, data: bytes):
        return self.__serial.write(data)

    def close(self):
        return self.__serial.close()


class FakeSerial(Serial):
    def __init__(self, number_of_leds: int):
        self.__number_of_leds = int(number_of_leds)

    @property
    def number_of_bytes_in_buffer(self) -> int:
        return 1

    def read(self, number_of_bytes: int) -> Any:
        LENGTH = 2
        BYTE_ORDER = 'big'

        return self.__number_of_leds.to_bytes(LENGTH, BYTE_ORDER)

    def write(self, data: bytes):
        pass

    def close(self):
        pass
