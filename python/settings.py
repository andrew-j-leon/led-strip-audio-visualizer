from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load(directory: Path) -> Settings:
    settings_file = directory.joinpath('settings')

    try:
        with settings_file.open('r') as file:
            settings = json.load(file)
            return Settings(**settings)

    except FileNotFoundError:
        if (directory.is_file()):
            raise NotADirectoryError(f'The path {directory} points to a file, not a directory.')

        elif (directory.is_dir()):
            raise ValueError(f'There was no saved Settings in the directory {directory}.')

        raise FileNotFoundError(f'The directory {directory} does not exist.')


def save(settings: Settings, directory: Path):
    SETTINGS_JSON = dict(start_led=settings.start_led,
                         end_led=settings.end_led,
                         milliseconds_per_audio_chunk=settings.milliseconds_per_audio_chunk,
                         serial_port=settings.serial_port,
                         serial_baudrate=settings.serial_baudrate,
                         brightness=settings.brightness,
                         minimum_frequency=settings.minimum_frequency,
                         maximum_frequency=settings.maximum_frequency,
                         should_reverse_leds=settings.should_reverse_leds,
                         number_of_groups=settings.number_of_groups)

    TEMPORARY_SAVE_FILE = directory.joinpath('temp')

    try:
        with TEMPORARY_SAVE_FILE.open('w') as file:
            json.dump(SETTINGS_JSON, file, indent=4)

        SAVE_FILE = directory.joinpath('settings')

        if (SAVE_FILE.is_file()):
            SAVE_FILE.unlink()

        TEMPORARY_SAVE_FILE.rename(SAVE_FILE)

    except NotADirectoryError:
        raise NotADirectoryError(f'The path {directory} points to a file, not a directory.')

    except FileNotFoundError:
        raise FileNotFoundError(f'The directory {directory} does not exist.')

    except PermissionError:
        raise PermissionError('The current user does not have the permissions '
                              f'to save in the directory {directory}.')


class Settings:
    SERIAL_BAUDRATES = [115200, 57600, 38400, 31250, 28800, 19200, 14400,
                        9600, 4800, 2400, 1200, 600, 300]

    def __init__(self, start_led: int = 0, end_led: int = 0, milliseconds_per_audio_chunk: int = 50,
                 serial_port: str = '', serial_baudrate: int = 115200, brightness: int = 0,
                 minimum_frequency: int = 0, maximum_frequency: int = 0, should_reverse_leds: bool = False,
                 number_of_groups: int = 0):

        self.start_led = start_led
        self.end_led = end_led
        self.milliseconds_per_audio_chunk = milliseconds_per_audio_chunk
        self.serial_port = serial_port
        self.serial_baudrate = serial_baudrate
        self.brightness = brightness
        self.minimum_frequency = minimum_frequency
        self.maximum_frequency = maximum_frequency
        self.should_reverse_leds = should_reverse_leds
        self.number_of_groups = number_of_groups

    def __repr__(self) -> str:
        return (f'Settings(start_led = {self.start_led}, end_led = {self.end_led}, '
                f'milliseconds_per_audio_chunk = {self.milliseconds_per_audio_chunk}, '
                f'serial_port = {self.serial_port}, serial_baudrate = {self.serial_baudrate}, '
                f'brightness = {self.brightness}, minimum_frequency = {self.minimum_frequency}, '
                f'maximum_frequency = {self.maximum_frequency}, should_reverse_leds = {self.should_reverse_leds}, '
                f'number_of_groups = {self.number_of_groups})')

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
                    and self.should_reverse_leds == other.should_reverse_leds
                    and self.number_of_groups == other.number_of_groups)

        return False

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
