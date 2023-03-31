#include <Arduino.h>
// #include <CDC.h> // Some systems need to include this header
#include <FastLED_NeoPixel.h>
#include "packet_state.h"
#include "group_setup_state.h"
#include "array.h"

#define SERIAL_BAUD_RATE 1000000
#define NUMBER_OF_LEDS 125
#define PIN_NUMBER 6
#define BYTES_PER_PACKET 4

u16Array* groups;

// FastLED_NeoPixel<NUMBER_OF_LEDS, PIN_NUMBER, NEO_GRB> led_strip; // Neopixel Strip
FastLED_NeoPixel<NUMBER_OF_LEDS, PIN_NUMBER, NEO_RGB> led_strip; // PL9823

PacketState packet_state = PacketState(BYTES_PER_PACKET);
GroupSetupState* group_setup_state = nullptr;


void setup() {
    Serial.begin(SERIAL_BAUD_RATE, SERIAL_8N1);

    if (!Serial) { // For Arduino Wifi-Rev2

    }

    int number_of_bytes_received = Serial.available();

    while (!(number_of_bytes_received == 1 && Serial.read() == 0x00)) {
        number_of_bytes_received = Serial.available();
    }

    const uint8 LOW_ORDER_BYTE = (uint8)NUMBER_OF_LEDS;
    const uint8 HIGH_ORDER_BYTE = ((uint16)NUMBER_OF_LEDS >> 8);

    Serial.write(LOW_ORDER_BYTE);
    Serial.write(HIGH_ORDER_BYTE);

    const uint8 brightness = read_serial();
    led_strip.setBrightness(brightness);

    led_strip.begin();
    led_strip.show();

    uint8 number_of_groups = read_serial();

    if (number_of_groups > 0) {
        group_setup_state = new GroupSetupState(number_of_groups);
        groups = new u16Array[number_of_groups];

        while (group_setup_state->get_state() != GroupSetupStateState::END) {
            group_setup_state->update_state(read_serial(), on_group_received);
        }
    }
    else {
        while(1);
    }
}

void loop() {
    if (Serial.available()) {
        uint8 serial_byte = read_serial();
        packet_state.update_state(serial_byte, on_end_of_message);
    }
}

void on_end_of_message(uint8* packets, unsigned int number_of_packets) {
    for (unsigned int packet_number = 0; packet_number < number_of_packets; packet_number++) {
        unsigned int packet_start = packet_number * BYTES_PER_PACKET;

        uint8 group_number = packets[packet_start];
        u16Array* group = &groups[group_number];

        uint32_t rgb = led_strip.Color(packets[packet_start+1], packets[packet_start+2], packets[packet_start+3]);

        for (unsigned int i = 0; i < group->get_length(); i += 2) {
            uint16 start_led = group->get(i);
            uint16 end_led= group->get(i + 1);

            for (uint16 led = start_led; led < end_led; led++) {
                led_strip.setPixelColor(led, rgb);
            }
        }
    }

    led_strip.show();
}


void on_group_received(uint16* led_ranges, uint8 number_of_led_ranges, uint8 group_number) {
    unsigned int led_ranges_length = number_of_led_ranges * GroupSetupState::LEDS_PER_LED_RANGE;
    groups[group_number].set_length(led_ranges_length);

    for (unsigned int i = 0; i < led_ranges_length; i++) {
        groups[group_number].set(i, led_ranges[i]);
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