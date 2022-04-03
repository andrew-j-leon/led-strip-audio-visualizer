# class A:
#     def __init__(self, num):
#         self._num = num

# class B(A):
#     def __init__(self, num, numB):
#         A.__init__(self, num)
#         self._numB = numB

#     def b_change_name(self):
#         self._num = 20

#     def b_get_num(self):
#         return self._num

# class C(A):
#     def __init__(self, num, numC):
#         A.__init__(self, num)
#         self._numC = numC

#     def c_change_num(self):
#         self._num = 10

#     def c_get_num(self):
#         return self._num

# class D(B, C):
#     def __init__(self, num, numB, numC):
#         B.__init__(self, num, numB)
#         C.__init__(self, num, numC)

# d = D(1,2,3)

# print("hello")



# class Parent:
#     def __init__(self):
#         self.q = [1,2,3]
#         self.use_implemented()

#     def _implement_me(self, *args):
#         pass

#     def use_implemented(self):
#         self._implement_me(self.q)

# class Child(Parent):
#     def __init__(self):
#         Parent.__init__(self)

#     def _implement_me(self, a_list):
#         print(a_list)

# c = Child()

# c.use_implemented()


# def test(a,b):
#     print(a,b)

# d = {"a":10, "b":20}

# test(*d)


# class A:
#     def __init__(self):
#         self.stuff = [1,2,3]
#         pass

#     def show(self):
#         pass

# class B(A):
#     def __init__(self):
#         A.__init__(self)

#     def show(self):
#         print("Hello from B ; Stuff {}".format(self.stuff))
#         self.stuff.append(4)

# class C(A):
#     def __init__(self):
#         A.__init__(self)

#     def show(self):
#         print("Hello from C ; Stuff {}".format(self.stuff))

# class D(B,C):
#     def __init__(self):
#         B.__init__(self)
#         C.__init__(self)

#     def show(self):
#         # super(D, self).show()
#         # super(B, self).show()
#         B.show(self)
#         C.show(self)


# d = D()

# d.show()

# print("Hello")





# from serial import Serial
# from serial.serialutil import EIGHTBITS, PARITY_EVEN, STOPBITS_ONE_POINT_FIVE

# PORT = "COM3"
# BAUD_RATE = 115200
# READ_TIMEOUT = 1
# WRITE_TIMEOUT = None
# PARITY = PARITY_EVEN
# STOPBITS = STOPBITS_ONE_POINT_FIVE
# BYTE_SIZE = EIGHTBITS

# arduino:Serial = Serial(port=PORT, baudrate=BAUD_RATE, timeout=READ_TIMEOUT, write_timeout=WRITE_TIMEOUT, parity=PARITY, stopbits=STOPBITS, bytesize=BYTE_SIZE)

# arduino.write((10).to_bytes(length=1, byteorder="big"))

# print("Hello")





# import wave
# import pyaudio

# CHUNK_SIZE = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100

# audio_player_maker:pyaudio.PyAudio = pyaudio.PyAudio()

# audio_player = audio_player_maker.open(format=FORMAT,
#                                        channels=CHANNELS,
#                                        rate=RATE,
#                                        input=True,
#                                        frames_per_buffer=CHUNK_SIZE)


# try:
#     while True:
#         print(audio_player.read(CHUNK_SIZE))
# except Exception as e:
#     print("An error ocurred: ", e)

# finally:
#     audio_player.close()
#     audio_player_maker.terminate()



# import subprocess
# import os
# from pathlib import Path
# import shutil
# import subprocess
# from pydub import AudioSegment

# AUDIO_FILE_DIRECTORY = '.audio_file'

# if (os.path.isdir(AUDIO_FILE_DIRECTORY)):
#     shutil.rmtree(AUDIO_FILE_DIRECTORY)

# os.mkdir(AUDIO_FILE_DIRECTORY)

# # audio_file = 'F:/Music_mp3/[Donkey Kong 2 OST] Bayou Bogie.mp3'
# audio_file = 'C:/Users/Lorena/Desktop/test/not_audio.txt'

# base = os.path.basename(audio_file)
# # dirname = os.path.dirname(audio_file)
# new_base = Path(base).with_suffix(".wav").name

# new_audio_file = os.path.join(AUDIO_FILE_DIRECTORY, new_base)

# print(new_audio_file)

# # os.system('ffmpeg -i "{}" "{}"'.format(audio_file, new_audio_file))
# # subprocess.call(["ffmpeg", "-i", audio_file, new_audio_file])
# sound = AudioSegment.from_file(audio_file)
# sound.export(new_audio_file, format="wav")


# from pynput.keyboard import Listener

# def on_press(key):
#     if str(key.value) == '<179>':
#         print('play/pause key pressed')

#     if str(key.value) == '<176>':
#         print('next key pressed')

#     if str(key.value) == '<177>':
#         print('prev key pressed')

# listener_thread = Listener(on_press=on_press, on_release=None)
# listener_thread.start()

# while True:
#     pass


# from pyaudio import PyAudio

# audio_player_maker:PyAudio = PyAudio()

# # print(audio_player_maker.get_host_api_count())
# # print(audio_player_maker.get_default_host_api_info())
# # print(audio_player_maker.get_device_count())
# print(audio_player_maker.get_default_input_device_info())
# # print(audio_player_maker.get_default_output_device_info())








# import time

# class A:
#     def __del__(self):
#         print("deleting")

# a = A()

# del a

# time.sleep(5)








# class Test:
#     class Inner:
#         A = "A"

# t1 = Test()
# t2 = Test()

# t1.Inner.A = "b"

# print(t1.Inner.A)
# print(t2.Inner.A)
# print(Test.Inner.A)

# Test.Inner.A = "z"

# print(t1.Inner.A)
# print(t2.Inner.A)
# print(Test.Inner.A)





# import python.util.util as util

# print(util.hsl_to_rgb(0, 0, 0))
# print(util.hsl_to_hex(10,20,30))



# class Test:
#     A = "a"
#     B = "b"
#     C = "c"

# def get_values():
#     for item in Test.__dict__.items():
#         print(item)

# get_values()


# from serial import Serial

# Serial(port="Invalid")



from python.util.enum import Enum, get_non_builtin_items
import python.util.util as util

from typing import Dict, Any

class Test(Enum):
    def get_dict(self) -> Dict[str, Any]:
        return get_non_builtin_items(Test)

    A = "a"
    B = "b"

print(Test.get_dict())

