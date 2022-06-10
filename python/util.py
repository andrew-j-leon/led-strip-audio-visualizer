from __future__ import annotations
import json

import os
from pathlib import Path
from typing import Any, Dict, Hashable, Iterable, List, Tuple


class Font:
    def __init__(self, name: str = 'Arial', size: int = 12, style: str = 'normal'):
        self.__name = name
        self.__size = size
        self.__style = style

    @property
    def name(self) -> str:
        return self.__name

    @property
    def size(self) -> int:
        return self.__size

    @property
    def style(self) -> str:
        return self.__style

    def __repr__(self) -> str:
        return f'Font(name={self.name}, size={self.size}, style={self.style})'

    def __eq__(self, right_value: Any) -> bool:
        if (isinstance(right_value, Font)):
            return (self.name == right_value.name
                    and self.size == right_value.size
                    and self.style == right_value.style)

        return False

    def __hash__(self) -> int:
        return hash((self.name, self.size, self.style))


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

        new_amplitude_rgbs: List[Tuple[int, int, int]] = []

        for i in range(len(amplitude_rgbs)):
            try:
                red, green, blue = amplitude_rgbs[i]

                if (red < 0 or red > 255):
                    raise ValueError(f'The red value for the rgb at index {i}, {amplitude_rgbs[i]}, was not >= 0 and <= 255.')

                if (green < 0 or green > 255):
                    raise ValueError(f'The green value for the rgb at index {i}, {amplitude_rgbs[i]}, was not >= 0 and <= 255.')

                if (blue < 0 or blue > 255):
                    raise ValueError(f'The blue value for the rgb at index {i}, {amplitude_rgbs[i]}, was not >= 0 and <= 255.')

                new_amplitude_rgbs.append((red, green, blue))

            except ValueError as error:
                error_message = str(error).casefold()

                if ('too many values to unpack' in error_message or 'not enough values to unpack' in error_message):
                    raise ValueError(f'The rgb at index {i}, {amplitude_rgbs[i]}, was not an Iterable with three values.')

                raise error

        self.__amplitude_rgbs = new_amplitude_rgbs


class SettingsCollection:

    class SettingsEncoder(json.JSONEncoder):
        def default(self, o: Any) -> Any:
            if (type(o) is Settings):
                return dict(start_led=o.start_led,
                            end_led=o.end_led,
                            milliseconds_per_audio_chunk=o.milliseconds_per_audio_chunk,
                            serial_port=o.serial_port,
                            serial_baudrate=o.serial_baudrate,
                            brightness=o.brightness,
                            minimum_frequency=o.minimum_frequency,
                            maximum_frequency=o.maximum_frequency,
                            should_reverse_leds=o.should_reverse_leds,
                            number_of_groups=o.number_of_groups,
                            amplitude_rgbs=o.amplitude_rgbs)

            return super().default(o)

    def __init__(self, collection: Dict[str, Settings] = dict()):
        self.__collection: Dict[str, Settings] = dict()

        self.load_from_dictionary(collection)

    def load_from_dictionary(self, collection: Dict[str, Settings]):
        for name, settings in collection.items():
            self[name] = settings

    def load_from_directory(self, directory: Path):
        collection: Dict[str, Settings] = dict()

        for save_file in directory.iterdir():
            with save_file.open() as file:
                try:
                    settings = json.load(file)
                    name = save_file.name

                    collection[name] = Settings(**settings)

                except json.decoder.JSONDecodeError:
                    pass

        for name, settings in collection.items():
            self[name] = settings

        current_name_file = directory.joinpath('.current_name')

        try:
            with current_name_file.open('r') as file:
                self.current_name = file.read().strip()

        except (FileNotFoundError, ValueError):
            pass

    def set_save_directory(self, directory: Path):
        self.__save_directory = directory

    def save_to_files(self):
        try:
            temporary_save_directory = self.__save_directory.joinpath('temp')
            temporary_save_directory.mkdir(exist_ok=True)

            for name, settings in self.__collection.items():
                save_file = temporary_save_directory.joinpath(name)

                with save_file.open('w') as file:
                    json.dump(settings, file, cls=self.SettingsEncoder, indent=4)

            try:
                current_name_save_file = temporary_save_directory.joinpath('.current_name')

                with current_name_save_file.open('w') as file:
                    file.write(self.current_name)

            except AttributeError:
                pass

            for save_file in self.__save_directory.iterdir():
                try:
                    save_file.unlink()

                except IsADirectoryError:
                    pass

            for save_file in temporary_save_directory.iterdir():
                new_file_name = self.__save_directory.joinpath(save_file.name)
                save_file.rename(new_file_name)

            temporary_save_directory.rmdir()

        except AttributeError:
            raise ValueError(f'No save directory is set for this SettingsCollection.')

    @property
    def current_settings(self):
        try:
            return self[self.current_name]

        except AttributeError:
            raise AttributeError('There are no Settings in this SettingsCollection.')

    @property
    def current_name(self):
        try:
            return self.__current_name

        except AttributeError:
            raise AttributeError('There are no Settings (and, hence, no Settings names) in this SettingsCollection.')

    @current_name.setter
    def current_name(self, name: Hashable):
        if (name not in self):
            raise ValueError(f'There is no Settings in this SettingsCollection with the name {name}.')

        self.__current_name = name

    def names(self):
        return self.__collection.keys()

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, SettingsCollection)):

            if (self.names() == other.names() and self.current_name == other.current_name
                    and self.current_settings == other.current_settings):
                for name in self.names():
                    if (self[name] != other[name]):
                        return False

                return True

        return False

    def __len__(self):
        return len(self.__collection)

    def __contains__(self, name: Hashable):
        return name in self.__collection

    def __iter__(self):
        return self.__collection.__iter__()

    def __getitem__(self, name: Hashable) -> Settings:
        try:
            return self.__collection[name]

        except KeyError:
            raise KeyError(f'This SettingsCollection contains no Settings with the name {name}.')

    def __setitem__(self, name: Hashable, settings: Settings):
        if (not isinstance(settings, Settings)):
            raise TypeError(f'settings argument ({settings}) of type {type(settings)} must be an instance of type Settings.')

        self.__collection[name] = settings

        if (len(self.__collection) == 1):
            self.current_name = name

    def __delitem__(self, name: str):
        try:
            del self.__collection[name]

            if (name == self.current_name):
                del self.__current_name

            INDEX = 0
            self.current_name = list(self.names()).pop(INDEX)

        except KeyError:
            raise KeyError(f'This SettingsCollection contains no Settings with the name {name}.')

        except IndexError:
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
