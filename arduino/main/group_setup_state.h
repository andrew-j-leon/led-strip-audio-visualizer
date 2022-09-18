#ifndef GROUP_SETUP_STATE_H
#define GROUP_SETUP_STATE_H

#include "util.h"
#include "array.h"

enum class GroupSetupStateState {
    START_OF_MESSAGE,
    NUMBER_OF_LED_RANGES,
    START_LED_LOWER_BYTE,
    START_LED_UPPER_BYTE,
    END_LED_LOWER_BYTE,
    END_LED_UPPER_BYTE,
    CHECK_SUM,
    END_OF_MESSAGE,
    END
};

class GroupSetupState {
    public:
        static const uint8 START_OF_MESSAGE_CODE = 0xFE;
        static const uint8 END_OF_MESSAGE_CODE = 0xFF;
        static const int LEDS_PER_LED_RANGE = 2;

    private:
        GroupSetupStateState state;
        uint16* group;

        uint8 groups_expected;
        uint8 groups_received;

        uint8 led_ranges_expected;
        uint8 led_ranges_received;

        uint8 start_led_lower_byte;
        uint8 start_led_upper_byte;

        uint8 end_led_lower_byte;
        uint8 end_led_upper_byte;

    public:
        GroupSetupState(uint8 number_of_expected_groups);
        ~GroupSetupState();

        void update_state(uint8 byte, void (*on_group_received)(uint16*, uint8, uint8));
        GroupSetupStateState get_state();

    private:
        uint8 get_check_sum();
};


#endif