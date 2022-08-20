import unittest
from queue import Empty

from util import TimedCircularQueue


class TestTimedCircularQueue(unittest.TestCase):
    def test_seconds_between_dequeues_is_less_than_0(self):
        with self.assertRaises(ValueError):
            ITEMS = []
            SECONDS_BETWEEN_DEQUEUES = -1

            TimedCircularQueue(ITEMS, SECONDS_BETWEEN_DEQUEUES)

    def test_setting_valid_seconds_between_dequeues(self):
        VALID_SECONDS = [0, 1, 20, 100]

        queue = TimedCircularQueue()

        for seconds in VALID_SECONDS:
            with self.subTest(seconds=seconds):
                queue.seconds_between_dequeues = seconds

                self.assertEqual(seconds, queue.seconds_between_dequeues)

    def test_setting_invalid_seconds_between_dequeues(self):
        INVALID_SECONDS = [-1, -10]

        queue = TimedCircularQueue()

        ORIGINAL_SECONDS_BETWEEN_DEQUEUES = queue.seconds_between_dequeues

        for seconds in INVALID_SECONDS:
            with self.subTest(seconds=seconds):
                with self.assertRaises(ValueError):
                    queue.seconds_between_dequeues = seconds

                self.assertEqual(ORIGINAL_SECONDS_BETWEEN_DEQUEUES,
                                 queue.seconds_between_dequeues)

    def test_enqueue(self):
        queue = TimedCircularQueue()

        queue.enqueue(1)

        EXPECTED_LENGTH = 1

        self.assertEqual(len(queue), EXPECTED_LENGTH)

    def test_dequeue_empty_queue(self):
        queue = TimedCircularQueue()

        with self.assertRaises(Empty):
            queue.dequeue()

    def test_dequeue_before_next_dequeue_is_allowed(self):
        ITEMS = [0, 1, 2]
        SECONDS_BETWEEN_DEQUEUES = 10

        queue = TimedCircularQueue(ITEMS, SECONDS_BETWEEN_DEQUEUES)

        queue.dequeue()

        with self.assertRaises(ValueError):
            queue.dequeue()

    def test_dequeue_when_next_dequeue_is_allowed(self):
        ITEMS = [0, 1, 2]
        SECONDS_BETWEEN_DEQUEUS = 0

        queue = TimedCircularQueue(ITEMS, SECONDS_BETWEEN_DEQUEUS)

        dequeued_item_1 = queue.dequeue()
        dequeued_item_2 = queue.dequeue()

        self.assertEqual(dequeued_item_1, ITEMS[0])
        self.assertEqual(dequeued_item_2, ITEMS[1])
