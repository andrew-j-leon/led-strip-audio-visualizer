#include <Arduino.h>
#include <CDC.h>
#include <FastLED_NeoPixel.h>
#include "matrix.h"

#define SERIAL_BAUD_RATE 1000000
#define NUMBER_OF_LEDS 600
#define PIN_NUMBER 6
#define BYTES_PER_PACKET 4

Matrix_uint16* group_index_to_led_range = nullptr;
uint8_t* packet = nullptr;

bool is_a_new_strip_state;
int packet_index;

uint8_t packets_expected_this_strip_state;
uint8_t packets_received_this_strip_state;

FastLED_NeoPixel<NUMBER_OF_LEDS, PIN_NUMBER, NEO_GRB> led_strip;


void setup() {
  Serial.begin(SERIAL_BAUD_RATE, SERIAL_8N1);
  while (!Serial) {
    ;
  }

  const uint8_t LOW_ORDER_BYTE = (uint8_t)NUMBER_OF_LEDS;
  const uint8_t HIGH_ORDER_BYTE = ( (uint16_t)NUMBER_OF_LEDS >> 8 );
  Serial.write(LOW_ORDER_BYTE);
  Serial.write(HIGH_ORDER_BYTE);

  is_a_new_strip_state = true;
  packet_index = 0;

  const uint8_t brightness = read_serial();
  led_strip.setBrightness(brightness);

  led_strip.begin();
  led_strip.show();

  packet = new uint8_t[BYTES_PER_PACKET];
  setup_group_indices_to_led_ranges();
}

void setup_group_indices_to_led_ranges() {
  uint8_t number_of_groups = read_serial();
  group_index_to_led_range = new Matrix_uint16(number_of_groups, 2);

  const int COLUMN_0 = 0;
  const int COLUMN_1 = 1;

  for (int row_index = 0; row_index < group_index_to_led_range->get_number_of_rows(); row_index++) {
    uint8_t start_index_high_order_byte = read_serial();
    uint8_t start_index_low_order_byte = read_serial();

    uint8_t end_index_high_order_byte = read_serial();
    uint8_t end_index_low_order_byte = read_serial();

    group_index_to_led_range->set(row_index, COLUMN_0, uint8_to_uint16(start_index_high_order_byte, start_index_low_order_byte));
    group_index_to_led_range->set(row_index, COLUMN_1, uint8_to_uint16(end_index_high_order_byte, end_index_low_order_byte));
  }
}

/**
 * Reads (then echos back) the next available byte from the serial connection.
 *
 * @return uint8_t The byte that was read from the serial connection.
 */
uint8_t read_serial() {
  while (!Serial.available()) {
    ;
  }
  uint8_t byte_ = Serial.read();
  Serial.write(byte_);
  return byte_;
}

uint16_t uint8_to_uint16(uint8_t high_order_byte, uint8_t low_order_byte) {
  return (uint16_t)(high_order_byte << 8 | low_order_byte);
}

void loop() {
  if (Serial.available()) {
    uint8_t serial_byte = read_serial();

    if (is_a_new_strip_state) {
      packets_expected_this_strip_state = serial_byte;
      packets_received_this_strip_state = 0;

      if (packets_expected_this_strip_state > 0) {
        is_a_new_strip_state = false;
      }
    }

    else {
      if (packet_index < BYTES_PER_PACKET) {
        packet[packet_index] = serial_byte;
      }

      if (packet_index + 1 == BYTES_PER_PACKET) {
        uint32_t rgb = led_strip.Color(packet[1], packet[2], packet[3]);

        uint8_t group_index = packet[0];
        uint16_t end_led_index = group_index_to_led_range->get(group_index, 1);
        for (uint16_t led_index = group_index_to_led_range->get(group_index, 0); led_index < end_led_index; led_index++) {
          led_strip.setPixelColor(led_index, rgb);
        }
        packet_index = 0;
        packets_received_this_strip_state += 1;
      } else {
        packet_index++;
      }

      if (packets_received_this_strip_state == packets_expected_this_strip_state) {
        led_strip.show();
        is_a_new_strip_state = true;
      }
    }
  }
}