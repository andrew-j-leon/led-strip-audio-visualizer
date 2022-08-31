#include <Arduino.h>
#include <CDC.h>
#include <FastLED_NeoPixel.h>
#include "packet_state.h"
#include "strip_groups.h"

#define SERIAL_BAUD_RATE 1000000
#define NUMBER_OF_LEDS 600
#define PIN_NUMBER 6
#define BYTES_PER_PACKET 4

StripGroups* strip_groups;
uint8* packets;

FastLED_NeoPixel<NUMBER_OF_LEDS, PIN_NUMBER, NEO_GRB> led_strip;
PacketState packet_state = PacketState(BYTES_PER_PACKET);


void setup() {
    Serial.begin(SERIAL_BAUD_RATE, SERIAL_8N1);
    while (!Serial) {
        ;
    }

    const uint8 LOW_ORDER_BYTE = (uint8)NUMBER_OF_LEDS;
    const uint8 HIGH_ORDER_BYTE = ( (uint16_t)NUMBER_OF_LEDS >> 8 );
    Serial.write(LOW_ORDER_BYTE);
    Serial.write(HIGH_ORDER_BYTE);

    const uint8 brightness = read_serial();
    led_strip.setBrightness(brightness);

    led_strip.begin();
    led_strip.show();

    setup_group_indices_to_led_ranges();
}


void loop() {
    if (Serial.available()) {
        uint8 serial_byte = read_serial();
        packet_state.update_state(serial_byte, on_end_of_message);
    }
}

void on_end_of_message(uint8* packets, unsigned int number_of_packets) {
    for (unsigned int packet_number = 0; packet_number < number_of_packets; packet_number++) {
        unsigned int packet_start = packet_number*BYTES_PER_PACKET;

        uint8 group = packets[packet_start];
        uint16 start_led = strip_groups->get_start_led(group);
        uint16 end_led = strip_groups->get_end_led(group);

        uint32_t rgb = led_strip.Color(packets[packet_start+1], packets[packet_start+2], packets[packet_start+3]);

        for (uint16 led = start_led; led < end_led; led++) {
            led_strip.setPixelColor(led, rgb);
        }
    }

    led_strip.show();
}


void setup_group_indices_to_led_ranges() {
    uint8 number_of_groups = read_serial();
    strip_groups = new StripGroups(number_of_groups);

    for (uint8 group_number = 0; group_number < strip_groups->get_number_of_groups(); group_number++) {
        uint8 start_led_high_order_byte = read_serial();
        uint8 start_led_low_order_byte = read_serial();

        uint8 end_led_high_order_byte = read_serial();
        uint8 end_led_low_order_byte = read_serial();

        uint16 start_led = uint8_to_uint16(start_led_high_order_byte, start_led_low_order_byte);
        uint16 end_led = uint8_to_uint16(end_led_high_order_byte, end_led_low_order_byte);

        strip_groups->set_group(group_number, start_led, end_led);
    }
}

/**
 * Reads (then echos back) the next available byte from the serial connection.
 *
 * @return uint8 The byte that was read from the serial connection.
 */
uint8 read_serial() {
    while (!Serial.available()) {
        ;
    }

    uint8 byte_ = Serial.read();
    Serial.write(byte_);
    return byte_;
}


uint16_t uint8_to_uint16(uint8 high_order_byte, uint8 low_order_byte) {
    return (uint16_t)(high_order_byte << 8 | low_order_byte);
}