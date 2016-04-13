#!/bin/sh
pep8 $1 | ./pep8_wrapper.py > violations.json
./syntax_check.py violations.json $1 > errors.html
xdg-open errors.html