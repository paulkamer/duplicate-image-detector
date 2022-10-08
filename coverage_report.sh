#!/bin/bash

# Probably because of OpenCV, the coverage report contains data for these two files which do not exist
touch config.py
touch config-3.py

python -m coverage report

rm config.py
rm config-3.py