# import math
# from typing import Dict, List, Tuple, Union

# import python.util.util as util
# from python.visualizer.visualizer import Visualizer
# from python.led_strip.array.array_led_strip import ArrayLedStrip
# from python.visualizer.amplitude.util import ColorShifter


# class AmplitudeVisualizer(Visualizer):
#     """
#     Uses an LED_Strip as an audio amplitude visualizer. Lights radiate out from the
#     center of the LED_Strip.
#     """
#     def __init__(self, array_led_strips:List[ArrayLedStrip]=[], color_shifter:ColorShifter=ColorShifter(), number_of_update_calls_per_color_shift:int=7):

#         self.__strip_length_to_led_strips:Dict[int, List[ArrayLedStrip]] = dict()
#         self.__store_led_strips_by_length(array_led_strips)

#         self.__color_shifter = color_shifter

#         self.__number_of_update_calls_per_color_shift = number_of_update_calls_per_color_shift
#         self.__number_of_update_calls = 0

#         self.__previous_amplitude:float = 0.0
#         self.__current_amplitude:float = 0.0

#     def __store_led_strips_by_length(self, led_strips:List[ArrayLedStrip]):
#         for led_strip in led_strips:
#             if (led_strip.get_number_of_leds() in self.__strip_length_to_led_strips):
#                 self.__strip_length_to_led_strips[led_strip.get_number_of_leds()].append(led_strip)
#             elif (led_strip.get_number_of_leds() > 0):
#                 self.__strip_length_to_led_strips[led_strip.get_number_of_leds()] = [led_strip]

#     def _do_stuff_on_del(self):
#         for led_strips in self.__strip_length_to_led_strips.values():
#             for led_strip in led_strips:
#                 del led_strip

#     def _turn_on_leds(self, audio_data:bytes):
#         color_has_shifted = self.__update_color_shifter()

#         amplitude = util.get_average_amplitude(audio_data)

#         self.__previous_amplitude = self.__current_amplitude
#         self.__current_amplitude = amplitude

#         for strip_length in self.__strip_length_to_led_strips:
#             previous_number_of_leds_turned_on = AmplitudeVisualizer.__get_number_of_leds_turned_on(self.__previous_amplitude, strip_length)
#             current_number_of_leds_turned_on = AmplitudeVisualizer.__get_number_of_leds_turned_on(self.__current_amplitude, strip_length)

#             led_strip_middle_index = int(strip_length/2)

#             # New LEDs were turned on OR no new LEDs were turned on, but the color has shifted
#             if (previous_number_of_leds_turned_on < current_number_of_leds_turned_on or (previous_number_of_leds_turned_on == current_number_of_leds_turned_on
#                                                                                          and color_has_shifted)):
#                 self.__set_led_strips_ranges(strip_length, AmplitudeVisualizer.__get_bounds_left_of_center(led_strip_middle_index, current_number_of_leds_turned_on),
#                                     1+AmplitudeVisualizer.__get_bounds_right_of_center(led_strip_middle_index, current_number_of_leds_turned_on, strip_length),
#                                     self.__color_shifter.get_rgb())

#                 self.__show_led_strips(strip_length)

#             # Some LEDs were turned off
#             elif (previous_number_of_leds_turned_on > current_number_of_leds_turned_on):
#                 # Turn LEDs on the edges off
#                 BLACK_RGB = (0,0,0)

#                 self.__set_led_strips_ranges(strip_length, AmplitudeVisualizer.__get_bounds_left_of_center(led_strip_middle_index, previous_number_of_leds_turned_on),
#                                     1+AmplitudeVisualizer.__get_bounds_left_of_center(led_strip_middle_index, current_number_of_leds_turned_on),
#                                     BLACK_RGB)
#                 self.__set_led_strips_ranges(strip_length, AmplitudeVisualizer.__get_bounds_right_of_center(led_strip_middle_index, current_number_of_leds_turned_on,
#                                                                                                             strip_length),
#                                     1+AmplitudeVisualizer.__get_bounds_right_of_center(led_strip_middle_index, previous_number_of_leds_turned_on, strip_length),
#                                     BLACK_RGB)

#                 self.__show_led_strips(strip_length)

#                 # Relight the LEDs still turned on b/c the color has shifted
#                 if (color_has_shifted):
#                     self.__set_led_strips_ranges(strip_length, AmplitudeVisualizer.__get_bounds_left_of_center(led_strip_middle_index, current_number_of_leds_turned_on),
#                                     1+AmplitudeVisualizer.__get_bounds_right_of_center(led_strip_middle_index, current_number_of_leds_turned_on, strip_length),
#                                     self.__color_shifter.get_rgb())

#                     self.__show_led_strips(strip_length)

#     def __update_color_shifter(self)->bool:
#         """
#             Returns:
#                 `bool`: True if the color has shifted. False if it hasn't.
#         """
#         if (self.__number_of_update_calls >= self.__number_of_update_calls_per_color_shift):
#             self.__number_of_update_calls = 0
#             self.__color_shifter.update()
#             return True
#         else:
#             self.__number_of_update_calls += 1
#             return False

#     @staticmethod
#     def __get_number_of_leds_turned_on(amplitude:Union[float,int], number_of_leds:int)->int:
#         amplitude_threshold = AmplitudeVisualizer.__get_amplitude_threshold(number_of_leds)
#         number_of_leds_lit_per_decibel = AmplitudeVisualizer.__get_number_of_leds_lit_per_decibel(number_of_leds)
#         return max(0, math.floor((amplitude - amplitude_threshold) * number_of_leds_lit_per_decibel))

#     @staticmethod
#     def __get_bounds_left_of_center(center_led_index:int, amplitude:int, min_index=0)->int:
#         left_bounds = center_led_index - amplitude
#         return max(min_index, left_bounds)

#     @staticmethod
#     def __get_bounds_right_of_center(center_led_index:int, amplitude:int, max_index:int)->int:
#         # max_index is exclusive
#         right_bounds = center_led_index + amplitude
#         return min(max_index-1, right_bounds)

#     def __show_led_strips(self, strip_length:int):
#         if (strip_length in self.__strip_length_to_led_strips):
#             for led_strip in self.__strip_length_to_led_strips[strip_length]:
#                 led_strip.show()

#     @staticmethod
#     def __get_amplitude_threshold(number_of_leds:int)->float:
#         if (number_of_leds <= 0):
#             return 0

#         # This equation is based on my observation that for 300 LEDs, an amplitude threshold of 45 dB looks nicest.
#         # Therefore, we have : (45 dB / 300 LEDs) = (y dB / x LEDs) -> y = (45/300)x
#         return (45/300)*number_of_leds

#     @staticmethod
#     def __get_number_of_leds_lit_per_decibel(number_of_leds:int)->float:
#         if (number_of_leds <= 0):
#             return 0

#         # This equation is based on my observation that for 300 LEDs, lighting up 3.8 LEDs per dB (above the amplitude threshold)
#         # looks nicest. Therefore, we have (3.8 LEDs lit / 300 Total LEDs) = (y LEDs lit / x Total LEDs) -> y = (3.8/300)x
#         return (3.8/300)*number_of_leds

#     def __set_led_strips_ranges(self, strip_length:int, start_index:int, end_index:int, rgb:Tuple[int,int,int]):
#         if (strip_length in self.__strip_length_to_led_strips):
#             for led_strip in self.__strip_length_to_led_strips[strip_length]:
#                 led_strip.set_range_color(start_index, end_index, rgb)

#     def _turn_off_leds(self):
#         BLACK_RGB = (0,0,0)
#         for strip_length in self.__strip_length_to_led_strips:
#             self.__set_led_strips_ranges(strip_length, 0, strip_length, BLACK_RGB)
#             self.__show_led_strips(strip_length)
