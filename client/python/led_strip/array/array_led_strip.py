
from typing import Dict, Tuple

import python.led_strip.led_strip as led_strip


class ArrayLedStrip(led_strip.LedStrip):
    # Base class for an LED strip that represents an LED strip as an array. You set colors using set_range_color
    # This is most efficient when LEDs are NOT divided into groups. If they are, use GroupedLedStrip instead!

    def __init__(self, led_index_range: Tuple[int, int]):
        led_strip.LedStrip.__init__(self, led_index_range)

        self.__led_index_to_its_rgb: Dict[int, Tuple[int, int, int]] = dict()
        for i in range(self._get_start_index(), self._get_end_index() + 1):
            self.__led_index_to_its_rgb[i] = (0, 0, 0)

    def led_matches_rgb(self, led_index: int, rgb: Tuple[int, int, int]) -> bool:
        return self.__led_index_to_its_rgb[self._shift_led_index_up_by_start_index(led_index)] == rgb

    def set_range_color(self, start_index: int, end_index: int, rgb: Tuple[int, int, int]):
        if (start_index >= end_index):
            raise ValueError("start_index must be < end_index")

        if (end_index > self.get_number_of_leds()):
            raise IndexError("indicies range from 0 to {}, but end_index was {}.".format(self.get_number_of_leds() - 1, end_index))

        shifted_start_index = self._shift_led_index_up_by_start_index(start_index)
        shifted_end_index = self._shift_led_index_up_by_start_index(end_index)

        self._enqueue_color_change_by_index(shifted_start_index, shifted_end_index, rgb)

    def _show(self):
        self._for_each_queued_color_change(self.__set_color)

    def __set_color(self, start_index: int, end_index: int, rgb: Tuple[int, int, int]):
        for index in range(start_index, end_index):
            self.__led_index_to_its_rgb[index] = rgb


# class Remote_LED_Strip(LED_Strip):
#     def __init__(self, number_of_leds:int, host:str, port:int):
#         super().__init__()

#         self.__number_of_leds = number_of_leds
#         self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.__socket.connect((host, port))

#     def __del__(self):
#         self.__socket.close()

#     def __len__(self):
#         return self.__number_of_leds

#     def show(self):
#         self.__socket.sendall(self._queued_color_changes.qsize().to_bytes(length=1, byteorder="big")) # Tell the Arduino how many packets will be sent in this call to show()

#         while (self._queued_color_changes.empty()):
#             self.__send_packet(*self._queued_color_changes.get())

#     def __send_packet(self, start_index, end_index, rgb):
#         packet = start_index.to_bytes(length=2, byteorder="big") + end_index.to_bytes(2, "big")

#         for color in rgb:
#             packet += color.to_bytes(1, "big")

#         self.__socket.sendall(packet)

#     # def set_range_color(self, start_index:int, end_index:int, rgb:Tuple[int,int,int]):
#     #     """Set all LED colors from start_index (inclusive) to end_index (exclusive)
#     #        to the provided rgb 3-tuple (red, green, blue).

#     #     Args:
#     #         start_index (int) : Inclusive
#     #         end_index (int) : Exclusive
#     #         rgb (Tuple[int,int,int]): (red, green, blue) values. Each color is an integer
#     #         in the range [0, 255].

#     #     Raises:
#     #         IndexError, ValueError
#     #     """

#     #     packet = start_index.to_bytes(length=2, byteorder="big") + end_index.to_bytes(2, "big")

#     #     for color in rgb:
#     #         packet += color.to_bytes(1, "big")

#     #     self.__socket.sendall(packet)
