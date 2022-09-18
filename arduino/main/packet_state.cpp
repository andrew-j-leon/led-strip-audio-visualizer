#include "packet_state.h"

PacketState::PacketState() {
    state = PacketStateState::START_OF_MESSAGE;
    packets = nullptr;
    packets_remaining = 0;
    packet_bytes_remaining = 0;
    bytes_per_packet = 0;
}

PacketState::PacketState(unsigned int the_bytes_per_packet) {
    bytes_per_packet = the_bytes_per_packet;
    packet_bytes_remaining = 0;
    state = PacketStateState::START_OF_MESSAGE;
    packets = nullptr;
    packets_remaining = 0;
}

PacketState::~PacketState() {
    delete[] packets;
}

void PacketState::update_state(uint8 byte, void (*on_end_of_message)(uint8*, unsigned int)) {
    if (state == PacketStateState::START_OF_MESSAGE && byte == START_OF_MESSAGE_CODE) {
        state = PacketStateState::NUMBER_OF_PACKETS;
    } else if (state == PacketStateState::NUMBER_OF_PACKETS) {
        packets_expected = packets_remaining = byte;
        packet_bytes_remaining = bytes_per_packet;
        state = (packets_expected > 0x00) ? PacketStateState::PACKET : PacketStateState::END_OF_MESSAGE;

        delete[] packets;
        packets = new uint8[packets_expected * bytes_per_packet];
    } else if (state == PacketStateState::PACKET) {
        const unsigned int PACKET_INDEX = bytes_per_packet - packet_bytes_remaining;
        packets[(get_packet_number() * bytes_per_packet) + PACKET_INDEX] = byte;

        packet_bytes_remaining--;

        if (packet_bytes_remaining == 0) {
            packet_bytes_remaining = bytes_per_packet;
            state = PacketStateState::CHECK_SUM;
        }
    } else if (state == PacketStateState::CHECK_SUM) {
        if (byte != get_check_sum()) {
            state = PacketStateState::START_OF_MESSAGE;
        } else {
            packets_remaining--;

            state = (packets_remaining == 0) ? PacketStateState::END_OF_MESSAGE : PacketStateState::PACKET;
        }
    } else if (state == PacketStateState::END_OF_MESSAGE) {
        if (byte == END_OF_MESSAGE_CODE) {
            on_end_of_message(packets, packets_expected);
            state = PacketStateState::START_OF_MESSAGE;
        }
    }
}

uint8 PacketState::get_check_sum() {
    uint8 sum = 0;

    const unsigned int START_INDEX = get_packet_number() * bytes_per_packet;
    const unsigned int END_INDEX = START_INDEX + bytes_per_packet;

    for (unsigned int i = START_INDEX; i < END_INDEX; i++) {
        sum += packets[i];
    }

    return sum;
}

unsigned int PacketState::get_packet_number() {
    return packets_expected - packets_remaining;
}

PacketStateState PacketState::get_state() {
    return state;
}