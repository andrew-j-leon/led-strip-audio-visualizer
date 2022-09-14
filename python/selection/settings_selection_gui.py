from enum import Enum, auto
from typing import Any, Dict, List

from libraries.widget import CheckBox, Combo, Input, Text, Widget
from libraries.widget_gui import WidgetGui
from selection.selection import Selection
from selection.selection_gui import SelectionGui
from settings import Settings
from util import Font


class Element(Enum):
    START_LED_INPUT = auto()
    END_LED_INPUT = auto()
    MILLISECONDS_PER_AUDIO_CHUNK_INPUT = auto()
    SERIAL_PORT_INPUT = auto()
    SERIAL_BAUDRATE_COMBO = auto()
    BRIGHTNESS_INPUT = auto()
    NUMBER_OF_GROUPS_INPUT = auto()
    MINIMUM_FREQUENCY_INPUT = auto()
    MAXIMUM_FREQUENCY_INPUT = auto()
    REVERSE_LEDS_CHECK_BOX = auto()


class SettingsSelectionGui(SelectionGui):
    def _get_title(self) -> str:
        return 'Settings'

    def _get_selection(self, selected_key, gui):
        settings = self.__create_settings_from_widget_gui(gui)
        return Selection({selected_key: settings})

    def _create_layout(self, selection):
        WIDGETS = self.__create_updatable_widgets(selection)

        START_LED_INPUT = WIDGETS[Element.START_LED_INPUT]
        END_LED_INPUT = WIDGETS[Element.END_LED_INPUT]
        MILLISECONDS_PER_AUDIO_CHUNK_INPUT = WIDGETS[Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT]
        SERIAL_PORT_INPUT = WIDGETS[Element.SERIAL_PORT_INPUT]
        BAUDRATES_COMBO = WIDGETS[Element.SERIAL_BAUDRATE_COMBO]
        BRIGHTNESS_INPUT = WIDGETS[Element.BRIGHTNESS_INPUT]
        NUMBER_OF_GROUPS_INPUT = WIDGETS[Element.NUMBER_OF_GROUPS_INPUT]
        MINIMUM_FREQUENCY_INPUT = WIDGETS[Element.MINIMUM_FREQUENCY_INPUT]
        MAXIMUM_FREQUENCY_INPUT = WIDGETS[Element.MAXIMUM_FREQUENCY_INPUT]
        REVERSE_LEDS_CHECK_BOX = WIDGETS[Element.REVERSE_LEDS_CHECK_BOX]

        FONT = Font("Courier New", 14)

        START_LED_LABEL = Text(text="Start LED (inclusive):", font=FONT)
        END_LED_LABEL = Text(text="End LED (exclusive):", font=FONT)
        MILLISECONDS_PER_AUDIO_CHUNK_LABEL = Text(text="Milliseconds per Audio Chunk:", font=FONT)
        SERIAL_PORT_LABEL = Text(text="Port:", font=FONT)
        BAUDRATES_LABEL = Text(text="Baudrate:", font=FONT)
        BRIGHTNESS_LABEL = Text(text="Brightness", font=FONT)
        NUMBER_OF_GROUPS_LABEL = Text(text="Number of Groups:", font=FONT)
        MINIMUM_FREQUENCY_LABEL = Text(text="Minimum Frequency:", font=FONT)
        MAXIMUM_FREQUENCY_LABEL = Text(text="Maximum Frequency:", font=FONT)

        LAYOUT = [[START_LED_LABEL, START_LED_INPUT],
                  [END_LED_LABEL, END_LED_INPUT],
                  [MILLISECONDS_PER_AUDIO_CHUNK_LABEL, MILLISECONDS_PER_AUDIO_CHUNK_INPUT],
                  [SERIAL_PORT_LABEL, SERIAL_PORT_INPUT],
                  [BAUDRATES_LABEL, BAUDRATES_COMBO],
                  [BRIGHTNESS_LABEL, BRIGHTNESS_INPUT],
                  [NUMBER_OF_GROUPS_LABEL, NUMBER_OF_GROUPS_INPUT],
                  [MINIMUM_FREQUENCY_LABEL, MINIMUM_FREQUENCY_INPUT],
                  [MAXIMUM_FREQUENCY_LABEL, MAXIMUM_FREQUENCY_INPUT],
                  [REVERSE_LEDS_CHECK_BOX]]

        return LAYOUT

    def _create_updatable_widgets(self, selection):
        return self.__create_updatable_widgets(selection).values()

    def __create_updatable_widgets(self, selection: Selection[Settings]) -> Dict[Element, Widget]:
        SETTINGS = (Settings() if (not hasattr(selection, 'selected_value'))
                    else selection.selected_value)

        def create_baudrates_combo():
            BAUDRATES = [str(baudrate) for baudrate in Settings.SERIAL_BAUDRATES]

            combo = Combo(Element.SERIAL_BAUDRATE_COMBO, BAUDRATES)
            combo.value = str(SETTINGS.serial_baudrate)

            return combo

        FONT = Font("Courier New", 14)

        START_LED_INPUT = Input(Element.START_LED_INPUT, str(SETTINGS.start_led))
        END_LED_INPUT = Input(Element.END_LED_INPUT, str(SETTINGS.end_led))

        MILLISECONDS_PER_AUDIO_CHUNK_INPUT = Input(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                                                   str(SETTINGS.milliseconds_per_audio_chunk))

        SERIAL_PORT_INPUT = Input(Element.SERIAL_PORT_INPUT, SETTINGS.serial_port)

        BAUDRATES_COMBO = create_baudrates_combo()

        BRIGHTNESS_INPUT = Input(Element.BRIGHTNESS_INPUT, str(SETTINGS.brightness))

        NUMBER_OF_GROUPS_INPUT = Input(Element.NUMBER_OF_GROUPS_INPUT, str(SETTINGS.number_of_groups))

        MINIMUM_FREQUENCY_INPUT = Input(Element.MINIMUM_FREQUENCY_INPUT, str(SETTINGS.minimum_frequency))

        MAXIMUM_FREQUENCY_INPUT = Input(Element.MAXIMUM_FREQUENCY_INPUT, str(SETTINGS.maximum_frequency))

        REVERSE_LEDS_CHECK_BOX = CheckBox(Element.REVERSE_LEDS_CHECK_BOX,
                                          "Reverse LEDs", FONT, SETTINGS.should_reverse_leds)

        WIDGETS: List[Widget] = [START_LED_INPUT, END_LED_INPUT, MILLISECONDS_PER_AUDIO_CHUNK_INPUT, SERIAL_PORT_INPUT,
                                 BAUDRATES_COMBO, BRIGHTNESS_INPUT, NUMBER_OF_GROUPS_INPUT,
                                 MINIMUM_FREQUENCY_INPUT, MAXIMUM_FREQUENCY_INPUT, REVERSE_LEDS_CHECK_BOX]

        return dict((widget.key, widget) for widget in WIDGETS)

    def __create_settings_from_widget_gui(self, gui: WidgetGui) -> Settings:
        def get_setting_from_wiget_gui(setting_element: Element) -> Any:
            INTEGER_SETTINGS = {Element.START_LED_INPUT,
                                Element.END_LED_INPUT,
                                Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT,
                                Element.SERIAL_BAUDRATE_COMBO,
                                Element.BRIGHTNESS_INPUT,
                                Element.MINIMUM_FREQUENCY_INPUT,
                                Element.MAXIMUM_FREQUENCY_INPUT,
                                Element.NUMBER_OF_GROUPS_INPUT}

            WIDGET = gui.get_widget(setting_element)
            WIDGET_VALUE = WIDGET.value

            if (setting_element in INTEGER_SETTINGS):
                return int(WIDGET_VALUE)

            return WIDGET_VALUE

        START_LED = get_setting_from_wiget_gui(Element.START_LED_INPUT)
        END_LED = get_setting_from_wiget_gui(Element.END_LED_INPUT)
        MILLISECONDS_PER_AUDIO_CHUNK = get_setting_from_wiget_gui(Element.MILLISECONDS_PER_AUDIO_CHUNK_INPUT)
        SERIAL_PORT = get_setting_from_wiget_gui(Element.SERIAL_PORT_INPUT)
        SERIAL_BAUDRATE = get_setting_from_wiget_gui(Element.SERIAL_BAUDRATE_COMBO)
        BRIGHTNESS = get_setting_from_wiget_gui(Element.BRIGHTNESS_INPUT)
        MINIMUM_FREQUENCY = get_setting_from_wiget_gui(Element.MINIMUM_FREQUENCY_INPUT)
        MAXIMUM_FREQUENCY = get_setting_from_wiget_gui(Element.MAXIMUM_FREQUENCY_INPUT)
        SHOULD_REVERSE_LEDS = get_setting_from_wiget_gui(Element.REVERSE_LEDS_CHECK_BOX)
        NUMBER_OF_GROUPS = get_setting_from_wiget_gui(Element.NUMBER_OF_GROUPS_INPUT)

        return Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK, SERIAL_PORT,
                        SERIAL_BAUDRATE, BRIGHTNESS, MINIMUM_FREQUENCY, MAXIMUM_FREQUENCY,
                        SHOULD_REVERSE_LEDS, NUMBER_OF_GROUPS)
