#include "matrix.h"

Matrix_uint16::Matrix_uint16(int number_of_rows, int number_of_columns) {
  this->number_of_rows = number_of_rows;
  this->number_of_columns = number_of_columns;
  this->matrix = new uint16_t[number_of_rows * number_of_columns];
}

Matrix_uint16::~Matrix_uint16() {
  delete[] this->matrix;
}

int Matrix_uint16::get_number_of_rows() {
  return this->number_of_rows;
}

uint16_t Matrix_uint16::get(int row_index, int column_index) {
  return matrix[column_index + (row_index * this->number_of_columns)];
}

void Matrix_uint16::set(int row_index, int column_index, uint16_t value) {
  matrix[column_index + (row_index * this->number_of_columns)] = value;
}