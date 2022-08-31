#ifndef PACKET_STATE_H
#define PACKET_STATE_H

#include "util.h"

const uint8 START_OF_MESSAGE_CODE = 0xFE;
const uint8 END_OF_MESSAGE_CODE = 0xFF;

enum State {
    START_OF_MESSAGE_STATE,
    NUMBER_OF_PACKETS_STATE,
    PACKET_STATE,
    CHECK_SUM_STATE,
    END_OF_MESSAGE_STATE
};

class PacketState {
    private:
        int state;
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
        int get_state();

    private:
        uint8 get_check_sum();
        unsigned int get_packet_number();
};

#endif