from gui.audio_in_controller import AudioInController
from libraries.gui import WidgetGui

if __name__ == '__main__':

    TITLE = 'Audio In Music Visualizer'

    with WidgetGui(title=TITLE) as widget_gui:
        audio_controller = AudioInController(widget_gui)
        audio_controller.start()
