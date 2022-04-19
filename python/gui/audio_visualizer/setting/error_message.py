from typing import List

import serial
import util


def get_amplitude_to_rgb_error_message(amplitude_to_rgb: str) -> str:
    error_message: str = ""

    if (amplitude_to_rgb != ""):
        amplitude_to_rgb: List[str] = amplitude_to_rgb.split("\n")
        for amplitude in range(len(amplitude_to_rgb)):
            rgb: List[str] = amplitude_to_rgb[amplitude].split(",")

            if (len(rgb) != 3):
                error_message += ("Line {} of amplitude_to_rgb ({}) must have three comma separated integer values.\n").format(amplitude, amplitude_to_rgb[amplitude])

            else:
                for color_value in rgb:
                    if (not util.string_is_int(color_value)):
                        error_message += ("The color value {} on line {} must be an integer.\n").format(color_value, amplitude)
                    elif (int(color_value) < 0 or int(color_value) > 255):
                        error_message += ("The color value {} on line {} must be >= 0 and <= 255\n.").format(color_value, amplitude)

    return error_message


def get_number_of_groups_error_message(number_of_groups: str) -> str:
    error_message: str = ""

    if (not util.string_is_int(number_of_groups)):
        error_message += ("number_of_groups ({}) must be an integer.\n").format(number_of_groups)

    if (util.string_is_int(number_of_groups) and int(number_of_groups) < 1):
        error_message += ("number_of_groups ({}) must be >= 1.\n").format(number_of_groups)

    return error_message


def get_should_reverse_indicies_error_message(should_reverse_indicies: bool) -> str:
    error_message: str = ""

    if (not isinstance(should_reverse_indicies, bool)):
        error_message += ("__should_reverse_indicies should be a boolean value, not a {}.\n").format(type(should_reverse_indicies))

    return error_message


def get_frequency_range_error_message(minimum_frequency: str, maximum_frequency: str) -> str:
    error_message: str = ""

    if (not util.string_is_int(minimum_frequency)):
        error_message += ("The minimum_frequency ({}) is not an integer.\n").format(minimum_frequency)

    if (not util.string_is_int(maximum_frequency)):
        error_message += ("The maximum_frequency ({}) is not an integer.\n").format(maximum_frequency)

    if (util.string_is_int(minimum_frequency) and util.string_is_int(maximum_frequency) and int(minimum_frequency) >= int(maximum_frequency)):
        error_message += ("The minimum_frequency ({}) must be < the maximum_frequency ({}).\n").format(minimum_frequency, maximum_frequency)

    if (util.string_is_int(minimum_frequency) and int(minimum_frequency) < 0):
        error_message += ("The minimum_frequency ({}) must be >= 0 Hz.\n").format(minimum_frequency)

    return error_message


def get_brightness_error_message(brightness: str) -> str:
    error_message: str = ""

    if (not util.string_is_int(brightness)):
        error_message += ("The brightness ({}) is not an integer.\n").format(brightness)

    if (util.string_is_int(brightness) and (int(brightness) < 0 or int(brightness) > 255)):
        error_message += ("The brightness ({}) must be >= 0 and <= 255.\n").format(brightness)

    return error_message


def get_serial_baudrate_error_message(baudrate: str, baudrates: List[str]) -> str:
    error_message: str = ""

    if (baudrate not in baudrates):
        error_message += ("The baudrate ({}) is not a valid baudrate ({}).\n").format(baudrate, baudrates)

    return error_message


def get_serial_port_error_message(serial_port: str) -> str:
    error_message: str = ""

    try:
        serial_connection = serial.Serial(port=serial_port)
        serial_connection.close()
    except serial.SerialException as e:
        error_message += (str(e) + "\n")

    return error_message


def get_milliseconds_per_audio_chunk_error_message(milliseconds_per_audio_chunk: str) -> str:
    error_message = ""

    if (not util.string_is_int(milliseconds_per_audio_chunk)):
        error_message += ("milliseconds_per_audio_chunk ({}) must be an integer.\n").format(milliseconds_per_audio_chunk)

    if (util.string_is_int(milliseconds_per_audio_chunk) and int(milliseconds_per_audio_chunk) <= 0):
        error_message += ("milliseconds_per_audio_chunk ({}) must be >= 1.\n").format(milliseconds_per_audio_chunk)

    return error_message


def get_led_index_range_error_message(start_led_index: str, end_led_index: str) -> str:
    error_message = ""

    if (not util.string_is_int(start_led_index)):
        error_message += ("The start_led_index {} must be an integer.\n").format(start_led_index)

    if (not util.string_is_int(end_led_index)):
        error_message += ("The end_led_index {} must be an integer.\n").format(end_led_index)

    if (util.string_is_int(start_led_index) and util.string_is_int(end_led_index) and int(start_led_index) >= int(end_led_index)):
        error_message += ("The start_led_index ({}) must be < the end_led_index ({}).\n").format(start_led_index, end_led_index)

    if (util.string_is_int(start_led_index) and int(start_led_index) < 0):
        error_message += ("The start_led_index ({}) must be >= 0.\n").format(start_led_index)

    return error_message
