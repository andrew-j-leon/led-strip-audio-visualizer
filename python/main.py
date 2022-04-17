import gui.main.main_controller as main_controller

app = main_controller.MainController()
app.start()


# import time
# import pyaudio

# audio_player_maker = pyaudio.PyAudio()

# defaults = audio_player_maker.get_default_input_device_info()

# audio_player = audio_player_maker.open(format=pyaudio.paInt16, channels=defaults["maxInputChannels"],
#                                        rate=int(defaults["defaultSampleRate"]), input=True)


# while True:
#     time.sleep(0.1)
#     chunk_value = int.from_bytes(audio_player.read(1024), 'big')
#     if (chunk_value != 0):
#         print(1)

#     else:
#         print(0)
