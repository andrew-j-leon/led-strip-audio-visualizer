from typing import List, Tuple

from python.led_strip.grouped.grouped_led_strip import GroupedLedStrip
from python.led_strip.graphic.graphic_led_strip import GraphicLedStrip
import python.util.util as util


class GraphicGroupedLedStrip(GroupedLedStrip, GraphicLedStrip):
    def __init__(self, led_index_range: Tuple[int, int], group_index_to_led_range: List[Tuple[int, int]], **kwargs):
        GroupedLedStrip.__init__(self, led_index_range, group_index_to_led_range)
        GraphicLedStrip.__init__(self, led_index_range, **kwargs)

    def _recolor_leds(self, group_index: int, rgb: Tuple[int, int, int]):
        for led_index in range(*(self._group_index_to_led_range[group_index])):
            self._get_canvas().TKCanvas.itemconfig(self._get_tkinter_id(led_index), fill=util.rgb_to_hex(*rgb))

    def _show(self):
        GraphicLedStrip._show(self)
        GroupedLedStrip._show(self)
