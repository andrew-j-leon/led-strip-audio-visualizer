#include "array.h"

u16Array::u16Array() {
    length = 0;
    array = nullptr;
}

u16Array::u16Array(unsigned int the_length) {
    length = the_length;
    array = new uint16[the_length];
}

u16Array::u16Array(unsigned int the_length, uint16 elements[]) {
    length = the_length;
    array = new uint16[the_length];

    for (unsigned int i = 0; i < length; i++) {
        set(i, elements[i]);
    }
}

u16Array::~u16Array() {
    delete[] array;
    array = nullptr;
}

unsigned int u16Array::get_length() {
    return length;
}

uint16 u16Array::get(unsigned int index) {
    return array[index];
}

void u16Array::set(unsigned int index, uint16 element) {
    array[index] = element;
}

bool u16Array::is_equal(u16Array& other) {
    if (get_length() == other.get_length()) {
        for (unsigned int i = 0; i < get_length(); i++) {
            if (get(i) != other.get(i)) {
                return false;
            }
        }

        return true;
    }

    return false;
}

void u16Array::set_length(unsigned int new_length) {
    unsigned int min_length = (new_length < length) ? new_length : length;

    uint16* new_array = new uint16[new_length];

    for (unsigned int i = 0; i < min_length; i++) {
        new_array[i] = array[i];
    }

    delete[] array;
    array = new_array;
    length = new_length;
}