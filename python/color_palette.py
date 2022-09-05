from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from selection import Selection


def load(directory: Path) -> Selection[ColorPalette]:
    collection: Dict[str, ColorPalette] = dict()

    try:
        for save_file in directory.iterdir():
            with save_file.open('r') as file:
                try:
                    color_palette = json.load(file)
                    key = save_file.name

                    collection[key] = ColorPalette(**color_palette)

                except (json.decoder.JSONDecodeError, PermissionError, TypeError):
                    pass

    except FileNotFoundError:
        raise FileNotFoundError(f'The directory {directory} does not exist.')

    except NotADirectoryError:
        raise NotADirectoryError(f'The path {directory} points to a file, not a directory.')

    COLOR_PALETTE_SELECTION = Selection(collection)

    SELECTED_NAME_FILE = directory.joinpath('.selected_key')

    if (SELECTED_NAME_FILE.is_file()):
        with SELECTED_NAME_FILE.open('r') as file:

            SELECTED_KEY = file.read().strip()
            COLOR_PALETTE_SELECTION.selected_key = SELECTED_KEY

    return COLOR_PALETTE_SELECTION


class ColorPaletteEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if (type(o) is ColorPalette):
            return dict(amplitude_rgbs=o.amplitude_rgbs)

        return super().default(o)


def save(color_palette_selection: Selection[ColorPalette], directory: Path):
    if (len(color_palette_selection) == 0):
        _delete_saved_color_palette_collection(directory)

    else:
        temporary_save_directory = directory.joinpath('temp')

        try:
            temporary_save_directory.mkdir(exist_ok=True)

            for key, color_palette in color_palette_selection.items():
                save_file = temporary_save_directory.joinpath(key)

                with save_file.open('w') as file:
                    json.dump(color_palette, file, cls=ColorPaletteEncoder, indent=4)

            selected_key_file = temporary_save_directory.joinpath('.selected_key')

            with selected_key_file.open('w') as file:
                file.write(color_palette_selection.selected_key)

            _delete_saved_color_palette_collection(directory)

            for save_file in temporary_save_directory.iterdir():
                new_save_file = directory.joinpath(save_file.name)
                save_file.rename(new_save_file)

        except FileNotFoundError:
            raise FileNotFoundError(f'The directory {directory} does not exist.')

        except NotADirectoryError:
            raise NotADirectoryError(f'The pathname {directory} points to a file, not a directory.')

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
