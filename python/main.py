from contextlib import closing
from pathlib import Path

from color_palette import ColorPalette
from color_palette import load as load_color_palette_selection
from color_palette import save as save_color_palette_selection
from controller.audio_in_controller import AudioInController
from controller.color_palette_controller import ColorPaletteController
from controller.settings_controller import SettingsController
from led_strip.led_strip import LedStrip, ProductionLedStrip
from libraries.audio_in_stream import AudioInStream, ProductionAudioInStream
from libraries.canvas_gui import CanvasGui, ProductionCanvasGui
from libraries.serial import ProductionSerial, Serial
from libraries.widget_gui import ProductionWidgetGui, WidgetGui
from selection import Selection
from settings import Settings
from settings import load as load_settings
from settings import save as save_settings
from spectrogram import ProductionSpectrogram, Spectrogram


def create_serial() -> Serial:
    return ProductionSerial()


def create_widget_gui() -> WidgetGui:
    return ProductionWidgetGui()


def create_canvas_gui() -> CanvasGui:
    WIDTH = 1350
    HEIGHT = 600

    return ProductionCanvasGui(WIDTH, HEIGHT)


def create_audio_in_stream() -> AudioInStream:
    return ProductionAudioInStream()


def create_led_strip() -> LedStrip:
    return ProductionLedStrip()


def create_spectrogram() -> Spectrogram:
    return ProductionSpectrogram()


if __name__ == '__main__':
    SETTINGS_SAVE_DIRECTORY = Path('./saves/settings')
    COLOR_PALETTE_SELECTION_SAVE_DIRECTORY = Path('./saves/color_palettes')

    settings = Settings()

    try:
        settings = load_settings(SETTINGS_SAVE_DIRECTORY)

    except FileNotFoundError:
        SETTINGS_SAVE_DIRECTORY.mkdir(parents=True)

    color_palette_selection = Selection()

    try:
        color_palette_selection = load_color_palette_selection(COLOR_PALETTE_SELECTION_SAVE_DIRECTORY)

    except FileNotFoundError:
        COLOR_PALETTE_SELECTION_SAVE_DIRECTORY.mkdir(parents=True)

    def create_settings_controller(settings: Settings) -> SettingsController:
        def save_settings_to_file(settings: Settings):
            save_settings(settings, SETTINGS_SAVE_DIRECTORY)

        return SettingsController(create_widget_gui, save_settings_to_file, settings)

    def create_color_palette_controller(color_palette_selection: Selection[ColorPalette]) -> ColorPaletteController:
        def save_color_palette_selection_to_file(color_palette_selection: Selection[ColorPalette]):
            save_color_palette_selection(color_palette_selection, COLOR_PALETTE_SELECTION_SAVE_DIRECTORY)

        return ColorPaletteController(create_widget_gui, save_color_palette_selection_to_file, color_palette_selection)

    # Passing in an object's dependencies rather than having said object
    # construct its own dependencies is known as "Dependency Injection"
    with closing(AudioInController(create_settings_controller, settings,
                                   create_color_palette_controller, color_palette_selection,
                                   create_widget_gui, create_canvas_gui,
                                   create_serial, create_audio_in_stream,
                                   create_led_strip, create_spectrogram)) as audio_in_controller:
        audio_in_controller.run()
