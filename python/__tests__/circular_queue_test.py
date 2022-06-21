import unittest

from util import CircularQueue


class TestCircularQueue(unittest.TestCase):

    def test_enqueue(self):
        queue = CircularQueue()

        queue.enqueue(1)

        EXPECTED_LENGTH = 1

        self.assertEqual(len(queue), EXPECTED_LENGTH)

    def test_dequeue(self):
        ELEMENTS = [0, 1, 2, 3]

        queue = CircularQueue(ELEMENTS)

        for cycle_number in range(1, 3):
            with self.subTest(cycle_number=cycle_number):
                for expected_element in ELEMENTS:
                    with self.subTest(expected_element=expected_element):

                        self.assertEqual(queue.dequeue(), expected_element)
                        self.assertEqual(len(ELEMENTS), len(queue))

    def test_dequeue_on_empty_queue(self):
        queue = CircularQueue()

        with self.assertRaises(ValueError):
            queue.dequeue()
