import unittest
from unittest.mock import MagicMock, patch

import libraries.serial
from libraries.serial import EIGHTBITS, INIT_SERIAL_MESSAGE, PARITY_NONE, STOPBITS_ONE_POINT_FIVE, ProductionSerial, SerialException

libraries.serial.SERIAL_INIT_DELAY = 0


class SerialTestCase(unittest.TestCase):
    PORT = '/dev/ttyACM0'
    BAUD_RATE = 115200
    READ_TIMEOUT = 1
    WRITE_TIMEOUT = 0

    def setUp(self):
        self.__serial_patch = patch('libraries.serial.serial.Serial')

        self.addCleanup(self.__serial_patch.stop)

        self.__serial_mock = self.__serial_patch.start()
        self.serial_instance_mock = self.__serial_mock.return_value = MagicMock()

        self.production_serial = ProductionSerial()


class TestOpen(SerialTestCase):
    def test_open_and_connection_succeeded(self):
        NUMBER_OF_LEDS = 100
        NUMBER_OF_BYTES = 2
        BYTE_ORDER = 'little'

        self.serial_instance_mock.read.return_value = NUMBER_OF_LEDS.to_bytes(NUMBER_OF_BYTES, BYTE_ORDER)

        self.production_serial.open(self.PORT, self.BAUD_RATE, PARITY_NONE, STOPBITS_ONE_POINT_FIVE,
                                    EIGHTBITS, self.READ_TIMEOUT, self.WRITE_TIMEOUT)

        self.serial_instance_mock.write.assert_called_once_with(INIT_SERIAL_MESSAGE)
        self.assertEqual(self.production_serial.number_of_leds, NUMBER_OF_LEDS)

    def test_open_but_connection_failed(self):
        self.serial_instance_mock.read.return_value = bytes()

        with self.assertRaises(SerialException):
            self.production_serial.open(self.PORT, self.BAUD_RATE, PARITY_NONE, STOPBITS_ONE_POINT_FIVE,
                                        EIGHTBITS, self.READ_TIMEOUT, self.WRITE_TIMEOUT)


class TestProductionSerialWhenConnectionIsClosed(SerialTestCase):
    def test_number_of_leds(self):
        with self.assertRaises(SerialException):
            self.production_serial.number_of_leds

    def test_read(self):
        with self.assertRaises(SerialException):
            NUMBER_OF_BYTES = 1
            self.production_serial.read(NUMBER_OF_BYTES)

    def test_write(self):
        with self.assertRaises(SerialException):
            DATA = b''
            self.production_serial.write(DATA)

    def test_close(self):
        self.production_serial.close()

    def test_close_when_already_closed(self):
        self.production_serial.close()
        self.production_serial.close()


class TestProductionSerialWhenConnectionIsOpen(SerialTestCase):
    NUMBER_OF_LEDS = 100

    def setUp(self):
        super().setUp()

        NUMBER_OF_BYTES = 2
        BYTE_ORDER = 'little'
        self.serial_instance_mock.read.return_value = self.NUMBER_OF_LEDS.to_bytes(NUMBER_OF_BYTES, BYTE_ORDER)

        self.production_serial.open(self.PORT, self.BAUD_RATE, PARITY_NONE, STOPBITS_ONE_POINT_FIVE,
                                    EIGHTBITS, self.READ_TIMEOUT, self.WRITE_TIMEOUT)

        self.serial_instance_mock.read.reset_mock()

    def test_number_of_leds(self):
        ACTUAL_NUMBER_OF_LEDS = self.production_serial.number_of_leds

        self.assertEqual(ACTUAL_NUMBER_OF_LEDS, self.NUMBER_OF_LEDS)

    def test_read_fewer_bytes_than_requested(self):
        NUMBER_OF_BYTES = 10

        TOO_FEW_BYTES = [b'', b'a', b'a' * (NUMBER_OF_BYTES - 1)]

        for bytes_ in TOO_FEW_BYTES:
            with self.subTest(f"{NUMBER_OF_BYTES} bytes received."):
                self.serial_instance_mock.read.return_value = bytes_

                with self.assertRaises(SerialException):
                    self.production_serial.read(NUMBER_OF_BYTES)

                self.serial_instance_mock.read.assert_called_once_with(NUMBER_OF_BYTES)
                self.serial_instance_mock.read.reset_mock()

    def test_read_more_bytes_than_requested(self):
        self.serial_instance_mock.read.return_value = b'hello'

        NUMBER_OF_BYTES = 10

        TOO_FEW_BYTES = [b'a' * (NUMBER_OF_BYTES + 1), b'a' * (NUMBER_OF_BYTES + 2)]

        for bytes_ in TOO_FEW_BYTES:
            with self.subTest(f"{NUMBER_OF_BYTES} bytes received."):
                self.serial_instance_mock.read.return_value = bytes_

                data = self.production_serial.read(NUMBER_OF_BYTES)
                self.assertEqual(data, bytes_)

                self.serial_instance_mock.read.assert_called_once_with(NUMBER_OF_BYTES)
                self.serial_instance_mock.read.reset_mock()

    def test_read_zero_bytes(self):
        NUMBER_OF_BYTES = 0

        BYTES = [b'', b'a', b'a' * 10]

        for bytes_ in BYTES:
            with self.subTest(f"{NUMBER_OF_BYTES} bytes received."):
                self.serial_instance_mock.read.return_value = bytes_

                data = self.production_serial.read(NUMBER_OF_BYTES)
                self.assertEqual(data, bytes_)

                self.serial_instance_mock.read.assert_called_once_with(NUMBER_OF_BYTES)
                self.serial_instance_mock.read.reset_mock()

    def test_read_one_byte(self):
        NUMBER_OF_BYTES = 1

        BYTES = [b'a', b'aa', b'a' * 10]

        for bytes_ in BYTES:
            with self.subTest(f"{NUMBER_OF_BYTES} bytes received."):
                self.serial_instance_mock.read.return_value = bytes_

                data = self.production_serial.read(NUMBER_OF_BYTES)
                self.assertEqual(data, bytes_)

                self.serial_instance_mock.read.assert_called_once_with(NUMBER_OF_BYTES)
                self.serial_instance_mock.read.reset_mock()

    def test_read_multiple_bytes(self):
        NUMBER_OF_BYTES = 10

        BYTES = [b'a' * NUMBER_OF_BYTES, b'a' * (NUMBER_OF_BYTES + 1), b'a' * (NUMBER_OF_BYTES + 2)]

        for bytes_ in BYTES:
            with self.subTest(f"{NUMBER_OF_BYTES} bytes received."):
                self.serial_instance_mock.read.return_value = bytes_

                data = self.production_serial.read(NUMBER_OF_BYTES)
                self.assertEqual(data, bytes_)

                self.serial_instance_mock.read.assert_called_once_with(NUMBER_OF_BYTES)
                self.serial_instance_mock.read.reset_mock()

    def test_write(self):
        DATA = b'hello'

        self.production_serial.write(DATA)

        self.serial_instance_mock.write.assert_called_with(DATA)

    def test_close(self):
        self.production_serial.close()

        self.serial_instance_mock.close.assert_called_once()

    def test_close_when_already_closed(self):
        self.production_serial.close()
        self.production_serial.close()
