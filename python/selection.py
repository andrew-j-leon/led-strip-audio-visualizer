import json
import shutil
from pathlib import Path
from typing import Any, Dict, Generic, Type, TypeVar

from util import Jsonable

T = TypeVar('T')


class Selection(Generic[T]):
    def __init__(self, items: Dict[str, T] = dict()):
        self.__items: Dict[str, T] = dict()

        for name, value in items.items():
            self[name] = value

    @property
    def selected_value(self):
        try:
            return self[self.selected_key]

        except AttributeError:
            raise AttributeError('There are no items in this Selection.')

    @property
    def selected_key(self):
        try:
            return self.__selected_key

        except AttributeError:
            raise AttributeError('There are no items in this Selection.')

    @selected_key.setter
    def selected_key(self, key: str):
        if (key not in self):
            raise ValueError(f'There is no "{key}" key in this Selection.')

        self.__selected_key = key

    def keys(self):
        return self.__items.keys()

    def values(self):
        return self.__items.values()

    def items(self):
        return self.__items.items()

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Selection)):
            try:
                if (self.keys() == other.keys()
                    and self.selected_key == other.selected_key
                        and self.selected_value == other.selected_value):
                    for key in self.keys():
                        if (self[key] != other[key]):
                            return False

                    return True

            except AttributeError:
                return (len(self) == 0 and len(other) == 0)

        return False

    def __len__(self):
        return len(self.__items)

    def __contains__(self, key: str):
        return key in self.__items

    def __iter__(self):
        return self.__items.__iter__()

    def __getitem__(self, key: str) -> T:
        try:
            return self.__items[key]

        except KeyError:
            raise KeyError(f'There is no "{key}" key in this Selection.')

    def __setitem__(self, key: str, value: T):
        self.__items[key] = value

        if (len(self.__items) == 1):
            self.selected_key = key

    def __delitem__(self, key: str):
        try:
            del self.__items[key]

            if (key == self.selected_key):
                del self.__selected_key

            INDEX = 0
            self.selected_key = list(self.keys()).pop(INDEX)

        except KeyError:
            raise KeyError(f'There is no "{key}" key in this Selection.')

        except IndexError:
            pass


def load(directory: Path, jsonable_class: Type[Jsonable]) -> Selection[Jsonable]:
    items: Dict[str, Jsonable] = dict()

    try:
        for save_file in directory.iterdir():
            with save_file.open('r') as file:
                try:
                    json_data = json.load(file)
                    key = save_file.name

                    cls = jsonable_class(**json_data)
                    items[key] = cls

                except (json.decoder.JSONDecodeError, PermissionError, TypeError):
                    pass

    except FileNotFoundError:
        raise FileNotFoundError(f'The directory {directory} does not exist.')

    except NotADirectoryError:
        raise NotADirectoryError(f'The path "{directory}" is not a directory.')

    SELECTION = Selection(items)

    FILE_FOR_SELECTED_KEY = directory.joinpath('.selected_key')

    if (FILE_FOR_SELECTED_KEY.is_file() and len(SELECTION) > 0):
        with FILE_FOR_SELECTED_KEY.open('r') as file:

            SELECTED_KEY = file.read().strip()
            SELECTION.selected_key = SELECTED_KEY

    return SELECTION


def save(selection: Selection[Jsonable], directory: Path):
    try:
        temporary_save_directory = directory.joinpath('.temporary_save_directory')
        temporary_save_directory.mkdir(exist_ok=True)

        for key, value in selection.items():
            save_file = temporary_save_directory.joinpath(key)

            with save_file.open('w') as file:
                json.dump(value.to_json(), file, indent=4)

        FILE_FOR_SELECTED_KEY = temporary_save_directory.joinpath('.selected_key')

        with FILE_FOR_SELECTED_KEY.open('w') as file:
            try:
                file.write(selection.selected_key)

            except AttributeError:
                pass

        _clear_directory(directory)

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


def _clear_directory(directory: Path):
    for save_file in directory.iterdir():
        try:
            save_file.unlink()

        except (IsADirectoryError, PermissionError):
            pass
