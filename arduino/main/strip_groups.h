#ifndef STRIP_GROUPS_H
#define STRIP_GROUPS_H

#include "util.h"

class StripGroups {
    private:
        uint8 number_of_groups;
        uint16* groups;

    public:
        StripGroups(uint8 the_number_of_groups);
        ~StripGroups();

        uint8 get_number_of_groups();
        uint16 get_start_led(uint8 group_number);
        uint16 get_end_led(uint8 group_number);

        void set_group(uint8 group_number, uint16 start_led, uint16 end_led);
};


#endif