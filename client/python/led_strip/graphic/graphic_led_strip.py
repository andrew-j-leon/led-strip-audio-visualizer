from typing import Dict, Union, List, Tuple
import math

import PySimpleGUI as sg

import python.led_strip.led_strip as led_strip
from python.gui.window import Window

class _Point:
    def __init__(self, x_value:Union[int,float], y_value:Union[int,float]):
        self.__x = x_value
        self.__y = y_value

    @property
    def x_value(self)->Union[int,float]:
        return self.__x
    @property
    def y_value(self)->Union[int,float]:
        return self.__y

    def get_tuple(self)->Tuple[Union[int,float], Union[int,float]]:
        return (self.__x, self.__y)

class GraphicLedStrip(led_strip.LedStrip):
    def __init__(self, led_index_range:Tuple[int,int], led_diameter:int=30, **kwargs):
        """
            Args:
                `led_diameter (int, optional)`: Each led's diameter length (in pixels).
        """
        led_strip.LedStrip.__init__(self, led_index_range)

        self.__set_window(**kwargs)
        self.__update_window()
        self.__led_index_to_tkinter_id:Dict[int,int] = dict()
        self.__draw_and_store_leds(led_diameter)

    def __set_window(self, **kwargs):
        canvas_:sg.Canvas = sg.Canvas(key="canvas", **kwargs) if (len(kwargs) > 0) else sg.Canvas(size=(1350, 600), background_color='#4a4a4a', key="canvas")
        layout:List[List[sg.Element]] = [[canvas_]]
        self.__window:Window = Window('LED Strip Visualizer', layout=layout, resizable=True, element_padding=(0,0),
                                            margins=(0,0), titlebar_background_color="#000917", titlebar_text_color="#8a8a8a", disable_close=True, disable_minimize=False)

    def _get_canvas(self):
        return self.__window["canvas"]

    def __del__(self):
        self.__window.close()

    def __draw_and_store_leds(self, led_diameter:Union[int, float]):
        MAX_X_COORDINATE = self._get_canvas().get_size()[0]
        LEDS_PER_ROW = math.floor(MAX_X_COORDINATE / led_diameter)
        LED_RADIUS = led_diameter / 2

        BLACK_HEX = "#000000"
        WHITE_HEX = "#ffffff"

        # Draw the LEDs on the TKinter Canvas
        # for i in range(self.get_number_of_leds()):
        for i in range(self._get_start_index(), self._get_end_index()+1):
            # center coordinates of the LED
            led_center_point = _Point(x_value=LED_RADIUS + led_diameter*(i % LEDS_PER_ROW), y_value=LED_RADIUS + led_diameter*(i // LEDS_PER_ROW),)

            top_left_point = _Point(led_center_point.x_value - LED_RADIUS, led_center_point.y_value - LED_RADIUS)
            bottom_right_point = _Point(led_center_point.x_value + LED_RADIUS, led_center_point.y_value + LED_RADIUS)

            self.__led_index_to_tkinter_id[i] = (self._get_canvas().TKCanvas.create_oval(top_left_point.get_tuple(), bottom_right_point.get_tuple(), fill=BLACK_HEX))

            # This font size ensures that the longest index values are as large as possible while still fitting inside
            # their LEDs
            font_size_pixels = (led_diameter+5)/len(str(self.get_number_of_leds()))
            font = ('Arial', int(-1*font_size_pixels), 'bold')

            # Draw the index numbers in each led
            self._get_canvas().TKCanvas.create_text(led_center_point.x_value, led_center_point.y_value, text=str(i), fill=WHITE_HEX, font=font)

        self.__update_window()

    def _show(self):
        self._for_each_queued_color_change(self._recolor_leds)
        self.__update_window()

    def __update_window(self):
        self.__window.read(timeout=0)

    def _recolor_leds(self, *args):
        pass

    def _get_tkinter_id(self, led_index:int)->int:
        return self.__led_index_to_tkinter_id[led_index]
