from controller.audio_in_controller import AudioInController
from controller.settings_controller import SettingsController
from libraries.widget_gui import ProductionWidgetGui
from util import Settings, SettingsCollection

if __name__ == '__main__':

    AUDIO_IN_GUI_TITLE = 'Audio In Music Visualizer'
    SETTINGS_GUI_TITLE = 'Settings'

    with (ProductionWidgetGui(title=AUDIO_IN_GUI_TITLE) as audio_in_controller_widget_gui,
          ProductionWidgetGui(SETTINGS_GUI_TITLE) as settings_controller_widget_gui):

        START_LED = 0
        END_LED = 300
        MILLISECONDS_PER_AUDIO_CHUNK = 50
        SERIAL_PORT = 'COM3'
        SERIAL_BAUDRATE = 115200
        BRIGHTNESS = 20
        MINIMUM_FREQUENCY = 0
        MAXIMUM_FREQUENCY = 2300
        SHOULD_REVERSE_LEDS = False
        NUMBER_OF_GROUPS = 60

        AMPLITUDE_RGBS = ([(13, 13, 165)] * 27
                          + [(13, 165, 165)] * 5
                          + [(13, 165, 13)] * 6
                          + [(165, 165, 13)] * 5
                          + [(165, 13, 13)] * 100)

        DEFAULT_SETTINGS = Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK, SERIAL_PORT,
                                    SERIAL_BAUDRATE, BRIGHTNESS, MINIMUM_FREQUENCY, MAXIMUM_FREQUENCY,
                                    SHOULD_REVERSE_LEDS, NUMBER_OF_GROUPS, AMPLITUDE_RGBS)

        DEFAULT_SETTINGS_NAME = 'default'

        COLLECTION = {DEFAULT_SETTINGS_NAME: DEFAULT_SETTINGS}

        settings_collection = SettingsCollection(COLLECTION)

        settings_controller = SettingsController(settings_controller_widget_gui,
                                                 settings_collection)

        audio_in_controller = AudioInController(audio_in_controller_widget_gui,
                                                settings_controller)

        audio_in_controller.run()
