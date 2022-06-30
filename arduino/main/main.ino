#include <Arduino.h>
#include <CDC.h>
#include <FastLED_NeoPixel.h>

#define SERIAL_BAUD_RATE 500000
#define NUMBER_OF_LEDS 600
#define PIN_NUMBER 7

struct LedStripType {
  uint8_t id;
  uint8_t number_of_bytes_per_packet;
};

struct LedStripType ARRAY;
struct LedStripType GROUPED;

class Matrix_uint16 {
    int number_of_rows;
    int number_of_columns;
    uint16_t* matrix;

    public:
        Matrix_uint16(int number_of_rows, int number_of_columns) {
            this->number_of_rows = number_of_rows;
            this->number_of_columns = number_of_columns;
            this->matrix = new uint16_t[number_of_rows * number_of_columns];
        }

        ~Matrix_uint16() {
            delete[] this->matrix;
        }

		int get_number_of_rows() {
			return this->number_of_rows;
		}

        uint16_t get(int row_index, int column_index) {
            return matrix[column_index + (row_index*this->number_of_columns)];
        }

        void set(int row_index, int column_index, uint16_t value) {
            matrix[column_index + (row_index*this->number_of_columns)] = value;
        }
};

uint8_t brightness;
uint8_t led_strip_type_id;

Matrix_uint16* group_index_to_led_range = nullptr;
uint8_t* packet = nullptr;

bool is_a_new_strip_state;
int packet_index;

uint8_t packets_expected_this_strip_state;
uint8_t packets_received_this_strip_state;

FastLED_NeoPixel<NUMBER_OF_LEDS, PIN_NUMBER, NEO_GRB> led_strip;


void setup() {
	deallocate_variables();

    Serial.begin(SERIAL_BAUD_RATE, SERIAL_8N1);
	while (!Serial) {
		;
	}

    uint16_t number_of_leds = (uint16_t)NUMBER_OF_LEDS;
    uint8_t buff[2];
    uint16_to_uint8(number_of_leds, buff);

    Serial.write(buff[1]); // the right byte of the number_of_leds
    Serial.write(buff[0]); // the left byte of the number_of_leds

	initialize_variables();
}

void deallocate_variables() {
	if (group_index_to_led_range != nullptr) {
		delete group_index_to_led_range;
		group_index_to_led_range = nullptr;
	}

	if (packet != nullptr) {
		delete[] packet;
		packet = nullptr;
	}
}

void initialize_variables() {
	is_a_new_strip_state = true;
    packet_index = 0;

	ARRAY.id = 0;
    ARRAY.number_of_bytes_per_packet = 7;

    GROUPED.id = 1;
    GROUPED.number_of_bytes_per_packet = 4;

	read_and_set_configuration_data_from_serial();
}

void read_and_set_configuration_data_from_serial() {
    read_and_set_led_strip_from_serial();
    read_and_set_led_strip_type_from_serial();

	if (led_strip_type_id == ARRAY.id) {
		packet = new uint8_t[ARRAY.number_of_bytes_per_packet];
	}

    else if (led_strip_type_id == GROUPED.id) {
		packet = new uint8_t[GROUPED.number_of_bytes_per_packet];
        read_and_set_group_indicies_to_led_ranges_from_serial();
    }
}

void read_and_set_led_strip_from_serial() {
    read_and_set_led_strip_brightness_from_serial();

    led_strip.setBrightness(brightness);

    led_strip.begin();
	led_strip.show();
}

void read_and_set_led_strip_brightness_from_serial() {
    brightness = read_and_echo_serial_byte();
}

void read_and_set_led_strip_type_from_serial() {
    led_strip_type_id = read_and_echo_serial_byte();
}

void read_and_set_group_indicies_to_led_ranges_from_serial() {
	uint8_t number_of_groups = read_and_echo_serial_byte();
	group_index_to_led_range = new Matrix_uint16(number_of_groups, 2);

	for (int row_index = 0; row_index < group_index_to_led_range->get_number_of_rows(); row_index++) {
        uint8_t start_index_left_byte = read_and_echo_serial_byte();
        uint8_t start_index_right_byte = read_and_echo_serial_byte();

        uint8_t end_index_left_byte = read_and_echo_serial_byte();
        uint8_t end_index_right_byte = read_and_echo_serial_byte();

		group_index_to_led_range->set(row_index, 0, uint8_to_uint16(start_index_left_byte, start_index_right_byte));
		group_index_to_led_range->set(row_index, 1, uint8_to_uint16(end_index_left_byte, end_index_right_byte));
    }
}

uint8_t read_and_echo_serial_byte() {
    while (!Serial.available()) {
        ;
    }
    uint8_t byte_ = Serial.read();
    Serial.write(byte_);
    return byte_;
}

uint16_t uint8_to_uint16(uint8_t left_bits, uint8_t right_bits) {
	return (uint16_t)(left_bits << 8 | right_bits);
}

void uint16_to_uint8(uint16_t value, uint8_t* buff) {
    buff[0] = value & 0xff;
    buff[1] = (value >> 8);
}

void loop() {
    if (Serial.available()) {
        handle_serial_byte();
    }
}

void handle_serial_byte() {

    uint8_t serial_byte = read_and_echo_serial_byte();

    if (is_a_new_strip_state) {
        packets_expected_this_strip_state = serial_byte;
        packets_received_this_strip_state = 0;

        if (packets_expected_this_strip_state > 0) {
            is_a_new_strip_state = false;
        }
    }

    else {
        if (packet_index < get_number_of_bytes_per_packet()) {
            packet[packet_index] = serial_byte;
        }

        if (packet_index + 1 == get_number_of_bytes_per_packet()) {
            set_led_colors_with_packet_data();
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

uint8_t get_number_of_bytes_per_packet() {
    if (led_strip_type_id == GROUPED.id) {
        return GROUPED.number_of_bytes_per_packet;
    }

    else if (led_strip_type_id == ARRAY.id) {
        return ARRAY.number_of_bytes_per_packet;
    }
}

void set_led_colors_with_packet_data() {
    if (led_strip_type_id == GROUPED.id) {
        set_grouped_led_colors_with_packet_data();
    }

    else if (led_strip_type_id == ARRAY.id) {
        set_array_led_colors_with_packet_data();
    }
}

void set_grouped_led_colors_with_packet_data() {
    uint32_t rgb = led_strip.Color(packet[1], packet[2], packet[3]);

    uint8_t group_index = packet[0];
    uint16_t end_led_index = group_index_to_led_range->get(group_index, 1);
    for (uint16_t led_index = group_index_to_led_range->get(group_index, 0); led_index < end_led_index; led_index++) {
        led_strip.setPixelColor(led_index, rgb);
    }
}

void set_array_led_colors_with_packet_data() {
    uint32_t rgb = led_strip.Color(packet[4], packet[5], packet[6]);

    uint16_t start_index = uint8_to_uint16(packet[0], packet[1]); // start_index (first 2 bytes [16 bits] represent the value of the start_index)
    uint16_t end_index = uint8_to_uint16(packet[2], packet[3]); // end_index (next 2 bytes represent the value of the end_index [exclusive])

    for (uint16_t i = start_index; i < end_index; i++) {
        led_strip.setPixelColor(i, rgb);
    }
}
