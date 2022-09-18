#ifndef ARRAY_H
#define ARRAY_H

#include "util.h"

class u16Array {
    private:
        unsigned int length;
        uint16* array;

    public:
        u16Array();
        u16Array(unsigned int the_length);
        u16Array(unsigned int the_length, uint16 elements[]);
        ~u16Array();

        unsigned int get_length();
        uint16 get(unsigned int index);
        void set(unsigned int index, uint16 element);
        void set_length(unsigned int new_length);

        bool is_equal(u16Array& other);
};

#endif