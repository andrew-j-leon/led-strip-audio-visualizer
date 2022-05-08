import unittest
from unittest.mock import MagicMock, patch

from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial


class TestConstructor(unittest.TestCase):
    PORT = '/dev/ttyACM0'
    BAUD_RATE = 115200
    READ_TIMEOUT = 1
    WRITE_TIMEOUT = 0

    def setUp(self):
        self.__serial_patch = patch('libraries.serial.serial.Serial')

        self.__serial_mock = self.__serial_patch.start()
        self.addCleanup(self.__serial_patch.stop)

        self.serial_instance_mock = self.__serial_mock.return_value = MagicMock()

    def test_serial_connection_succeeded(self):
        NUMBER_OF_LEDS = 100
        NUMBER_OF_BYTES = 2
        BYTE_ORDER = 'big'

        self.serial_instance_mock.read.return_value = NUMBER_OF_LEDS.to_bytes(NUMBER_OF_BYTES, BYTE_ORDER)

        production_serial = ProductionSerial(self.PORT, self.BAUD_RATE, PARITY_NONE, STOPBITS_ONE_POINT_FIVE,
                                             EIGHTBITS, self.READ_TIMEOUT, self.WRITE_TIMEOUT)

        self.assertEqual(production_serial.number_of_leds, NUMBER_OF_LEDS)

    def test_serial_connection_failed(self):
        self.serial_instance_mock.read.return_value = bytes()

        with self.assertRaises(ValueError) as error:

            ProductionSerial(self.PORT, self.BAUD_RATE, PARITY_NONE, STOPBITS_ONE_POINT_FIVE,
                             EIGHTBITS, self.READ_TIMEOUT, self.WRITE_TIMEOUT)

        error_message = str(error.exception)

        EXPECTED_NUMBER_OF_BYTES = 2
        ACTUAL_NUMBER_OF_BYTES = 0
        expected_error_message = f'ProductionSerial expected {EXPECTED_NUMBER_OF_BYTES} bytes from the serial connection (representing the number of leds in the led strip), but instead received {ACTUAL_NUMBER_OF_BYTES} bytes.'

        self.assertEqual(error_message, expected_error_message)


class TestMethods(unittest.TestCase):
    NUMBER_OF_LEDS = 100

    def setUp(self):
        self.__serial_patch = patch('libraries.serial.serial.Serial')

        self.__serial_mock = self.__serial_patch.start()
        self.addCleanup(self.__serial_patch.stop)

        self.serial_instance_mock = self.__serial_mock.return_value = MagicMock()

        NUMBER_OF_BYTES = 2
        BYTE_ORDER = 'big'
        self.serial_instance_mock.read.return_value = self.NUMBER_OF_LEDS.to_bytes(NUMBER_OF_BYTES, BYTE_ORDER)

        PORT = '/dev/ttyACM0'
        BAUD_RATE = 115200
        READ_TIMEOUT = 1
        WRITE_TIMEOUT = 0

        self.serial = ProductionSerial(PORT, BAUD_RATE, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, EIGHTBITS, READ_TIMEOUT, WRITE_TIMEOUT)

        self.serial_instance_mock.read.reset_mock()

    def test_number_of_bytes_in_buffer(self):
        NUMBER_OF_BYTES_IN_BUFFER = 5

        self.serial_instance_mock.in_waiting = NUMBER_OF_BYTES_IN_BUFFER

        self.assertEqual(self.serial.number_of_bytes_in_buffer, NUMBER_OF_BYTES_IN_BUFFER)

    def test_read(self):
        self.serial_instance_mock.read.return_value = b'hello'

        NUMBER_OF_BYTES = 10
        data = self.serial.read(NUMBER_OF_BYTES)

        self.serial_instance_mock.read.assert_called_once_with(NUMBER_OF_BYTES)
        self.assertEqual(data, b'hello')

    def test_write(self):
        DATA = b'hello'

        self.serial.write(DATA)

        self.serial_instance_mock.write.assert_called_once_with(DATA)

    def test_close(self):
        self.serial.close()

        self.serial_instance_mock.close.assert_called_once()
