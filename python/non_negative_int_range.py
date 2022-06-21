from functools import total_ordering
from typing import Iterator


class NonNegativeIntRange:
    def __init__(self, start: int = 0, end: int = 0):
        '''
            Args:
                `start (NonNegativeInt)`: Inclusive.
                `end (NonNegativeInt)`: Exclusive.

            Example 1 : NonNegativeIntRange(0, 5) includes integers 0, 1, 2, 3, 4.

            Example 2 : NonNegativeIntRange(0, 0) is an empty set.
        '''
        if (not isinstance(start, int)):
            raise TypeError(f'start ({start}) must be of type int, but was of type {type(start)}.')

        if (not isinstance(end, int)):
            raise TypeError(f'end ({end}) must be of type int, but was of type {type(end)}.')

        start_non_negative_integer = NonNegativeInt(start)
        end_non_negative_integer = NonNegativeInt(end)

        if (start_non_negative_integer > end_non_negative_integer):
            raise ValueError(f'start ({start}) must be < end ({end}).')

        self.__start = start_non_negative_integer
        self.__end = end_non_negative_integer

    @property
    def start(self) -> int:
        return int(self.__start)

    @property
    def end(self) -> int:
        return int(self.__end)

    def __repr__(self) -> str:
        return f'NonNegativeIntRange({int(self.start)}, {int(self.end)})'

    def __contains__(self, value):
        if (self.start == self.end):
            return False

        if (isinstance(value, NonNegativeIntRange)):
            if (value.start == value.end):
                return True

            return (value.start in self) and (value.end - 1 in self)

        return (value >= self.start) and (value <= self.end - 1)

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.__start, self.__end))


@total_ordering
class NonNegativeInt:
    def __init__(self, value):

        if (int(value) < 0):
            raise ValueError(f'int({value}) must be >= 0.')

        self.__value = int(value)

    def __repr__(self) -> str:
        return f'NonNegativeInt({self.__value})'

    def __int__(self):
        return self.__value

    def __index__(self) -> int:
        return self.__value

    def __eq__(self, right_value):
        if (isinstance(right_value, NonNegativeInt)):
            return self.__value == int(right_value)

        return self.__value == right_value

    def __lt__(self, right_value):
        if (isinstance(right_value, NonNegativeInt)):
            return self.__value < int(right_value)

        return self.__value < right_value

    def __gt__(self, right_value):
        if (isinstance(right_value, NonNegativeInt)):
            return self.__value > int(right_value)

        return self.__value > right_value

    def __add__(self, right_value):
        if (isinstance(right_value, NonNegativeInt)):
            return NonNegativeInt(self.__value + int(right_value))

        return self.__value + right_value

    def __radd__(self, left_value):
        return left_value + self.__value

    def __sub__(self, right_value):
        if (isinstance(right_value, NonNegativeInt)):
            return self.__value - int(right_value)

        return self.__value - right_value

    def __rsub__(self, left_value):
        return left_value - self.__value

    def __mul__(self, right_value):
        if (isinstance(right_value, NonNegativeInt)):
            return NonNegativeInt(self.__value * int(right_value))

        return self.__value * right_value

    def __rmul__(self, left_value):
        return left_value * self.__value

    def __truediv__(self, right_value):
        if (isinstance(right_value, NonNegativeInt)):
            return self.__value / int(right_value)

        return self.__value / right_value

    def __rtruediv__(self, left_value):
        return left_value / self.__value
