#!/bin/bash

autopep8 --in-place -v --ignore E501 --recursive client
autoflake --in-place --remove-all-unused-imports --recursive client
git add -v .