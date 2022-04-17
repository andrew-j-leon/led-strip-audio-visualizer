import gui.main.main_view as main_view
import gui.controller as controller

import gui.audio_visualizer.audio_controller as audio_controller
import gui.audio_visualizer.audio_in.audio_in_controller as audio_in_controller
import gui.audio_visualizer.audio_out.audio_out_controller as audio_out_controller


class MainController(controller.Controller):
    def __init__(self):
        controller.Controller.__init__(self, main_view.MainView())
        self.__audio_controller: audio_controller.AudioController = None

    def start(self):
        self._view.run_concurrent(self.__on_gui_event)

    def __on_gui_event(self, event: str):
        if (event == main_view.Event.START_AUDIO_IN_PLAYER):
            self._view.set_audio_player_is_running_state()
            self.__audio_controller = audio_in_controller.AudioInController()
            self.__audio_controller.start()
            self.__delete_audio_controller()
            self._view.set_audio_is_stopped_state()

        elif (event == main_view.Event.START_AUDIO_OUT_PLAYER):
            self._view.set_audio_player_is_running_state()
            self.__audio_controller = audio_out_controller.AudioOutController()
            self.__audio_controller.start()
            self.__delete_audio_controller()
            self._view.set_audio_is_stopped_state()

    def __delete_audio_controller(self):
        if (self.__audio_controller):
            del self.__audio_controller
            self.__audio_controller = None
