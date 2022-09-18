#include "util.h"

uint16 uint8_to_uint16(uint8 high_order_byte, uint8 low_order_byte) {
    return (uint16)(high_order_byte << 8 | low_order_byte);
}