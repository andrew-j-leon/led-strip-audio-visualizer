from __future__ import annotations

from typing import Any

from util import Jsonable


class Settings(Jsonable):
    SERIAL_BAUDRATES = [2000000, 1000000, 500000, 115200, 57600, 38400, 31250, 28800, 19200, 14400,
                        9600, 4800, 2400, 1200, 600, 300]

    def __init__(self, start_led: int = 0, end_led: int = 0, milliseconds_per_audio_chunk: int = 50,
                 serial_port: str = '', serial_baudrate: int = 1000000, brightness: int = 0,
                 minimum_frequency: int = 0, maximum_frequency: int = 0, should_reverse_groups: bool = False,
                 number_of_groups: int = 0, should_mirror_groups: bool = False):

        self.start_led = start_led
        self.end_led = end_led
        self.milliseconds_per_audio_chunk = milliseconds_per_audio_chunk
        self.serial_port = serial_port
        self.serial_baudrate = serial_baudrate
        self.brightness = brightness
        self.minimum_frequency = minimum_frequency
        self.maximum_frequency = maximum_frequency
        self.should_reverse_groups = should_reverse_groups
        self.number_of_groups = number_of_groups
        self.should_mirror_groups = should_mirror_groups

    def __repr__(self) -> str:
        return (f'Settings(start_led = {self.start_led}, end_led = {self.end_led}, '
                f'milliseconds_per_audio_chunk = {self.milliseconds_per_audio_chunk}, '
                f'serial_port = {self.serial_port}, serial_baudrate = {self.serial_baudrate}, '
                f'brightness = {self.brightness}, minimum_frequency = {self.minimum_frequency}, '
                f'maximum_frequency = {self.maximum_frequency}, should_reverse_groups = {self.should_reverse_groups}, '
                f'number_of_groups = {self.number_of_groups}, should_mirror_groups = {self.should_mirror_groups})')

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Settings)):
            return (self.start_led == other.start_led
                    and self.end_led == other.end_led
                    and self.milliseconds_per_audio_chunk == other.milliseconds_per_audio_chunk
                    and self.serial_port == other.serial_port
                    and self.serial_baudrate == other.serial_baudrate
                    and self.brightness == other.brightness
                    and self.minimum_frequency == other.minimum_frequency
                    and self.maximum_frequency == other.maximum_frequency
                    and self.should_reverse_groups == other.should_reverse_groups
                    and self.number_of_groups == other.number_of_groups
                    and self.should_mirror_groups == other.should_mirror_groups)

        return False

    def to_json(self):
        return {'start_led': self.start_led, 'end_led': self.end_led,
                'milliseconds_per_audio_chunk': self.milliseconds_per_audio_chunk,
                'serial_port': self.serial_port, 'serial_baudrate': self.serial_baudrate,
                'brightness': self.brightness, 'minimum_frequency': self.minimum_frequency,
                'maximum_frequency': self.maximum_frequency,
                'should_reverse_groups': self.should_reverse_groups, 'number_of_groups': self.number_of_groups,
                'should_mirror_groups': self.should_mirror_groups}

    @property
    def start_led(self) -> int:
        return self.__start_led

    @start_led.setter
    def start_led(self, start_led: int) -> int:
        try:
            if (start_led < 0):
                raise ValueError(f'start_led ({start_led}) must be >= 0.')

            if (start_led > self.end_led):
                raise ValueError(f'start_led ({start_led}) must be <= end_led ({self.end_led}).')

            self.__start_led = start_led

        except AttributeError:
            self.__start_led = start_led

    @property
    def end_led(self) -> int:
        return self.__end_led

    @end_led.setter
    def end_led(self, end_led: int):
        try:
            if (end_led < 0):
                raise ValueError(f'end_led ({end_led}) must be >= 0.')

            if (end_led < self.start_led):
                raise ValueError(f'end_led ({end_led}) must be >= start_led ({self.start_led}).')

            self.__end_led = end_led

        except AttributeError:
            self.__end_led = end_led

    @property
    def milliseconds_per_audio_chunk(self) -> int:
        return self.__milliseconds_per_audio_chunk

    @milliseconds_per_audio_chunk.setter
    def milliseconds_per_audio_chunk(self, milliseconds_per_audio_chunk: int):
        if (milliseconds_per_audio_chunk < 0):
            raise ValueError(f'milliseconds_per_audio_chunk ({milliseconds_per_audio_chunk}) must be >= 0.')

        self.__milliseconds_per_audio_chunk = milliseconds_per_audio_chunk

    @property
    def serial_baudrate(self) -> int:
        return self.__serial_baudrate

    @serial_baudrate.setter
    def serial_baudrate(self, serial_baudrate: int):
        if (serial_baudrate not in self.SERIAL_BAUDRATES):
            raise ValueError(f'Invalid serial_baudrate. Valid serial baudrates include: {self.SERIAL_BAUDRATES}')

        self.__serial_baudrate = serial_baudrate

    @property
    def brightness(self) -> int:
        return self.__brightness

    @brightness.setter
    def brightness(self, brightness: int):
        if (brightness < 0 or brightness > 255):
            raise ValueError(f'brightness ({brightness}) must be >= 0 and <= 255.')

        self.__brightness = brightness

    @property
    def minimum_frequency(self) -> int:
        return self.__minimum_frequency

    @minimum_frequency.setter
    def minimum_frequency(self, minimum_frequency: int):
        try:
            if (minimum_frequency < 0):
                raise ValueError(f'minimum_frequency ({minimum_frequency}) must be >= 0.')

            if (minimum_frequency > self.maximum_frequency):
                raise ValueError(f'minimum_frequency ({minimum_frequency}) must be <= maximum_frequency ({self.maximum_frequency}).')

            self.__minimum_frequency = minimum_frequency

        except AttributeError:
            self.__minimum_frequency = minimum_frequency

    @property
    def maximum_frequency(self) -> int:
        return self.__maximum_frequency

    @maximum_frequency.setter
    def maximum_frequency(self, maximum_frequency: int):
        try:
            if (maximum_frequency < 0):
                raise ValueError(f'maximum_frequency ({maximum_frequency}) must be >= 0.')

            if (maximum_frequency < self.minimum_frequency):
                raise ValueError(f'maximum_frequency ({maximum_frequency}) must be >= minimum_frequency ({self.minimum_frequency}).')

            self.__maximum_frequency = maximum_frequency

        except AttributeError:
            self.__maximum_frequency = maximum_frequency

    @property
    def number_of_groups(self) -> int:
        return self.__number_of_groups

    @number_of_groups.setter
    def number_of_groups(self, number_of_groups: int):
        if (number_of_groups < 0 or number_of_groups > 255):
            raise ValueError(f'number_of_groups ({number_of_groups}) must be >= 0 and <= 255.')

        self.__number_of_groups = number_of_groups
