#!/bin/bash -e

WD=$(dirname $0)

source "${WD}/env/bin/activate"
python3 "${WD}/cartographer.py" $@
