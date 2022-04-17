#!/bin/bash

autoflake --in-place --remove-all-unused-imports --recursive python
autopep8 --in-place -v --ignore E501 --recursive python
pipreqs --force python
git add -v .