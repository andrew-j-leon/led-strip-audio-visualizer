#!/bin/bash

autoflake --in-place --remove-all-unused-imports --recursive python --exclude python/venv # remove unused imports
isort -l 140 --gitignore . -v # sort imports
autopep8 --in-place -v --ignore E501 --recursive python --exclude python/venv # formatting
pipreqs --force python --ignore python/venv # create requirements.txt

echo "pyserial==3.5" >> python/requirements.txt

git add -v .