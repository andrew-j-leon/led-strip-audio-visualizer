#include <gtest/gtest.h>
#include "../strip_groups.h"

class StripGroupsTest : public ::testing::Test {
    public:
        static const uint8 number_of_groups = 10;
        StripGroups* strip_groups;

        StripGroupsTest() {
            strip_groups = new StripGroups(number_of_groups);
        }

        ~StripGroupsTest() {
            delete strip_groups;
        }
};

TEST(StripGroups_ConstructorTest, ZeroGroups) {
    const uint8 NUMBER_OF_GROUPS = 0;
    StripGroups strip_groups = StripGroups(NUMBER_OF_GROUPS);

    EXPECT_EQ(NUMBER_OF_GROUPS, strip_groups.get_number_of_groups());
}

TEST(StripGroups_ConstructorTest, OneGroup) {
    const uint8 NUMBER_OF_GROUPS = 1;
    StripGroups strip_groups = StripGroups(NUMBER_OF_GROUPS);

    EXPECT_EQ(NUMBER_OF_GROUPS, strip_groups.get_number_of_groups());
}

TEST(StripGroups_ConstructorTest, TenGroups) {
    const uint8 NUMBER_OF_GROUPS = 10;
    StripGroups strip_groups = StripGroups(NUMBER_OF_GROUPS);

    EXPECT_EQ(NUMBER_OF_GROUPS, strip_groups.get_number_of_groups());
}

TEST(StripGroups_ConstructorTest, TwoHundredFiftyFiveGroups) {
    const uint8 NUMBER_OF_GROUPS = 255;
    StripGroups strip_groups = StripGroups(NUMBER_OF_GROUPS);

    EXPECT_EQ(NUMBER_OF_GROUPS, strip_groups.get_number_of_groups());
}

TEST_F(StripGroupsTest, SetFirstGroup) {
    uint8 group = 0;
    uint16 start_led = 0;
    uint16 end_led = 5;

    strip_groups->set_group(group, start_led, end_led);

    EXPECT_EQ(start_led, strip_groups->get_start_led(group));
    EXPECT_EQ(end_led, strip_groups->get_end_led(group));
}

TEST_F(StripGroupsTest, SetSecondGroup) {
    uint8 group = 1;
    uint16 start_led = 0;
    uint16 end_led = 5;

    strip_groups->set_group(group, start_led, end_led);

    EXPECT_EQ(start_led, strip_groups->get_start_led(group));
    EXPECT_EQ(end_led, strip_groups->get_end_led(group));
}

TEST_F(StripGroupsTest, SetPenultimateGroup) {
    uint8 group = number_of_groups - 2;
    uint16 start_led = 0;
    uint16 end_led = 5;

    strip_groups->set_group(group, start_led, end_led);

    EXPECT_EQ(start_led, strip_groups->get_start_led(group));
    EXPECT_EQ(end_led, strip_groups->get_end_led(group));
}

TEST_F(StripGroupsTest, SetLastGroup) {
    uint8 group = number_of_groups - 1;
    uint16 start_led = 0;
    uint16 end_led = 5;

    strip_groups->set_group(group, start_led, end_led);

    EXPECT_EQ(start_led, strip_groups->get_start_led(group));
    EXPECT_EQ(end_led, strip_groups->get_end_led(group));
}

TEST_F(StripGroupsTest, SetMultipleGroups) {
    const uint8 NUMBER_OF_GROUPS = 255;

    StripGroups strip_groups = StripGroups(NUMBER_OF_GROUPS);

    uint16 start_led = 0;
    uint16 end_led = 1;

    for (uint8 group = 0; group < NUMBER_OF_GROUPS; group++) {
        strip_groups.set_group(group, start_led, end_led);

        EXPECT_EQ(start_led, strip_groups.get_start_led(group));
        EXPECT_EQ(end_led, strip_groups.get_end_led(group));

        start_led++;
        end_led++;
    }

    // Check after all groups have been set
    start_led = 0;
    end_led = 1;

    for (uint8 group = 0; group < NUMBER_OF_GROUPS; group++) {
        EXPECT_EQ(start_led, strip_groups.get_start_led(group));
        EXPECT_EQ(end_led, strip_groups.get_end_led(group));

        start_led++;
        end_led++;
    }
}