from controller.audio_in_controller import AudioInController
from controller.settings_controller import SettingsController
from libraries.audio_in_stream import AudioInStream, ProductionAudioInStream
from libraries.canvas_gui import CanvasGui, ProductionCanvasGui
from libraries.serial import ProductionSerial, Serial
from libraries.widget_gui import ProductionWidgetGui, WidgetGuiEvent
from util import Settings, SettingsCollection

from pathlib import Path


def create_default_settings():
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

    return Settings(START_LED, END_LED, MILLISECONDS_PER_AUDIO_CHUNK, SERIAL_PORT,
                    SERIAL_BAUDRATE, BRIGHTNESS, MINIMUM_FREQUENCY, MAXIMUM_FREQUENCY,
                    SHOULD_REVERSE_LEDS, NUMBER_OF_GROUPS, AMPLITUDE_RGBS)


def create_serial_connection() -> Serial:
    return ProductionSerial()


def create_canvas_gui() -> CanvasGui:
    WIDTH = 1350
    HEIGHT = 600

    return ProductionCanvasGui(WIDTH, HEIGHT)


def create_audio_in_stream() -> AudioInStream:
    return ProductionAudioInStream()


if __name__ == '__main__':
    DEFAULT_SETTINGS = create_default_settings()
    DEFAULT_SETTINGS_COLLECTION = {'default': DEFAULT_SETTINGS}

    SETTINGS_COLLECTION = SettingsCollection(DEFAULT_SETTINGS_COLLECTION)

    SAVE_DIRECTORY = Path('./saved_settings')
    SAVE_DIRECTORY.mkdir(exist_ok=True)

    SETTINGS_COLLECTION.load_from_directory(SAVE_DIRECTORY)
    SETTINGS_COLLECTION.set_save_directory(SAVE_DIRECTORY)

    AUDIO_IN_GUI_TITLE = 'Audio In Music Visualizer'
    SETTINGS_GUI_TITLE = 'Settings'

    with (ProductionWidgetGui(AUDIO_IN_GUI_TITLE) as audio_in_controller_widget_gui,
          ProductionWidgetGui(SETTINGS_GUI_TITLE) as settings_controller_widget_gui):

        settings_controller = SettingsController(settings_controller_widget_gui,
                                                 SETTINGS_COLLECTION)

        with AudioInController(audio_in_controller_widget_gui, settings_controller,
                               create_serial_connection, create_canvas_gui, create_audio_in_stream) as audio_in_controller:

            audio_in_controller.display()

            event = audio_in_controller.read_event_and_update_gui()

            while (event != WidgetGuiEvent.CLOSE_WINDOW):
                audio_in_controller.handle_event(event)
                event = audio_in_controller.read_event_and_update_gui()

            audio_in_controller.handle_event(event)
