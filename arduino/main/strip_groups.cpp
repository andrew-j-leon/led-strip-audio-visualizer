#include "strip_groups.h"

#define START(group_number) (group_number*2)
#define END(group_number) (group_number*2 + 1)

StripGroups::StripGroups(uint8 the_number_of_groups) {
    number_of_groups = the_number_of_groups;
    groups = new uint16[number_of_groups * 2];
}

StripGroups::~StripGroups() {
    delete[] groups;
}

uint8 StripGroups::get_number_of_groups() {
    return number_of_groups;
}

uint16 StripGroups::get_start_led(uint8 group_number) {
    return groups[START(group_number)];
}

uint16 StripGroups::get_end_led(uint8 group_number) {
    return groups[END(group_number)];
}

void StripGroups::set_group(uint8 group_number, uint16 start_led, uint16 end_led) {
    groups[START(group_number)] = start_led;
    groups[END(group_number)] = end_led;
}
