#!/bin/bash

coverage run -m unittest discover -s ./python -p "*_test.py" -v
coverage html