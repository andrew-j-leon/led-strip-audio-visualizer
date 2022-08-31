#include <iostream>
using namespace std;

typedef unsigned char uint8;

int main() {

    uint8 a[] = {0x00, 0x10, 0x20, 0x30};

    cout << sizeof(a) << endl;

    return 0;
}