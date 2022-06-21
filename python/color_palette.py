from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, Hashable, Iterable, List, Tuple


def load(directory: Path) -> ColorPaletteSelection:
    collection: Dict[str, ColorPalette] = dict()

    try:
        for save_file in directory.iterdir():
            with save_file.open('r') as file:
                try:
                    color_palette = json.load(file)
                    name = save_file.name

                    collection[name] = ColorPalette(**color_palette)

                except (json.decoder.JSONDecodeError, PermissionError, TypeError):
                    pass

    except FileNotFoundError:
        raise FileNotFoundError(f'The directory {directory} does not exist.')

    except NotADirectoryError:
        raise NotADirectoryError(f'The path {directory} points to a file, not a directory.')

    COLOR_PALETTE_SELECTION = ColorPaletteSelection(collection)

    SELECTED_NAME_FILE = directory.joinpath('.selected_name')

    if (SELECTED_NAME_FILE.is_file()):
        with SELECTED_NAME_FILE.open('r') as file:

            SELECTED_NAME = file.read().strip()
            COLOR_PALETTE_SELECTION.selected_name = SELECTED_NAME

    return COLOR_PALETTE_SELECTION


class ColorPaletteEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if (type(o) is ColorPalette):
            return dict(amplitude_rgbs=o.amplitude_rgbs)

        return super().default(o)


def save(color_palette_selection: ColorPaletteSelection, directory: Path):
    if (len(color_palette_selection) == 0):
        _delete_saved_color_palette_collection(directory)

    else:
        temporary_save_directory = directory.joinpath('temp')

        try:
            temporary_save_directory.mkdir(exist_ok=True)

            for name, color_palette in color_palette_selection.items():
                save_file = temporary_save_directory.joinpath(name)

                with save_file.open('w') as file:
                    json.dump(color_palette, file, cls=ColorPaletteEncoder, indent=4)

            selected_name_file = temporary_save_directory.joinpath('.selected_name')

            with selected_name_file.open('w') as file:
                file.write(color_palette_selection.selected_name)

            _delete_saved_color_palette_collection(directory)

            for save_file in temporary_save_directory.iterdir():
                new_save_file = directory.joinpath(save_file.name)
                save_file.rename(new_save_file)

        except FileNotFoundError:
            raise FileNotFoundError(f'The directory {directory} does not exist.')

        except NotADirectoryError:
            raise NotADirectoryError(f'The path name {directory} points to a file, not a directory.')

        except PermissionError:
            raise PermissionError('The current user does not have the '
                                  f'permissions to save to the directory {directory}.')

        finally:
            shutil.rmtree(str(temporary_save_directory), ignore_errors=True)


def _delete_saved_color_palette_collection(directory: Path):
    for save_file in directory.iterdir():
        try:
            save_file.unlink()

        except (IsADirectoryError, PermissionError):
            pass


class ColorPalette:
    def __init__(self, amplitude_rgbs: List[Iterable[int]] = []):
        self.amplitude_rgbs = amplitude_rgbs

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, ColorPalette)):
            return self.amplitude_rgbs == other.amplitude_rgbs

        return False

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
                raise ValueError(f'The rgb at index {i}, {amplitude_rgbs[i]}, was not an Iterable with three values.')

        self.__amplitude_rgbs = new_amplitude_rgbs


class ColorPaletteSelection:
    def __init__(self, palettes: Dict[str, ColorPalette] = dict()):

        self.__collection: Dict[str, ColorPalette] = dict()
        for name, color_palette in palettes.items():
            self[name] = color_palette

    @property
    def selected_palette(self):
        try:
            return self[self.selected_name]

        except AttributeError:
            raise AttributeError('There are no ColorPalettes in this ColorPaletteSelection.')

    @property
    def selected_name(self):
        try:
            return self.__current_name

        except AttributeError:
            raise AttributeError('There are no ColorPalettes in this ColorPaletteSelection.')

    @selected_name.setter
    def selected_name(self, name: Hashable):
        if (name not in self):
            raise ValueError(f'There is no ColorPalette in this ColorPaletteSelection with the name {name}.')

        self.__current_name = name

    def names(self):
        return self.__collection.keys()

    def palettes(self):
        return self.__collection.values()

    def items(self):
        return self.__collection.items()

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, ColorPaletteSelection)):

            try:
                if (self.names() == other.names() and self.selected_name == other.selected_name
                        and self.selected_palette == other.selected_palette):
                    for name in self.names():
                        if (self[name] != other[name]):
                            return False

                    return True

            except AttributeError:
                return (len(self) == 0 and len(other) == 0)

        return False

    def __len__(self):
        return len(self.__collection)

    def __contains__(self, name: Hashable):
        return name in self.__collection

    def __iter__(self):
        return self.__collection.__iter__()

    def __getitem__(self, name: Hashable) -> ColorPalette:
        try:
            return self.__collection[name]

        except KeyError:
            raise KeyError(f'This ColorPaletteSelection contains no ColorPalette with the name {name}.')

    def __setitem__(self, name: Hashable, color_palette: ColorPalette):
        if (not isinstance(color_palette, ColorPalette)):
            raise TypeError(f'color_palette argument ({color_palette}) of type {type(color_palette)} must be an instance of type ColorPalette.')

        self.__collection[name] = color_palette

        if (len(self.__collection) == 1):
            self.selected_name = name

    def __delitem__(self, name: Hashable):
        try:
            del self.__collection[name]

            if (name == self.selected_name):
                del self.__current_name

            INDEX = 0
            self.selected_name = list(self.names()).pop(INDEX)

        except KeyError:
            raise KeyError(f'This ColorPaletteSelection contains no ColorPalette with the name {name}.')

        except IndexError:
            pass
