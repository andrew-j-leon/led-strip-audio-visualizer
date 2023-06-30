import argparse
import json
import sys
import time
from collections import namedtuple
from contextlib import closing
from typing import List, Set, Tuple

import text
from color_palette import ColorPalette, load_color_palettes
from leds.frequency_band_leds import GraphicFrequencyBandLeds, SerialFrequencyBandLeds
from leds.led_array import ProductionLedArray
from libraries.audio_in_stream import ProductionAudioInStream
from libraries.canvas_gui import ProductionCanvasGui
from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE, ProductionSerial, SerialException
from spectrogram import ProductionSpectrogram


def create_bands(start_led: int, end_led: int, number_of_bands: int) -> List[Set[Tuple[int, int]]]:
    if (start_led < 0):
        raise ValueError(f'start_led must be >= 0, but was {start_led}.')

    if (end_led < 0):
        raise ValueError(f'end_led must be >= 0, but was {end_led}.')

    if (number_of_bands < 0):
        raise ValueError(f'number_of_bands ({number_of_bands}) must be >= 0.')

    NUMBER_OF_LEDS = end_led - start_led

    if (NUMBER_OF_LEDS < 0):
        raise ValueError(f'start_led ({start_led}) must be <= end_led ({end_led}).')

    if (NUMBER_OF_LEDS == 0 or number_of_bands == 0):
        return []

    NUMBER_OF_LEDS_PER_BAND = 0 if (number_of_bands == 0) else max(1, NUMBER_OF_LEDS // number_of_bands)

    band_number = 0
    band_start_led = start_led
    band_end_led = band_start_led + NUMBER_OF_LEDS_PER_BAND

    band_led_ranges: List[Set[Tuple[int, int]]] = [set() for band_number in range(number_of_bands)]

    while (band_number < number_of_bands and band_start_led < end_led):
        band_led_ranges[band_number].add((band_start_led, band_end_led))

        band_start_led += NUMBER_OF_LEDS_PER_BAND
        band_end_led += NUMBER_OF_LEDS_PER_BAND
        band_number += 1

    try:
        LAST_BAND_LED_RANGE = band_led_ranges[-1].pop()
        LAST_BAND_START_LED = LAST_BAND_LED_RANGE[0]
        band_led_ranges[-1].add((LAST_BAND_START_LED, end_led))

    except IndexError as err:
        if (not len(band_led_ranges) == 0):
            raise err

    except KeyError as err:
        if (not len(band_led_ranges[-1]) == 0):
            raise err

    return band_led_ranges


def create_mirrored_bands(start_led: int, end_led: int, number_of_bands: int) -> List[Set[Tuple[int, int]]]:
    if (start_led < 0):
        raise ValueError(f'start_led must be >= 0, but was {start_led}.')

    if (end_led < 0):
        raise ValueError(f'end_led must be >= 0, but was {end_led}.')

    if (number_of_bands < 0):
        raise ValueError(f'number_of_bands ({number_of_bands}) must be >= 0.')

    NUMBER_OF_LEDS = end_led - start_led

    if (NUMBER_OF_LEDS < 0):
        raise ValueError(f'start_led ({start_led}) must be <= end_led ({end_led}).')

    if (NUMBER_OF_LEDS == 0 or number_of_bands == 0):
        return []

    NUMBER_OF_LEDS_PER_BAND = max(1, NUMBER_OF_LEDS // number_of_bands)
    NUMBER_OF_LEDS_PER_LED_RANGE = max(1, NUMBER_OF_LEDS_PER_BAND // 2)

    band_led_ranges: List[Set[Tuple[int, int]]] = [set() for band_number in range(number_of_bands)]

    led_range_start = start_led
    led_range_end = led_range_start + NUMBER_OF_LEDS_PER_LED_RANGE

    band_number = number_of_bands - 1

    while (band_number >= 0 and led_range_end <= end_led):
        band_led_ranges[band_number].add((led_range_start, led_range_end))

        led_range_start += NUMBER_OF_LEDS_PER_LED_RANGE
        led_range_end += NUMBER_OF_LEDS_PER_LED_RANGE
        band_number -= 1

    NUMBER_OF_LED_RANGES = NUMBER_OF_LEDS // NUMBER_OF_LEDS_PER_LED_RANGE
    band_number = 0 if (NUMBER_OF_LED_RANGES % 2 == 0) else 1

    while (band_number < number_of_bands and led_range_end <= end_led):
        band_led_ranges[band_number].add((led_range_start, led_range_end))

        led_range_start += NUMBER_OF_LEDS_PER_LED_RANGE
        led_range_end += NUMBER_OF_LEDS_PER_LED_RANGE
        band_number += 1

    return band_led_ranges


def create_default_color_palettes():
    BLUE_1 = (13, 13, 165)
    LIGHT_BLUE_1 = (13, 165, 165)
    GREEN_1 = (13, 165, 13)
    YELLOW_1 = (165, 165, 13)
    RED_1 = (165, 13, 13)

    GREEN_2 = (0, 79, 79)
    BLUE_2 = (80, 199, 118)
    YELLOW_2 = (219, 237, 52)
    ORANGE_2 = (250, 124, 0)

    PURPLE_3 = (13, 0, 51)
    LIGHT_PURPLE_3 = (96, 0, 148)
    LIGHTER_PURPLE_3 = (209, 88, 134)
    PINK_3 = (252, 0, 80)

    PURPLE_4 = (66, 10, 92)
    PINK_4 = (235, 18, 181)
    BLUE_4 = (0, 166, 166)
    YELLOW_4 = (253, 253, 0)

    COLOR_PALETTE_1 = ColorPalette(30 * [BLUE_1] + 5 * [LIGHT_BLUE_1] + 5 * [GREEN_1] + 5 * [YELLOW_1] + 1 * [RED_1])
    COLOR_PALETTE_2 = ColorPalette(30 * [GREEN_2] + 7 * [BLUE_2] + 8 * [YELLOW_2] + 1 * [ORANGE_2])
    COLOR_PALETTE_3 = ColorPalette(30 * [PURPLE_3] + 7 * [LIGHT_PURPLE_3] + 8 * [LIGHTER_PURPLE_3] + 1 * [PINK_3])
    COLOR_PALETTE_4 = ColorPalette(30 * [PURPLE_4] + 7 * [PINK_4] + 8 * [BLUE_4] + 1 * [YELLOW_4])

    return [COLOR_PALETTE_1, COLOR_PALETTE_2, COLOR_PALETTE_3, COLOR_PALETTE_4]


if __name__ == '__main__':
    SETTINGS_FILENAME_ARG = 'settings_filename'
    COLOR_PALETTES_FILENAME_ARG = 'color_palettes_filename'
    DURATION_OPT = ['-d', '--duration']
    SERIAL_PORT_OPT = ['-p', '--serial_port']
    BAUDRATE_OPT = ['-r', '--baudrate']
    BRIGHTNESS_OPT = ['-b', '--brightness']

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description=(text.wrap_text('Display an audio spectrogram of this device\'s default audio input on an array of LEDs. '
                                                                 'Physical LEDs require a microcontroller (or similar device); '
                                                                 'serial data is sent from this program to said '
                                                                 'microcontroller via a user specified serial port.',
                                                                 width=100)))

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument(SETTINGS_FILENAME_ARG, help=text.wrap_text(text.SETTINGS_HELP_MESSAGE))
    parser.add_argument(COLOR_PALETTES_FILENAME_ARG, nargs='?', help=text.wrap_text(text.COLOR_PALETTES_HELP_MESSAGE))
    parser.add_argument(*DURATION_OPT, type=int, help=text.wrap_text(text.DURATION_HELP_MESSAGE))
    parser.add_argument(*SERIAL_PORT_OPT, help=text.wrap_text(text.SERIAL_PORT_HELP_MESSAGE))
    parser.add_argument(*BAUDRATE_OPT, type=int, default=1999999, help=text.wrap_text(text.BAUDRATE_HELP_MESSAGE))
    parser.add_argument(*BRIGHTNESS_OPT, type=int, default=20, help=text.wrap_text(text.BRIGHTNESS_HELP_MESSAGE))

    args = parser.parse_args()

    if (args.duration is not None and args.duration < 0):
        parser.error(text.create_invalid_choice_parser_error(DURATION_OPT, args.duration, 'an integer >= 0'))

    if (args.baudrate < 1):
        parser.error(text.create_invalid_choice_parser_error(BAUDRATE_OPT, args.baudrate, 'an integer >= 1'))

    if (args.brightness not in range(0, 255)):
        parser.error(text.create_invalid_choice_parser_error(BRIGHTNESS_OPT, args.brightness, 'an integer from the range [0, 255])'))

    SETTINGS_FIELDNAMES = ['start_led', 'end_led', 'milliseconds_per_audio_chunk', 'min_frequency',
                           'max_frequency', 'number_of_bands', 'reverse_bands', 'mirror_bands']
    SettingsTuple = namedtuple('SettingsTuple', SETTINGS_FIELDNAMES)

    settings: SettingsTuple = None

    try:
        with open(args.settings_filename) as file:
            settings = SettingsTuple(**json.load(file))

    except FileNotFoundError:
        parser.error(text.create_file_not_found_parser_error(SETTINGS_FILENAME_ARG, args.settings_filename))

    except PermissionError:
        parser.error(text.create_read_permission_error_parser_error(SETTINGS_FILENAME_ARG, args.settings_filename))

    except TypeError:
        parser.error(f'The {SETTINGS_FILENAME_ARG} {args.settings_filename} must point to a JSON '
                     f'file with only the following fields: {SETTINGS_FIELDNAMES}.')

    color_palettes = create_default_color_palettes()

    try:
        with open(args.color_palettes_filename) as file:
            color_palettes = load_color_palettes(file)

    except TypeError as err:
        if (args.color_palettes_filename is not None):
            parser.error(f'The {COLOR_PALETTES_FILENAME_ARG} {args.color_palettes_filename} is not properly formatted. '
                         'See the --help documentation for more information.')

    except FileNotFoundError:
        parser.error(text.create_file_not_found_parser_error(COLOR_PALETTES_FILENAME_ARG, args.settings_filename))

    except PermissionError:
        parser.error(text.create_read_permission_error_parser_error(COLOR_PALETTES_FILENAME_ARG, args.settings_filename))

    led_strip = ProductionLedArray()
    spectrogram = ProductionSpectrogram()
    try:
        spectrogram = ProductionSpectrogram(color_palettes[0], settings.min_frequency, settings.max_frequency)
    except IndexError:
        spectrogram = ProductionSpectrogram(min_frequency=settings.min_frequency, max_frequency=settings.max_frequency)

    with (closing(ProductionAudioInStream()) as audio_in_stream,
          closing(ProductionCanvasGui()) as canvas_gui,
          closing(ProductionSerial()) as serial):

        led_groups = (create_mirrored_bands(settings.start_led, settings.end_led, settings.number_of_bands)
                      if (settings.mirror_bands) else create_bands(settings.start_led, settings.end_led, settings.number_of_bands))

        if (settings.reverse_bands):
            led_groups.reverse()

        LED_RANGE = (settings.start_led, settings.end_led)

        try:
            if (args.serial_port is not None):
                READ_TIMEOUT = 10
                WRITE_TIMEOUT = 10

                serial.open(args.serial_port, args.baudrate, PARITY_NONE, STOPBITS_ONE, EIGHTBITS, READ_TIMEOUT, WRITE_TIMEOUT)
                led_strip = ProductionLedArray(SerialFrequencyBandLeds(LED_RANGE, led_groups, serial, args.brightness))

            else:
                canvas_gui.open()
                led_strip = ProductionLedArray(GraphicFrequencyBandLeds(LED_RANGE, led_groups, canvas_gui))

        except ValueError as err:
            if (settings.start_led < 0):
                parser.error(f'The {SETTINGS_FILENAME_ARG} {args.settings_filename} defines a start_led ({settings.start_led}) that is less than 0.')

            elif (settings.end_led < 0):
                parser.error(f'The {SETTINGS_FILENAME_ARG} {args.settings_filename} defines an end_led ({settings.end_led}) that is less than 0.')

            elif (settings.start_led > settings.end_led):
                parser.error(f'The {SETTINGS_FILENAME_ARG} {args.settings_filename} defines a start_led ({settings.start_led}) that is greater than the end_led ({settings.end_led}).')

            raise err

        except SerialException as err:
            parser.error(f'Could not open a serial connection on port {args.serial_port}. Error:\n\n{str(err)}')

        epoch_until_next_color_palette_change = time.time()

        try:
            audio_in_stream.open()

        except OSError as err:
            print('No default input device was found. Make sure your Operating System has a default input device set.', file=sys.stderr)
            exit(1)

        MILLISECONDS_PER_SECOND = 1000
        FRAMES_PER_MILLISECOND = audio_in_stream.sample_rate / MILLISECONDS_PER_SECOND
        NUMBER_OF_FRAMES = int(FRAMES_PER_MILLISECOND * settings.milliseconds_per_audio_chunk)

        color_palette_index = 0

        while True:
            try:
                if (args.duration is not None and time.time() >= epoch_until_next_color_palette_change and len(color_palettes) > 0):
                    spectrogram.set_amplitude_colors(color_palettes[color_palette_index])
                    color_palette_index = (color_palette_index + 1) % len(color_palettes)
                    epoch_until_next_color_palette_change = time.time() + args.duration

                AUDIO_CHUNK = audio_in_stream.read(NUMBER_OF_FRAMES)
                spectrogram.update_led_strip(led_strip, AUDIO_CHUNK, NUMBER_OF_FRAMES, audio_in_stream.sample_rate)

            except KeyboardInterrupt:
                if (serial.is_open()):
                    led_strip.turn_off()

                print("\nShutting down.")
                break

            except Exception as e:
                if (serial.is_open()):
                    led_strip.turn_off()

                raise e
