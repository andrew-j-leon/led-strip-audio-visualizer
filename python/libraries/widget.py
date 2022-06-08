from __future__ import annotations

from abc import ABC, abstractmethod
from copy import copy
from typing import Hashable, Any, List, Tuple

from util import Font


class Widget(ABC):
    def __init__(self, key: Hashable = None):
        self.__key = key

    @property
    def key(self) -> Hashable:
        if (self.__key is None):
            raise AttributeError('This Widget does not have a key attribute.')

        return self.__key

    @property
    @abstractmethod
    def value(self) -> Any:
        pass

    @value.setter
    @abstractmethod
    def value(self, value: Any):
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __eq__(self, other: Any) -> bool:
        if (isinstance(other, Widget)):
            SELF_HAS_KEY = hasattr(self, 'key')
            OTHER_HAS_KEY = hasattr(other, 'key')

            NEITHER_HAVE_KEY = not SELF_HAS_KEY and not OTHER_HAS_KEY
            BOTH_HAVE_KEY = SELF_HAS_KEY and OTHER_HAS_KEY

            return (NEITHER_HAVE_KEY or (BOTH_HAVE_KEY and self.key == other.key))

        return False


class Button(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font(), enabled: bool = True):
        super().__init__(key)
        self.__text = text
        self.__font = font
        self.enabled = enabled

    @property
    def value(self) -> str:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = str(value)

    @property
    def font(self) -> Font:
        return copy(self.__font)

    def __repr__(self):
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Button({KEY_ARGUMENT}text={self.value}, font={self.font}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        return (super().__eq__(other)
                and type(other) is Button
                and self.value == other.value
                and self.font == other.font
                and self.enabled == other.enabled)


class CheckBox(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font(), value: bool = False,
                 enabled: bool = True):
        super().__init__(key)

        self.__value = value
        self.text = text
        self.__font = font
        self.enabled = enabled

    @property
    def value(self) -> bool:
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = bool(value)

    @property
    def font(self) -> Font:
        return self.__font

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'CheckBox({KEY_ARGUMENT}text={self.text}, font={self.font}, value={self.value}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        return (super().__eq__(other)
                and type(other) is CheckBox
                and self.text == other.text
                and self.font == other.font
                and self.value == other.value
                and self.enabled == other.enabled)


class Combo(Widget):
    def __init__(self, key: Hashable = None, values: List[str] = [],
                 font: Font = Font(), size: Tuple[int, int] = (20, 7), enabled: bool = True):
        super().__init__(key)

        self.__values = list(str(value) for value in dict.fromkeys(values))
        self.__value = 0
        self.font = font
        self.size = size
        self.enabled = enabled

    @property
    def values(self) -> List[str]:
        return self.__values.copy()

    @property
    def value(self) -> str:
        try:
            return self.__values[self.__value]

        except IndexError:
            raise AttributeError('This Combo does not have any values.')

    @value.setter
    def value(self, value):
        try:
            self.__value = self.__values.index(value)

        except ValueError:
            raise ValueError(f"{value} is not in this Combo's list of values.")

    def add_value(self, value: str):
        if (value not in self.__values):
            self.__values.append(value)

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '
        VALUE = 'value=None, ' if (not hasattr(self, 'value')) else f'value={self.value}, '

        return f'Combo({KEY_ARGUMENT}values={self.__values}, {VALUE}font={self.font}, size={self.size}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        SELF_HAS_VALUE = hasattr(self, 'value')
        OTHER_HAS_VALUE = hasattr(other, 'value')

        NEITHER_HAVE_VALUE = not SELF_HAS_VALUE and not OTHER_HAS_VALUE
        BOTH_HAVE_VALUE = SELF_HAS_VALUE and OTHER_HAS_VALUE

        VALUES_ARE_EQUAL = (NEITHER_HAVE_VALUE
                            or (BOTH_HAVE_VALUE and self.value == other.value))

        return (super().__eq__(other)
                and type(other) is Combo
                and self.values == other.values
                and VALUES_ARE_EQUAL
                and self.font == other.font
                and self.size == other.size
                and self.enabled == other.enabled)


class Input(Widget):
    def __init__(self, key: Hashable = None, text: str = '', enabled: bool = True):
        super().__init__(key)

        self.__text = text
        self.enabled = enabled

    @property
    def value(self) -> str:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = str(value)

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Input({KEY_ARGUMENT}text={self.value}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        return(super().__eq__(other)
               and type(other) is Input
               and self.value == other.value
               and self.enabled == other.enabled)


class Multiline(Widget):
    def __init__(self, key: Hashable = None, text: str = '', size: Tuple[int, int] = (50, 7),
                 auto_scroll: bool = True, enabled: bool = True):
        super().__init__(key)

        self.__text = text
        self.size = size
        self.auto_scroll = auto_scroll
        self.enabled = enabled

    @property
    def value(self) -> str:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = str(value)

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Multiline({KEY_ARGUMENT}text={self.value}, size={self.size}, auto_scroll={self.auto_scroll}, enabled={self.enabled})'

    def __eq__(self, other: Any) -> bool:
        return (super().__eq__(other)
                and type(other) is Multiline
                and self.value == other.value
                and self.size == other.size
                and self.auto_scroll == other.auto_scroll
                and self.enabled == other.enabled)


class Text(Widget):
    def __init__(self, key: Hashable = None, text: str = '', font: Font = Font()):
        super().__init__(key)
        self.__text = text
        self.font = font

    @property
    def value(self) -> str:
        return self.__text

    @value.setter
    def value(self, value):
        self.__text = str(value)

    def __repr__(self) -> str:
        KEY_ARGUMENT = 'key=None, ' if (not hasattr(self, 'key')) else f'key={self.key}, '

        return f'Text({KEY_ARGUMENT}text={self.value}, font={self.font})'

    def __eq__(self, other: Any) -> bool:
        return (super().__eq__(other)
                and type(other) is Text
                and self.value == other.value
                and self.font == other.font)
