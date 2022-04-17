# from typing import Callable, Tuple, Union, Dict


# # TODO : have a timer running in a separate thread which updates the color. Using # of iterations is a bad
# # idea b/c it's not consistent.
# class ColorShifter:
#     def __init__(self, iteration_to_rgb:Callable=None, iteration_domain:Tuple[int,int]=None):
#         if (iteration_to_rgb and iteration_domain):
#             self.__iteration_to_rgb = iteration_to_rgb
#             self.__iteration_domain = iteration_domain
#         else:
#             self.__iteration_to_rgb = ColorShifter.iteration_to_rgb
#             self.__iteration_domain = (0, 360)

#         self.__iteration_to_rgb_memo:Dict[int, Tuple[int,int,int]] = dict()
#         self.__set_iteration_to_rgb_memo()

#         self.__iteration = self.__iteration_domain[0]

#     def __set_iteration_to_rgb_memo(self):
#         for iteration in range(*self.__iteration_domain):
#             r,g,b = self.__iteration_to_rgb(iteration)
#             self.__iteration_to_rgb_memo[iteration] = (int(r), int(g), int(b))

#     def update(self):
#         if (self.__iteration + 1 >= self.__iteration_domain[1]):
#             self.__iteration = self.__iteration_domain[0]
#         else:
#             self.__iteration += 1

#     def get_rgb(self)->Tuple[int,int,int]:
#         return self.__iteration_to_rgb_memo[self.__iteration]

#     @staticmethod
#     def iteration_to_rgb(iteration:int)->Tuple[Union[int,float],Union[int,float],Union[int,float]]:
#         red = 0
#         green = 0
#         blue = 0
#         if (iteration >= 0 and iteration <= 60):
#             red = 212
#             green = 17 + (195/60)*iteration
#             blue = 17
#         elif (iteration >= 61 and iteration <= 120):
#             red = (24043/59) - (192/59)*iteration
#             green = 212
#             blue = 17
#         elif (iteration >= 121 and iteration <= 180):
#             red = 17
#             green = 212
#             blue = (-22052/59) + (192/59)*iteration
#         elif (iteration >= 181 and iteration <= 240):
#             red = 17
#             green = (47083/59) - (192/59)*iteration
#             blue = 212
#         elif (iteration >= 241 and iteration <= 300):
#             red = (-45092/59) + (192/59)*iteration
#             green = 17
#             blue = 212
#         elif (iteration >= 301 and iteration <= 360):
#             red = 212
#             blue = 17
#             green = (70123/59) - (192/59)*iteration

#         return (red,green,blue)
