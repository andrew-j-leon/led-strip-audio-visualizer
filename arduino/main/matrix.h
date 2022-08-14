#ifndef MATRIX_H
#define MATRIX_H

#include <Arduino.h>

class Matrix_uint16 {
  int number_of_rows;
  int number_of_columns;
  uint16_t* matrix;

public:
  Matrix_uint16(int number_of_rows, int number_of_columns);

  ~Matrix_uint16();

  int get_number_of_rows();

  uint16_t get(int row_index, int column_index);

  void set(int row_index, int column_index, uint16_t value);
};

#endif