import unittest
from unittest.mock import MagicMock, patch

from libraries.serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial


class TestConstructor(unittest.TestCase):
    def test_constructor(self):
        PORT = '/dev/ttyACM0'
        BAUD_RATE = 115200
        READ_TIMEOUT = 1
        WRITE_TIMEOUT = 0

        with patch('libraries.serial.serial.Serial'):
            ProductionSerial(PORT, BAUD_RATE, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, EIGHTBITS, READ_TIMEOUT, WRITE_TIMEOUT)


class TestMethods(unittest.TestCase):
    def setUp(self):
        self.__serial_patch = patch('libraries.serial.serial.Serial')

        self.__serial_mock = self.__serial_patch.start()
        self.addCleanup(self.__serial_patch.stop)

        self.serial_instance_mock = self.__serial_mock.return_value = MagicMock()

        PORT = '/dev/ttyACM0'
        BAUD_RATE = 115200
        READ_TIMEOUT = 1
        WRITE_TIMEOUT = 0

        self.serial = ProductionSerial(PORT, BAUD_RATE, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, EIGHTBITS, READ_TIMEOUT, WRITE_TIMEOUT)

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
