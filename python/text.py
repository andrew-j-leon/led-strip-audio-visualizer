import textwrap


def create_generic_parser_error(argument_names, message):
    args = '/'.join(argument_names)
    return (f'argument {args}: {message}')


def create_invalid_choice_parser_error(argument_names, choice, valid_choices):
    args = '/'.join(argument_names)
    return f'{args}: invalid choice: {choice} (must be {valid_choices})'


def create_file_not_found_parser_error(argument_name, filename):
    return f'Could not find the {argument_name} "{filename}".'


def create_read_permission_error_parser_error(argument_name, filename):
    return f'Could not open the {argument_name} "{filename}" : do not have read permission.'


def _wrap_text(text: str, width: int = 80) -> str:
    lines = text.splitlines()

    for i, line in enumerate(lines):
        lines[i] = textwrap.fill(line, width)

    return '\n'.join(lines)


PROGRAM_DESCRIPTION = _wrap_text('Display an audio spectrogram of this device\'s default audio input on an array of LEDs. '
                                 'Physical LEDs require a microcontroller (or similar device); '
                                 'serial data is sent from this program to said '
                                 'microcontroller via a user specified serial port.')

SETTINGS_HELP_MESSAGE = _wrap_text(
    '''\
The path to a JSON file containing configuration settings for this program. Said JSON file MUST include the following fields:

start_led (int): The index of the first LED.

end_led (int): The index of the last LED.

milliseconds_per_audio_chunk (int): How many milliseconds of audio to analyze per spectrogram update.

min_frequency (int): The minimum frequency (in Hertz [Hz]) of the frequency range this audio spectrogram will display.

max_frequency (int): The maximum frequency (in Hertz [Hz]) of the frequency range this audio spectrogram will display.

number_of_bands (int): The number of audio bands the audio spectrogram will divide the frequency range into. The LED range [start_led, end_led] is equally divided into number_of_bands many band; each band of LEDs represents a frequency band. If number_of_bands is not a factor of the number of LEDs, then all remaining LEDs are treated as the last frequency band.

reverse_bands (boolean): If True, will display bands ascending (from highest frequency to lowest frequency). If False, will display bands ascending (from lowest frequency to highest frequency).

mirror_bands (boolean): If True, will split bands symmetrically about the center LED.\
'''
)


COLOR_PALETTES_EXAMPLE = _wrap_text(
    '''\
# Green, Blue, Yellow, Orange
30 0 79 39
7 80 199 118
8 219 237 52
1 250 124 0

# Purple -> Pink
30 13 0 51
7 96 0 148
8 209 88 134
1 252 0 80\
'''
)

COLOR_PALETTES_HELP_MESSAGE = _wrap_text(
    f'''\
The path to a text file containing information about each color palette. If left empty, this program uses a default color palette.

A color palette tells the spectrogram what colors to assign to a frequency based on said frequency\'s amplitude (in decibels [dB]).

The following is a valid example which creates two color palettes:

{COLOR_PALETTES_EXAMPLE}

The previous example is read as follows:

*Note: The program rounds decibel values to the nearest integer.

*Note: Comments should be on their own line and start with the '#' character.

*Note: You must separate each color palette at least one "empty" (i.e. whitespace) line.

Line 1: *A comment*

Line 2: "Represent the first 30 decibels [0, 29] with the RGB color (0, 79, 79)"

Line 3: "Represent the next 7 decibels [30, 36] with the RGB color (80, 199, 118)"

Line 4: "Represent the next 8 decibels [37, 44] with the RGB color (219 237 52)"

Line 5: "Represent the next 1 decibel [45] with the RGB color (250, 124, 0). Because this is the last entry in the color palette, all decibels >= 45 will be represented with this color."

Line 6: *An "empty" (whitespace) line separates different color palettes.*

Line 7: *A comment*

Lines 8 - 11: *These lines define another color palette (similar to lines 2-5).*\
'''
)

DURATION_HELP_MESSAGE = _wrap_text('The number of seconds between each color palette change. If left empty, the first color palette is used indefinitely.')
SERIAL_PORT_HELP_MESSAGE = _wrap_text('The serial port. If left empty, will display a graphical LED spectrogram.')
BAUDRATE_HELP_MESSAGE = _wrap_text('The serial baudrate.')
BRIGHTNESS_HELP_MESSAGE = _wrap_text('The brightness of the physical LEDs. Allowed values include integers within the range [0, 255].')
REVERSE_BANDS_HELP_MESSAGE = _wrap_text('A value of 0 will order frequency bands from smallest_frequency -> largest_frequency. A non-zero value will order frequency bands from largest_frequency -> smallest_freqency. Will override (not "overwrite") the settings file\'s configuration.')
