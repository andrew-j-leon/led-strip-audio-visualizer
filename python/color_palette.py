from typing import List

from util import RGB


class ColorPalette:
    def __init__(self, colors: List[List[RGB]], amp_upper_bounds: List[int]):
        self.__colors = colors
        self.__amp_upper_bounds = amp_upper_bounds

    def get_colors(self, amp: int) -> List[RGB]:
        for i in range(len(self.__amp_upper_bounds)):
            if (amp <= self.__amp_upper_bounds[i]):
                return self.__colors[i]

        return self.__colors[-1]
