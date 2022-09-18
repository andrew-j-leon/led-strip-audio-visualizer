#ifndef PACKET_STATE_H
#define PACKET_STATE_H

#include "util.h"

enum class PacketStateState {
    START_OF_MESSAGE,
    NUMBER_OF_PACKETS,
    PACKET,
    CHECK_SUM,
    END_OF_MESSAGE
};

class PacketState {
    public:
        static const uint8 START_OF_MESSAGE_CODE = 0xFE;
        static const uint8 END_OF_MESSAGE_CODE = 0xFF;

    private:
        PacketStateState state;
        uint8* packets;

        unsigned int packets_expected;
        unsigned int packets_remaining;

        unsigned int bytes_per_packet;
        unsigned int packet_bytes_remaining;

    public:
        PacketState();
        PacketState(unsigned int the_bytes_per_packet);
        ~PacketState();
        void update_state(uint8 byte, void (*on_end_of_message)(uint8*, unsigned int));
        PacketStateState get_state();

    private:
        uint8 get_check_sum();
        unsigned int get_packet_number();
};

#endif