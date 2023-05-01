#include <gtest/gtest.h>
#include "../group_setup_state.h"

uint16* group_received_led_ranges = nullptr;
uint8 group_received_number_of_led_ranges = 0;
uint8 group_received_number_of_groups_received = 0;
uint8 group_received_group_number = 0;

void on_group_received(uint16* led_ranges, uint8 number_of_led_ranges, uint8 band_number) {
    group_received_led_ranges = led_ranges;
    group_received_number_of_led_ranges = number_of_led_ranges;
    group_received_group_number = band_number;
    group_received_number_of_groups_received++;
}

uint8 get_checksum(uint8 number_of_led_ranges, uint8 start_led_lower_byte, uint8 start_led_upper_byte,
                   uint8 end_led_lower_byte, uint8 end_led_upper_byte)
{
    return (number_of_led_ranges + start_led_lower_byte + start_led_upper_byte +
            end_led_lower_byte + end_led_upper_byte);
}

bool are_equal(uint16* array_1, uint16* array_2, unsigned int length) {
    if (array_1 == nullptr || array_2 == nullptr) {
        return array_1 == array_2;
    }

    for (unsigned int i = 0; i < length; i++) {
        if (array_1[i] != array_2[i]) {
            return false;
        }
    }

    return true;
}

class GroupSetupStateTest : public ::testing::Test {
    public:
        uint8 number_of_expected_groups;
        GroupSetupState* group_setup_state = nullptr;

        GroupSetupStateTest() {
            number_of_expected_groups = 3;
            group_setup_state = new GroupSetupState(number_of_expected_groups);

            group_received_number_of_groups_received = 0;
            group_received_led_ranges = nullptr;
            group_received_number_of_led_ranges = 0;
        }

        void TearDown() override {
            delete group_setup_state;
            group_setup_state = nullptr;
        }

    protected:
        void send_led_ranges(uint16* led_ranges, uint8 number_of_led_ranges) {
            assert_on_state(GroupSetupStateState::NUMBER_OF_LED_RANGES);

            update_state(number_of_led_ranges);

            for (int led_range = 0; led_range < number_of_led_ranges; led_range++) {
                uint16 start_led = led_ranges[led_range * GroupSetupState::LEDS_PER_LED_RANGE];
                uint16 end_led = led_ranges[led_range * GroupSetupState::LEDS_PER_LED_RANGE + 1];

                uint8 start_led_lower_byte = start_led & 0x00FF;
                uint8 start_led_upper_byte = start_led >> 8;

                uint8 end_led_lower_byte = end_led & 0x00FF;
                uint8 end_led_upper_byte = end_led >> 8;

                assert_on_state(GroupSetupStateState::START_LED_LOWER_BYTE);

                update_state(start_led_lower_byte);
                assert_on_state(GroupSetupStateState::START_LED_UPPER_BYTE);

                update_state(start_led_upper_byte);
                assert_on_state(GroupSetupStateState::END_LED_LOWER_BYTE);

                update_state(end_led_lower_byte);
                assert_on_state(GroupSetupStateState::END_LED_UPPER_BYTE);

                update_state(end_led_upper_byte);
                assert_on_state(GroupSetupStateState::CHECK_SUM);

                update_state(get_checksum(number_of_led_ranges, start_led_lower_byte,
                                          start_led_upper_byte, end_led_lower_byte,
                                          end_led_upper_byte));
            }
        }

        void set_group_setup_state(uint8 the_number_of_expected_groups) {
            delete group_setup_state;
            group_setup_state = new GroupSetupState(the_number_of_expected_groups);
            number_of_expected_groups = the_number_of_expected_groups;
        }

        void go_to_start_led_lower_byte_state(uint8 expected_number_of_groups) {
            ASSERT_EQ(group_setup_state->get_state(), GroupSetupStateState::START_OF_MESSAGE);
            update_state(GroupSetupState::START_OF_MESSAGE_CODE);

            ASSERT_EQ(group_setup_state->get_state(), GroupSetupStateState::NUMBER_OF_LED_RANGES);
            update_state(expected_number_of_groups);

            ASSERT_EQ(group_setup_state->get_state(), GroupSetupStateState::START_LED_LOWER_BYTE);
        }

        void update_state(uint8 byte) {
            group_setup_state->update_state(byte, on_group_received);
        }

        void test_StartOfMessage_to_NumberOfLedRanges() {
            update_state(GroupSetupState::START_OF_MESSAGE_CODE);

            EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::NUMBER_OF_LED_RANGES);
            EXPECT_EQ(group_received_number_of_groups_received, 0);
        }

        void test_NumberOfLedRanges_to_StartLedLowerByte(uint8 number_of_led_ranges) {
            test_StartOfMessage_to_NumberOfLedRanges();
            update_state(number_of_led_ranges);

            EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::START_LED_LOWER_BYTE);
            EXPECT_EQ(group_received_number_of_groups_received, 0);
        }

        void test_StartLedLowerByte_to_StartLedUpperByte(uint8 number_of_led_ranges, uint8 start_led_lower_byte) {
            test_NumberOfLedRanges_to_StartLedLowerByte(number_of_led_ranges);
            update_state(start_led_lower_byte);

            EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::START_LED_UPPER_BYTE);
            EXPECT_EQ(group_received_number_of_groups_received, 0);
        }

        void test_StartLedUpperByte_to_EndLedLowerByte(uint8 number_of_led_ranges, uint8 start_led_lower_byte,
                                                       uint8 start_led_upper_byte) {
            test_StartLedLowerByte_to_StartLedUpperByte(number_of_led_ranges, start_led_lower_byte);
            update_state(start_led_upper_byte);

            EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::END_LED_LOWER_BYTE);
            EXPECT_EQ(group_received_number_of_groups_received, 0);
        }

        void test_EndLedLowerByte_to_EndLedUpperByte(uint8 number_of_led_ranges, uint8 start_led_lower_byte,
                                                     uint8 start_led_upper_byte, uint8 end_led_lower_byte) {
            test_StartLedUpperByte_to_EndLedLowerByte(number_of_led_ranges, start_led_lower_byte, start_led_upper_byte);
            update_state(end_led_lower_byte);

            EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::END_LED_UPPER_BYTE);
            EXPECT_EQ(group_received_number_of_groups_received, 0);
        }

        void test_EndLedUpperByte_to_CheckSum(uint8 number_of_led_ranges, uint8 start_led_lower_byte,
                                              uint8 start_led_upper_byte, uint8 end_led_lower_byte,
                                              uint8 end_led_upper_byte) {
            test_EndLedLowerByte_to_EndLedUpperByte(number_of_led_ranges, start_led_lower_byte,
                                                    start_led_upper_byte, end_led_lower_byte);
            update_state(end_led_upper_byte);

            EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::CHECK_SUM);
            EXPECT_EQ(group_received_number_of_groups_received, 0);
        }

        void test_CheckSum_to_EndOfMessage() {
            update_state(GroupSetupState::START_OF_MESSAGE_CODE);

            const uint8 NUMBER_OF_LED_RANGES = 0x01;
            const uint8 start_led_lower_byte = 0x02;
            const uint8 start_led_upper_byte = 0x03;
            const uint8 end_led_lower_byte = 0x04;
            const uint8 end_led_upper_byte = 0x05;

            for (int i = 0; i < number_of_expected_groups; i++) {
                update_state(NUMBER_OF_LED_RANGES);
                update_state(start_led_lower_byte);
                update_state(start_led_upper_byte);
                update_state(end_led_lower_byte);
                update_state(end_led_upper_byte);

                update_state(get_checksum(NUMBER_OF_LED_RANGES, start_led_lower_byte,
                                        start_led_upper_byte, end_led_lower_byte, end_led_upper_byte));
            }

            EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::END_OF_MESSAGE);
            EXPECT_EQ(group_received_number_of_groups_received, number_of_expected_groups);
        }

        void assert_on_state(GroupSetupStateState state) {
            ASSERT_EQ(group_setup_state->get_state(), state);
        }
};

TEST_F(GroupSetupStateTest, StartOfMessage_to_StartOfMessage) {
    const uint8 INVALID_START_OF_MESSAGE_CODE = GroupSetupState::START_OF_MESSAGE_CODE + 0x01;

    update_state(INVALID_START_OF_MESSAGE_CODE);

    EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::START_OF_MESSAGE);
    EXPECT_EQ(group_received_number_of_groups_received, 0);
}

TEST_F(GroupSetupStateTest, StartOfMessage_to_NumberOfLedRanges) {
    test_StartOfMessage_to_NumberOfLedRanges();
}

TEST_F(GroupSetupStateTest, NumberOfLedRanges_to_CheckSum) {
    test_StartOfMessage_to_NumberOfLedRanges();
    uint8 number_of_led_ranges = 0x00;
    update_state(number_of_led_ranges);

    EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::CHECK_SUM);
}

TEST_F(GroupSetupStateTest, NumberOfLedRanges_to_StartLedLowerByte) {
    uint8 number_of_led_ranges = 0x01;
    test_NumberOfLedRanges_to_StartLedLowerByte(number_of_led_ranges);
}

TEST_F(GroupSetupStateTest, StartLedLowerByte_to_StartLedUpperByte) {
    uint8 number_of_led_ranges = 0x01;
    uint8 start_led_lower_byte = 0x01;
    test_StartLedLowerByte_to_StartLedUpperByte(number_of_led_ranges, start_led_lower_byte);
}

TEST_F(GroupSetupStateTest, StartLedUpperByte_to_EndLedLowerByte) {
    uint8 number_of_led_ranges = 0x01;
    uint8 start_led_lower_byte = 0x01;
    uint8 start_led_upper_byte = 0x02;
    test_StartLedUpperByte_to_EndLedLowerByte(number_of_led_ranges, start_led_lower_byte,
                                              start_led_upper_byte);
}

TEST_F(GroupSetupStateTest, EndLedLowerByte_to_EndLedUpperByte) {
    uint8 number_of_led_ranges = 0x01;
    uint8 start_led_lower_byte = 0x01;
    uint8 start_led_upper_byte = 0x02;
    uint8 end_led_lower_byte = 0x03;
    test_EndLedLowerByte_to_EndLedUpperByte(number_of_led_ranges, start_led_lower_byte,
                                            start_led_upper_byte, end_led_lower_byte);
}

TEST_F(GroupSetupStateTest, EndLedUpperByte_to_CheckSum) {
    uint8 number_of_led_ranges = 0x01;
    uint8 start_led_lower_byte = 0x01;
    uint8 start_led_upper_byte = 0x02;
    uint8 end_led_lower_byte = 0x03;
    uint8 end_led_upper_byte = 0x04;
    test_EndLedUpperByte_to_CheckSum(number_of_led_ranges, start_led_lower_byte,
                                     start_led_upper_byte, end_led_lower_byte,
                                     end_led_upper_byte);
}

TEST_F(GroupSetupStateTest, CheckSum_to_StartOfMessage) {
    uint8 number_of_led_ranges = 0x01;
    uint8 start_led_lower_byte = 0x01;
    uint8 start_led_upper_byte = 0x02;
    uint8 end_led_lower_byte = 0x03;
    uint8 end_led_upper_byte = 0x04;
    test_EndLedUpperByte_to_CheckSum(number_of_led_ranges, start_led_lower_byte,
                                     start_led_upper_byte, end_led_lower_byte,
                                     end_led_upper_byte);

    const uint8 invalid_checksum = get_checksum(number_of_led_ranges, start_led_lower_byte,
                                                start_led_upper_byte, end_led_lower_byte, end_led_upper_byte) + 0x01;

    update_state(invalid_checksum);

    EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::START_OF_MESSAGE);
    EXPECT_EQ(group_received_number_of_groups_received, 0);
}

TEST_F(GroupSetupStateTest, CheckSum_to_StartLedLowerByte) {
    uint8 number_of_led_ranges = 0x02;
    uint8 start_led_lower_byte = 0x01;
    uint8 start_led_upper_byte = 0x02;
    uint8 end_led_lower_byte = 0x03;
    uint8 end_led_upper_byte = 0x04;
    test_EndLedUpperByte_to_CheckSum(number_of_led_ranges, start_led_lower_byte,
                                     start_led_upper_byte, end_led_lower_byte,
                                     end_led_upper_byte);

    const uint8 checksum = get_checksum(number_of_led_ranges, start_led_lower_byte,
                                        start_led_upper_byte, end_led_lower_byte, end_led_upper_byte);

    update_state(checksum);

    EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::START_LED_LOWER_BYTE);
    EXPECT_EQ(group_received_number_of_groups_received, 0);
}

TEST_F(GroupSetupStateTest, CheckSum_to_NumberOfLedRanges) {
    uint8 number_of_led_ranges = 0x01;
    uint8 start_led_lower_byte = 0x01;
    uint8 start_led_upper_byte = 0x02;
    uint8 end_led_lower_byte = 0x03;
    uint8 end_led_upper_byte = 0x04;
    test_EndLedUpperByte_to_CheckSum(number_of_led_ranges, start_led_lower_byte,
                                     start_led_upper_byte, end_led_lower_byte,
                                     end_led_upper_byte);

    const uint8 checksum = get_checksum(number_of_led_ranges, start_led_lower_byte,
                                        start_led_upper_byte, end_led_lower_byte, end_led_upper_byte);

    update_state(checksum);

    EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::NUMBER_OF_LED_RANGES);
    EXPECT_EQ(group_received_number_of_groups_received, 1);
}

TEST_F(GroupSetupStateTest, CheckSum_to_EndOfMessage) {
    test_CheckSum_to_EndOfMessage();
}

TEST_F(GroupSetupStateTest, EndOfMessage_to_EndOfMessage) {
    test_CheckSum_to_EndOfMessage();

    uint8 invalid_eom_code = GroupSetupState::END_OF_MESSAGE_CODE + 0x01;
    update_state(invalid_eom_code);

    EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::END_OF_MESSAGE);
    EXPECT_EQ(group_received_number_of_groups_received, number_of_expected_groups);
}

TEST_F(GroupSetupStateTest, EndOfMessage_to_End) {
    test_CheckSum_to_EndOfMessage();

    update_state(GroupSetupState::END_OF_MESSAGE_CODE);

    EXPECT_EQ(group_setup_state->get_state(), GroupSetupStateState::END);
    EXPECT_EQ(group_received_number_of_groups_received, number_of_expected_groups);
}

TEST_F(GroupSetupStateTest, test_groups) {
    const uint8 NUMBER_OF_GROUPS = 4;
    set_group_setup_state(NUMBER_OF_GROUPS);

    assert_on_state(GroupSetupStateState::START_OF_MESSAGE);

    update_state(GroupSetupState::START_OF_MESSAGE_CODE);
    assert_on_state(GroupSetupStateState::NUMBER_OF_LED_RANGES);

    // Group 0
    uint8 group_0_number_of_led_ranges = 0;
    unsigned int group_0_led_ranges_length = 0;
    uint16* group_0_led_ranges = nullptr;
    uint8 group_0_checksum = 0;

    update_state(group_0_number_of_led_ranges);
    assert_on_state(GroupSetupStateState::CHECK_SUM);
    update_state(group_0_checksum);
    assert_on_state(GroupSetupStateState::NUMBER_OF_LED_RANGES);

    EXPECT_EQ(group_received_group_number, 0);
    EXPECT_EQ(group_received_number_of_groups_received, 1);
    EXPECT_EQ(group_received_number_of_led_ranges, group_0_number_of_led_ranges);
    EXPECT_TRUE(are_equal(group_received_led_ranges, group_0_led_ranges, group_0_led_ranges_length));

    // Group 1
    uint8 group_1_number_of_led_ranges = 1;
    unsigned int group_1_led_ranges_length = group_1_number_of_led_ranges * GroupSetupState::LEDS_PER_LED_RANGE;
    uint16 group_1_led_ranges[group_1_led_ranges_length] = {0, 10};

    send_led_ranges(group_1_led_ranges, group_1_number_of_led_ranges);
    assert_on_state(GroupSetupStateState::NUMBER_OF_LED_RANGES);

    EXPECT_EQ(group_received_group_number, 1);
    EXPECT_EQ(group_received_number_of_groups_received, 2);
    EXPECT_EQ(group_received_number_of_led_ranges, group_1_number_of_led_ranges);
    EXPECT_TRUE(are_equal(group_received_led_ranges, group_1_led_ranges, group_1_led_ranges_length));

    // Group 2
    uint8 group_2_number_of_led_ranges = 2;
    unsigned int group_2_led_ranges_length = group_2_number_of_led_ranges * GroupSetupState::LEDS_PER_LED_RANGE;
    uint16 group_2_led_ranges[group_2_led_ranges_length] = {0, 10, 10, 20};

    send_led_ranges(group_2_led_ranges, group_2_number_of_led_ranges);
    assert_on_state(GroupSetupStateState::NUMBER_OF_LED_RANGES);

    EXPECT_EQ(group_received_group_number, 2);
    EXPECT_EQ(group_received_number_of_groups_received, 3);
    EXPECT_EQ(group_received_number_of_led_ranges, group_2_number_of_led_ranges);
    EXPECT_TRUE(are_equal(group_received_led_ranges, group_2_led_ranges, group_2_led_ranges_length));

    // Group 3
    uint8 group_3_number_of_led_ranges = 4;
    unsigned int group_3_led_ranges_length = group_3_number_of_led_ranges * GroupSetupState::LEDS_PER_LED_RANGE;
    uint16 group_3_led_ranges[group_3_led_ranges_length] = {0, 10, 10, 20, 50, 60, 60, 70};

    send_led_ranges(group_3_led_ranges, group_3_number_of_led_ranges);
    assert_on_state(GroupSetupStateState::END_OF_MESSAGE);

    EXPECT_EQ(group_received_group_number, 3);
    EXPECT_EQ(group_received_number_of_groups_received, 4);
    EXPECT_EQ(group_received_number_of_led_ranges, group_3_number_of_led_ranges);
    EXPECT_TRUE(are_equal(group_received_led_ranges, group_3_led_ranges, group_3_led_ranges_length));

    assert_on_state(GroupSetupStateState::END_OF_MESSAGE);
    update_state(GroupSetupState::END_OF_MESSAGE_CODE);
    assert_on_state(GroupSetupStateState::END);
}