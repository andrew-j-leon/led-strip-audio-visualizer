from __future__ import annotations

from collections import Counter
from enum import Enum, auto
from typing import Any, Callable, Dict, Hashable, List, Tuple, Union

from color_palette import ColorPalette
from controller.controller import Controller
from libraries.widget import Button, ColorPicker, Combo, Input, Text, Widget
from libraries.widget_gui import WidgetGui, WidgetGuiEvent
from selection import Selection
from util import Font, hex_to_rgb, rgb_to_hex


class Element(Enum):
    SAVE_NAME_COMBO = auto()
    SAVE_BUTTON = auto()
    DELETE_BUTTON = auto()

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


class Event(Enum):
    SELECT_CURRENT_SAVE = auto()
    SELECT_NON_CURRENT_SAVE = auto()
    DELETE_SAVE_NAME = auto()
    ENTER_NEW_SAVE_NAME = auto()


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


class ColorPaletteController(Controller):
    def __init__(self, create_gui: Callable[[], WidgetGui],
                 save_selection: Callable[[Selection[ColorPalette]], None],
                 selection: Selection[ColorPalette] = Selection()):
        self.__gui = create_gui()
        self.__gui.title = 'Color Palettes'

        self.__save_selection = save_selection
        self.__selection = selection

    def close(self):
        self.__gui.close()

    def read_event_and_update_gui(self) -> Union[Element, WidgetGuiEvent, Event]:
        EVENT = self.__gui.read_event_and_update_gui()

        if (EVENT == WidgetGuiEvent.TIMEOUT):
            CURRENT_SAVE_NAME = self.__get_current_save_name()

            if (self.__the_current_name_is_selected(CURRENT_SAVE_NAME)):
                return Event.SELECT_CURRENT_SAVE

            elif (self.__a_non_current_name_is_selected(CURRENT_SAVE_NAME)):
                return Event.SELECT_NON_CURRENT_SAVE

            elif (CURRENT_SAVE_NAME == ''):
                return Event.DELETE_SAVE_NAME

            return Event.ENTER_NEW_SAVE_NAME

        return EVENT

    def handle_event(self, event: Union[Element, WidgetGuiEvent]):
        CURRENT_SAVE_NAME = self.__get_current_save_name()

        if (event == Element.SAVE_BUTTON):
            self.__set_color_palette()
            self.__save_selection(self.__selection)
            self.__update_widgets()

        elif (event == Element.DELETE_BUTTON):
            try:
                del self.__selection[CURRENT_SAVE_NAME]
                self.__save_selection(self.__selection)
                self.__update_widgets()

            except KeyError:
                raise ValueError(f'There is no ColorPalette with the name {CURRENT_SAVE_NAME} to delete.')

        elif (event == WidgetGuiEvent.CLOSE_WINDOW):
            self.__gui.close()

        elif (event != WidgetGuiEvent.TIMEOUT):
            SAVE_BUTTON: Button = self.__gui.get_widget(Element.SAVE_BUTTON)
            DELETE_BUTTON: Button = self.__gui.get_widget(Element.DELETE_BUTTON)

            if (event == Event.SELECT_CURRENT_SAVE):
                SAVE_BUTTON.enabled = True
                DELETE_BUTTON.enabled = True

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

            elif (event == Event.SELECT_NON_CURRENT_SAVE):
                try:
                    self.__selection.selected_key = CURRENT_SAVE_NAME
                    self.__update_widgets()

                except ValueError:
                    raise ValueError(f"The selected color_pallete name {CURRENT_SAVE_NAME} is not in "
                                     "this ColorPaletteController's ColorPalette Selection.")

            elif (event == Event.DELETE_SAVE_NAME):
                SAVE_BUTTON.enabled = False
                DELETE_BUTTON.enabled = False

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

            elif (event == Event.ENTER_NEW_SAVE_NAME):
                SAVE_BUTTON.enabled = True
                DELETE_BUTTON.enabled = False

                self.__gui.update_widgets(SAVE_BUTTON, DELETE_BUTTON)

            else:
                raise ValueError(f'This ColorPaletteController does not recognize the event {event}.')

    def display(self):
        WIDGETS = self.__create_widgets()

        def get_widget(widget_key: Element) -> Widget:
            return WIDGETS[widget_key]

        SAVE_NAME_COMBO = get_widget(Element.SAVE_NAME_COMBO)
        SAVE_BUTTON = get_widget(Element.SAVE_BUTTON)
        DELETE_BUTTON = get_widget(Element.DELETE_BUTTON)

        DECIBEL_INPUT_0 = get_widget(Element.DECIBEL_INPUT_0)
        COLOR_PICKER_0 = get_widget(Element.COLOR_PICKER_0)

        DECIBEL_INPUT_1 = get_widget(Element.DECIBEL_INPUT_1)
        COLOR_PICKER_1 = get_widget(Element.COLOR_PICKER_1)

        DECIBEL_INPUT_2 = get_widget(Element.DECIBEL_INPUT_2)
        COLOR_PICKER_2 = get_widget(Element.COLOR_PICKER_2)

        DECIBEL_INPUT_3 = get_widget(Element.DECIBEL_INPUT_3)
        COLOR_PICKER_3 = get_widget(Element.COLOR_PICKER_3)

        DECIBEL_INPUT_4 = get_widget(Element.DECIBEL_INPUT_4)
        COLOR_PICKER_4 = get_widget(Element.COLOR_PICKER_4)

        FONT = Font("Courier New", 14)

        FIRST_TEXT = Text(text='First', font=FONT)
        NEXT_TEXT = Text(text='next', font=FONT)
        DECIBELS_TEXT = Text(text='decibels (dB) are')

        LAYOUT = [[SAVE_NAME_COMBO, SAVE_BUTTON, DELETE_BUTTON],
                  [FIRST_TEXT, DECIBEL_INPUT_0, DECIBELS_TEXT, COLOR_PICKER_0],
                  [NEXT_TEXT, DECIBEL_INPUT_1, DECIBELS_TEXT, COLOR_PICKER_1],
                  [NEXT_TEXT, DECIBEL_INPUT_2, DECIBELS_TEXT, COLOR_PICKER_2],
                  [NEXT_TEXT, DECIBEL_INPUT_3, DECIBELS_TEXT, COLOR_PICKER_3],
                  [NEXT_TEXT, DECIBEL_INPUT_4, DECIBELS_TEXT, COLOR_PICKER_4]]

        self.__gui.set_layout(LAYOUT)
        self.__gui.display_layout()

    def __get_current_save_name(self) -> str:
        try:
            COMBO = self.__gui.get_widget(Element.SAVE_NAME_COMBO)
            return COMBO.value

        except AttributeError:
            return ''

    def __the_current_name_is_selected(self, name: str) -> bool:
        try:
            return name == self.__selection.selected_key

        except AttributeError:
            return False

    def __a_non_current_name_is_selected(self, name: str):
        return (name in self.__selection
                and name != self.__selection.selected_key)

    def __update_widgets(self):
        WIDGETS = self.__create_widgets()

        for widget in WIDGETS.values():
            self.__gui.update_widget(widget)

    def __create_widgets(self) -> Dict[Element, Widget]:
        def create_save_name_combo():
            SAVE_NAMES = list(self.__selection.keys())
            COMBO_SIZE = (40, 7)

            combo = Combo(Element.SAVE_NAME_COMBO, SAVE_NAMES, size=COMBO_SIZE)

            try:
                combo.value = self.__selection.selected_key
                return combo

            except AttributeError:
                return combo

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

        FONT = Font("Courier New", 14)
        COLOR_PALETTE = (ColorPalette() if (not hasattr(self.__selection, 'selected_value'))
                         else self.__selection.selected_value)

        SAVE_NAME_COMBO = create_save_name_combo()
        SAVE_BUTTON = Button(Element.SAVE_BUTTON, "Save", FONT, True)
        DELETE_BUTTON = Button(Element.DELETE_BUTTON, "Delete", FONT, True)

        def create_widgets(*widgets: Widget) -> Dict[Hashable, Widget]:
            result = dict()

            for widget in widgets:
                result[widget.key] = widget

            return result

        return create_widgets(SAVE_NAME_COMBO, SAVE_BUTTON, DELETE_BUTTON,
                              *create_amplitude_rgbs_widgets(COLOR_PALETTE))

    def __set_color_palette(self):
        COLOR_PALETTE = self.__create_color_palette_from_widget_gui()

        SAVE_NAME_COMBO = self.__gui.get_widget(Element.SAVE_NAME_COMBO)
        NAME = SAVE_NAME_COMBO.value

        self.__selection[NAME] = COLOR_PALETTE
        self.__selection.selected_key = NAME

    def __create_color_palette_from_widget_gui(self) -> ColorPalette:
        NUMBER_OF_DECIBELS_1 = self.__get_setting_from_widget_gui(Element.DECIBEL_INPUT_0)
        NUMBER_OF_DECIBELS_2 = self.__get_setting_from_widget_gui(Element.DECIBEL_INPUT_1)
        NUMBER_OF_DECIBELS_3 = self.__get_setting_from_widget_gui(Element.DECIBEL_INPUT_2)
        NUMBER_OF_DECIBELS_4 = self.__get_setting_from_widget_gui(Element.DECIBEL_INPUT_3)
        NUMBER_OF_DECIBELS_5 = self.__get_setting_from_widget_gui(Element.DECIBEL_INPUT_4)

        COLOR_PICKER_0 = self.__get_setting_from_widget_gui(Element.COLOR_PICKER_0)
        COLOR_PICKER_1 = self.__get_setting_from_widget_gui(Element.COLOR_PICKER_1)
        COLOR_PICKER_2 = self.__get_setting_from_widget_gui(Element.COLOR_PICKER_2)
        COLOR_PICKER_3 = self.__get_setting_from_widget_gui(Element.COLOR_PICKER_3)
        COLOR_PICKER_4 = self.__get_setting_from_widget_gui(Element.COLOR_PICKER_4)

        AMPLITUDE_RGBS = ([hex_to_rgb(COLOR_PICKER_0)] * NUMBER_OF_DECIBELS_1
                          + [hex_to_rgb(COLOR_PICKER_1)] * NUMBER_OF_DECIBELS_2
                          + [hex_to_rgb(COLOR_PICKER_2)] * NUMBER_OF_DECIBELS_3
                          + [hex_to_rgb(COLOR_PICKER_3)] * NUMBER_OF_DECIBELS_4
                          + [hex_to_rgb(COLOR_PICKER_4)] * NUMBER_OF_DECIBELS_5)

        return ColorPalette(AMPLITUDE_RGBS)

    def __get_setting_from_widget_gui(self, setting_element: Element) -> Any:
        INTEGER_SETTINGS = {Element.DECIBEL_INPUT_0,
                            Element.DECIBEL_INPUT_1,
                            Element.DECIBEL_INPUT_2,
                            Element.DECIBEL_INPUT_3,
                            Element.DECIBEL_INPUT_4}

        WIDGET = self.__gui.get_widget(setting_element)
        WIDGET_VALUE = WIDGET.value

        if (setting_element in INTEGER_SETTINGS):
            return int(WIDGET_VALUE)

        return WIDGET_VALUE
