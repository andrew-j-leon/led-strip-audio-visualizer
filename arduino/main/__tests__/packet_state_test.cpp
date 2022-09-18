#include <gtest/gtest.h>
#include "../packet_state.h"

bool on_EOM_was_called = false;
uint8* EOM_packets = nullptr;
unsigned int EOM_number_of_packets = 0;

void on_end_of_message(uint8* packets, unsigned int number_of_packets) {
    on_EOM_was_called = true;
    EOM_packets = packets;
    EOM_number_of_packets = number_of_packets;
}

bool are_equal(uint8 array_1[], uint8 array_2[], unsigned int size) {
    if (array_1 == nullptr || array_2 == nullptr) {
        return (array_1 == nullptr && array_2 == nullptr);
    }

    for (unsigned long i = 0; i < size; i++) {
        if (array_1[i] != array_2[i]) {
            return false;
        }
    }

    return true;
}

uint8 get_checksum(uint8 bytes[], unsigned int start, unsigned int end) {
    uint8 sum = 0;

    for (unsigned int i = start; i < end; i++) {
        sum += bytes[i];
    }

    return sum;
}

class PacketStateTest : public ::testing::Test {
    public:
        unsigned int bytes_per_packet;
        PacketState packet_state;

        PacketStateTest() {
            bytes_per_packet = 4;
            packet_state = PacketState(bytes_per_packet);

            on_EOM_was_called = false;
            EOM_packets = nullptr;
            EOM_number_of_packets = 0;
        }

    protected:
        void go_to_packet_state(uint8 number_of_packets) {
            ASSERT_EQ(packet_state.get_state(), PacketStateState::START_OF_MESSAGE);
            update_state(PacketState::START_OF_MESSAGE_CODE);

            ASSERT_EQ(packet_state.get_state(), PacketStateState::NUMBER_OF_PACKETS);
            update_state(number_of_packets);
        }

        void update_state(uint8 byte) {
            packet_state.update_state(byte, on_end_of_message);
        }

        void test_packets(uint8 packets[], unsigned int number_of_packets) {
            if (number_of_packets > 0) {
                unsigned int start = 0;
                unsigned int end = bytes_per_packet;

                unsigned int packet_number = 0;

                while (packet_number < number_of_packets - 1) {
                    test_packet(packets, start, end);
                    update_state(get_checksum(packets, start, end));
                    ASSERT_EQ(packet_state.get_state(), PacketStateState::PACKET);

                    packet_number++;
                    start += bytes_per_packet;
                    end += bytes_per_packet;
                }

                test_packet(packets, start, end);
                update_state(get_checksum(packets, start, end));
                ASSERT_EQ(packet_state.get_state(), PacketStateState::END_OF_MESSAGE);
            }
        }

        void send_packets(uint8 packets[], unsigned int number_of_packets) {
            if (number_of_packets > 0) {
                unsigned int start = 0;
                unsigned int end = bytes_per_packet;

                unsigned int packet_number = 0;

                while (packet_number < number_of_packets - 1) {
                    send_packet(packets, start, end);
                    update_state(get_checksum(packets, start, end));

                    packet_number++;
                    start += bytes_per_packet;
                    end += bytes_per_packet;
                }

                send_packet(packets, start, end);
                update_state(get_checksum(packets, start, end));
            }
        }

        void test_checksum_failure(uint8 packets[], unsigned int number_of_packets, unsigned int failing_packet_number) {
            ASSERT_LT(failing_packet_number, number_of_packets);

            if (number_of_packets > 0) {
                unsigned int start = 0;
                unsigned int end = bytes_per_packet;

                unsigned int packet_number = 0;

                while (packet_number < failing_packet_number) {
                    test_packet(packets, start, end);
                    update_state(get_checksum(packets, start, end));
                    ASSERT_EQ(packet_state.get_state(), PacketStateState::PACKET);

                    packet_number++;
                    start += bytes_per_packet;
                    end += bytes_per_packet;
                }

                test_packet(packets, start, end);
                update_state(get_checksum(packets, start, end) + 0x01);
                ASSERT_EQ(packet_state.get_state(), PacketStateState::START_OF_MESSAGE);
            }
        }

        void test_end_state(uint8 packets[], unsigned int number_of_packets) {
            update_state(PacketState::END_OF_MESSAGE_CODE);

            EXPECT_TRUE(on_EOM_was_called);

            const unsigned int SIZE = number_of_packets * bytes_per_packet;
            EXPECT_TRUE(are_equal(packets, EOM_packets, SIZE));

            EXPECT_EQ(EOM_number_of_packets, number_of_packets);

            EXPECT_EQ(packet_state.get_state(), PacketStateState::START_OF_MESSAGE);
        }

        void test_packet(uint8 packets[], unsigned int start, unsigned int end) {
            send_packet(packets, start, end);
            ASSERT_EQ(packet_state.get_state(), PacketStateState::CHECK_SUM);
        }

        void send_packet(uint8 packets[], unsigned int start, unsigned int end) {
            for (unsigned int i = start; i < end; i++) {
                update_state(packets[i]);
            }
        }
};

TEST_F(PacketStateTest, StartOfMessage_to_StartOfMessage) {
    const uint8 INVALID_START_OF_MESSAGE_CODE = PacketState::START_OF_MESSAGE_CODE + 0x01;

    update_state(INVALID_START_OF_MESSAGE_CODE);

    EXPECT_EQ(packet_state.get_state(), PacketStateState::START_OF_MESSAGE);
    EXPECT_FALSE(on_EOM_was_called);
}

TEST_F(PacketStateTest, StartOfMessage_to_NumberOfPackets) {
    update_state(PacketState::START_OF_MESSAGE_CODE);

    EXPECT_EQ(packet_state.get_state(), PacketStateState::NUMBER_OF_PACKETS);
    EXPECT_FALSE(on_EOM_was_called);
}

TEST_F(PacketStateTest, NumberOfPackets_to_Packet) {
    update_state(PacketState::START_OF_MESSAGE_CODE);

    const uint8 NUMBER_OF_PACKETS = 0x01;
    update_state(NUMBER_OF_PACKETS);

    EXPECT_EQ(packet_state.get_state(), PacketStateState::PACKET);
    EXPECT_FALSE(on_EOM_was_called);
}

TEST_F(PacketStateTest, NumberOfPackets_to_EndOfMessage) {
    update_state(PacketState::START_OF_MESSAGE_CODE);

    const uint8 NUMBER_OF_PACKETS = 0x00;
    update_state(NUMBER_OF_PACKETS);

    EXPECT_EQ(packet_state.get_state(), PacketStateState::END_OF_MESSAGE);
    EXPECT_FALSE(on_EOM_was_called);
}

TEST_F(PacketStateTest, EndOfMessage_to_StartOfMessage) {
    update_state(PacketState::START_OF_MESSAGE_CODE);

    const uint8 NUMBER_OF_PACKETS = 0x00;
    update_state(NUMBER_OF_PACKETS);
    update_state(PacketState::END_OF_MESSAGE_CODE);

    EXPECT_EQ(packet_state.get_state(), PacketStateState::START_OF_MESSAGE);
    EXPECT_TRUE(on_EOM_was_called);
}

TEST_F(PacketStateTest, OnePacket) {
    uint8 NUMBER_OF_PACKETS = 1;
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets[] = {0x00, 0x10, 0x20, 0x30};

    ASSERT_EQ(sizeof(packets), bytes_per_packet * NUMBER_OF_PACKETS);

    test_packets(packets, NUMBER_OF_PACKETS);
    test_end_state(packets, NUMBER_OF_PACKETS);
}

TEST_F(PacketStateTest, ThreePackets) {
    uint8 NUMBER_OF_PACKETS = 3;
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets[] = {0x00, 0x10, 0x20, 0x30,
                       0x01, 0x11, 0x21, 0x31,
                       0x02, 0x12, 0x22, 0x32};

    ASSERT_EQ(sizeof(packets), bytes_per_packet * NUMBER_OF_PACKETS);

    test_packets(packets, NUMBER_OF_PACKETS);
    test_end_state(packets, NUMBER_OF_PACKETS);
}

TEST_F(PacketStateTest, FirstPacketCheckSumFailed) {
    uint8 NUMBER_OF_PACKETS = 3;
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets[] = {0x00, 0x10, 0x20, 0x30,
                       0x01, 0x11, 0x21, 0x31,
                       0x02, 0x12, 0x22, 0x32};

    ASSERT_EQ(sizeof(packets), bytes_per_packet * NUMBER_OF_PACKETS);

    unsigned int failing_packet_number = 0;
    test_checksum_failure(packets, NUMBER_OF_PACKETS, failing_packet_number);
}

TEST_F(PacketStateTest, SecondPacketCheckSumFailed) {
    uint8 NUMBER_OF_PACKETS = 3;
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets[] = {0x00, 0x10, 0x20, 0x30,
                       0x01, 0x11, 0x21, 0x31,
                       0x02, 0x12, 0x22, 0x32};

    ASSERT_EQ(sizeof(packets), bytes_per_packet * NUMBER_OF_PACKETS);

    unsigned int failing_packet_number = 1;
    test_checksum_failure(packets, NUMBER_OF_PACKETS, failing_packet_number);
}

TEST_F(PacketStateTest, LastPacketCheckSumFailed) {
    uint8 NUMBER_OF_PACKETS = 3;
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets[] = {0x00, 0x10, 0x20, 0x30,
                       0x01, 0x11, 0x21, 0x31,
                       0x02, 0x12, 0x22, 0x32};

    ASSERT_EQ(sizeof(packets), bytes_per_packet * NUMBER_OF_PACKETS);

    unsigned int failing_packet_number = 2;
    test_checksum_failure(packets, NUMBER_OF_PACKETS, failing_packet_number);
}

TEST_F(PacketStateTest, InvalidEndOfMessageCode) {
    uint8 NUMBER_OF_PACKETS = 1;
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets[] = {0x00, 0x10, 0x20, 0x30};

    ASSERT_EQ(sizeof(packets), bytes_per_packet * NUMBER_OF_PACKETS);

    test_packets(packets, NUMBER_OF_PACKETS);

    update_state(PacketState::START_OF_MESSAGE_CODE);
    EXPECT_FALSE(on_EOM_was_called);
    EXPECT_EQ(packet_state.get_state(), PacketStateState::END_OF_MESSAGE);
}

TEST_F(PacketStateTest, TwoCompleteStateTransitions) {
    // Transition 1
    uint8 NUMBER_OF_PACKETS = 3;
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets[] = {0x00, 0x10, 0x20, 0x30,
                       0x01, 0x11, 0x21, 0x31,
                       0x02, 0x12, 0x22, 0x32};

    ASSERT_EQ(sizeof(packets), bytes_per_packet * NUMBER_OF_PACKETS);

    test_packets(packets, NUMBER_OF_PACKETS);
    test_end_state(packets, NUMBER_OF_PACKETS);

    // Transition 2
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets_2[] = {0x02, 0x20, 0x30, 0x40,
                         0x01, 0x21, 0x31, 0x41,
                         0x02, 0x22, 0x32, 0x42};

    ASSERT_EQ(sizeof(packets_2), bytes_per_packet * NUMBER_OF_PACKETS);

    test_packets(packets_2, NUMBER_OF_PACKETS);
    test_end_state(packets_2, NUMBER_OF_PACKETS);
}

TEST_F(PacketStateTest, TwoCompleteStateTransitions_IncorrectStartOfMessageCodeOnFirst) {
    // Transition 1
    uint8 NUMBER_OF_PACKETS = 3;
    ASSERT_EQ(packet_state.get_state(), PacketStateState::START_OF_MESSAGE);
    update_state(PacketState::START_OF_MESSAGE_CODE + 0x01);
    ASSERT_EQ(packet_state.get_state(), PacketStateState::START_OF_MESSAGE);

    uint8 packets[] = {0x00, 0x10, 0x20, 0x30,
                       0x01, 0x11, 0x21, 0x31,
                       0x02, 0x12, 0x22, 0x32};

    ASSERT_EQ(sizeof(packets), bytes_per_packet * NUMBER_OF_PACKETS);

    send_packets(packets, NUMBER_OF_PACKETS);
    update_state(PacketState::END_OF_MESSAGE_CODE);

    // Transition 2
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets_2[] = {0x02, 0x20, 0x30, 0x40,
                         0x01, 0x21, 0x31, 0x41,
                         0x02, 0x22, 0x32, 0x42};

    ASSERT_EQ(sizeof(packets_2), bytes_per_packet * NUMBER_OF_PACKETS);

    test_packets(packets_2, NUMBER_OF_PACKETS);
    test_end_state(packets_2, NUMBER_OF_PACKETS);
}

TEST_F(PacketStateTest, TwoCompleteStateTransitions_CheckSumFailureOnFirst) {
    // Transition 1
    uint8 NUMBER_OF_PACKETS = 3;
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets[] = {0x00, 0x10, 0x20, 0x30,
                       0x01, 0x11, 0x21, 0x31,
                       0x02, 0x12, 0x22, 0x32};

    ASSERT_EQ(sizeof(packets), bytes_per_packet * NUMBER_OF_PACKETS);

    unsigned int failing_packet_number = 1;
    test_checksum_failure(packets, NUMBER_OF_PACKETS, failing_packet_number);

    const unsigned int START = (NUMBER_OF_PACKETS - 1)*bytes_per_packet;
    const unsigned int END = START + bytes_per_packet;
    send_packet(packets, START, END);

    update_state(PacketState::END_OF_MESSAGE_CODE);

    // Transition 2
    go_to_packet_state(NUMBER_OF_PACKETS);

    uint8 packets_2[] = {0x02, 0x20, 0x30, 0x40,
                         0x01, 0x21, 0x31, 0x41,
                         0x02, 0x22, 0x32, 0x42};

    ASSERT_EQ(sizeof(packets_2), bytes_per_packet * NUMBER_OF_PACKETS);

    test_packets(packets_2, NUMBER_OF_PACKETS);
    test_end_state(packets_2, NUMBER_OF_PACKETS);
}

TEST_F(PacketStateTest, TwoCompleteStateTransitions_ZeroPacketsOnFirst) {
    // Transition 1
    uint8 number_of_packets = 0;
    go_to_packet_state(number_of_packets);

    uint8 packets[0];

    ASSERT_EQ(sizeof(packets), bytes_per_packet * number_of_packets);

    send_packets(packets, number_of_packets);
    update_state(PacketState::END_OF_MESSAGE_CODE);

    // Transition 2
    number_of_packets = 3;
    go_to_packet_state(number_of_packets);

    uint8 packets_2[] = {0x02, 0x20, 0x30, 0x40,
                         0x01, 0x21, 0x31, 0x41,
                         0x02, 0x22, 0x32, 0x42};

    ASSERT_EQ(sizeof(packets_2), bytes_per_packet * number_of_packets);

    test_packets(packets_2, number_of_packets);
    test_end_state(packets_2, number_of_packets);
}