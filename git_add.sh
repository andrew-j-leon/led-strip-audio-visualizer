#!/bin/bash

autoflake --in-place --remove-all-unused-imports --recursive python # remove unused imports
isort -l 140 --gitignore . -v # sort imports
autopep8 --in-place -v --ignore E501 --recursive python # formatting
pipreqs --force python # create requirements.txt
git add -v .