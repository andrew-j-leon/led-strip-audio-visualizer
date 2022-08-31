default:
	g++ -Wall -W -Wconversion -Wshadow -Wcast-qual -Wwrite-strings -g \
	main_test.cpp packet_state_test.cpp ../packet_state.cpp strip_groups_test.cpp ../strip_groups.cpp \
	-lgtest -lgtest_main -o main_test

test:
	make && ./main_test