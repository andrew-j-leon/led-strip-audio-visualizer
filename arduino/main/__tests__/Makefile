OPTIONS = -Wall -W -Wconversion -Wshadow -Wcast-qual -Wwrite-strings -g -o main_test
LIBRARIES = -lgtest -lgtest_main
MAIN_SOURCE = main_test.cpp

DEFAULT_COMMAND = g++ $(OPTIONS) $(MAIN_SOURCE) $(LIBRARIES)

UTIL_SOURCE = ../util.cpp

ARRAY_SOURCE = ../array.cpp
ARRAY_TEST_SOURCE = array_test.cpp $(ARRAY_SOURCE)

PACKET_STATE_SOURCE = ../packet_state.cpp
PACKET_STATE_TEST_SOURCE = packet_state_test.cpp $(PACKET_STATE_SOURCE)

GROUP_SETUP_STATE_SOURCE = ../group_setup_state.cpp
GROUP_SETUP_STATE_TEST_SOURCE = group_setup_state_test.cpp $(GROUP_SETUP_STATE_SOURCE)

default:
	$(DEFAULT_COMMAND) $(GROUP_SETUP_STATE_TEST_SOURCE) $(PACKET_STATE_TEST_SOURCE) \
	$(ARRAY_TEST_SOURCE) $(UTIL_SOURCE)

test:
	make && ./main_test && make clean

test_array:
	$(DEFAULT_COMMAND) $(ARRAY_TEST_SOURCE) && ./main_test && make clean

test_strip_groups:
	$(DEFAULT_COMMAND) $(STRIP_GROUPS_TEST_SOURCE) $(ARRAY_SOURCE) && ./main_test && make clean

test_packet_state:
	$(DEFAULT_COMMAND) $(PACKET_STATE_TEST_SOURCE) && ./main_test && make clean

test_group_setup_state:
	$(DEFAULT_COMMAND) $(GROUP_SETUP_STATE_TEST_SOURCE) $(UTIL_SOURCE) && ./main_test && make clean

clean:
	rm ./main_test