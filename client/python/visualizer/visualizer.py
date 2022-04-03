import python.util.util as util

class Visualizer:
    def update_led_strips(self, audio_data:bytes, *args, **kwargs):
        """
            Updates the led_strip to a new state based on audio_data. If
            audio_data is empty, all leds will turn off.

            Args:
                `audio_data (bytes)`: Audio data from a .wav file.
        """
        if (util.is_empty(audio_data)):
            self._turn_off_leds()
        else:
            self._turn_on_leds(audio_data, *args, **kwargs)

    def __del__(self):
        self._turn_off_leds()
        self._do_stuff_on_del()

    def _turn_off_leds(self):
        pass

    def _do_stuff_on_del(self):
        pass

    def _turn_on_leds(self, audio_data:bytes, *args, **kwargs):
        pass