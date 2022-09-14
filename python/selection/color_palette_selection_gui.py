from __future__ import annotations

from collections import Counter
from enum import Enum, auto
from typing import Any, Dict, List, Tuple

from color_palette import ColorPalette
from libraries.widget import ColorPicker, Input, Text, Widget
from libraries.widget_gui import WidgetGui
from selection.selection import Selection
from selection.selection_gui import SelectionGui
from settings import Settings
from util import Font, hex_to_rgb, rgb_to_hex


class Element(Enum):
    DECIBEL_INPUT_0 = auto()
    COLOR_PICKER_0 = auto()

    DECIBEL_INPUT_1 = auto()
    COLOR_PICKER_1 = auto()

    DECIBEL_INPUT_2 = auto()
    COLOR_PICKER_2 = auto()

    DECIBEL_INPUT_3 = auto()
    COLOR_PICKER_3 = auto()

    DECIBEL_INPUT_4 = auto()
    COLOR_PICKER_4 = auto()


def create_color_palette_gui_values(amplitude_rgbs: List[Tuple[int, int, int]],
                                    number_of_colors: int) -> List[Tuple[int, str]]:
    COUNTER = Counter(amplitude_rgbs)

    gui_values: List[Tuple[int, str]] = []

    i = -1
    for rgb, count in COUNTER.items():
        i += 1

        if (i < number_of_colors):
            red, green, blue = rgb
            hex = rgb_to_hex(red, green, blue)
            gui_values.append((count, hex))

    NUMBER_OF_DECIBELS = 0
    BLACK_HEX = '#000000'

    for j in range(i + 1, number_of_colors):
        gui_values.append((NUMBER_OF_DECIBELS, BLACK_HEX))

    return gui_values


class ColorPaletteSelectionGui(SelectionGui):
    def _get_title(self) -> str:
        return 'Color Palettes'

    def _get_selection(self, selected_key, gui):
        color_palette = self.__create_color_palette_from_widget_gui(gui)
        return Selection({selected_key: color_palette})

    def _create_layout(self, selection):
        WIDGETS = self.__create_updatable_widgets(selection)

        DECIBEL_INPUT_0 = WIDGETS[Element.DECIBEL_INPUT_0]
        COLOR_PICKER_0 = WIDGETS[Element.COLOR_PICKER_0]

        DECIBEL_INPUT_1 = WIDGETS[Element.DECIBEL_INPUT_1]
        COLOR_PICKER_1 = WIDGETS[Element.COLOR_PICKER_1]

        DECIBEL_INPUT_2 = WIDGETS[Element.DECIBEL_INPUT_2]
        COLOR_PICKER_2 = WIDGETS[Element.COLOR_PICKER_2]

        DECIBEL_INPUT_3 = WIDGETS[Element.DECIBEL_INPUT_3]
        COLOR_PICKER_3 = WIDGETS[Element.COLOR_PICKER_3]

        DECIBEL_INPUT_4 = WIDGETS[Element.DECIBEL_INPUT_4]
        COLOR_PICKER_4 = WIDGETS[Element.COLOR_PICKER_4]

        FONT = Font("Courier New", 14)

        FIRST_TEXT = Text(text='First', font=FONT)
        NEXT_TEXT = Text(text='next', font=FONT)
        DECIBELS_TEXT = Text(text='decibels (dB) are')

        LAYOUT = [[FIRST_TEXT, DECIBEL_INPUT_0, DECIBELS_TEXT, COLOR_PICKER_0],
                  [NEXT_TEXT, DECIBEL_INPUT_1, DECIBELS_TEXT, COLOR_PICKER_1],
                  [NEXT_TEXT, DECIBEL_INPUT_2, DECIBELS_TEXT, COLOR_PICKER_2],
                  [NEXT_TEXT, DECIBEL_INPUT_3, DECIBELS_TEXT, COLOR_PICKER_3],
                  [NEXT_TEXT, DECIBEL_INPUT_4, DECIBELS_TEXT, COLOR_PICKER_4]]

        return LAYOUT

    def _create_updatable_widgets(self, selection):
        return self.__create_updatable_widgets(selection).values()

    def __create_updatable_widgets(self, selection: Selection[Settings]) -> Dict[Element, Widget]:
        def create_amplitude_rgbs_widgets(color_palette: ColorPalette) -> List[Widget]:
            KEYS = [(Element.DECIBEL_INPUT_0, Element.COLOR_PICKER_0),
                    (Element.DECIBEL_INPUT_1, Element.COLOR_PICKER_1),
                    (Element.DECIBEL_INPUT_2, Element.COLOR_PICKER_2),
                    (Element.DECIBEL_INPUT_3, Element.COLOR_PICKER_3),
                    (Element.DECIBEL_INPUT_4, Element.COLOR_PICKER_4)]

            NUMBER_OF_COLORS = len(KEYS)
            GUI_VALUES = create_color_palette_gui_values(color_palette.amplitude_rgbs, NUMBER_OF_COLORS)

            widgets = []

            for i in range(NUMBER_OF_COLORS):
                count, color = GUI_VALUES[i]
                input_key, color_picker_key = KEYS[i]

                widgets += [Input(input_key, count), ColorPicker(color_picker_key, color)]

            return widgets

        COLOR_PALETTE = (ColorPalette() if (not hasattr(selection, 'selected_value'))
                         else selection.selected_value)

        return dict((widget.key, widget) for widget in create_amplitude_rgbs_widgets(COLOR_PALETTE))

    def __create_color_palette_from_widget_gui(self, gui: WidgetGui) -> Settings:
        def get_setting_from_wiget_gui(setting_element: Element) -> Any:
            INTEGER_SETTINGS = {Element.DECIBEL_INPUT_0,
                                Element.DECIBEL_INPUT_1,
                                Element.DECIBEL_INPUT_2,
                                Element.DECIBEL_INPUT_3,
                                Element.DECIBEL_INPUT_4}

            WIDGET = gui.get_widget(setting_element)
            WIDGET_VALUE = WIDGET.value

            if (setting_element in INTEGER_SETTINGS):
                return int(WIDGET_VALUE)

            return WIDGET_VALUE

        NUMBER_OF_DECIBELS_1 = get_setting_from_wiget_gui(Element.DECIBEL_INPUT_0)
        NUMBER_OF_DECIBELS_2 = get_setting_from_wiget_gui(Element.DECIBEL_INPUT_1)
        NUMBER_OF_DECIBELS_3 = get_setting_from_wiget_gui(Element.DECIBEL_INPUT_2)
        NUMBER_OF_DECIBELS_4 = get_setting_from_wiget_gui(Element.DECIBEL_INPUT_3)
        NUMBER_OF_DECIBELS_5 = get_setting_from_wiget_gui(Element.DECIBEL_INPUT_4)

        COLOR_PICKER_0 = get_setting_from_wiget_gui(Element.COLOR_PICKER_0)
        COLOR_PICKER_1 = get_setting_from_wiget_gui(Element.COLOR_PICKER_1)
        COLOR_PICKER_2 = get_setting_from_wiget_gui(Element.COLOR_PICKER_2)
        COLOR_PICKER_3 = get_setting_from_wiget_gui(Element.COLOR_PICKER_3)
        COLOR_PICKER_4 = get_setting_from_wiget_gui(Element.COLOR_PICKER_4)

        AMPLITUDE_RGBS = ([hex_to_rgb(COLOR_PICKER_0)] * NUMBER_OF_DECIBELS_1
                          + [hex_to_rgb(COLOR_PICKER_1)] * NUMBER_OF_DECIBELS_2
                          + [hex_to_rgb(COLOR_PICKER_2)] * NUMBER_OF_DECIBELS_3
                          + [hex_to_rgb(COLOR_PICKER_3)] * NUMBER_OF_DECIBELS_4
                          + [hex_to_rgb(COLOR_PICKER_4)] * NUMBER_OF_DECIBELS_5)

        return ColorPalette(AMPLITUDE_RGBS)
