from unittest import TestCase

from main import create_bands, create_mirrored_bands


class TestCreateGroups(TestCase):
    def test_start_led_is_negative(self):
        START_LED = -1
        END_LED = 0
        NUMBER_OF_GROUPS = 1

        with self.assertRaises(ValueError):
            create_bands(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_end_led_is_negative(self):
        START_LED = 0
        END_LED = -1
        NUMBER_OF_GROUPS = 1

        with self.assertRaises(ValueError):
            create_bands(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_zero_leds(self):
        START_LED = 0
        END_LED = 0
        NUMBER_OF_GROUPS = 5

        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), [])

    def test_one_led(self):
        START_LED = 0
        END_LED = 1
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(START_LED, END_LED)}, set(), set(), set(), set()]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_ten_leds(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 2)}, {(2, 4)}, {(4, 6)}, {(6, 8)}, {(8, 10)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_six_hundred_leds(self):
        START_LED = 0
        END_LED = 600
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 120)}, {(120, 240)}, {(240, 360)}, {(360, 480)}, {(480, 600)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_negative_leds(self):
        START_LED = 1
        END_LED = 0
        NUMBER_OF_GROUPS = 5

        with self.assertRaises(ValueError):
            create_bands(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_zero_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 0

        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), [])

    def test_one_group(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 1

        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), [{(0, 100)}])

    def test_ten_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 10

        EXPECTED = [{(start, start + 10)} for start in range(START_LED, 91, 10)]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_one_hundred_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 100

        EXPECTED = [{(start, start + 1)} for start in range(START_LED, 100)]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_one_led_per_group(self):
        START_LED = 0
        END_LED = 5
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 1)}, {(1, 2)}, {(2, 3)}, {(3, 4)}, {(4, 5)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_two_leds_per_group(self):
        START_LED = 0
        END_LED = 6
        NUMBER_OF_GROUPS = 3

        EXPECTED = [{(0, 2)}, {(2, 4)}, {(4, 6)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_ten_leds_per_group(self):
        START_LED = 0
        END_LED = 50
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 10)}, {(10, 20)}, {(20, 30)}, {(30, 40)}, {(40, 50)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_negative_number_of_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = -1

        with self.assertRaises(ValueError):
            create_bands(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_number_of_groups_greater_than_number_of_leds(self):
        START_LED = 0
        END_LED = 3
        NUMBER_OF_GROUPS = 4

        EXPECTED = [{(START_LED, 1)}, {(1, 2)}, {(2, END_LED)}, set()]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_number_of_leds_divided_by_three_groups_has_a_remainder_of_1(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 3

        EXPECTED = [{(START_LED, 3)}, {(3, 6)}, {(6, END_LED)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_number_of_leds_divided_by_three_groups_has_a_remainder_of_2(self):
        START_LED = 0
        END_LED = 29
        NUMBER_OF_GROUPS = 3

        EXPECTED = [{(START_LED, 9)}, {(9, 18)}, {(18, END_LED)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_zero(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(0, 2)}, {(2, 4)}, {(4, 6)}, {(6, 8)}, {(8, 10)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_one(self):
        START_LED = 1
        END_LED = 11
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(1, 3)}, {(3, 5)}, {(5, 7)}, {(7, 9)}, {(9, 11)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_one_hundred(self):
        START_LED = 100
        END_LED = 110
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(100, 102)}, {(102, 104)}, {(104, 106)}, {(106, 108)}, {(108, 110)}]
        self.assertEqual(create_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)


class TestCreateMirroredGroups(TestCase):
    def test_start_led_is_negative(self):
        START_LED = -1
        END_LED = 0
        NUMBER_OF_GROUPS = 1

        with self.assertRaises(ValueError):
            create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_end_led_is_negative(self):
        START_LED = 0
        END_LED = -1
        NUMBER_OF_GROUPS = 1

        with self.assertRaises(ValueError):
            create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_zero_leds(self):
        START_LED = 0
        END_LED = 0
        NUMBER_OF_GROUPS = 5

        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), [])

    def test_one_led(self):
        START_LED = 0
        END_LED = 1
        NUMBER_OF_GROUPS = 5

        EXPECTED = [set(), set(), set(), set(), {(0, 1)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_ten_leds(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(4, 5), (5, 6)}, {(3, 4), (6, 7)}, {(2, 3), (7, 8)}, {(1, 2), (8, 9)}, {(0, 1), (9, 10)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_six_hundred_leds(self):
        START_LED = 0
        END_LED = 600
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(240, 300), (300, 360)}, {(180, 240), (360, 420)},
                    {(120, 180), (420, 480)}, {(60, 120), (480, 540)},
                    {(0, 60), (540, 600)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_negative_leds(self):
        START_LED = 1
        END_LED = 0
        NUMBER_OF_GROUPS = 5

        with self.assertRaises(ValueError):
            create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_zero_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 0

        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), [])

    def test_one_group(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = 1

        EXPECTED = [{(0, 50), (50, 100)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_five_groups(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(4, 5), (5, 6)}, {(3, 4), (6, 7)}, {(2, 3), (7, 8)}, {(1, 2), (8, 9)}, {(0, 1), (9, 10)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_negative_number_of_groups(self):
        START_LED = 0
        END_LED = 100
        NUMBER_OF_GROUPS = -1

        with self.assertRaises(ValueError):
            create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS)

    def test_number_of_groups_greater_than_number_of_leds(self):
        START_LED = 0
        END_LED = 3
        NUMBER_OF_GROUPS = 4

        EXPECTED = [set(), {(2, 3)}, {(1, 2)}, {(0, 1)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_cannot_evenly_divide_number_of_leds_by_number_of_groups(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 3

        EXPECTED = [{(2, 3), (3, 4)}, {(1, 2), (4, 5)}, {(0, 1), (5, 6)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_zero(self):
        START_LED = 0
        END_LED = 10
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(4, 5), (5, 6)}, {(3, 4), (6, 7)},
                    {(2, 3), (7, 8)}, {(1, 2), (8, 9)},
                    {(0, 1), (9, 10)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_one(self):
        START_LED = 1
        END_LED = 11
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(5, 6), (6, 7)}, {(4, 5), (7, 8)},
                    {(3, 4), (8, 9)}, {(2, 3), (9, 10)},
                    {(1, 2), (10, 11)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)

    def test_start_led_at_one_hundred(self):
        START_LED = 100
        END_LED = 110
        NUMBER_OF_GROUPS = 5

        EXPECTED = [{(104, 105), (105, 106)}, {(103, 104), (106, 107)},
                    {(102, 103), (107, 108)}, {(101, 102), (108, 109)},
                    {(100, 101), (109, 110)}]
        self.assertEqual(create_mirrored_bands(START_LED, END_LED, NUMBER_OF_GROUPS), EXPECTED)
