from typing import Tuple
from python.led_strip.array.array_led_strip import ArrayLedStrip
from python.led_strip.graphic.graphic_led_strip import GraphicLedStrip
import python.util.util as util

class GraphicArrayLedStrip(ArrayLedStrip, GraphicLedStrip):
    """An LED_Strip that displays to a Tkinter Canvas."""

    def __init__(self, led_index_range:Tuple[int,int], **kwargs):
        ArrayLedStrip.__init__(self, led_index_range)
        GraphicLedStrip.__init__(self, led_index_range, **kwargs)

    def _recolor_leds(self, start_index:int, end_index:int, rgb:Tuple[int,int,int]):
        for led_index in range(start_index, end_index):
            self._get_canvas().TKCanvas.itemconfig(self._get_tkinter_id(led_index), fill=util.rgb_to_hex(*rgb))

    def _show(self):
        GraphicLedStrip._show(self)
        ArrayLedStrip._show(self)