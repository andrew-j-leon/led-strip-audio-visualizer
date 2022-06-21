#!/bin/bash

coverage run --omit=python/libraries/PySimpleGUI.py,*/__init__.py,*_test.py -m unittest discover -s ./python -p "*_test.py" -v
coverage html