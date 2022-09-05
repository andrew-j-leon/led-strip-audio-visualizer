from typing import Any, Dict, Generic, TypeVar

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
