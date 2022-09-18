#include <gtest/gtest.h>
#include "../array.h"

class u16ArrayTest : public ::testing::Test {
    public:
        static const unsigned int length = 10;
        u16Array* array;

        u16ArrayTest() {
            array = new u16Array(length);
        }

        ~u16ArrayTest() {
            delete array;
        }
};

TEST(u16Array_ConstructorTest, DefaultConstructor) {
    u16Array array = u16Array();
    EXPECT_EQ(array.get_length(), 0);
}

TEST(u16Array_ConstructorTest, PresetElements) {
    const unsigned int LENGTH = 5;
    uint16 elements[LENGTH] = {0, 1, 2, 3, 4};
    u16Array array = u16Array(LENGTH, elements);

    for (unsigned int i = 0; i < LENGTH; i++) {
        EXPECT_EQ(elements[i], array.get(i));
    }
}

TEST(u16Array_ConstructorTest, LengthZero) {
    const unsigned int LENGTH = 0;
    u16Array array = u16Array(LENGTH);

    EXPECT_EQ(LENGTH, array.get_length());
}

TEST(u16Array_ConstructorTest, LengthOne) {
    const unsigned int LENGTH = 1;
    u16Array array = u16Array(LENGTH);

    EXPECT_EQ(LENGTH, array.get_length());
}

TEST(u16Array_ConstructorTest, LengthTen) {
    const unsigned int LENGTH = 10;
    u16Array array = u16Array(LENGTH);

    EXPECT_EQ(LENGTH, array.get_length());
}

TEST(u16Array_ConstructorTest, LengthTwoHundredFiftyFive) {
    const unsigned int LENGTH = 255;
    u16Array array = u16Array(LENGTH);

    EXPECT_EQ(LENGTH, array.get_length());
}

TEST_F(u16ArrayTest, SetIndexZero) {
    unsigned int index = 0;
    uint16 element = 10;

    array->set(index, element);

    EXPECT_EQ(element, array->get(index));
}

TEST_F(u16ArrayTest, SetIndexOne) {
    unsigned int index = 1;
    uint16 element = 10;

    array->set(index, element);

    EXPECT_EQ(element, array->get(index));
}

TEST_F(u16ArrayTest, SetPenultimateIndex) {
    unsigned int index = length - 2;
    uint16 element = 10;

    array->set(index, element);

    EXPECT_EQ(element, array->get(index));
}

TEST_F(u16ArrayTest, SetLastIndex) {
    unsigned int index = length - 1;
    uint16 element = 10;

    array->set(index, element);

    EXPECT_EQ(element, array->get(index));
}

TEST_F(u16ArrayTest, SetMultipleIndices) {
    const unsigned int LENGTH = 255;

    u16Array array = u16Array(LENGTH);

    uint16 element = 0;

    for (unsigned int index = 0; index < LENGTH; index++) {
        array.set(index, element);
        EXPECT_EQ(element, array.get(index));
        element++;
    }

    element = 0;

    for (unsigned int index = 0; index < LENGTH; index++) {
        EXPECT_EQ(element, array.get(index));
        element++;
    }
}

TEST(u16ArrayTestEqual, Equal) {
    unsigned int ARRAY_LENGTH = 3;
    uint16 elements[ARRAY_LENGTH] = {1, 2, 3};

    u16Array array_1 = u16Array(ARRAY_LENGTH, elements);
    u16Array array_2 = u16Array(ARRAY_LENGTH, elements);

    EXPECT_TRUE(array_1.is_equal(array_2));
}

TEST(u16ArrayTestEqual, DifferentLengths) {
    unsigned int ARRAY_LENGTH_1 = 2;
    uint16 elements_1[ARRAY_LENGTH_1] = {1, 2};

    unsigned int ARRAY_LENGTH_2 = 3;
    uint16 elements_2[ARRAY_LENGTH_2] = {1, 2, 3};

    u16Array array_1 = u16Array(ARRAY_LENGTH_1, elements_1);
    u16Array array_2 = u16Array(ARRAY_LENGTH_2, elements_2);

    EXPECT_FALSE(array_1.is_equal(array_2));
}

TEST(u16ArrayTestEqual, DifferentElements) {
    unsigned int ARRAY_LENGTH = 3;
    uint16 elements_1[ARRAY_LENGTH] = {1, 2, 3};
    uint16 elements_2[ARRAY_LENGTH] = {1, 2, 4};

    u16Array array_1 = u16Array(ARRAY_LENGTH, elements_1);
    u16Array array_2 = u16Array(ARRAY_LENGTH, elements_2);

    EXPECT_FALSE(array_1.is_equal(array_2));
}

TEST(u16ArrayTestSetLength, IncreaseLength) {
    unsigned int LENGTH = 3;
    uint16 elements[LENGTH] = {1, 2, 3};
    u16Array array = u16Array(LENGTH, elements);

    unsigned int NEW_LENGTH = LENGTH + 1;
    array.set_length(NEW_LENGTH);
    array.set(NEW_LENGTH - 1, 4);

    uint16 new_elements[NEW_LENGTH] = {1, 2, 3, 4};
    u16Array expected_array = u16Array(NEW_LENGTH, new_elements);

    EXPECT_TRUE(array.is_equal(expected_array));
}

TEST(u16ArrayTestSetLength, DecreaseLength) {
    unsigned int LENGTH = 3;
    uint16 elements[LENGTH] = {1, 2, 3};
    u16Array array = u16Array(LENGTH, elements);

    unsigned int NEW_LENGTH = LENGTH - 1;
    array.set_length(NEW_LENGTH);

    uint16 new_elements[NEW_LENGTH] = {1, 2};
    u16Array expected_array = u16Array(NEW_LENGTH, new_elements);

    EXPECT_TRUE(array.is_equal(expected_array));
}

TEST(u16ArrayTestSetLength, SameLength) {
    unsigned int LENGTH = 3;
    uint16 elements[LENGTH] = {1, 2, 3};
    u16Array array = u16Array(LENGTH, elements);

    array.set_length(LENGTH);

    u16Array expected_array = u16Array(LENGTH, elements);

    EXPECT_TRUE(array.is_equal(expected_array));
}