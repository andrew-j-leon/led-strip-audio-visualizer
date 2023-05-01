#include "util.h"
#include "group_setup_state.h"

GroupSetupState::GroupSetupState(uint8 number_of_expected_groups) {
    state = GroupSetupStateState::START_OF_MESSAGE;
    band = nullptr;

    groups_received = 0;
    groups_expected = number_of_expected_groups;

    led_ranges_expected = 0;
    led_ranges_received = 0;
}

GroupSetupState::~GroupSetupState() {
    delete[] band;
    band = nullptr;
}

void GroupSetupState::update_state(uint8 byte, void (*on_group_received)(uint16*, uint8, uint8)) {
    if (state == GroupSetupStateState::START_OF_MESSAGE && byte == START_OF_MESSAGE_CODE) {
        state = GroupSetupStateState::NUMBER_OF_LED_RANGES;
    }
    else if (state == GroupSetupStateState::NUMBER_OF_LED_RANGES) {
        led_ranges_expected = byte;
        led_ranges_received = 0;
        delete[] band;

        if (led_ranges_expected > 0) {
            band = new uint16[led_ranges_expected * LEDS_PER_LED_RANGE];
            state = GroupSetupStateState::START_LED_LOWER_BYTE;
        }
        else {
            band = nullptr;
            start_led_lower_byte = 0x00;
            start_led_upper_byte = 0x00;
            end_led_lower_byte = 0x00;
            end_led_upper_byte = 0x00;
            state = GroupSetupStateState::CHECK_SUM;
        }
    }
    else if (state == GroupSetupStateState::START_LED_LOWER_BYTE) {
        start_led_lower_byte = byte;
        state = GroupSetupStateState::START_LED_UPPER_BYTE;
    }
    else if (state == GroupSetupStateState::START_LED_UPPER_BYTE) {
        start_led_upper_byte = byte;
        band[led_ranges_received * LEDS_PER_LED_RANGE] = uint8_to_uint16(start_led_upper_byte, start_led_lower_byte);
        state = GroupSetupStateState::END_LED_LOWER_BYTE;
    }
    else if (state == GroupSetupStateState::END_LED_LOWER_BYTE) {
        end_led_lower_byte = byte;
        state = GroupSetupStateState::END_LED_UPPER_BYTE;
    }
    else if (state == GroupSetupStateState::END_LED_UPPER_BYTE) {
        end_led_upper_byte = byte;
        band[led_ranges_received * LEDS_PER_LED_RANGE + 1] = uint8_to_uint16(end_led_upper_byte, end_led_lower_byte);
        state = GroupSetupStateState::CHECK_SUM;
    }
    else if (state == GroupSetupStateState::CHECK_SUM) {
        if (byte != get_check_sum()) {
            state = GroupSetupStateState::START_OF_MESSAGE;
        }
        else {
            led_ranges_received++;

            if (led_ranges_received < led_ranges_expected) {
                state = GroupSetupStateState::START_LED_LOWER_BYTE;
            }
            else {
                on_group_received(band, led_ranges_expected, groups_received);

                groups_received++;

                if (groups_received < groups_expected) {
                    state = GroupSetupStateState::NUMBER_OF_LED_RANGES;
                }
                else {
                    state = GroupSetupStateState::END_OF_MESSAGE;
                }
            }
        }
    }
    else if (state == GroupSetupStateState::END_OF_MESSAGE && byte == END_OF_MESSAGE_CODE) {
        state = GroupSetupStateState::END;
    }
    else if (state == GroupSetupStateState::END) {
        ;
    }
}

GroupSetupStateState GroupSetupState::get_state() {
    return state;
}

uint8 GroupSetupState::get_check_sum() {
    return (led_ranges_expected + start_led_lower_byte + start_led_upper_byte +
            end_led_lower_byte + end_led_upper_byte);
}