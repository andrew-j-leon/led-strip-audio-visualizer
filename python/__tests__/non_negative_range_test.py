import unittest

from spectrogram import NonNegativeRange


class TestConstructor(unittest.TestCase):

    def test_valid(self):
        RANGES = [(0, 0), (0, 1), (1, 1), (0, 100), (1, 100),
                  (0.1, 1), (0.1, 1.1), (1.1, 1.1), (2.56, 104.54)]

        for start, end in RANGES:
            with self.subTest(range=(start, end)):

                NonNegativeRange(start, end)

    def test_start_is_negative(self):
        RANGES = [(-1, 0), (-100, 0),
                  (-0.1, 0), (-0.1, 0)]

        for start, end in RANGES:
            with self.subTest(range=(start, end)):

                with self.assertRaises(ValueError):
                    NonNegativeRange(start, end)

    def test_end_is_negative(self):
        RANGES = [(0, -1), (0, -100),
                  (0, -0.1), (0, -100.1)]

        for start, end in RANGES:
            with self.subTest(range=(start, end)):

                with self.assertRaises(ValueError):
                    NonNegativeRange(start, end)

    def test_start_is_greater_than_end(self):
        RANGES = [(1, 0), (100, 0), (2, 1), (100, 1),
                  (1.1, 1), (100.1, 1)]

        for start, end in RANGES:
            with self.subTest(range=(start, end)):

                with self.assertRaises(ValueError):
                    NonNegativeRange(start, end)


class TestStartAndEnd(unittest.TestCase):
    def test_start(self):
        RANGES = [(0, 0), (0, 1), (1, 1), (0, 100), (1, 100),
                  (0.1, 1), (0.1, 1.1), (1.1, 1.1), (2.56, 104.54)]

        for start, end in RANGES:
            with self.subTest(range=(start, end)):

                non_negative_range = NonNegativeRange(start, end)

                self.assertEqual(non_negative_range.start, start)

    def test_end(self):
        RANGES = [(0, 0), (0, 1), (1, 1), (0, 100), (1, 100),
                  (0.1, 1), (0.1, 1.1), (1.1, 1.1), (2.56, 104.54)]

        for start, end in RANGES:
            with self.subTest(range=(start, end)):

                non_negative_range = NonNegativeRange(start, end)

                self.assertEqual(non_negative_range.end, end)
