import argparse
import json
import sys
import time
from contextlib import closing
from types import SimpleNamespace
from typing import List

import spectrogram
import text
from color_palette import ColorPalette
from grouped_leds import GraphicGroupedLeds, GroupedLedsQueue, SerialGroupedLeds
from libraries.audio_in_stream import ProductionAudioInStream
from libraries.canvas_gui import ProductionCanvasGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE, ProductionSerial
from util import RGB


def create_color_palettes(color_palettes: List[List[List[int]]], upper_amplitudes: List[List[int]]) -> List[ColorPalette]:
    result: List[ColorPalette] = []

    for palettes, amp_upper_bounds in zip(color_palettes, upper_amplitudes):
        colors: List[List[RGB]] = []

        for palette in palettes:
            rgbs: List[RGB] = []

            for i in range(0, len(palette), 3):
                rgbs.append(RGB(palette[i], palette[i + 1], palette[i + 2]))

            colors.append(rgbs)

        result.append(ColorPalette(colors, amp_upper_bounds))

    return result


def create_color_palette_groups(color_palettes: List[ColorPalette], groupings: List[List[int]]) -> List[List[ColorPalette]]:
    color_palette_groups: List[List[ColorPalette]] = []

    for grouping in groupings:
        palette_group: List[ColorPalette] = []

        for i in grouping:
            palette_group.append(color_palettes[i])

        color_palette_groups.append(palette_group)

    return color_palette_groups


if __name__ == '__main__':
    LED_CONFIG_FILE_ARG = 'led_config_file'

    MILLISECONDS_PER_AUDIO_CHUNK_OPT = ['-m', '--milliseconds_per_audio_chunk']
    DURATION_OPT = ['-d', '--duration']
    SERIAL_PORT_OPT = ['-p', '--serial_port']
    BAUDRATE_OPT = ['-r', '--baudrate']
    BRIGHTNESS_OPT = ['-b', '--brightness']
    # SONES_OPT = ['-s', '--sones']

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description=text.PROGRAM_DESCRIPTION)

    parser.add_argument(LED_CONFIG_FILE_ARG)
    parser.add_argument(*MILLISECONDS_PER_AUDIO_CHUNK_OPT, type=int, default=55)
    parser.add_argument(*DURATION_OPT, type=int)
    parser.add_argument(*SERIAL_PORT_OPT)
    parser.add_argument(*BAUDRATE_OPT, type=int, default=1999999)
    parser.add_argument(*BRIGHTNESS_OPT, type=int, default=20)
    # parser.add_argument(*SONES_OPT, type=bool, action=argparse.BooleanOptionalAction, default=False)

    args = parser.parse_args()

    settings = SimpleNamespace()

    with open(args.led_config_file) as file:
        settings = SimpleNamespace(**json.load(file))

    color_settings = SimpleNamespace(**settings.color_data)

    color_palettes = create_color_palettes(color_settings.color_palettes, color_settings.upper_amplitudes)
    color_palette_groups = create_color_palette_groups(color_palettes, color_settings.groupings)

    grouped_leds_queue = GroupedLedsQueue()

    with (closing(ProductionAudioInStream()) as audio_in_stream,
          closing(ProductionCanvasGui()) as canvas_gui,
          closing(ProductionSerial()) as serial):

        if (args.serial_port is not None):
            READ_TIMEOUT = 10
            WRITE_TIMEOUT = 10

            serial.open(args.serial_port, args.baudrate, PARITY_NONE, STOPBITS_ONE, EIGHTBITS, READ_TIMEOUT, WRITE_TIMEOUT)
            grouped_leds_queue = GroupedLedsQueue(SerialGroupedLeds(settings.led_range, settings.led_groups, serial, args.brightness))

        else:
            canvas_gui.open()
            grouped_leds_queue = GroupedLedsQueue(GraphicGroupedLeds(settings.led_range, settings.led_groups, canvas_gui))

        try:
            audio_in_stream.open()

        except OSError as err:
            print('No default input device was found. Make sure your Operating System has a default input device set.', file=sys.stderr)
            exit(1)

        MILLISECONDS_PER_SECOND = 1000
        FRAMES_PER_MILLISECOND = audio_in_stream.sample_rate / MILLISECONDS_PER_SECOND
        NUMBER_OF_FRAMES = int(FRAMES_PER_MILLISECOND * args.milliseconds_per_audio_chunk)

        color_palette_group_deadline = time.time() if (args.duration is None) else time.time() + args.duration
        color_palette_group_index = 0

        # sones = []
        # if (args.sones):
        #     for band in settings.bands:
        #         avg_frequency = (band[0] + band[1])/2
        #         sones.append(Sones(round(avg_frequency)))

        while True:
            try:
                if (args.duration is not None and time.time() >= color_palette_group_deadline):

                    color_palette_group_index = (color_palette_group_index + 1) % len(color_palette_groups)
                    color_palette_group_deadline = time.time() + args.duration

                AUDIO_CHUNK = audio_in_stream.read(NUMBER_OF_FRAMES)

                # if (args.sones):
                #     spectrogram.update_sones(grouped_leds_queue, AUDIO_CHUNK, NUMBER_OF_FRAMES, audio_in_stream.sample_rate,
                #                    settings.bands, color_palette_groups[color_palette_group_index], sones)

                spectrogram.update(grouped_leds_queue, AUDIO_CHUNK, NUMBER_OF_FRAMES, audio_in_stream.sample_rate,
                                   settings.bands, color_palette_groups[color_palette_group_index])

            except KeyboardInterrupt:
                if (serial.is_open()):
                    for i in range(3):
                        grouped_leds_queue.turn_off()

                print("\nShutting down.")
                break

            except Exception as e:
                if (serial.is_open()):
                    for i in range(3):
                        grouped_leds_queue.turn_off()

                raise e
