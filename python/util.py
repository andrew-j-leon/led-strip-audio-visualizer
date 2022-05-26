from __future__ import annotations

import os
from typing import Any, Dict, Hashable, Iterable, List, Tuple


class RGB:
    def __init__(self, red: int = 0, green: int = 0, blue: int = 0):
        rgb = (red, green, blue)

        for channel in rgb:
            if (channel < 0 or channel > 255):
                raise ValueError(f'rgb values must be between 0 (inclusive) & 255 (inclusive), (red, green, blue) was {rgb}.')

        self.__red = red
        self.__green = green
        self.__blue = blue

    @property
    def red(self) -> int:
        return self.__red

    @property
    def green(self) -> int:
        return self.__green

    @property
    def blue(self) -> int:
        return self.__blue

    def __iter__(self):
        yield self.red
        yield self.green
        yield self.blue

    def __repr__(self) -> str:
        return f'RGB({self.red}, {self.green}, {self.blue})'

    def __eq__(self, right_value) -> bool:
        return tuple(self) == tuple(right_value)


class Settings:
    SERIAL_BAUDRATES = [115200, 57600, 38400, 31250, 28800, 19200, 14400,
                        9600, 4800, 2400, 1200, 600, 300]

    def __init__(self, start_led: int = 0, end_led: int = 0, milliseconds_per_audio_chunk: int = 50,
                 serial_port: str = 'COM3', serial_baudrate: int = 115200, brightness: int = 0,
                 minimum_frequency: int = 0, maximum_frequency: int = 0, should_reverse_leds: bool = False,
                 number_of_groups: int = 0, amplitude_rgbs: List[Iterable[int]] = []):

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
        self.amplitude_rgbs = amplitude_rgbs

    def __repr__(self) -> str:
        return (f'Settings(start_led = {self.start_led}, end_led = {self.end_led}, '
                f'milliseconds_per_audio_chunk = {self.milliseconds_per_audio_chunk}, '
                f'serial_port = {self.serial_port}, serial_baudrate = {self.serial_baudrate}, '
                f'brightness = {self.brightness}, minimum_frequency = {self.minimum_frequency}, '
                f'maximum_frequency = {self.maximum_frequency}, should_reverse_leds = {self.should_reverse_leds}, '
                f'number_of_groups = {self.number_of_groups}, amplitude_rgbs = {self.amplitude_rgbs})')

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
                    and self.number_of_groups == other.number_of_groups
                    and self.amplitude_rgbs == other.amplitude_rgbs)

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

    @property
    def amplitude_rgbs(self) -> List[Tuple[int, int, int]]:
        return self.__amplitude_rgbs

    @amplitude_rgbs.setter
    def amplitude_rgbs(self, amplitude_rgbs: List[Iterable[int]]):
        for i in range(len(amplitude_rgbs)):
            try:
                red, green, blue = amplitude_rgbs[i]

                if (red < 0 or red > 255):
                    raise ValueError(f'The red value for the rgb at index {i}, {amplitude_rgbs[i]}, was not >= 0 and <= 255.')

                if (green < 0 or green > 255):
                    raise ValueError(f'The green value for the rgb at index {i}, {amplitude_rgbs[i]}, was not >= 0 and <= 255.')

                if (blue < 0 or blue > 255):
                    raise ValueError(f'The blue value for the rgb at index {i}, {amplitude_rgbs[i]}, was not >= 0 and <= 255.')

            except ValueError as error:
                error_message = str(error).casefold()

                if ('too many values to unpack' in error_message or 'not enough values to unpack' in error_message):
                    raise ValueError(f'The rgb at index {i}, {amplitude_rgbs[i]}, was not an Iterable with three values.')

                raise error

        self.__amplitude_rgbs = amplitude_rgbs


class SettingsCollection:
    def __init__(self, collection: Dict[Hashable, Settings] = {'default': Settings()}):
        self.__collection: Dict[Hashable, Settings] = dict()

        for settings_name, settings in collection.items():
            self.update_collection(settings_name, settings)

    def __contains__(self, settings_name: Hashable) -> bool:
        return settings_name in self.__collection

    @property
    def settings_names(self) -> List[Hashable]:
        return list(self.__collection.keys())

    @property
    def current_settings(self) -> Settings:
        try:
            return self.__collection[self.current_settings_name]

        except AttributeError:
            raise AttributeError('There are no Settings in this SettingsCollection. Call update_collection to add a Setting.')

    @property
    def current_settings_name(self) -> Hashable:
        try:
            return self.__current_settings_name

        except AttributeError:
            raise AttributeError('There are no Settings in this SettingsCollection. Call update_collection to add a Setting.')

    @current_settings_name.setter
    def current_settings_name(self, settings_name: Hashable):
        if (settings_name not in self.__collection):
            raise ValueError(f'There is no Settings in this SettingsCollection with the name {settings_name}. '
                             + f'Recognized Settings names include: {self.settings_names}')

        self.__current_settings_name = settings_name

    def get_settings(self, settings_name: Hashable) -> Settings:
        try:
            return self.__collection[settings_name]

        except KeyError:
            raise KeyError(f'There is no Settings in this SettingsCollection with the name {settings_name}. '
                           + f'Recognized Settings names include: {self.settings_names}')

    def update_collection(self, settings_name: Hashable, settings: Settings):
        self.__collection[settings_name] = settings

        if (len(self.__collection) == 1):
            self.current_settings_name = settings_name

    def delete_settings(self, settings_name: Hashable):
        try:
            self.__collection.pop(settings_name)

            if (len(self.__collection) == 0):
                del self.__current_settings_name

            elif (settings_name == self.current_settings_name):
                self.current_settings_name = self.settings_names.pop()

        except (KeyError, AttributeError):
            pass


def convert_to_hex(red: int, green: int, blue: int) -> str:
    '''
        Args:
            `red (int)`: The red value within the range [0,255]
            `green (int)`: The green value within the range [0,255]
            `blue (int)`: The blue value within the range [0,255]

        Returns:
            `str`: A hexadecimal conversion of the given RGB color. For example,
                    an RGB of (3, 14, 210) returns "#0314D2"
    '''
    return "#{:02x}{:02x}{:02x}".format(red, green, blue)


def join_paths(parent_path: str, relative_path: str) -> str:
    '''
        Returns:
            `str`: The normalized path formed by parent_path + relative_path.

                Example : If parent_path = "A/B/C/D" and relative_path = "../../E",
                this function returns "A/B/E".
    '''
    return os.path.normpath(os.path.join(parent_path, relative_path))
